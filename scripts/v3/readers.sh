#!/usr/bin/env bash
# v3 reader map (docs/v3/spec.md, section 3): one opus session reads intel/<topic>/brief.md and the demand rows and writes
# intel/<topic>/readers.md: at least 10 "## Reader: <name>" sections, each with Key and the six fields (Situation, Questions in their
# words, Decisions with numbers, Timeline, Mistakes and cost, Brief facts that matter). Prints the count. Log: build/runs/v2/readers-<ts>.log
#   scripts/v3/readers.sh <topic-slug> [--model opus] [--max-turns 80] [--timeout 5400] [--min-readers 10] [--intel-dir DIR]
# Topics: scripts/v3/topics.yml. Stop cleanly: scripts/v2/stop.sh.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
PY="$ROOT/worker/.venv/bin/python"
for a in "$@"; do case "$a" in -h|--help) sed -n '2,6p' "$0"; exit 0;; esac; done
[ $# -ge 1 ] || { sed -n '2,6p' "$0"; exit 2; }
cd "$ROOT"
set -a; [ -f worker/.env ] && . worker/.env; set +a
export PATH="$HOME/.local/bin:$PATH"
exec "$PY" - "$@" <<'PY'
import argparse
import sys
from datetime import date

sys.path.insert(0, "scripts/v3")
sys.path.insert(0, "scripts/v2")
import brief as B
import plan as P
from lib import sessions

ap = argparse.ArgumentParser(prog="readers.sh", add_help=False)
ap.add_argument("topic")
ap.add_argument("--model", default="opus")
ap.add_argument("--max-turns", type=int, default=80)
ap.add_argument("--timeout", type=int, default=5400)
ap.add_argument("--min-readers", type=int, default=10)
ap.add_argument("--intel-dir", default=None)
a = ap.parse_args()
t = B.topic_or_exit(a.topic)
tdir = B.intel_root(a.intel_dir) / a.topic
brief, out, demand = tdir / "brief.md", tdir / "readers.md", tdir / "raw" / "demand-questions.md"
if not brief.exists():
    sys.exit(f"{B.rel(brief)} is missing; run scripts/v3/brief.sh {a.topic} first")
log, log_path = sessions.open_log("readers")
sessions.clear_stop(log)
today = date.today().isoformat()


def check():
    if not out.exists():
        return [f"missing {B.rel(out)}"]
    readers = P.reader_map(out.read_text(encoding="utf-8"))
    problems = [f"{r['name']}: missing {', '.join(r['missing'])}" for r in readers if r["missing"]]
    if len(readers) < a.min_readers:
        problems.insert(0, f"{len(readers)} reader sections, {a.min_readers} required")
    keys = [r["key"] for r in readers]
    if len(set(keys)) != len(keys):
        problems.append("duplicate reader keys: " + ", ".join(sorted({k for k in keys if keys.count(k) > 1})))
    return problems


if out.exists():
    have = P.reader_map(out.read_text(encoding="utf-8"))
    status = (f"{B.rel(out)} exists with {len(have)} reader sections ({', '.join(r['key'] for r in have)}). Read it first; keep what is good, "
              f"complete the fields that are missing ({'; '.join(f'{r['name']}: {', '.join(r['missing'])}' for r in have if r['missing']) or 'none'}) and add the readers that are missing.")
else:
    status = "No reader map exists yet."
template = (B.PROMPTS / "readers.md").read_text(encoding="utf-8")
prompt = sessions.fill(template, today=today, topic_title=t["title"], topic_scope=t["scope"], topic_slug=a.topic, topic_dir=t["dir"], brief_path=B.rel(brief),
                       demand_path=B.rel(demand) if demand.exists() else "(none exported)", voice_files=B.file_list(B.lane_files(tdir / "raw", "voice")),
                       out_path=B.rel(out), min_readers=a.min_readers, status=status, brief_words=f"{B.words(brief.read_text(encoding='utf-8')):,}")
sessions.save_prompt("readers", a.topic, prompt)
log(f"reader map for {t['title']} ({a.topic}): one {a.model} session, {a.max_turns} turns, at least {a.min_readers} readers; brief {B.words(brief.read_text(encoding='utf-8')):,} words")
job = {"id": f"{a.topic}:readers", "prompt": prompt, "expect": [str(out)], "check": check}
st = sessions.run_jobs([job], workers=1, label="readers", model=a.model, max_turns=a.max_turns, allowed_tools=",".join(["Read", "Grep", "Glob", B.tool_rule("Write", tdir)]),
                       timeout_s=a.timeout, log=log)
readers = P.reader_map(out.read_text(encoding="utf-8")) if out.exists() else []
for r in readers:
    log(f"  {r['key']:<28} {r['name']}" + (f"  (missing: {', '.join(r['missing'])})" if r["missing"] else ""))
problems = check()
log(f"READERS {len(readers)} in {B.rel(out)}" + (f"; problems: {'; '.join(problems)}" if problems else "") + f"; log {B.rel(log_path)}; next: scripts/v3/plan.sh {a.topic}")
sys.exit(0 if readers and not problems else 1)
PY
