#!/usr/bin/env bash
# Ask the running loop to stop after the current iteration (specs/continuous-local-run.md R3; AT4).
# Creates .run/STOP. The current iteration finishes and commits; no new iteration starts.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
RUN_DIR="${CAMPUS_RUN_DIR:-$ROOT/.run}"
mkdir -p "$RUN_DIR"; touch "$RUN_DIR/STOP"
if [ -f "$RUN_DIR/lock/pid" ] && kill -0 "$(cat "$RUN_DIR/lock/pid")" 2>/dev/null; then
  echo "STOP file created; run (pid $(cat "$RUN_DIR/lock/pid")) will stop after the current iteration"
else
  echo "STOP file created; no run is active right now (the next run.sh clears it on start)"
fi
