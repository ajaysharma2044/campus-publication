"""SUBSCRIPTION-ONLY bulk mode (owner decision 2026-11-07, overrides specs/bulk-mode.md where they conflict): the same stages run
through parallel `claude -p` workers on the owner's subscription instead of the Message Batches API. Never the API.

A worker session handles one chunk of pages and nothing else: it Reads the page files the driver exported and Writes one JSON file
per page inside its run folder (the only tools it is allowed). Code does everything after that: the verbatim-quote check (the same
`extract.process_results`), the dossier and question map, the code checks, verdict application, publishing, the preview redeploy every
25 pages, the progress report (pages published, pages per hour), and the clean pause / auto-resume when the plan's usage limit hits.
`.run/STOP` (scripts/stop.sh) stops the run after the sessions in flight.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import threading
import time
from collections import deque
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import UUID

from ..agents.dispatch import _USAGE, _cli_result_text
from ..config import REPO_ROOT
from ..db import connect
from . import check as checkmod
from . import crawl as crawlmod
from . import dossier as dossiermod
from . import extract as extractmod
from . import plan as planmod
from . import questions as questionsmod
from . import rank as rankmod
from . import verify as verifymod
from . import write as writemod
from .batch_client import BatchResult
from .util import json_default

RUN_ROOT = REPO_ROOT / "build" / "bulk" / "headless"
STOP_FILE = REPO_ROOT / ".run" / "STOP"
ALLOWED_TOOLS = "Read,Write(build/bulk/headless/**)"
DEFAULT_PAUSE_MIN = 20
MAX_ATTEMPTS = 2
MIN_CLAIMS_PER_PAGE = 2   # a page with a single supported fact is thin; two verified facts is the floor (owner's lean minimum is one, raised after the first article pass)


# ----------------------------------------------------------------------------------------------- sessions
@dataclass
class SessionResult:
    code: int
    text: str
    err: str
    usage_limit: bool
    duration_s: float
    turns: int | None = None
    cost_usd: float | None = None


def run_session(prompt: str, *, model: str = "sonnet", max_turns: int = 40, timeout_s: int = 1500, runner=None) -> SessionResult:
    """One `claude -p` session with Read + path-scoped Write only (no Bash, no git). `runner` replaces the CLI in tests."""
    if runner is not None:
        return runner(prompt, model=model, max_turns=max_turns)
    cmd = ["claude", "-p", prompt, "--output-format", "json", "--permission-mode", "dontAsk", "--model", model, "--max-turns", str(max_turns), "--allowedTools", ALLOWED_TOOLS]
    env = dict(os.environ)
    env["PATH"] = f"{Path.home()}/.local/bin:" + env.get("PATH", "")
    env["CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS"] = "0"
    t0 = time.monotonic()
    try:
        p = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True, timeout=timeout_s, env=env, stdin=subprocess.DEVNULL)
        code, out, err = p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired as e:
        code, out, err = 124, (e.stdout or "") if isinstance(e.stdout, str) else "", f"timeout after {timeout_s}s"
    cli, text = _cli_result_text(out)
    limit = bool(_USAGE.search((text or "") + " " + (err or "")))
    return SessionResult(code, text or "", err or "", limit, round(time.monotonic() - t0, 1), (cli or {}).get("num_turns"), (cli or {}).get("total_cost_usd"))


def stopped() -> bool:
    return STOP_FILE.exists()


# ----------------------------------------------------------------------------------------------- usage-limit pause
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
            if until is None:
                return
            if stopped():
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


def cli_probe(model: str = "haiku", runner=None) -> bool:
    r = run_session("Reply with exactly: OK", model=model, max_turns=1, timeout_s=120, runner=runner)
    return not r.usage_limit and r.code == 0


# ----------------------------------------------------------------------------------------------- shared worker loop
class Progress:
    def __init__(self, run_dir: Path, *, log=print):
        self.run_dir, self.log = run_dir, log
        self.lock = threading.Lock()
        self.started = time.monotonic()
        self.counts: dict[str, int] = {}
        self.cost_usd = 0.0
        self.sessions = 0

    def add(self, **kw) -> None:
        with self.lock:
            for k, v in kw.items():
                self.counts[k] = self.counts.get(k, 0) + int(v)

    def session(self, r: SessionResult) -> None:
        with self.lock:
            self.sessions += 1
            self.cost_usd += float(r.cost_usd or 0)

    def hours(self) -> float:
        return max(1e-6, (time.monotonic() - self.started) / 3600)

    def line(self, stage: str) -> str:
        c = dict(self.counts)
        per_hour = {k: round(v / self.hours(), 1) for k, v in c.items() if k in ("pages", "published")}
        return f"[{stage}] {json.dumps(c)} per hour {json.dumps(per_hour)} sessions {self.sessions} session-cost-equivalent ${self.cost_usd:.2f} elapsed {self.hours():.2f} h"

    def write(self, stage: str, extra: dict | None = None) -> None:
        self.run_dir.mkdir(parents=True, exist_ok=True)
        with (self.run_dir / "progress.jsonl").open("a") as fh:
            fh.write(json.dumps({"ts": datetime.now(timezone.utc).isoformat(), "stage": stage, "counts": self.counts, "sessions": self.sessions, "cost_usd": round(self.cost_usd, 2), "hours": round(self.hours(), 3), **(extra or {})}, default=json_default) + "\n")


def _dsn(dsn: str | None = None) -> str:
    if dsn:
        return dsn
    from ..config import get_settings

    return os.environ.get("DATABASE_URL") or get_settings().database_url


def run_chunks(chunks: list, *, workers: int, handle, pause: Pause, log=print, label: str, dsn: str | None = None) -> dict:
    """Run `handle(chunk, conn)` over the chunks with `workers` threads (one DB connection each); `handle` returns (ok, requeue_chunk)
    and raises nothing. A usage limit inside handle is signalled by returning (False, chunk) after pause.trigger()."""
    q: deque = deque(chunks)
    lock = threading.Lock()
    stats = {"chunks": len(chunks), "done": 0, "requeued": 0, "stopped": False}
    dsn = _dsn(dsn)

    def worker(i: int) -> None:
        conn = connect(dsn)
        try:
            while True:
                if stopped():
                    with lock:
                        stats["stopped"] = True
                    return
                pause.wait_if_paused()
                with lock:
                    if not q:
                        return
                    chunk = q.popleft()
                try:
                    ok, requeue = handle(chunk, conn)
                except Exception as e:  # noqa: BLE001 — one chunk never kills a worker
                    conn.rollback()
                    log(f"  {label} worker {i}: chunk failed: {type(e).__name__}: {str(e)[:160]}")
                    ok, requeue = False, None
                with lock:
                    stats["done"] += 1 if ok else 0
                    if requeue:
                        q.append(requeue)
                        stats["requeued"] += 1
        finally:
            conn.close()

    threads = [threading.Thread(target=worker, args=(i,), daemon=True, name=f"{label}-{i}") for i in range(max(1, workers))]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return stats


# ----------------------------------------------------------------------------------------------- extraction
EXTRACT_WORKER_RULES = """You are an extraction worker in a batch run. For EACH page listed below: use Read on the page file, then use Write to create its
output file with ONE JSON object following the extraction rules. Do nothing else: no other files, no commands, no web. Work through
the whole list even if some pages have no usable facts (then write {"claims": [], "entities": [], "processes": []}). When every output
file exists, reply with exactly: DONE <number of files written>

