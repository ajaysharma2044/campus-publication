#!/usr/bin/env bash
# Continuous v3 driver (docs/v3/spec.md, speed mode): write -> fix round -> check -> publish, for one topic, until .run/STOP, until the
# topic has no plan rows left to write, or until a cycle makes no progress (every row came back to where it started). Appends the newly
# published pages to reports/to-read.md (Ajay's spot check) and prints a REPORT line every 10 published pages: articles per hour,
# session-minutes per article (from the run logs) and minutes paused on usage limits.
#   scripts/v3/run.sh <topic-slug> [--workers 8] [--model opus] [--check-model sonnet] [--deploy-every 10] [--once] [--no-publish]
#                     [--no-images] [--queue FILE] [--intel-dir DIR] [--articles-dir DIR] [--content-dir DIR] [--state-file FILE] [--runs-dir DIR]
# Stop cleanly: scripts/v2/stop.sh (sessions in flight finish; the next step does not start). Log: build/runs/v2/run-<ts>.log
# Bash 3.2 (macOS /bin/bash): no arrays beyond "$@", no mapfile, no associative arrays.
set -u
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"; cd "$ROOT"
TOPIC=""; WORKERS=8; MODEL=opus; CHECK_MODEL=sonnet; DEPLOY_EVERY=10; ONCE=0; PUBLISH=1; PASS=""; IMG=""; QUEUE="queue/queue.csv"; REPORTS="reports"; RUNS="build/runs/v2"
while [ $# -gt 0 ]; do
  case "$1" in
    --workers) WORKERS="$2"; shift 2;;
    --model) MODEL="$2"; shift 2;;
    --check-model) CHECK_MODEL="$2"; shift 2;;
    --deploy-every) DEPLOY_EVERY="$2"; shift 2;;
    --once) ONCE=1; shift;;
    --no-publish) PUBLISH=0; shift;;
    --no-images) IMG="--no-images"; shift;;
    --queue) QUEUE="$2"; PASS="$PASS --queue $2"; shift 2;;
    --reports-dir) REPORTS="$2"; shift 2;;
    --runs-dir) RUNS="$2"; PASS="$PASS --runs-dir $2"; shift 2;;
    --intel-dir|--articles-dir|--content-dir|--state-file) PASS="$PASS $1 $2"; shift 2;;
    -h|--help) sed -n '2,9p' "$0"; exit 0;;
    -*) echo "unknown option $1" >&2; exit 2;;
    *) TOPIC="$1"; shift;;
  esac
