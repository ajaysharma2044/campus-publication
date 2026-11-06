#!/usr/bin/env bash
# Continuous local run (specs/continuous-local-run.md R2–R6, R10, R41; AT3–AT7, AT40).
#
#   scripts/run.sh [--max N] [--mode normal|sweep] [--model M] [--max-turns T]
#                  [--force-fail] [--simulate-usage-limit] [--iteration-cmd CMD]
#
# One iteration = one `claude -p` call with scripts/iteration_prompt.md under a fixed tool allowlist.
# Stops (and logs the reason) on: .run/STOP, no unblocked work, 3 consecutive failed iterations,
# a usage-limit or auth error from the CLI, or --max N. Exit codes: 0 stop_file/no_work/max... see below.
#   0  stopped cleanly (stop_file, no_work)      12 max_iterations reached
#   1  consecutive_failures                      11 locked (another run active)
#   20 usage_paused (never retried in a loop)    30 auth_error / blocked
# Keeps the Mac awake with caffeinate; takes a single-instance mkdir lock; Ctrl-C == stop.sh.
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export PATH="$ROOT/worker/.venv/bin:$HOME/.local/bin:/opt/homebrew/opt/php@8.3/bin:/opt/homebrew/opt/postgresql@16/bin:/opt/homebrew/bin:$PATH"
RUN_DIR="${CAMPUS_RUN_DIR:-$ROOT/.run}"; LOG_DIR="${CAMPUS_RUN_LOG_DIR:-$ROOT/build/runs}"
mkdir -p "$RUN_DIR" "$LOG_DIR"
MAX=0; MODE="${CAMPUS_RUN_MODE:-normal}"; MODEL="${CAMPUS_COORDINATOR_MODEL:-sonnet}"; MAX_TURNS="${CAMPUS_ITERATION_MAX_TURNS:-80}"
ITER_CMD="${CAMPUS_ITERATION_CMD:-claude}"; FORCE_FAIL=0; SIM_USAGE=0
while [ $# -gt 0 ]; do
  case "$1" in
    --max) MAX="$2"; shift 2;;
    --mode) MODE="$2"; shift 2;;
    --print-argv) PRINT_ARGV=1; shift;;
    --model) MODEL="$2"; shift 2;;
    --max-turns) MAX_TURNS="$2"; shift 2;;
    --force-fail) FORCE_FAIL=1; shift;;
    --simulate-usage-limit) SIM_USAGE=1; shift;;
    --iteration-cmd) ITER_CMD="$2"; shift 2;;
    -h|--help) sed -n 2,14p "$0"; exit 0;;
    *) echo "unknown option $1"; exit 2;;
  esac
done
case "$MODE" in normal|sweep) ;; *) echo "--mode must be normal or sweep"; exit 2;; esac
PY="$ROOT/worker/.venv/bin/python"; [ -x "$PY" ] || PY="$(command -v python3)"
if [ -f "$ROOT/worker/.env" ]; then set -a; . "$ROOT/worker/.env"; set +a; fi

# ---- single-instance lock (mkdir is atomic; flock is absent on macOS) --------------------------
LOCK="$RUN_DIR/lock"
if ! mkdir "$LOCK" 2>/dev/null; then
  oldpid="$(cat "$LOCK/pid" 2>/dev/null || true)"
  if [ -n "$oldpid" ] && kill -0 "$oldpid" 2>/dev/null; then echo "locked: run.sh already active (pid $oldpid)"; exit 11; fi
  echo "stale lock from pid ${oldpid:-?}; taking over"; rm -rf "$LOCK"; mkdir "$LOCK" || { echo "locked"; exit 11; }
fi
echo $$ > "$LOCK/pid"
STOP_FILE="$RUN_DIR/STOP"; rm -f "$STOP_FILE"
RUN_START="$(date -u +%Y%m%dT%H%M%SZ)"; RUN_LOG="$LOG_DIR/$RUN_START.jsonl"; export CAMPUS_RUN_ID="$RUN_START" CAMPUS_RUN_LOG="$RUN_LOG" CAMPUS_RUN_MODE="$MODE"
CAFF_PID=""
if command -v caffeinate >/dev/null && [ -z "${CAMPUS_NO_CAFFEINATE:-}" ]; then caffeinate -dimsu -w $$ & CAFF_PID=$!; fi
cleanup() { rm -rf "$LOCK"; [ -n "$CAFF_PID" ] && kill "$CAFF_PID" 2>/dev/null; }
trap cleanup EXIT
on_int() { echo; echo "signal received: finishing the current iteration, then stopping (STOP file created)"; touch "$STOP_FILE"; }
trap on_int INT TERM

cd "$ROOT"
PROMPT_FILE="$ROOT/scripts/iteration_prompt.md"
# one comma-joined argument: a pattern such as "Bash(python -m campus_worker.*)" must reach the CLI as one token, never word-split
ALLOWED="$(grep -v '^\s*$' "$ROOT/scripts/iteration_tools.txt" | paste -sd, -)"
if [ "${PRINT_ARGV:-0}" = 1 ]; then printf '%s\n' claude -p "<prompt>" --output-format json --permission-mode dontAsk --model "$MODEL" --max-turns "$MAX_TURNS" --allowedTools "$ALLOWED"; cleanup; trap - EXIT; exit 0; fi
ITER=0; FAILS=0; STOP_REASON=""; EXIT=0; LAST_DAY="$(date -u +%F)"
echo "run $RUN_START mode=$MODE model=$MODEL max=${MAX:-0} log=$RUN_LOG"

