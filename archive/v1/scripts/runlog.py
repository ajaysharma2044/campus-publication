"""Run-log writer and iteration classifier for scripts/run.sh (specs/continuous-local-run.md R5, R6, R7, R10).

  runlog.py append --log L --iteration N --start S --end E --duration D --exit-code C --output claude.json --stderr err --commit SHA --mode M
      → appends one JSON line with every R10 field and prints "<result> <task_id>"
  runlog.py stop --log L --reason R --iterations N --exit-code C
      → appends the stop line
  runlog.py sweep-complete --output claude.json  → exit 0 when the coordinator reported sweep_complete=true

Result classes: succeeded | failed | held | no_work | usage_paused | auth_error.
Usage limits are recognised from the CLI result text and never retried by the loop (R6).
Also records one unpriced session usage entry per iteration in the ledger when DATABASE_URL is set (R7).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

USAGE_PATTERNS = re.compile(r"(usage limit|hit your limit|rate limit|rate_limit|too many requests|\b429\b|overloaded|out of extra usage|limit will reset)", re.I)
AUTH_PATTERNS = re.compile(r"(not logged in|please run /login|authentication[_ ]failed|invalid api key|unauthori[sz]ed|\b401\b|billing_error)", re.I)
SUMMARY_KEY = "iteration_summary"


def load_output(path: str) -> tuple[dict | None, str]:
    try:
        raw = Path(path).read_text(encoding="utf-8", errors="replace")
    except FileNotFoundError:
        return None, ""
    raw = raw.strip()
    if not raw:
        return None, ""
    # the CLI may print warnings before the JSON object; take the last JSON object in the stream
    for line in reversed(raw.splitlines()):
        line = line.strip()
        if line.startswith("{"):
            try:
                return json.loads(line), raw
            except json.JSONDecodeError:
                continue
    try:
        return json.loads(raw), raw
    except json.JSONDecodeError:
        return None, raw


def extract_summary(text: str) -> dict:
    """The coordinator ends its reply with a JSON object {"iteration_summary": {...}}. Find the last one."""
    if not text:
        return {}
    idx = text.rfind(SUMMARY_KEY)
    if idx < 0:
        return {}
    start = text.rfind("{", 0, idx)
    depth = 0
    for i in range(start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(text[start:i + 1]).get(SUMMARY_KEY, {}) or {}
                except json.JSONDecodeError:
                    return {}
    return {}


def classify(data: dict | None, raw: str, stderr: str, exit_code: int) -> tuple[str, dict]:
    text = " ".join(filter(None, [raw, stderr, (data or {}).get("result") if isinstance((data or {}).get("result"), str) else ""]))
    summary = extract_summary((data or {}).get("result") or raw)
    if AUTH_PATTERNS.search(text):
        return "auth_error", summary
    if USAGE_PATTERNS.search(text):
        return "usage_paused", summary
    if data is None:
        return "failed", summary
    if data.get("is_error") or exit_code != 0:
        return "failed", summary
    res = (summary.get("result") or "").lower()
    if res in ("succeeded", "failed", "held", "no_work"):
        return res, summary
    return "succeeded", summary


def record_session_usage(entry: dict) -> str | None:
    if not os.environ.get("DATABASE_URL"):
        return "no DATABASE_URL: ledger entry skipped"
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "worker"))
        from campus_worker import budget
        from campus_worker.db import connect
        conn = connect(os.environ["DATABASE_URL"])
        try:
            budget.record_session_usage(conn, kind="iteration", task_id=entry.get("task_id"), agent=None, duration_s=entry["duration_s"],
                                        turns=entry.get("turns"), iteration=entry["iteration"], extra={"run_id": entry["run_id"], "result": entry["result"]})
        finally:
            conn.close()
        return None
    except Exception as e:  # noqa: BLE001 — logged, never fatal for the loop
        return f"ledger write failed: {type(e).__name__}: {e}"


def cmd_append(a) -> int:
    data, raw = load_output(a.output)
    stderr = Path(a.stderr).read_text(errors="replace") if a.stderr and Path(a.stderr).exists() else ""
    result, summary = classify(data, raw, stderr, a.exit_code)
    entry = {
        "iteration": a.iteration, "run_id": os.environ.get("CAMPUS_RUN_ID"), "mode": a.mode, "start": a.start, "end": a.end, "duration_s": a.duration,
        "task_id": summary.get("task_id") or None, "lane": summary.get("lane"), "agents_dispatched": summary.get("agents") or [],
        "result": result, "checks": summary.get("checks") or [], "commit": a.commit, "exit_code": a.exit_code,
        "turns": (data or {}).get("num_turns"), "session_id": (data or {}).get("session_id"), "cli_subtype": (data or {}).get("subtype"),
        "cli_is_error": (data or {}).get("is_error"), "stop_reason": None, "notes": summary.get("notes"),
        "error": ((data or {}).get("result") if result in ("failed", "usage_paused", "auth_error") and isinstance((data or {}).get("result"), str) else None) or (stderr.strip()[-300:] if result == "failed" and stderr.strip() else None),
    }
    note = record_session_usage(entry)
    if note:
        entry["ledger_note"] = note
    with open(a.log, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, default=str) + "\n")
    print(f"{result} {entry['task_id'] or '-'}")
    return 0


def cmd_stop(a) -> int:
    with open(a.log, "a", encoding="utf-8") as fh:
        fh.write(json.dumps({"run_id": os.environ.get("CAMPUS_RUN_ID"), "stop_reason": a.reason, "iterations": a.iterations, "exit_code": a.exit_code}) + "\n")
    return 0


def cmd_sweep_complete(a) -> int:
    data, raw = load_output(a.output)
    summary = extract_summary((data or {}).get("result") or raw)
    return 0 if summary.get("sweep_complete") is True else 1


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("append")
    for name, kw in (("--log", {}), ("--iteration", {"type": int}), ("--start", {}), ("--end", {}), ("--duration", {"type": int}), ("--exit-code", {"type": int}),
                     ("--output", {}), ("--stderr", {}), ("--commit", {}), ("--mode", {})):
        s.add_argument(name, required=True, **kw)
    s.set_defaults(fn=cmd_append)
    t = sub.add_parser("stop")
    t.add_argument("--log", required=True); t.add_argument("--reason", required=True); t.add_argument("--iterations", type=int, required=True); t.add_argument("--exit-code", type=int, required=True)
    t.set_defaults(fn=cmd_stop)
    w = sub.add_parser("sweep-complete"); w.add_argument("--output", required=True); w.set_defaults(fn=cmd_sweep_complete)
    a = p.parse_args(argv)
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
