#!/usr/bin/env bash
# Restore the newest research.dump into a scratch database and verify row counts — proves the restore path
# without touching the live database. Usage: scripts/restore_test.sh [backup_dir]
# Works on Linux (service postgres, `su postgres`) and macOS (Homebrew postgresql@16, current user is superuser).
# Env: PG_ADMIN_URL   admin connection used to drop/create the scratch DB (default: local postgres DB as current user)
#      TEST_DATABASE_URL  only its host/port/user are reused; the scratch DB is always campus_restore_test
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DIR="${1:-$(ls -d "$ROOT"/backups/*/ | sort | tail -1)}"
[ -f "$DIR/research.dump" ] || { echo "no research.dump in $DIR"; exit 1; }
if command -v sha256sum >/dev/null 2>&1; then (cd "$DIR" && sha256sum -c SHA256SUMS --quiet); else (cd "$DIR" && shasum -a 256 -c SHA256SUMS --quiet); fi && echo "checksums ok"
SCRATCH="campus_restore_test"
ADMIN_URL="${PG_ADMIN_URL:-postgresql://localhost:5432/postgres}"
LOCAL_URL="${TEST_DATABASE_URL:-postgresql://campus:campus_local_dev@localhost:5432/campus_research_test}"
# scratch URL = local URL with the database name swapped
SCRATCH_URL="$(printf '%s' "$LOCAL_URL" | sed -E "s#/[^/?]+(\?.*)?\$#/$SCRATCH\1#")"
if [ "$(uname -s)" = "Linux" ] && id postgres >/dev/null 2>&1 && [ "$(id -u)" = "0" ]; then
  su postgres -c "psql -q -c 'DROP DATABASE IF EXISTS $SCRATCH;' -c 'CREATE DATABASE $SCRATCH OWNER campus;'" >/dev/null
else
  psql -q "$ADMIN_URL" -c "DROP DATABASE IF EXISTS $SCRATCH;" -c "CREATE DATABASE $SCRATCH OWNER campus;" >/dev/null
fi
pg_restore --no-owner --dbname="$SCRATCH_URL" "$DIR/research.dump"
psql -At "$SCRATCH_URL" -c "SELECT 'institutions=' || count(*) FROM institutions UNION ALL SELECT 'claims=' || count(*) FROM claims UNION ALL SELECT 'jobs=' || count(*) FROM jobs UNION ALL SELECT 'migrations=' || max(version) FROM schema_migrations;"
echo "restore into $SCRATCH verified"
