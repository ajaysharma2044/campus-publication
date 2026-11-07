#!/usr/bin/env bash
# SUBSCRIPTION-ONLY bulk run (owner decision 2026-11-07): extraction → dossier → articles through N parallel `claude -p` workers, never the API.
#   scripts/headless_bulk.sh [--workers N] [--stage all|extract|dossier|articles] [--school slug] [--model M] [--run id] [--no-deploy]
# Keeps the Mac awake (caffeinate), takes a single-instance lock, restarts the driver after a crash (the driver resumes from the
# database), and stops when `.run/STOP` exists (scripts/stop.sh). Log: build/runs/bulk/headless-<run>.log
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
WORKERS=6; STAGE=all; SCHOOL=cornell-university; MODEL=sonnet; RUN="headless-$(date -u +%Y%m%dT%H%MZ)"; EXTRA=()
while [ $# -gt 0 ]; do
  case "$1" in
    --workers) WORKERS="$2"; shift 2;;
    --stage) STAGE="$2"; shift 2;;
    --school) SCHOOL="$2"; shift 2;;
    --model) MODEL="$2"; shift 2;;
    --run) RUN="$2"; shift 2;;
    --no-deploy) EXTRA+=("--no-deploy"); shift;;
    *) echo "unknown option $1" >&2; exit 2;;
  esac
done
RUN_DIR="$ROOT/.run"; mkdir -p "$RUN_DIR" "$ROOT/build/runs/bulk"
LOCK="$RUN_DIR/headless.lock"
if ! mkdir "$LOCK" 2>/dev/null; then
  oldpid="$(cat "$LOCK/pid" 2>/dev/null || true)"
  if [ -n "$oldpid" ] && kill -0 "$oldpid" 2>/dev/null; then echo "locked: headless_bulk.sh already active (pid $oldpid)"; exit 11; fi
  rm -rf "$LOCK"; mkdir "$LOCK"
fi
echo $$ > "$LOCK/pid"
STOP_FILE="$RUN_DIR/STOP"; rm -f "$STOP_FILE"
cleanup() { rm -rf "$LOCK"; [ -n "${CAF_PID:-}" ] && kill "$CAF_PID" 2>/dev/null || true; }
trap cleanup EXIT
trap 'echo "signal: finishing the sessions in flight, then stopping (STOP file created)"; touch "$STOP_FILE"' INT TERM
if command -v caffeinate >/dev/null; then caffeinate -i -w $$ & CAF_PID=$!; fi
set -a; [ -f "$ROOT/worker/.env" ] && . "$ROOT/worker/.env"; set +a
export CAMPUS_RUN_ID="$RUN"
LOG="$ROOT/build/runs/bulk/headless-$RUN.log"
echo "subscription-only run $RUN: workers=$WORKERS stage=$STAGE school=$SCHOOL model=$MODEL log=$LOG"
ATTEMPT=0
while true; do
  if [ -f "$STOP_FILE" ]; then echo "stopped: STOP file"; break; fi
  ATTEMPT=$((ATTEMPT + 1))
  set +e
  worker/.venv/bin/python -m campus_worker.bulk headless --school "$SCHOOL" --run-id "$RUN" --workers "$WORKERS" --stage "$STAGE" --model "$MODEL" "${EXTRA[@]}" 2>&1 | tee -a "$LOG"
  CODE=${PIPESTATUS[0]}
  set -e
  if [ "$CODE" -eq 0 ]; then echo "driver finished (attempt $ATTEMPT)"; break; fi
  if [ -f "$STOP_FILE" ]; then echo "stopped after a driver error (exit $CODE)"; break; fi
  if [ "$ATTEMPT" -ge 20 ]; then echo "giving up after $ATTEMPT driver crashes (exit $CODE)"; exit 1; fi
  echo "driver exited $CODE; restarting in 120 s (resumes from the database)"; sleep 120
done
