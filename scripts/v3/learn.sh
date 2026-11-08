#!/usr/bin/env bash
# LEARN step (docs/v3/spec.md, steps 9 and 10; "Lessons (on demand)"). Ajay runs it by hand; nothing schedules it.
#   scripts/v3/learn.sh [--model opus] [--max-turns 120] [--since YYYY-MM-DD]
# One session reads the edit logs, fact-check fixes, Ajay's notes, blind compares, Search Console exports (reports/search-console/,
# owner-provided) and reader questions, runs the AI citation check for every live page's primary query, writes reports/learn-<date>.md,
# appends at most 5 proposed changes to reports/lessons.md (Ajay approves or rejects them there), and lists the 5 weakest pages to rewrite.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"; cd "$ROOT"
set -a; [ -f worker/.env ] && . worker/.env; set +a
export PATH="$HOME/.local/bin:$PATH"
MODEL=opus; MAX_TURNS=120; SINCE=""
while [ $# -gt 0 ]; do
  case "$1" in
    --model) MODEL="$2"; shift 2;; --max-turns) MAX_TURNS="$2"; shift 2;; --since) SINCE="$2"; shift 2;;
    -h|--help) sed -n '2,7p' "$0"; exit 0;; *) echo "unknown option $1" >&2; exit 2;;
  esac
done
exec worker/.venv/bin/python - "$MODEL" "$MAX_TURNS" "$SINCE" <<'PY'
import csv, re, sys
from datetime import date
from pathlib import Path
sys.path.insert(0, "scripts/v2")
from lib import sessions  # noqa: E402
import yaml  # noqa: E402
model, max_turns, since = sys.argv[1], int(sys.argv[2]), sys.argv[3]
runs = sorted(Path("reports").glob("learn-2*.md"))
since = since or (runs[-1].stem.split("-", 1)[1] if runs else "the start of the project")
rows = {r["id"]: r for r in csv.DictReader(open("queue/queue.csv"))}
queries = []
for art in sorted(Path("content/articles").glob("*/*.md")):
    fm = yaml.safe_load(art.read_text(encoding="utf-8").split("---", 2)[1])
    if rows.get(str(fm.get("queue_id")), {}).get("status") == "published":
        queries.append(f"- {fm.get('primary_query')} -> /{art.parent.name}/{art.stem}/")
cfg = yaml.safe_load(Path("config/monetization.yml").read_text()) or {}
base_url = ((cfg.get("site") or {}).get("domain") or "https://campus-ledger-preview.netlify.app")
if not str(base_url).startswith("http"): base_url = "https://" + str(base_url)
report = Path("reports") / f"learn-{date.today().isoformat()}.md"
log, log_path = sessions.open_log("learn"); sessions.clear_stop(log)
prompt = sessions.fill(Path("scripts/v3/prompts/learn.md").read_text(encoding="utf-8"), today=date.today().isoformat(), since=since, base_url=base_url,
                       n_queries=len(queries), queries="\n".join(queries) or "- (no live pages yet)", report_path=str(report))
log(f"learn run: {len(queries)} live pages, since {since}, model {model}; report {report}; log {log_path}")
st = sessions.run_jobs([{"id": "learn", "prompt": prompt, "expect": [str(report)]}], workers=1, label="learn", model=model, max_turns=max_turns,
                       allowed_tools="WebSearch,WebFetch,Read,Grep,Glob,Write(reports/**),Edit(reports/**),Edit(intel/**)", timeout_s=7200, log=log)
log(f"learn done: {st['ok']} ok, {st['failed']} failed; proposals in reports/lessons.md for Ajay to approve or reject")
PY
