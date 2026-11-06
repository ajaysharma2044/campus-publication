#!/usr/bin/env bash
# PreToolUse guard (specs/continuous-local-run.md §7 "Enforced by hook"; AT17, AT11). Logic lives in guard.py.
# Reads the hook JSON on stdin. Exit 2 + a message on stderr blocks the tool call; exit 0 allows it.
# Protected: SPEC.md, specs/**, .claude/settings.json, gate constants in editorial/gates.py,
#            live-ramp defaults in config.py, and .claude/skills/<name> unless adopted in docs/ops/skill-evaluations.md.
set -u
ROOT="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"
PY="$ROOT/worker/.venv/bin/python"; [ -x "$PY" ] || PY="$(command -v python3)"
exec "$PY" -I "$ROOT/.claude/hooks/guard.py" "$ROOT"
