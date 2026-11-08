#!/usr/bin/env bash
# Re-verify a topic brief (docs/v3/spec.md, section 2 and "Nothing runs on a schedule"): Ajay runs this by hand; it never runs on a timer.
#   scripts/v3/reverify.sh <topic> [--check-model sonnet] [--check-workers 5]
# Runs the once-only fact-check pass again over the existing intel/<topic>/brief.md (one sonnet session per research lane, facts
# confirmed or fixed in place, findings appended to intel/<topic>/brief-check.md) without rewriting the brief.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"; cd "$ROOT"
[ $# -ge 1 ] || { sed -n '2,6p' "$0"; exit 2; }
exec bash scripts/v3/brief.sh "$1" --resume "${@:2}"