done
[ -n "$TOPIC" ] || { echo "usage: scripts/v3/run.sh <topic-slug> [options]" >&2; exit 2; }
mkdir -p .run "$RUNS" "$REPORTS"
LOG="$RUNS/run-$(date +%Y%m%dT%H%M%S).log"
exec > >(tee -a "$LOG") 2>&1
rm -f .run/STOP
if command -v caffeinate >/dev/null; then caffeinate -i -w $$ & fi
# worker/.env is sourced for publish.sh's deploy and the image finder; write.py and check.py strip it from their sessions' environment
set -a; [ -f worker/.env ] && . worker/.env; set +a
export PATH="$HOME/.local/bin:$PATH"
PY=worker/.venv/bin/python
ts() { date +%H:%M:%S; }
# shellcheck disable=SC2086
pending() { "$PY" scripts/v3/write.py "$TOPIC" --count-pending $PASS; }
TDIR="$("$PY" -c "import sys, yaml; ts = yaml.safe_load(open('scripts/v3/topics.yml')); print(next((t['dir'] for t in ts if t['slug'] == sys.argv[1] or t['dir'] == sys.argv[1]), ''))" "$TOPIC")"
[ -n "$TDIR" ] || { echo "unknown topic $TOPIC (see scripts/v3/topics.yml)" >&2; exit 2; }
published_ids() { "$PY" -c "
import csv, sys
rows = csv.DictReader(open(sys.argv[1], newline='', encoding='utf-8-sig'))
print(' '.join(sorted(r['id'] for r in rows if r['status'] == 'published' and r['topic'] == sys.argv[2])))" "$QUEUE" "$TDIR"; }
# the topic's rows as "id:status" lines: a cycle that leaves this unchanged made no progress
signature() { "$PY" -c "
import csv, sys
rows = csv.DictReader(open(sys.argv[1], newline='', encoding='utf-8-sig'))
print(' '.join(sorted(f\"{r['id']}:{r['status']}\" for r in rows if r['topic'] == sys.argv[2])))" "$QUEUE" "$TDIR"; }
count_published() { published_ids | wc -w | tr -d ' '; }
START=$(date +%s); START_PUB=$(count_published); NEXT_REPORT=$(( (START_PUB / 10 + 1) * 10 )); CYCLE=0
echo "$(ts) v3 run for $TOPIC ($TDIR): workers=$WORKERS write model=$MODEL check model=$CHECK_MODEL deploy every $DEPLOY_EVERY; $START_PUB published in the topic so far; pending $(pending); log $LOG"
while true; do
  if [ -f .run/STOP ]; then echo "$(ts) STOP file present: stopping"; break; fi
  PENDING=$(pending)
  if [ "$PENDING" -eq 0 ]; then
    echo "$(ts) the topic has no plan rows left that this step can write (approved rows with a pillar to link, or rows in a fix round). Approve more rows (plan.sh --approve $TOPIC, or requeue_v2.py $TOPIC --approve) and start again."
    break
  fi
  CYCLE=$((CYCLE + 1)); echo "$(ts) ---- cycle $CYCLE: $PENDING pending"
  BEFORE="$(published_ids)"; SIG_BEFORE="$(signature)"
  # shellcheck disable=SC2086
  bash scripts/v3/write.sh "$TOPIC" --workers "$WORKERS" --model "$MODEL" --limit $((WORKERS * 2)) $IMG $PASS
  [ -f .run/STOP ] && { echo "$(ts) STOP file present: stopping before the fix round"; break; }
  # shellcheck disable=SC2086
  bash scripts/v3/write.sh "$TOPIC" --fix --workers "$WORKERS" --model "$MODEL" $IMG $PASS
  [ -f .run/STOP ] && { echo "$(ts) STOP file present: stopping before the check"; break; }
  # shellcheck disable=SC2086
  bash scripts/v3/check.sh "$TOPIC" --workers "$WORKERS" --model "$CHECK_MODEL" $PASS
  [ -f .run/STOP ] && { echo "$(ts) STOP file present: stopping before publish"; break; }
  if [ "$PUBLISH" -eq 1 ]; then
    RENDER=""   # a tool, dataset or start page published by the check has no article for publish.sh to count: ask for a render anyway
    [ "$(published_ids)" != "$BEFORE" ] && RENDER="--render"
    bash scripts/v2/publish.sh --deploy-every "$DEPLOY_EVERY" $RENDER
    # shellcheck disable=SC2086
    bash scripts/v3/write.sh "$TOPIC" --restore-rewrites $PASS
  else
    echo "$(ts) publish skipped (--no-publish)"
  fi
  AFTER="$(published_ids)"
  "$PY" - "$QUEUE" "$TDIR" "$BEFORE" "$AFTER" "$PASS" "$REPORTS" <<'PY'
# reports/to-read.md (docs/v3/spec.md §8): one entry per newly published page in the shape the file's header documents (and that
# render_site.py --to-read regenerates): "- <date> | <title> | <path> | <kind> | <topic dir>", a Summary line (the meta), an "Ajay:" line
# for the thumbs-up or note. A page is listed once (by its site path).
import re, sys
from datetime import date
from pathlib import Path
sys.path.insert(0, "scripts/v2")
from lib import queue as q
queue, tdir, before, after, extra, reports = sys.argv[1], sys.argv[2], set(sys.argv[3].split()), set(sys.argv[4].split()), sys.argv[5], Path(sys.argv[6])
m = re.search(r"--articles-dir (\S+)", extra)
content = Path(re.search(r"--content-dir (\S+)", extra).group(1)) if re.search(r"--content-dir (\S+)", extra) else Path("content")
articles = Path(m.group(1)) if m else content / "articles"
new = sorted(after - before)
if not new:
    sys.exit(0)
report = reports / "to-read.md"
head = ("# To read: Ajay's spot check (docs/v3/spec.md, step 8)\n\nEvery newly published page lands here with a one-line summary. Ajay reads all of the "
        "first topic, then 1 in 5, and marks each one on its `Ajay:` line: a thumbs-up, or a one-line note on what is wrong. Notes become style guide, "
        "exemplar or brief edits, never code rules. Pages marked good go to docs/v3/best/, pages with a note to docs/v3/worst/.\n\n## Entries\n\n")
text = report.read_text(encoding="utf-8") if report.exists() else head
rows = {r["id"]: r for r in q.read(queue)}
lines = []
for qid in new:
    r = rows.get(qid, {})
    ang = dict(p.split("=", 1) for p in re.split(r"\s*;\s*", r.get("angle", "")) if "=" in p)
    kind, slug = ang.get("kind", ""), ang.get("slug", "")
    fm, path = {}, ""
    if kind == "tool":
        fm, path = q.frontmatter(content / "tools" / slug / "tool.md"), f"/tools/{slug}/"
    elif kind == "dataset":
        fm, path = q.frontmatter(content / "datasets" / f"{slug}.md"), f"/datasets/{slug}/"
    elif kind == "start_here":
        fm, path = q.frontmatter(content / "start" / f"{slug}.md"), f"/start/{slug}/"
    else:
        for p in sorted(articles.glob("*/*.md")):
            if str(q.frontmatter(p).get("queue_id") or "") == qid:
                fm, path = q.frontmatter(p), f"/{p.parent.name}/{p.stem}/"
                break
    if not path or f"| {path} |" in text:
        continue
    title = " ".join(str(fm.get("title") or r.get("question") or qid).split())
    meta = " ".join(str(fm.get("meta") or "").split())
    kind_label = str(fm.get("kind") or kind or f"{fm.get('type') or 'article'} (v2)")
    lines.append(f"- {date.today().isoformat()} | {title} | {path} | {kind_label} | {tdir}\n  Summary: {meta}\n  Ajay: \n\n")
if lines:
    report.write_text(text.rstrip("\n") + "\n\n" + "".join(lines), encoding="utf-8")
    print(f"{report}: {len(lines)} new page(s) listed")
PY
  PUB=$(count_published); ELAPSED=$(( $(date +%s) - START ))
  echo "$(ts) cycle $CYCLE done: $PUB published in $TDIR (+$((PUB - START_PUB)) this run); pending $(pending)"
  if [ "$PUB" -ge "$NEXT_REPORT" ] || [ "$ONCE" -eq 1 ]; then
    "$PY" - "$PUB" "$START_PUB" "$ELAPSED" "$START" "$RUNS" <<'PY'
# REPORT (speed mode item 8): articles per hour, session-minutes per article and minutes paused, from this run's step logs (pick-best and
# cold-edit sessions log into the write log).
import re, sys
from datetime import timedelta
from pathlib import Path
pub, start_pub, elapsed, start = map(int, sys.argv[1:5])
runs = Path(sys.argv[5])
n = pub - start_pub
hours = max(elapsed, 1) / 3600
minutes = paused = 0.0
for log in runs.glob("*.log"):
    if not re.match(r"(write|write-fix|check)-\d{8}T\d{6}\.log$", log.name) or log.stat().st_mtime < start - 5:
        continue
    pause_at = None
    lines = log.read_text(encoding="utf-8", errors="replace").splitlines()
    for line in lines:
        m = re.search(r"\] \d+/\d+ (?:ok|FAILED) \S+ \((\d+(?:\.\d+)?) min", line)
        if m:
            minutes += float(m.group(1))
        t = re.match(r"(\d\d):(\d\d):(\d\d) ", line)
        if not t:
            continue
        at = timedelta(hours=int(t.group(1)), minutes=int(t.group(2)), seconds=int(t.group(3)))
        if "PAUSED on a usage limit" in line and pause_at is None:
            pause_at = at
        elif "usage limit cleared" in line and pause_at is not None:
            paused += ((at - pause_at) % timedelta(days=1)).total_seconds() / 60
            pause_at = None
    if pause_at is not None and lines:   # still paused when the log ended: count to the log's last line
        last = re.match(r"(\d\d):(\d\d):(\d\d) ", lines[-1])
        if last:
            paused += ((timedelta(hours=int(last.group(1)), minutes=int(last.group(2)), seconds=int(last.group(3))) - pause_at) % timedelta(days=1)).total_seconds() / 60
per = f"{minutes / n:.1f} session-minutes per published article" if n else f"{minutes:.0f} session-minutes, no article published yet"
print(f"REPORT: {n} published this run ({pub} in the topic) in {hours:.2f} h ({n / hours:.1f} articles/hour); {per}; {paused:.0f} min paused on usage limits")
PY
    NEXT_REPORT=$(( (PUB / 10 + 1) * 10 ))
  fi
  [ "$ONCE" -eq 1 ] && { echo "$(ts) one cycle done (--once)"; break; }
  if [ "$(signature)" = "$SIG_BEFORE" ]; then
    echo "$(ts) no progress this cycle: every row of $TDIR is back where it started (see the write and check logs above); stopping so the loop does not spend sessions on the same failures. Fix the cause, then start again."
    break
  fi
done
echo "$(ts) v3 run ended after $CYCLE cycle(s)"