EXTRACTION RULES
"""


def extraction_prompt(pairs: list[tuple[str, str]]) -> str:
    listing = "\n".join(f"- read {src} → write {dst}" for src, dst in pairs)
    return EXTRACT_WORKER_RULES + extractmod.EXTRACTION_SYSTEM + "\n\nPAGES\n" + listing + "\n"


def extract_stage(*, school: str, run_id: str, workers: int = 6, chunk_size: int = 10, model: str = "sonnet", pause: Pause, log=print, runner=None, max_chunks: int | None = None,
                  progress: Progress | None = None, dsn: str | None = None) -> dict:
    dsn = _dsn(dsn)
    run_dir = RUN_ROOT / run_id
    pages_dir, out_dir = run_dir / "pages", run_dir / "extract"
    pages_dir.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)
    progress = progress or Progress(run_dir, log=log)
    conn = connect(dsn)
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM institutions WHERE slug=%s", (school,))
            inst = cur.fetchone()["id"]
            cur.execute("SELECT id FROM places")
            places = [r["id"] for r in cur.fetchall()]
        try:
            cfg = crawlmod.load_config(school)
        except FileNotFoundError:
            cfg = {"sections": []}   # a school without a crawl config (fixtures): every page falls under the default topic
        topic_by_section = extractmod.section_topic(conn, cfg)
        pending = extractmod.pending_snapshots(conn, institution_id=inst, place_ids=places, limit=100_000)
    finally:
        conn.close()
    log(f"extract: {len(pending)} pages pending, {workers} workers, {chunk_size} pages per session, model {model}")
    rel = lambda p: str(p.relative_to(REPO_ROOT))
    for s in pending:
        f = pages_dir / f"{s['id']}.txt"
        if not f.exists():
            f.write_text(f"PAGE URL: {s['url']}\nPUBLISHER: {s.get('publisher') or ''}\nSECTION: {s.get('crawl_section') or 'default'}\nFETCHED: {s['fetched_at'].date().isoformat() if s.get('fetched_at') else ''}\n\nPAGE TEXT:\n"
                         + (s["retained_text"] or "")[:extractmod.PAGE_TEXT_LIMIT])
    chunks = [[str(s["id"]) for s in pending[i:i + chunk_size]] for i in range(0, len(pending), chunk_size)]
    if max_chunks:
        chunks = chunks[:max_chunks]
    attempts: dict[str, int] = {}
    counter = {"n": 0}
    clock = threading.Lock()

    def handle(chunk: list[str], conn) -> tuple[bool, list | None]:
        with clock:
            counter["n"] += 1
            n = counter["n"]
        pairs = [(rel(pages_dir / f"{sid}.txt"), rel(out_dir / f"{sid}.json")) for sid in chunk]
        r = run_session(extraction_prompt(pairs), model=model, max_turns=4 * len(chunk) + 6, timeout_s=900, runner=runner)
        progress.session(r)
        if r.usage_limit:
            pause.trigger(r.text + " " + r.err)
            return False, chunk
        if r.code == 124:   # a 10-page session normally takes under a minute; a 15-minute stall means the plan is being throttled: pause, probe, resume
            pause.trigger("session timed out after 15 minutes (plan throttling); pausing before new sessions")
        results, missing = [], []
        for sid in chunk:
            f = out_dir / f"{sid}.json"
            if f.exists() and f.stat().st_size > 2:
                results.append(BatchResult(f"extract:{sid}", True, f.read_text(), {}, None, f"headless:{model}"))
            else:
                missing.append(sid)
        stats = extractmod.process_results(conn, results, model=f"headless:{model}", topic_by_section=topic_by_section, batch_id=f"headless:{run_id}:{n}", default_institution_id=inst) if results else {}
        progress.add(pages=len(results), claims=stats.get("claims_stored", 0), dropped_no_quote=stats.get("claims_dropped_no_quote", 0), entities=stats.get("entities_created", 0), processes=stats.get("processes", 0))
        retry = []
        for sid in missing:
            attempts[sid] = attempts.get(sid, 0) + 1
            if attempts[sid] >= MAX_ATTEMPTS:
                with conn.cursor() as cur:
                    cur.execute("UPDATE fetch_snapshots SET extracted_at=now(), extraction_batch_id=%s WHERE id=%s", (f"headless:{run_id}:skipped", UUID(sid)))
                conn.commit()
                progress.add(skipped=1)
            else:
                retry.append(sid)
        log(f"  extract chunk {n}: {len(results)}/{len(chunk)} pages, {stats.get('claims_stored', 0)} claims stored ({stats.get('claims_dropped_no_quote', 0)} dropped without a verbatim quote), {r.duration_s}s, turns {r.turns}; " + progress.line("extract"))
        progress.write("extract", {"chunk": n, "pages": len(results), "claims": stats.get("claims_stored", 0), "session_s": r.duration_s})
        return True, (retry or None)

    stats = run_chunks(chunks, workers=workers, handle=handle, pause=pause, log=log, label="extract", dsn=dsn)
    out = {"pending_at_start": len(pending), "chunks": len(chunks), **stats, "counts": dict(progress.counts), "sessions": progress.sessions, "hours": round(progress.hours(), 2)}
    log("extract done: " + json.dumps(out))
    return out


# ----------------------------------------------------------------------------------------------- dossier
def dossier_stage(*, school: str, log=print, dsn: str | None = None, _retry: bool = True) -> dict:
    import psycopg as _pg

    try:
        return _dossier_stage(school=school, log=log, dsn=dsn)
    except _pg.OperationalError as e:
        if not _retry:
            raise
        log(f"dossier: database connection dropped ({str(e)[:80]}); reconnecting once and retrying (the inserts are idempotent)")
        time.sleep(15)
        return dossier_stage(school=school, log=log, dsn=dsn, _retry=False)


def _dossier_stage(*, school: str, log=print, dsn: str | None = None) -> dict:
    conn = connect(_dsn(dsn))
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM institutions WHERE slug=%s", (school,))
            inst = cur.fetchone()["id"]
        q = questionsmod.build(conn, slug=school)
        r = rankmod.rank_all(conn, institution_id=inst, practical_first=True)
        q["by_class"] = r["by_class"]
        d = dossiermod.build(conn, slug=school, question_stats=q)
        out = {"questions": q["total"], "ranked": r["ranked"], "by_class": r["by_class"], "claims": d.get("claims"), "entities_with_facts": d.get("entities_with_facts"), "path": d.get("path")}
        log("dossier: " + json.dumps(out, default=str))
        return out
    finally:
        conn.close()


# ----------------------------------------------------------------------------------------------- articles
WRITE_WORKER_RULES = """You are a writing worker in a batch run. For EACH page listed below: use Read on its packet file (the question, audience, facts with
quotes, win note and link targets), then use Write to create its draft file with ONE JSON object following the writing rules. Do nothing
else: no other files, no commands, no web, no outside knowledge. When every draft file exists, reply with exactly: DONE <number of files written>

