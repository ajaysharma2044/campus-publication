#!/usr/bin/env bash
# Parallel headless fallback (specs/bulk-mode.md section 3, last bullet; acceptance B5): page production with no API key, N `claude -p`
# workers at once, limited by plan usage.
#
#   scripts/parallel_headless.sh [N] [--pages <file>] [--limit M] [--dry-run] [--run <id>] [--model M] [--max-turns T]
#
# Shards the planned page list round-robin across N workers (default 4), starts one background `claude -p` per shard, each told to write only
# inside build/bulk/headless/<run>/worker-<i>/ (prompt.md, pages.json, out.json, err.txt, done.json, skipped.json, <slug>.json drafts), waits
# for all of them, then runs ONE serial merge: scripts/merge_headless_shards.py (fails loudly on a page path two workers both produced).
# Publishing stays with the pipeline: merged.json lists the version ids for `worker/.venv/bin/python -m campus_worker.pipeline publish <version_id>`.
#   --pages <file>  planned pages as JSON (`worker/.venv/bin/python -m campus_worker.bulk plan --limit M --json > file`); without it the list
#                   comes from `worker/.venv/bin/python -m campus_worker.lean queue --limit M --json` (the lean production queue)
#   --limit M       pages to take from the list (default 20)          --run <id>     run folder name (default: UTC timestamp)
#   --dry-run       everything except launching `claude -p`: prompts, a fake out.json per worker (every page skipped as "dry-run"), the merge
#   --model M       default $CAMPUS_COORDINATOR_MODEL or sonnet         --max-turns T  per worker (default 60; a page needs about 4 turns)
# Workers get run.sh's flags (--output-format json --permission-mode dontAsk --allowedTools from scripts/iteration_tools.txt) minus the git
# write commands: the prompt forbids git, publishing and writing outside the worker folder; the allowlist enforces the git part.
# Env: CAMPUS_HEADLESS_ROOT (default build/bulk/headless), CAMPUS_RUN_DIR (the lock dir shared with run.sh), CAMPUS_NO_CAFFEINATE=1.
# Exit: 0 merged without conflicts · 1 merge conflicts · 2 bad arguments or empty page list · 3 a worker exited non-zero (the merge still ran)
#       11 locked (run.sh or another parallel_headless.sh is active)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export PATH="$ROOT/worker/.venv/bin:$HOME/.local/bin:/opt/homebrew/opt/php@8.3/bin:/opt/homebrew/opt/postgresql@16/bin:/opt/homebrew/bin:$PATH"
N=4; PAGES=""; LIMIT=20; DRY=0; RUN_ID=""; MODEL="${CAMPUS_COORDINATOR_MODEL:-sonnet}"; MAX_TURNS=60
if [ $# -gt 0 ] && [[ "$1" =~ ^[0-9]+$ ]]; then N="$1"; shift; fi
while [ $# -gt 0 ]; do
  case "$1" in
    --pages) PAGES="$2"; shift 2;;
    --limit) LIMIT="$2"; shift 2;;
    --dry-run) DRY=1; shift;;
    --run) RUN_ID="$2"; shift 2;;
    --model) MODEL="$2"; shift 2;;
    --max-turns) MAX_TURNS="$2"; shift 2;;
    --print-argv) PRINT_ARGV=1; shift;;
    -h|--help) sed -n 2,20p "$0"; exit 0;;
    *) echo "unknown option $1 (usage: scripts/parallel_headless.sh [N] [--pages file] [--limit M] [--dry-run] [--run id] [--model M] [--max-turns T])" >&2; exit 2;;
  esac
