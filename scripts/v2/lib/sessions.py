#!/usr/bin/env python
"""`claude -p` sessions for the v2 pipeline (docs/v2/spec.md): a small thread pool with one retry per job, the usage-limit pause
copied from the v1 bulk driver, the .run/STOP file, a per-session timeout, a progress line per finished job and a summary.

    sys.path.insert(0, "scripts/v2"); from lib import sessions
    log, log_path = sessions.open_log("write")                      # build/runs/v2/write-<timestamp>.log
    stats = sessions.run_jobs(jobs, workers=4, label="write", model="sonnet", max_turns=40,
                              allowed_tools="Read,Write(content/articles/**)", timeout_s=2700, log=log, on_done=...)

A job is {"id": str, "prompt": str, "expect": [paths that must exist afterwards]}, plus two optional callables run in the worker
thread: "prepare" (before the session) and "check" (after it; returns a list of problems, non-empty counts as a failure).
on_done(job, ok, result, problems) runs once per finished job. A usage limit pauses every worker (Pause), requeues the job and
does not count as its retry. `python scripts/v2/lib/sessions.py probe` runs the one-turn haiku probe (exit 0 when the plan works).
CLAUDE_BIN overrides the executable name (tests point it at a stub).

Copied, trimmed, from archive/v1/worker/campus_worker/agents/dispatch.py (_USAGE, _cli_result_text) and
archive/v1/worker/campus_worker/bulk/headless.py (parse_reset, Pause, cli_probe, the worker loop).
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import threading
import time
from collections import deque
from datetime import datetime, timedelta
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
RUNS = REPO / "build" / "runs" / "v2"
STOP_FILE = REPO / ".run" / "STOP"
DEFAULT_PAUSE_MIN = 20
MAX_ATTEMPTS = 2        # one retry per job
MAX_SESSIONS = 4        # usage-limit requeues do not count as attempts, but no job runs more sessions than this
# the project settings allow more tools than a step needs (Edit, Bash(git ...)); these never run inside a pipeline session
DISALLOWED_TOOLS = "Bash,Edit,MultiEdit,NotebookEdit,Agent,Task"

# ------------------------------------------------------------------------------------------ copied from v1 (dispatch.py)
_USAGE = re.compile(r"(usage limit|hit your limit|rate limit|too many requests|\b429\b|not logged in|please run /login)", re.I)


def cli_result_text(stdout: str) -> tuple[dict | None, str]:
    """The JSON object `claude -p --output-format json` printed (the whole output, else the last JSON line), and its `result`
    text (or the raw stdout)."""
    out = (stdout or "").strip()
    for line in [out] + [l.strip() for l in reversed(out.splitlines())]:
        if line.startswith("{"):
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(d, dict):
                return d, d.get("result") if isinstance(d.get("result"), str) else stdout
    return None, stdout or ""


# ------------------------------------------------------------------------------------------ copied from v1 (headless.py)
RESET_IN = re.compile(r"resets?\s+in\s+(?:about\s+)?(\d+)\s*(minute|min|hour|hr|h)", re.I)
RESET_AT = re.compile(r"resets?\s+at\s+(\d{1,2})(?::(\d{2}))?\s*([ap]m)?", re.I)


def parse_reset(text: str, *, now: datetime | None = None) -> datetime | None:
    now = now or datetime.now()
    m = RESET_IN.search(text or "")
    if m:
        n, unit = int(m.group(1)), m.group(2).lower()
        return now + timedelta(hours=n) if unit.startswith("h") else now + timedelta(minutes=n)
    m = RESET_AT.search(text or "")
    if m:
        hour, minute, ampm = int(m.group(1)), int(m.group(2) or 0), (m.group(3) or "").lower()
        if ampm == "pm" and hour < 12:
            hour += 12
        if ampm == "am" and hour == 12:
            hour = 0
        t = now.replace(hour=hour % 24, minute=minute, second=0, microsecond=0)
        return t if t > now else t + timedelta(days=1)
    return None


def stopped() -> bool:
    return STOP_FILE.exists()


class Pause:
    """Shared by the worker threads: a usage limit pauses every worker cleanly (sessions in flight finish on their own); one probe
    session after the reset time clears it, or extends the pause when the limit still holds."""

    def __init__(self, *, log=print, probe=None, sleep=time.sleep, now=None):
        self.lock = threading.Lock()
        self.until: datetime | None = None
        self.reason = ""
        self.pauses = 0
        self.log, self.probe, self.sleep, self.now = log, probe, sleep, (now or datetime.now)

    def trigger(self, text: str) -> None:
        with self.lock:
            until = parse_reset(text, now=self.now()) or (self.now() + timedelta(minutes=DEFAULT_PAUSE_MIN))
            if self.until is None or until > self.until:
                self.until, self.reason = until, (text or "")[:200]
                self.pauses += 1
                self.log(f"PAUSED on a usage limit until about {until.strftime('%H:%M')} ({self.reason[:120]!r}); sessions in flight finish, nothing new starts")

    def wait_if_paused(self) -> None:
        while True:
            with self.lock:
                until = self.until
            if until is None or stopped():
                return
            remaining = (until - self.now()).total_seconds()
            if remaining > 0:
                self.sleep(min(60, remaining))
                continue
            with self.lock:
                if self.until is None:
                    return
                ok = self.probe() if self.probe else True
                if ok:
                    self.log("usage limit cleared; resuming")
                    self.until = None
                    return
                self.until = self.now() + timedelta(minutes=DEFAULT_PAUSE_MIN)
                self.log(f"still limited; next probe at about {self.until.strftime('%H:%M')}")


def cli_probe(model: str = "haiku") -> bool:
    r = run_session("Reply with exactly: OK", model=model, max_turns=1, allowed_tools="Read", timeout_s=120)
    return not r["usage_limit"] and r["code"] == 0


# ------------------------------------------------------------------------------------------ sessions
def run_session(prompt: str, *, model: str = "sonnet", max_turns: int = 40, allowed_tools: str = "Read", timeout_s: int = 1500) -> dict:
    """One `claude -p` session. Returns code, text (the result), err, usage_limit, duration_s, turns, cost_usd, is_error."""
    cmd = [os.environ.get("CLAUDE_BIN", "claude"), "-p", prompt, "--output-format", "json", "--permission-mode", "dontAsk",
           "--model", model, "--max-turns", str(max_turns), "--allowedTools", allowed_tools, "--disallowedTools", DISALLOWED_TOOLS]
    env = dict(os.environ)
    env["PATH"] = f"{Path.home()}/.local/bin:" + env.get("PATH", "")
    env["CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS"] = "0"
    t0 = time.monotonic()
    try:
        p = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, timeout=timeout_s, env=env, stdin=subprocess.DEVNULL)
        code, out, err = p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired as e:
        out = e.stdout.decode("utf-8", "replace") if isinstance(e.stdout, bytes) else (e.stdout or "")
        code, err = 124, f"timeout after {timeout_s}s"
    cli, text = cli_result_text(out)
    return {"code": code, "text": text or "", "err": err or "", "usage_limit": bool(_USAGE.search((text or "") + " " + (err or ""))),
            "duration_s": round(time.monotonic() - t0, 1), "turns": (cli or {}).get("num_turns"),
            "cost_usd": (cli or {}).get("total_cost_usd"), "is_error": bool((cli or {}).get("is_error"))}


def run_jobs(jobs: list[dict], *, workers: int, label: str, model: str, max_turns: int, allowed_tools: str, timeout_s: int,
             log=print, on_done=None) -> dict:
    """Run the jobs on `workers` threads. Returns {"jobs", "ok", "failed", "sessions", "stopped", "not_started", "hours", "pauses"}."""
    q: deque = deque(dict(j, attempts=0, sessions=0) for j in jobs)
    lock = threading.Lock()
    pause = Pause(log=log, probe=cli_probe)
    stats = {"jobs": len(jobs), "ok": 0, "failed": 0, "sessions": 0, "stopped": False}
    t0 = time.monotonic()
    sess_dir = RUNS / "sessions"
    sess_dir.mkdir(parents=True, exist_ok=True)
    empty = {"code": None, "text": "", "err": "", "usage_limit": False, "duration_s": 0.0, "turns": None, "cost_usd": None, "is_error": False}

    def hours() -> float:
        return max(1e-6, (time.monotonic() - t0) / 3600)

    def finish(job: dict, ok: bool, r: dict, problems: list[str]) -> None:
        with lock:
            stats["ok" if ok else "failed"] += 1
            done = stats["ok"] + stats["failed"]
        note = f": {'; '.join(problems)[:300]}" if problems else ""
        log(f"[{label}] {done}/{stats['jobs']} {'ok' if ok else 'FAILED'} {job['id']} ({r['duration_s'] / 60:.1f} min, "
            f"{r['turns'] if r['turns'] is not None else '?'} turns, {job['sessions']} session(s)){note} | {done / hours():.1f} jobs/h")
        if on_done:
            try:
                on_done(job, ok, r, problems)
            except Exception as e:  # noqa: BLE001 - a bookkeeping error never kills a worker
                log(f"[{label}] on_done failed for {job['id']}: {type(e).__name__}: {str(e)[:200]}")

    def worker(i: int) -> None:
        while True:
            pause.wait_if_paused()
            if stopped():
                with lock:
                    stats["stopped"] = True
                return
            with lock:
                if not q:
                    return
                job = q.popleft()
            try:
                if job.get("prepare"):
                    job["prepare"]()
            except Exception as e:  # noqa: BLE001
                finish(job, False, empty, [f"prepare failed: {type(e).__name__}: {str(e)[:200]}"])
                continue
            r = run_session(job["prompt"], model=model, max_turns=max_turns, allowed_tools=allowed_tools, timeout_s=timeout_s)
            with lock:
                stats["sessions"] += 1
                job["sessions"] += 1
            (sess_dir / f"{label}-{job['id']}-{job['sessions']}.txt").write_text(
                f"exit {r['code']} turns {r['turns']} duration {r['duration_s']}s cost {r['cost_usd']}\n\n{r['text']}\n\n--- stderr ---\n{r['err'][-3000:]}\n")
            if r["usage_limit"]:
                pause.trigger(r["text"] + " " + r["err"])
            elif r["code"] == 124:   # a session that hits the timeout is being throttled (v1 lesson): pause and probe before anything new starts
                pause.trigger(f"session timed out after {timeout_s}s (throttling); probing before new sessions")
                if job["sessions"] < MAX_SESSIONS:
                    with lock:
                        q.append(job)
                    continue
                finish(job, False, r, ["usage limit"])
                continue
            problems = [f"missing {p}" for p in job.get("expect", []) if not Path(p).exists()]
            if not problems and job.get("check"):
                problems = list(job["check"]() or [])
            if problems and r["code"] != 0:
                problems.append(f"exit {r['code']}: {(r['err'] or r['text'])[:200]}")
            elif r["code"] != 0:   # the files are there and pass their check, but the CLI died (network, API error): say so, the page may have skipped its last passes
                log(f"[{label}] {job['id']}: session exited {r['code']} after writing the page ({(r['err'] or r['text']).strip()[:160]}); counted as done because the page passes its checks")
            job["attempts"] += 1
            if problems and job["attempts"] < MAX_ATTEMPTS and not stopped():
                log(f"[{label}] retry {job['id']}: {'; '.join(problems)[:200]}")
                with lock:
                    q.append(job)
                continue
            finish(job, not problems, r, problems)

    threads = [threading.Thread(target=worker, args=(i,), daemon=True, name=f"{label}-{i}") for i in range(max(1, workers))]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    stats["not_started"] = len(q)
    stats["hours"] = round(hours(), 3)
    stats["pauses"] = pause.pauses
    log(f"[{label}] summary: {stats['ok']} ok, {stats['failed']} failed of {stats['jobs']} jobs; {stats['sessions']} sessions; "
        f"{stats['hours']:.2f} h; {stats['ok'] / hours():.1f} jobs/h; {stats['pauses']} pause(s)"
        + ("; STOPPED" if stats["stopped"] else "") + (f"; {len(q)} not started" if q else ""))
    return stats


# ------------------------------------------------------------------------------------------ small helpers for the step scripts
def open_log(step: str):
    """A thread-safe log(msg) that prints and appends to build/runs/v2/<step>-<timestamp>.log; returns (log, path)."""
    RUNS.mkdir(parents=True, exist_ok=True)
    path = RUNS / f"{step}-{datetime.now().strftime('%Y%m%dT%H%M%S')}.log"
    lock = threading.Lock()

    def log(msg: str) -> None:
        line = f"{datetime.now().strftime('%H:%M:%S')} {msg}"
        with lock:
            print(line, flush=True)
            with path.open("a", encoding="utf-8") as fh:
                fh.write(line + "\n")

    log(f"log: {path.relative_to(REPO)}")
    return log, path


def clear_stop(log=print) -> None:
    """A step start removes a STOP file left by an earlier run (stop.sh creates it; it would end the new run at once)."""
    if STOP_FILE.exists():
        STOP_FILE.unlink()
        log("removed a stale .run/STOP from an earlier stop")


def fill(template: str, **values) -> str:
    """Replace {{name}} placeholders; a placeholder left unfilled is a bug, so it raises."""
    for k, v in values.items():
        template = template.replace("{{" + k + "}}", str(v))
    left = re.findall(r"{{([a-z_]+)}}", template)
    if left:
        raise KeyError(f"prompt placeholders not filled: {sorted(set(left))}")
    return template


def save_prompt(label: str, job_id: str, prompt: str) -> Path:
    d = RUNS / "prompts"
    d.mkdir(parents=True, exist_ok=True)
    p = d / f"{label}-{job_id}.md"
    p.write_text(prompt, encoding="utf-8")
    return p


if __name__ == "__main__":
    if sys.argv[1:2] == ["probe"]:
        ok = cli_probe()
        print("OK" if ok else "LIMITED or failed")
        sys.exit(0 if ok else 1)
    print(__doc__)
    sys.exit(2)
