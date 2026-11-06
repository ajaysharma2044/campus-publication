#!/usr/bin/env bash
# Back up the research database (pg_dump custom format), the local WordPress SQLite DB + uploads, and the
# non-secret configuration, into backups/<timestamp>/. Credentials are NEVER included (.env is excluded).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; TS="$(date -u +%Y%m%dT%H%M%SZ)"; OUT="$ROOT/backups/$TS"; mkdir -p "$OUT"
DB_URL="${DATABASE_URL:-postgresql://campus:campus_local_dev@localhost:5432/campus_research}"
pg_dump --format=custom --no-owner --file="$OUT/research.dump" "$DB_URL"
[ -d "$ROOT/wp-local/wordpress/wp-content/database" ] && tar -czf "$OUT/wordpress-content.tgz" -C "$ROOT/wp-local/wordpress/wp-content" database uploads 2>/dev/null || true
tar -czf "$OUT/config.tgz" -C "$ROOT" worker/.env.example fixtures/synthetic/school_configs worker/campus_worker/migrations
(cd "$OUT" && files="$(ls | grep -v SHA256SUMS)" && if command -v sha256sum >/dev/null; then sha256sum $files; else shasum -a 256 $files; fi > SHA256SUMS)
echo "backup written to $OUT"; ls -la "$OUT"