done
[ "$N" -ge 1 ] 2>/dev/null || { echo "N must be a whole number >= 1" >&2; exit 2; }
[[ "$LIMIT" =~ ^[0-9]+$ ]] && [[ "$MAX_TURNS" =~ ^[0-9]+$ ]] || { echo "--limit and --max-turns take whole numbers" >&2; exit 2; }
if [ -n "$PAGES" ] && [ ! -f "$PAGES" ]; then echo "--pages: no such file $PAGES" >&2; exit 2; fi
PY="$ROOT/worker/.venv/bin/python"; [ -x "$PY" ] || PY="$(command -v python3)"
if [ -f "$ROOT/worker/.env" ]; then set -a; . "$ROOT/worker/.env"; set +a; fi
# one comma-joined argument (a pattern such as "Bash(python -m campus_worker.*)" must reach the CLI as one token); workers never commit, so the
# git write shapes are left out of their allowlist
ALLOWED="$(grep -v '^\s*$' "$ROOT/scripts/iteration_tools.txt" | grep -v -E '^Bash\(git (add|commit|push)' | paste -sd, -)"
if [ "${PRINT_ARGV:-0}" = 1 ]; then printf '%s\n' claude -p "<worker-<i>/prompt.md>" --output-format json --permission-mode dontAsk --model "$MODEL" --max-turns "$MAX_TURNS" --allowedTools "$ALLOWED"; exit 0; fi

# ---- single-instance lock shared with run.sh (mkdir is atomic; flock is absent on macOS); a dry run touches nothing, so it takes none -----
LOCK_DIR="${CAMPUS_RUN_DIR:-$ROOT/.run}"; LOCK="$LOCK_DIR/lock"; HAVE_LOCK=0
if [ "$DRY" = 0 ]; then
  mkdir -p "$LOCK_DIR"
  if ! mkdir "$LOCK" 2>/dev/null; then
    oldpid="$(cat "$LOCK/pid" 2>/dev/null || true)"
    if [ -n "$oldpid" ] && kill -0 "$oldpid" 2>/dev/null; then echo "locked: run.sh or another parallel_headless.sh is active (pid $oldpid)" >&2; exit 11; fi
    echo "stale lock from pid ${oldpid:-?}; taking over"; rm -rf "$LOCK"; mkdir "$LOCK" || { echo "locked" >&2; exit 11; }
  fi
  echo $$ > "$LOCK/pid"; HAVE_LOCK=1
fi

RUN_ID="${RUN_ID:-$(date -u +%Y%m%dT%H%M%SZ)}"
HEADLESS_ROOT="${CAMPUS_HEADLESS_ROOT:-$ROOT/build/bulk/headless}"
RUN_DIR="$HEADLESS_ROOT/$RUN_ID"
if ls -d "$RUN_DIR"/worker-* >/dev/null 2>&1; then echo "run folder $RUN_DIR already holds worker folders; pick another --run id" >&2; [ "$HAVE_LOCK" = 1 ] && rm -rf "$LOCK"; exit 2; fi
mkdir -p "$RUN_DIR"
export CAMPUS_RUN_ID="headless-$RUN_ID" CAMPUS_HEADLESS_ROOT="$HEADLESS_ROOT"
# headless Claude Code stops a session's background shell tasks 10 minutes after its last turn; a pipeline run takes longer (run.sh does the same)
export CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS=0
CAFF_PID=""; PIDS=(); IDX=()
cleanup() { [ "$HAVE_LOCK" = 1 ] && rm -rf "$LOCK"; [ -n "$CAFF_PID" ] && kill "$CAFF_PID" 2>/dev/null; return 0; }
trap cleanup EXIT
on_int() {  # bash 3.2 (macOS /bin/bash) treats an empty array as unbound under set -u: check the count before expanding it
  echo; echo "signal received: stopping the workers" >&2
  if [ "${#PIDS[@]}" -gt 0 ]; then for p in "${PIDS[@]}"; do pkill -P "$p" 2>/dev/null || true; kill "$p" 2>/dev/null || true; done; fi
}
trap on_int INT TERM

cd "$ROOT"
# ---- the page list: --pages (bulk plan output) or the lean production queue ----------------------------------------------------------------
if [ -n "$PAGES" ]; then PAGES_SRC="$PAGES"; SOURCE="file:$PAGES"
else
  PAGES_SRC="$RUN_DIR/queue.json"; SOURCE="campus_worker.lean queue --limit $LIMIT"
  "$PY" -m campus_worker.lean queue --limit "$LIMIT" --json > "$PAGES_SRC"
