#!/usr/bin/env bash
# Restore the newest research.dump into a scratch database and verify row counts — proves the restore path
# without touching the live database. Usage: scripts/restore_test.sh [backup_dir]
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DIR="${1:-$(ls -d "$ROOT"/backups/*/ | sort | tail -1)}"
[ -f "$DIR/research.dump" ] || { echo "no research.dump in $DIR"; exit 1; }
(cd "$DIR" && sha256sum -c SHA256SUMS --quiet) && echo "checksums ok"
SCRATCH="campus_restore_test"
su postgres -c "psql -q -c 'DROP DATABASE IF EXISTS $SCRATCH;' -c 'CREATE DATABASE $SCRATCH OWNER campus;'" >/dev/null
PGPASSWORD=campus_local_dev pg_restore --no-owner --dbname="postgresql://campus@localhost:5432/$SCRATCH" "$DIR/research.dump"
PGPASSWORD=campus_local_dev psql -At "postgresql://campus@localhost:5432/$SCRATCH" -c "SELECT 'institutions=' || count(*) FROM institutions UNION ALL SELECT 'claims=' || count(*) FROM claims UNION ALL SELECT 'jobs=' || count(*) FROM jobs UNION ALL SELECT 'migrations=' || max(version) FROM schema_migrations;"
echo "restore into $SCRATCH verified"