WRITING RULES
"""
VERIFY_WORKER_RULES = """You are a verification worker in a batch run. For EACH page listed below: use Read on its claims file, then use Write to create its verdict
file with ONE JSON object following the verification rules. Do nothing else. When every verdict file exists, reply with exactly: DONE <number of files written>

VERIFICATION RULES
"""


def _deploy(log=print) -> dict:
    r = subprocess.run(["bash", str(REPO_ROOT / "scripts" / "deploy_netlify.sh")], capture_output=True, text=True, timeout=900, cwd=REPO_ROOT)
    ok = r.returncode == 0 and "Deploy is live" in (r.stdout + r.stderr)
    log("deploy: " + ("live" if ok else f"failed exit {r.returncode}: {(r.stdout + r.stderr)[-300:]}"))
    return {"ok": ok, "exit": r.returncode}


def articles_stage(*, school: str, run_id: str, workers: int = 6, chunk_size: int = 5, verify_chunk: int = 8, model: str = "sonnet", pause: Pause, log=print, runner=None,
                   deploy_every: int = 25, batch_limit: int = 120, max_batches: int | None = None, deploy: bool = True, progress: Progress | None = None, settings=None, dsn: str | None = None) -> dict:
    dsn = _dsn(dsn)
    from ..config import get_settings
    from ..render import site
    from .run import _pages, _set

    settings = settings or get_settings()
    run_dir = RUN_ROOT / run_id
    art_dir = run_dir / "articles"
    art_dir.mkdir(parents=True, exist_ok=True)
    progress = progress or Progress(run_dir, log=log)
    rel = lambda p: str(p.relative_to(REPO_ROOT))
    today = datetime.now(timezone.utc).date()
    report = {"published": 0, "skipped": {}, "failed": 0, "batches": 0, "deploys": 0, "stopped": False}
    since_deploy = {"n": 0}

    def milestone(conn) -> None:
        site.render_shell(conn, out_root=site.OUT_DEFAULT, environment="staging", publication_name=settings.publication_name)
        if deploy:
            d = _deploy(log)
            report["deploys"] += 1 if d["ok"] else 0
        per_hour = report["published"] / progress.hours()
        line = f"REPORT: {report['published']} pages published in {progress.hours():.2f} h ({per_hour:.1f} pages/hour); skipped {sum(report['skipped'].values())}, failed {report['failed']}; sessions {progress.sessions}; session-cost-equivalent ${progress.cost_usd:.2f}"
        log(line)
        progress.write("articles", {"published": report["published"], "pages_per_hour": round(per_hour, 1), "skipped": report["skipped"], "failed": report["failed"]})
        (run_dir / "progress.md").write_text(f"# Subscription-only run {run_id}\n\n{line}\n\nSkip reasons: {json.dumps(report['skipped'])}\n")
        day = datetime.now(timezone.utc).date().isoformat()
        digest = REPO_ROOT / "docs" / "digest" / f"{day}.md"
        digest.parent.mkdir(parents=True, exist_ok=True)
        with digest.open("a") as fh:
            fh.write(f"\n- {datetime.now(timezone.utc).strftime('%H:%M')} UTC subscription-only run `{run_id}`: {line}\n")

    while not stopped():
        conn = connect(dsn)
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT id, canonical_name FROM institutions WHERE slug=%s", (school,))
                inst_row = cur.fetchone()
            inst, school_name = inst_row["id"], inst_row["canonical_name"]
            if not _pages(conn, run_id=run_id, stages=("planned", "gathered", "written", "checked", "verified")):
                out = planmod.plan_pages(conn, institution_id=inst, limit=batch_limit, run_id=run_id)
                for s in out["skipped"]:
                    report["skipped"][s["reason"]] = report["skipped"].get(s["reason"], 0) + 1
                if not out["planned"]:
                    log("articles: no queued questions left to plan")
                    break
                report["batches"] += 1
                log(f"articles batch {report['batches']}: {len(out['planned'])} pages planned ({len(out['skipped'])} skipped)")
            conn.commit()
            for p in _pages(conn, run_id=run_id, stages=("planned",)):
                g = planmod.gather(conn, p, institution_id=inst)
                if g["fact_count"] == 0:
                    report["skipped"]["no verified fact with a quote in scope"] = report["skipped"].get("no verified fact with a quote in scope", 0) + 1
            # ---- write
            gathered = _pages(conn, run_id=run_id, stages=("gathered",))
            for p in gathered:
                (art_dir / f"{p['id']}.packet.md").write_text(writemod.user_turn(p, school_name=school_name, today=today))
            by_id = {str(p["id"]): p for p in gathered}
            chunks = [[str(p["id"]) for p in gathered[i:i + chunk_size]] for i in range(0, len(gathered), chunk_size)]

            def write_handle(chunk, wconn):
                pairs = [(rel(art_dir / f"{pid}.packet.md"), rel(art_dir / f"{pid}.draft.json")) for pid in chunk]
                r = run_session(WRITE_WORKER_RULES + writemod.WRITER_SYSTEM + "\n\nPAGES\n" + "\n".join(f"- read {a} → write {b}" for a, b in pairs) + "\n", model=model, max_turns=4 * len(chunk) + 6, timeout_s=900, runner=runner)
                progress.session(r)
                if r.usage_limit:
                    pause.trigger(r.text + " " + r.err)
                    return False, chunk
                if r.code == 124:
                    pause.trigger("session timed out after 15 minutes (plan throttling); pausing before new sessions")
                for pid in chunk:
                    f = art_dir / f"{pid}.draft.json"
                    if not f.exists() and r.code == 124:
                        continue   # stays 'gathered'; the next pass writes it after the pause
                    draft, err = writemod.parse_draft(f.read_text()) if f.exists() else (None, "no draft file written")
                    if draft is None:
                        _set(wconn, UUID(pid), stage="failed", skip_reason=f"write: {err}")
                        report["failed"] += 1
                    else:
                        _set(wconn, UUID(pid), stage="written", draft=draft)
                progress.add(drafts=sum(1 for pid in chunk if (art_dir / f"{pid}.draft.json").exists()))
                log(f"  write chunk: {len(chunk)} pages, {r.duration_s}s, turns {r.turns}; " + progress.line("articles"))
                return True, None

            conn.commit()   # end the read transaction before the long wait: the hosted DB closes idle-in-transaction sessions
            if chunks:
                st = run_chunks(chunks, workers=workers, handle=write_handle, pause=pause, log=log, label="write", dsn=dsn)
                if st.get("stopped"):
                    report["stopped"] = True
                    break
                conn.close()
                conn = connect(dsn)
            # ---- check (code)
            with conn.cursor() as cur:
                cur.execute("SELECT v.body_markdown FROM pages p JOIN page_versions v ON v.id=p.current_version_id WHERE p.institution_id=%s AND v.gate_status='passed'", (inst,))
                existing = [r["body_markdown"] for r in cur.fetchall()]
            for p in _pages(conn, run_id=run_id, stages=("written",)):
                snaps = list({f["snapshot_id"] for f in p["gathered"]["facts"]})
                with conn.cursor() as cur:
                    cur.execute("SELECT id::text AS id, retained_text FROM fetch_snapshots WHERE id = ANY(%s::uuid[])", (snaps,))
                    texts = {r["id"]: r["retained_text"] or "" for r in cur.fetchall()}
                draft, rep = checkmod.check_draft(p["draft"], p["gathered"], question=p["plan"].get("primary_query") or p["plan"]["question"], hubs=p["gathered"].get("hubs") or [], existing_bodies=existing, source_texts=texts)
                if rep["status"] == "ok":
                    _set(conn, p["id"], stage="checked", draft=draft, checks=rep)
                else:
                    _set(conn, p["id"], stage="skipped", draft=draft, checks=rep, skip_reason="check: " + "; ".join(rep["reasons"]))
                    key = "check: " + "; ".join(rep["reasons"])[:80]
                    report["skipped"][key] = report["skipped"].get(key, 0) + 1
            # ---- verify (one pass)
            checked = _pages(conn, run_id=run_id, stages=("checked",))
            for p in checked:
                (art_dir / f"{p['id']}.claims.md").write_text(verifymod.build_request(p, model=model).user)
            vchunks = [[str(p["id"]) for p in checked[i:i + verify_chunk]] for i in range(0, len(checked), verify_chunk)]
            cby = {str(p["id"]): p for p in checked}

            def verify_handle(chunk, vconn):
                pairs = [(rel(art_dir / f"{pid}.claims.md"), rel(art_dir / f"{pid}.verdict.json")) for pid in chunk]
                r = run_session(VERIFY_WORKER_RULES + verifymod.VERIFY_SYSTEM + "\n\nPAGES\n" + "\n".join(f"- read {a} → write {b}" for a, b in pairs) + "\n", model=model, max_turns=4 * len(chunk) + 6, timeout_s=900, runner=runner)
                progress.session(r)
                if r.usage_limit:
                    pause.trigger(r.text + " " + r.err)
                    return False, chunk
                if r.code == 124:
                    pause.trigger("session timed out after 15 minutes (plan throttling); pausing before new sessions")
                for pid in chunk:
                    p = cby[pid]
                    f = art_dir / f"{pid}.verdict.json"
                    draft, rep = verifymod.apply_verdicts(p["draft"], f.read_text() if f.exists() else None)
                    survives = len(draft.get("claims") or []) >= MIN_CLAIMS_PER_PAGE and checkmod._words(draft.get("answer") or "") >= 8
                    reason = None if survives else ("verify: no supported claim left in the answer" if not draft.get("claims") else f"verify: fewer than {MIN_CLAIMS_PER_PAGE} supported facts (thin page)")
                    _set(vconn, UUID(pid), stage="verified" if survives else "skipped", draft=draft, verdicts=rep, skip_reason=reason)
                    if not survives:
                        report["skipped"][reason] = report["skipped"].get(reason, 0) + 1
                log(f"  verify chunk: {len(chunk)} pages, {r.duration_s}s; " + progress.line("articles"))
                return True, None

            conn.commit()
            if vchunks:
                st = run_chunks(vchunks, workers=workers, handle=verify_handle, pause=pause, log=log, label="verify", dsn=dsn)
                if st.get("stopped"):
                    report["stopped"] = True
                    break
                conn.close()
                conn = connect(dsn)
            # ---- publish
            for p in _pages(conn, run_id=run_id, stages=("verified",)):
                try:
                    verifymod.publish(conn, p, institution_id=inst, settings=settings, model=f"headless:{model}", run_id=run_id)
                    report["published"] += 1
                    progress.add(published=1)
                    since_deploy["n"] += 1
                except Exception as e:  # noqa: BLE001
                    conn.rollback()
                    _set(conn, p["id"], stage="failed", skip_reason=f"publish: {type(e).__name__}: {str(e)[:160]}")
                    report["failed"] += 1
                if since_deploy["n"] >= deploy_every:
                    since_deploy["n"] = 0
                    milestone(conn)
            if max_batches and report["batches"] >= max_batches:
                break
        finally:
            conn.close()
    conn = connect(dsn)
    try:
        if since_deploy["n"] or report["published"] == 0:
            milestone(conn)
    finally:
        conn.close()
    report["hours"] = round(progress.hours(), 2)
    report["pages_per_hour"] = round(report["published"] / progress.hours(), 1)
    log("articles done: " + json.dumps(report, default=str))
    return report


# ----------------------------------------------------------------------------------------------- all
def run_all(*, school: str, run_id: str, workers: int = 6, model: str = "sonnet", stage: str = "all", chunk_size: int = 10, deploy_every: int = 25, deploy: bool = True,
            log=print, runner=None, max_chunks: int | None = None, max_batches: int | None = None, dsn: str | None = None) -> dict:
    run_dir = RUN_ROOT / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    pause = Pause(log=log, probe=lambda: cli_probe(runner=runner))
    out: dict = {"run_id": run_id, "stage": stage, "started": datetime.now(timezone.utc).isoformat()}
    if stage in ("all", "extract"):
        out["extract"] = extract_stage(school=school, run_id=run_id, workers=workers, chunk_size=chunk_size, model=model, pause=pause, log=log, runner=runner, max_chunks=max_chunks, dsn=dsn)
        if stopped():
            out["stopped"] = True
            return out
    if stage in ("all", "dossier"):
        out["dossier"] = dossier_stage(school=school, log=log, dsn=dsn)
    if stage in ("all", "articles"):
        out["articles"] = articles_stage(school=school, run_id=run_id, workers=workers, model=model, pause=pause, log=log, runner=runner, deploy_every=deploy_every, deploy=deploy, max_batches=max_batches, dsn=dsn)
    out["pauses"] = pause.pauses
    out["stopped"] = stopped()
    (run_dir / "run.json").write_text(json.dumps(out, indent=1, default=json_default))
    return out
