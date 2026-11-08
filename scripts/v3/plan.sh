#!/usr/bin/env bash
# v3 content and data plan (docs/v3/spec.md, section 4): one opus session writes intel/<topic>/plan.md (one pillar, 10 to 30 spokes,
# reader guides, tools, datasets, start-here paths, rewrites) from the brief and the reader map; the script turns the plan table into
# queue/queue.csv rows (status proposed, verdict plan; one row per slug and topic, ever) and prints the summary Ajay reads. --approve
# flips the topic's proposed plan rows that are in the plan to approved (with an existing plan.md: no session, the approval step after
# the read; a row Ajay removed from the plan is left proposed and named; a proposed row whose plan line was edited is synced first).
#   scripts/v3/plan.sh <topic-slug> [--model opus] [--max-turns 80] [--timeout 5400] [--limit-spokes 30] [--approve] [--dry-run]
#                                   [--intel-dir DIR] [--queue FILE] [--content-dir DIR] [--articles-dir DIR]
# Topics: scripts/v3/topics.yml. Stop cleanly: scripts/v2/stop.sh. Log: build/runs/v2/plan-<ts>.log
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"; cd "$ROOT"
set -a; [ -f worker/.env ] && . worker/.env; set +a
export PATH="$HOME/.local/bin:$PATH"
exec worker/.venv/bin/python scripts/v3/plan.py "$@"
