#!/usr/bin/env bash
# Environment doctor (specs/continuous-local-run.md R1, R32; AT1, AT29).
# Prints PASS/FAIL per item with the installed version, exits non-zero if any REQUIRED item fails.
# Usage: scripts/doctor.sh [--quiet]
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/opt/homebrew/opt/postgresql@16/bin:/opt/homebrew/opt/python@3.13/bin:/opt/homebrew/opt/php@8.3/bin:$PATH"
# load non-secret-safe env: values are never printed
if [ -f "$ROOT/worker/.env" ]; then set -a; . "$ROOT/worker/.env"; set +a; fi
FAIL=0; WARN=0
pass() { printf 'PASS  %-34s %s\n' "$1" "${2:-}"; }
fail() { printf 'FAIL  %-34s %s\n' "$1" "${2:-}"; FAIL=$((FAIL+1)); }
warn() { printf 'WARN  %-34s %s\n' "$1" "${2:-}"; WARN=$((WARN+1)); }
ver() { "$@" 2>&1 | head -1; }

# --- toolchain (R32) ---------------------------------------------------------------------------
PY="$(command -v python3.13 || command -v python3 || true)"
if [ -n "$PY" ] && "$PY" -c 'import sys; sys.exit(0 if sys.version_info[:2] >= (3,12) else 1)'; then pass "python >= 3.12" "$(ver "$PY" --version) ($PY)"; else fail "python >= 3.12" "found: ${PY:-none} $( [ -n "$PY" ] && ver "$PY" --version)"; fi
if [ -n "$PY" ] && "$PY" -c 'import campus_worker, psycopg, pydantic, jsonschema, jinja2, httpx, bs4, lxml, pdfplumber, yaml, pytest' 2>/dev/null; then pass "worker deps installed" "pip install -e worker[dev]"; else fail "worker deps installed" "run: $PY -m pip install -e \"$ROOT/worker[dev]\""; fi
if [ -n "$PY" ] && "$PY" -c 'import playwright' 2>/dev/null && [ -d "$HOME/Library/Caches/ms-playwright" ] && ls "$HOME/Library/Caches/ms-playwright" 2>/dev/null | grep -q chromium; then pass "playwright chromium" "$(ls "$HOME/Library/Caches/ms-playwright" | grep chromium | head -1)"; else fail "playwright chromium" "run: $PY -m playwright install chromium"; fi
if command -v psql >/dev/null; then pass "postgresql client" "$(ver psql --version)"; else fail "postgresql client" "brew install postgresql@16"; fi
if command -v pg_dump >/dev/null; then pass "pg_dump" "$(ver pg_dump --version)"; else fail "pg_dump" "needed for backups"; fi
if command -v php >/dev/null; then
  missing=""; for ext in pdo_sqlite mbstring curl gd zip; do php -m 2>/dev/null | grep -qi "^$ext\$" || missing="$missing $ext"; done
  if [ -z "$missing" ]; then pass "php 8.3 + extensions" "$(ver php --version)"; else fail "php 8.3 + extensions" "missing:$missing"; fi
else fail "php 8.3 + extensions" "brew install php@8.3"; fi
if command -v node >/dev/null && node -e 'process.exit(parseInt(process.versions.node)>=22?0:1)'; then pass "node >= 22" "$(ver node --version)"; else fail "node >= 22" "$(command -v node >/dev/null && ver node --version || echo none)"; fi
command -v git >/dev/null && pass "git" "$(ver git --version)" || fail "git" "not found"
command -v gh >/dev/null && pass "gh" "$(ver gh --version)" || fail "gh" "not found"
if command -v claude >/dev/null; then pass "claude --version" "$(ver claude --version)"; else fail "claude --version" "install: curl -fsSL https://claude.ai/install.sh | bash"; fi
command -v caffeinate >/dev/null && pass "caffeinate" "present" || fail "caffeinate" "macOS only"

