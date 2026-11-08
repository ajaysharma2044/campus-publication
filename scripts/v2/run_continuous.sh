#!/usr/bin/env bash
# Continuous v2 run (docs/v2/spec.md, acceptance 4): write -> review -> one fix round -> review -> publish, 4 workers, until .run/STOP.
# Refills the queue with find_demand when approved rows run low. Prints REPORT lines (articles per hour) after every 10 published.
#   scripts/v2/run_continuous.sh [--workers 4] [--batch 12] [--model sonnet|opus] [--refill-below 20]
# Stop cleanly: scripts/v2/stop.sh (sessions in flight finish; the next step does not start). Log: build/runs/v2/continuous-<ts>.log
set -u
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"; cd "$ROOT"
WORKERS=4; BATCH=12; MODEL=sonnet; REFILL_BELOW=20
while [ $# -gt 0 ]; do
  case "$1" in
    --workers) WORKERS="$2"; shift 2;; --batch) BATCH="$2"; shift 2;; --model) MODEL="$2"; shift 2;; --refill-below) REFILL_BELOW="$2"; shift 2;;
    -h|--help) sed -n '2,5p' "$0"; exit 0;;
    *) echo "unknown option $1" >&2; exit 2;;
  esac
done
mkdir -p .run build/runs/v2
LOG="build/runs/v2/continuous-$(date -u +%Y%m%dT%H%M%SZ).log"
exec > >(tee -a "$LOG") 2>&1
rm -f .run/STOP
if command -v caffeinate >/dev/null; then caffeinate -i -w $$ & fi
set -a; [ -f worker/.env ] && . worker/.env; set +a
export PATH="$HOME/.local/bin:$PATH"
PY=worker/.venv/bin/python
ts() { date +%H:%M:%S; }
counts() { "$PY" -c "
import csv
from collections import Counter
c = Counter(r['status'] for r in csv.DictReader(open('queue/queue.csv')))
print(c.get('published', 0), c.get('approved', 0), c.get('rejected', 0), c.get('owned', 0))"; }
read -r START_PUB START_APPR START_REJ START_OWNED < <(counts)
START=$(date +%s); NEXT_REPORT=$(( (START_PUB / 10 + 1) * 10 )); CYCLE=0
echo "$(ts) continuous run: workers=$WORKERS batch=$BATCH model=$MODEL; published so far $START_PUB, approved $START_APPR, rejected $START_REJ; log $LOG"
while true; do
  if [ -f .run/STOP ]; then echo "$(ts) STOP file present: stopping"; break; fi
  CYCLE=$((CYCLE + 1)); echo "$(ts) ---- cycle $CYCLE"
  read -r PUB APPR REJ OWNED < <(counts)
  if [ "$APPR" -lt "$REFILL_BELOW" ]; then
    echo "$(ts) approved rows $APPR below $REFILL_BELOW: running find_demand for every topic seed"
    bash scripts/v2/find_demand.sh all --auto-approve --workers "$WORKERS" --model "$MODEL"
    read -r PUB APPR REJ OWNED < <(counts)
    if [ "$APPR" -eq 0 ]; then echo "$(ts) no approved questions after a demand pass; sleeping 30 minutes"; sleep 1800; continue; fi
  fi
  bash scripts/v2/write.sh --workers "$WORKERS" --limit "$BATCH" --model "$MODEL"
  [ -f .run/STOP ] && { echo "$(ts) STOP file present: stopping before review"; break; }
  bash scripts/v2/review.sh --workers "$WORKERS"
  [ -f .run/STOP ] && { echo "$(ts) STOP file present: stopping before the fix round"; break; }
  bash scripts/v2/write.sh --fix --workers "$WORKERS" --model "$MODEL"
  bash scripts/v2/review.sh --workers "$WORKERS"
  bash scripts/v2/publish.sh --deploy-every 10
  read -r PUB APPR REJ OWNED < <(counts)
  ELAPSED=$(( $(date +%s) - START ))
  echo "$(ts) cycle $CYCLE done: published total $PUB (+$((PUB - START_PUB)) this run), rejected $REJ, approved left $APPR"
  if [ "$PUB" -ge "$NEXT_REPORT" ]; then
    "$PY" -c "
import sys
pub, start_pub, elapsed, rej, start_rej, appr = map(int, sys.argv[1:])
hours = max(elapsed, 1) / 3600
print(f'REPORT: {pub - start_pub} articles published this run ({pub} total) in {hours:.2f} h ({(pub - start_pub) / hours:.1f} articles/hour); rejected {rej - start_rej} this run; approved left {appr}')" "$PUB" "$START_PUB" "$ELAPSED" "$REJ" "$START_REJ" "$APPR" | sed "s/^/$(ts) /"
    NEXT_REPORT=$(( (PUB / 10 + 1) * 10 ))
  fi
done
echo "$(ts) continuous run ended after $CYCLE cycle(s)"
