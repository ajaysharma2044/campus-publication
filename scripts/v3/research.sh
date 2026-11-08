#!/usr/bin/env bash
# v3 research sprint (docs/v3/spec.md, step 1): parallel lanes per topic write raw, sourced, dated notes to intel/<topic>/raw/<lane>.md.
#   scripts/v3/research.sh <topic-slug> [--lanes A,B,C,D,E] [--workers 5] [--model sonnet|opus] [--max-turns 120] [--timeout 7200]
# Topics and scopes: scripts/v3/topics.yml. Stop cleanly: scripts/v2/stop.sh. Log: build/runs/v2/research-<ts>.log
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"; cd "$ROOT"
if command -v caffeinate >/dev/null 2>&1; then caffeinate -i -w $$ & fi   # no idle sleep while this runs (a closed lid still sleeps)
set -a; [ -f worker/.env ] && . worker/.env; set +a
export PATH="$HOME/.local/bin:$PATH"
exec worker/.venv/bin/python scripts/v3/research.py "$@"