# --- databases (R1, R32) -----------------------------------------------------------------------
if [ -z "${DATABASE_URL:-}" ]; then fail "DATABASE_URL set" "put DATABASE_URL in worker/.env (hosted Postgres 16)"
elif command -v psql >/dev/null && psql -X -At "$DATABASE_URL" -c 'select 1' >/dev/null 2>&1; then
  pass "DATABASE_URL reachable" "$(psql -X -At "$DATABASE_URL" -c 'show server_version' 2>/dev/null)"
  if [ -n "$PY" ] && (cd "$ROOT/worker" && "$PY" -m campus_worker.db status 2>/dev/null | grep -q '"pending": \[\]'); then pass "migrations current" ""; else fail "migrations current" "run: cd worker && python -m campus_worker.db migrate"; fi
else fail "DATABASE_URL reachable" "connection failed (value not shown)"; fi
TEST_URL="${TEST_DATABASE_URL:-}"
if [ -z "$TEST_URL" ]; then fail "TEST_DATABASE_URL set" "local test DB, never the hosted one"
elif [ "$TEST_URL" = "${DATABASE_URL:-}" ]; then fail "TEST_DATABASE_URL separate" "must differ from DATABASE_URL"
elif command -v psql >/dev/null && psql -X -At "$TEST_URL" -c 'select 1' >/dev/null 2>&1; then pass "TEST_DATABASE_URL reachable" "local"; else fail "TEST_DATABASE_URL reachable" "start local postgresql@16"; fi

# --- git remote (R1) -----------------------------------------------------------------------------
if (cd "$ROOT" && git push --dry-run -q origin HEAD >/dev/null 2>&1); then pass "git push to origin" "$(cd "$ROOT" && git rev-parse --abbrev-ref HEAD)"; else fail "git push to origin" "dry-run push failed"; fi

# --- network (R1) --------------------------------------------------------------------------------
for host in scl.cornell.edu living.cornell.edu admissions.cornell.edu nces.ed.gov; do
  code="$(curl -s -o /dev/null -m 15 -w '%{http_code}' -A 'campus-publication-doctor/1.0' "https://$host/" 2>/dev/null)"; code="${code:-000}"
  case "$code" in 2*|3*) pass "https://$host" "HTTP $code";; 403|429) warn "https://$host" "HTTP $code (reachable, access limited)";; *) fail "https://$host" "HTTP $code";; esac
done

# --- Claude Code project files (R1, R32) ---------------------------------------------------------
if [ -d "$ROOT/.claude/agents" ]; then
  bad=0; n=0
  for f in "$ROOT"/.claude/agents/*.md; do [ -e "$f" ] || continue; n=$((n+1))
    if ! "$PY" - "$f" <<'PY' 2>/dev/null; then bad=$((bad+1)); echo "      bad agent file: $f"; fi
import sys,re
t=open(sys.argv[1],encoding='utf-8').read()
m=re.match(r'^---\n(.*?)\n---\n',t,re.S); assert m, 'no frontmatter'
fm=dict(l.split(':',1) for l in m.group(1).splitlines() if ':' in l)
for k in ('name','description','tools','model'): assert k in fm, 'missing '+k
assert 'contract' in t.lower() and '.json' in t, 'no contract named'
PY
  done
  [ "$bad" = 0 ] && pass "agent files parse" "$n files" || fail "agent files parse" "$bad bad"
else warn "agent files parse" ".claude/agents not created yet (milestone 6)"; fi
[ -L "$ROOT/.claude/skills/national-college-publishing" ] && pass "project skill symlink" "" || warn "project skill symlink" "not installed yet (milestone 3)"
[ -f "$ROOT/.claude/settings.json" ] && "$PY" -c "import json,sys; json.load(open('$ROOT/.claude/settings.json'))" 2>/dev/null && pass "settings.json valid JSON" "" || warn "settings.json valid JSON" "missing (milestone 3)"
[ -d "$ROOT/wp-local/wordpress" ] && pass "wp-local clone" "" || warn "wp-local clone" "see docs/ops/run.md"

echo "----"; echo "doctor: $FAIL required failure(s), $WARN warning(s)"
[ "$FAIL" = 0 ]