# run one child, surviving trapped signals: a trapped INT interrupts `wait`, so re-wait until the child really exits
run_child() { "$@" & local c=$!; local rc; while :; do wait "$c"; rc=$?; kill -0 "$c" 2>/dev/null || break; done; return "$rc"; }

digest() { "$PY" -c 'import campus_worker.digest' 2>/dev/null && (cd "$ROOT/worker" && "$PY" -m campus_worker.digest --reason "$1" >/dev/null 2>&1 || true); }

while :; do
  if [ -f "$STOP_FILE" ]; then STOP_REASON="stop_file"; EXIT=0; break; fi
  if [ "${MAX:-0}" -gt 0 ] && [ "$ITER" -ge "$MAX" ]; then STOP_REASON="max_iterations"; EXIT=12; break; fi
  ITER=$((ITER+1)); export CAMPUS_ITERATION="$ITER"
  TODAY="$(date -u +%F)"; if [ "$TODAY" != "$LAST_DAY" ]; then digest "midnight"; LAST_DAY="$TODAY"; fi
  START="$(date -u +%FT%TZ)"; T0=$(date +%s)
  OUT="$RUN_DIR/iter-$ITER.json"; ERR="$RUN_DIR/iter-$ITER.err"
  if [ "$FORCE_FAIL" = 1 ]; then
    run_child "$ROOT/scripts/fixtures/iteration_stub.sh" fail > "$OUT" 2> "$ERR" < /dev/null; CODE=$?
  elif [ "$SIM_USAGE" = 1 ]; then
    run_child "$ROOT/scripts/fixtures/iteration_stub.sh" usage > "$OUT" 2> "$ERR" < /dev/null; CODE=$?
  elif [ "$ITER_CMD" != "claude" ]; then
    run_child "$ITER_CMD" > "$OUT" 2> "$ERR" < /dev/null; CODE=$?
  else
    PROMPT="$(sed -e "s/{{ITERATION}}/$ITER/g" -e "s/{{MODE}}/$MODE/g" -e "s/{{RUN_ID}}/$RUN_START/g" "$PROMPT_FILE")"
    run_child claude -p "$PROMPT" --output-format json --permission-mode dontAsk --model "$MODEL" --max-turns "$MAX_TURNS" \
        --allowedTools "$ALLOWED" > "$OUT" 2> "$ERR" < /dev/null; CODE=$?
    if grep -q "unknown option '--max-turns'" "$ERR" 2>/dev/null; then
      echo "note: installed claude has no --max-turns; retrying this iteration without it (turn budget via prompt)"
      run_child claude -p "$PROMPT" --output-format json --permission-mode dontAsk --model "$MODEL" \
          --allowedTools "$ALLOWED" > "$OUT" 2> "$ERR" < /dev/null; CODE=$?
    fi
  fi
  END="$(date -u +%FT%TZ)"; DUR=$(( $(date +%s) - T0 ))
  # autosave: the coordinator commits itself; anything left behind is committed so no work is lost (R4)
  if [ -z "${CAMPUS_RUN_NO_GIT:-}" ] && [ -n "$(cd "$ROOT" && git status --porcelain --untracked-files=no 2>/dev/null)" ]; then
    (cd "$ROOT" && git add -u && git commit -q -m "run $RUN_START iteration $ITER: autosave of uncommitted changes (specs/continuous-local-run.md R4)" && git push -q 2>/dev/null) || true
  fi
  COMMIT="$(cd "$ROOT" && git rev-parse --short HEAD 2>/dev/null || echo unknown)"
  # classify + log one JSON line (R10); prints: <result> <task_id>
  CLASS="$("$PY" "$ROOT/scripts/runlog.py" append --log "$RUN_LOG" --iteration "$ITER" --start "$START" --end "$END" --duration "$DUR" \
           --exit-code "$CODE" --output "$OUT" --stderr "$ERR" --commit "$COMMIT" --mode "$MODE" 2>>"$ERR")"
  RESULT="${CLASS%% *}"; TASK="${CLASS#* }"
  echo "iteration $ITER: exit=$CODE result=$RESULT task=$TASK duration=${DUR}s commit=$COMMIT"
  case "$RESULT" in
    usage_paused) STOP_REASON="usage_paused"; EXIT=20; break;;
    auth_error)   STOP_REASON="auth_error"; EXIT=30; break;;
    no_work)      STOP_REASON="no_work"; EXIT=0; break;;
    failed)       FAILS=$((FAILS+1)); [ "$FAILS" -ge 3 ] && { STOP_REASON="consecutive_failures"; EXIT=1; break; };;
    *)            FAILS=0;;
  esac
  if [ "$MODE" = sweep ] && "$PY" "$ROOT/scripts/runlog.py" sweep-complete --output "$OUT" 2>/dev/null; then
    echo "sweep complete: switching to the normal lane mix (R41)"; MODE="normal"; export CAMPUS_RUN_MODE="$MODE"
  fi
done
"$PY" "$ROOT/scripts/runlog.py" stop --log "$RUN_LOG" --reason "$STOP_REASON" --iterations "$ITER" --exit-code "$EXIT" 2>/dev/null || true
digest "run_end"
echo "STOP: $STOP_REASON after $ITER iteration(s) (exit $EXIT)"
exit "$EXIT"
