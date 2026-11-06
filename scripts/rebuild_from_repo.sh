#!/usr/bin/env bash
# Rebuild the hosted database from committed files (specs/continuous-local-run.md R31; AT28).
# Safe to run twice. Usage: scripts/rebuild_from_repo.sh [--verify]
# Reads DATABASE_URL from worker/.env (never printed). Override for a local dry run:
#   DATABASE_URL=postgresql://... scripts/rebuild_from_repo.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PY="$ROOT/worker/.venv/bin/python"; [ -x "$PY" ] || PY="$(command -v python3.13 || command -v python3)"
if [ -z "${DATABASE_URL:-}" ] && [ -f "$ROOT/worker/.env" ]; then set -a; . "$ROOT/worker/.env"; set +a; fi
[ -n "${DATABASE_URL:-}" ] || { echo "DATABASE_URL is not set (worker/.env)"; exit 2; }
if [ -n "${TEST_DATABASE_URL:-}" ] && [ "$DATABASE_URL" = "$TEST_DATABASE_URL" ]; then echo "refusing: DATABASE_URL equals TEST_DATABASE_URL"; exit 2; fi
cd "$ROOT/worker"
echo "== checksum =="; (cd "$ROOT" && if command -v sha256sum >/dev/null; then sha256sum -c data/ipeds/SHA256SUMS; else shasum -a 256 -c data/ipeds/SHA256SUMS; fi)
echo "== rebuild =="; "$PY" -m campus_worker.rebuild "$@"