fi
printf '{"run": "%s", "workers": %d, "model": "%s", "max_turns": %d, "dry_run": %s, "limit": %d, "pages_source": "%s", "started": "%s"}\n' \
  "$RUN_ID" "$N" "$MODEL" "$MAX_TURNS" "$([ "$DRY" = 1 ] && echo true || echo false)" "$LIMIT" "$SOURCE" "$(date -u +%FT%TZ)" > "$RUN_DIR/run.json"
# ---- shard: worker-<i>/pages.json + prompt.md (+ the fake out.json in a dry run) ------------------------------------------------------------
SHARD_ARGS=(--pages "$PAGES_SRC" --workers "$N" --run-dir "$RUN_DIR" --limit "$LIMIT"); [ "$DRY" = 1 ] && SHARD_ARGS+=(--dry-run)
"$PY" "$ROOT/scripts/shard_headless_pages.py" "${SHARD_ARGS[@]}"
echo "run $RUN_ID: $N workers, pages from $SOURCE, model=$MODEL max-turns=$MAX_TURNS dry-run=$DRY folder=$RUN_DIR"

worker() {  # i dir: one `claude -p` with the worker's prompt; stdout is its JSON reply, stderr its log
  local i="$1" d="$2" rc=0
  claude -p "$(cat "$d/prompt.md")" --output-format json --permission-mode dontAsk --model "$MODEL" --max-turns "$MAX_TURNS" \
      --allowedTools "$ALLOWED" > "$d/out.json" 2> "$d/err.txt" < /dev/null || rc=$?
  echo "$rc" > "$d/exit_code"
  return "$rc"
}
if [ "$DRY" = 0 ] && command -v caffeinate >/dev/null && [ -z "${CAMPUS_NO_CAFFEINATE:-}" ]; then caffeinate -dimsu -w $$ & CAFF_PID=$!; fi
for i in $(seq 0 $((N - 1))); do
  d="$RUN_DIR/worker-$i"; k="$(cat "$d/page_count")"
  if [ "$k" -eq 0 ]; then printf '{"worker": %d, "done": [], "skipped": []}\n' "$i" > "$d/out.json"; echo 0 > "$d/exit_code"; echo "worker $i: no pages, not started"; continue; fi
  if [ "$DRY" = 1 ]; then echo "worker $i: $k page(s), dry run (prompt written, claude -p not launched)"; continue; fi
  worker "$i" "$d" & PIDS+=($!); IDX+=("$i")
  echo "worker $i: $k page(s), started (pid $!)"
done
FAILED=0; j=0
while [ "$j" -lt "${#PIDS[@]}" ]; do
  rc=0; while :; do wait "${PIDS[$j]}" && rc=0 || rc=$?; kill -0 "${PIDS[$j]}" 2>/dev/null || break; done  # a trapped signal interrupts wait: re-wait until the child really exits
  echo "worker ${IDX[$j]}: exit=$rc"
  if [ "$rc" -ne 0 ]; then FAILED=$((FAILED + 1)); fi
  j=$((j + 1))
done

# ---- ONE serial merge; publishing stays with the pipeline (merged.json lists the version ids) ------------------------------------------------
MERGE_RC=0
"$PY" "$ROOT/scripts/merge_headless_shards.py" "$RUN_DIR" || MERGE_RC=$?
if [ "$MERGE_RC" -ne 0 ]; then echo "STOP: merge exit $MERGE_RC (see $RUN_DIR/merged.json)" >&2; exit "$MERGE_RC"; fi
if [ "$FAILED" -gt 0 ]; then echo "STOP: $FAILED worker(s) exited non-zero (see worker-<i>/err.txt); merge ran" >&2; exit 3; fi
echo "DONE: run $RUN_ID merged without conflicts ($RUN_DIR/merged.json)"
exit 0
