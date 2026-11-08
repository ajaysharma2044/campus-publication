#!/usr/bin/env bash
# v3 write step (docs/v3/spec.md §5, speed mode): one opus session per approved plan row writes and edits the page from the topic brief.
#   scripts/v3/write.sh <topic-slug> [--workers 8] [--model opus] [--limit N] [--ids a,b] [--kind spoke|pillar|reader_guide|tool|dataset|rewrite|start_here]
#                       [--fix] [--max-turns 80] [--timeout 3600] [--two-drafts pillar] [--cold-edit-every 10] [--cold-edit] [--no-images]
#   scripts/v3/write.sh <topic-slug> --count-pending | --restore-rewrites
# Topics: scripts/v3/topics.yml. Stop cleanly: scripts/v2/stop.sh. Log: build/runs/v2/write-<ts>.log. Details: scripts/v3/write.py --help
# worker/.env is sourced for the image finder's UNSPLASH_ACCESS_KEY / PEXELS_API_KEY only: write.py hands those two to the finder and
# strips every variable the file defines from the environment before any claude session starts.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"; cd "$ROOT"
set -a; [ -f worker/.env ] && . worker/.env; set +a
export PATH="$HOME/.local/bin:$PATH"
exec worker/.venv/bin/python scripts/v3/write.py "$@"
