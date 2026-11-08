#!/usr/bin/env bash
# v3 fact check (docs/v3/spec.md §7, speed mode): one sonnet session per written plan page checks the facts not in the brief and our own
# math, fixes in place, writes content/checks/<slug>.json and the v2-shaped content/reviews/<slug>.json that publish.sh reads.
#   scripts/v3/check.sh <topic-slug> [--workers 8] [--model sonnet] [--limit N] [--ids a,b] [--recheck] [--max-turns 50] [--timeout 1800]
# Stop cleanly: scripts/v2/stop.sh. Log: build/runs/v2/check-<ts>.log. Details: scripts/v3/check.py --help
# worker/.env is not sourced here: nothing in this step needs it, and the sessions must not inherit it.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"; cd "$ROOT"
export PATH="$HOME/.local/bin:$PATH"
exec worker/.venv/bin/python scripts/v3/check.py "$@"
