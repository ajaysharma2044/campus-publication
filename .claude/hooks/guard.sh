#!/usr/bin/env bash
# PreToolUse guard (Footnote Daily v2, owner spec 2026-11-07): only the .env block remains. Logic lives in guard.py.
# Reads the hook JSON on stdin. Exit 2 + a message on stderr blocks the tool call; exit 0 allows it.
# Protected: .env files (Claude never reads, prints or copies them; sourcing from a script stays allowed).
set -u
ROOT="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"
PY="$ROOT/worker/.venv/bin/python"; [ -x "$PY" ] || PY="$(command -v python3)"
exec "$PY" -I "$ROOT/.claude/hooks/guard.py" "$ROOT"
