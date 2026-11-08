#!/usr/bin/env bash
# v3 topic intelligence brief (docs/v3/spec.md, section 2): one opus synthesis session merges intel/<topic>/raw/*.md into
# intel/<topic>/brief.md (11 sections, 15,000 to 40,000 words, every fact with Source URL, Applies to and Checked), one more
# "expand" session when it is short, then one sonnet fact-check session per lane that fixes the brief in place and appends its
# findings to intel/<topic>/brief-check.md.
#   scripts/v3/brief.sh <topic-slug> [--model opus] [--max-turns 200] [--check-model sonnet] [--skip-check] [--resume]
#                                    [--check-max-turns 80] [--check-workers 5] [--timeout 10800] [--check-timeout 3600] [--intel-dir DIR]
# Topics: scripts/v3/topics.yml. Stop cleanly: scripts/v2/stop.sh. Log: build/runs/v2/brief-<ts>.log
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"; cd "$ROOT"
if command -v caffeinate >/dev/null 2>&1; then caffeinate -i -w $$ & fi   # no idle sleep while this runs (a closed lid still sleeps)
set -a; [ -f worker/.env ] && . worker/.env; set +a
export PATH="$HOME/.local/bin:$PATH"
exec worker/.venv/bin/python scripts/v3/brief.py "$@"
