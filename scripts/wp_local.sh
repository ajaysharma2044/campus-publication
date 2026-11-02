#!/usr/bin/env bash
# Local WordPress staging on SQLite (no MySQL needed) for testing the Campus Core plugin + theme + REST adapter.
# Usage: scripts/wp_local.sh setup|start|stop|status   (serves on http://127.0.0.1:8089)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WP="$ROOT/wp-local/wordpress"; SQL="$ROOT/wp-local/sqlite-plugin/packages/plugin-sqlite-database-integration"; PORT=8089; PID="$ROOT/wp-local/php.pid"; LOG="$ROOT/wp-local/php.log"
case "${1:-}" in
  setup)
    [ -d "$WP" ] || { echo "clone WordPress into wp-local/wordpress first"; exit 1; }
    mkdir -p "$WP/wp-content/plugins" "$WP/wp-content/themes" "$WP/wp-content/database"
    rm -rf "$WP/wp-content/plugins/sqlite-database-integration"; cp -r "$SQL" "$WP/wp-content/plugins/sqlite-database-integration"
    rm -rf "$WP/wp-content/plugins/sqlite-database-integration/wp-includes/database"; cp -r "$ROOT/wp-local/sqlite-plugin/packages/mysql-on-sqlite/src" "$WP/wp-content/plugins/sqlite-database-integration/wp-includes/database"
    cp "$SQL/db.copy" "$WP/wp-content/db.php"
    sed -i "s#{SQLITE_IMPLEMENTATION_FOLDER_PATH}#$WP/wp-content/plugins/sqlite-database-integration#; s#{SQLITE_PLUGIN}#sqlite-database-integration/load.php#" "$WP/wp-content/db.php"
    ln -sfn "$ROOT/wp/plugins/campus-core" "$WP/wp-content/plugins/campus-core"
    ln -sfn "$ROOT/wp/themes/campus-editorial" "$WP/wp-content/themes/campus-editorial"
    cat > "$WP/wp-config.php" <<CFG
<?php
define( 'DB_NAME', 'campus_local' ); define( 'DB_USER', 'unused' ); define( 'DB_PASSWORD', 'unused' ); define( 'DB_HOST', 'localhost' );
define( 'DB_CHARSET', 'utf8' ); define( 'DB_COLLATE', '' );
\$table_prefix = 'wp_';
define( 'WP_ENVIRONMENT_TYPE', 'staging' );
define( 'WP_DEBUG', true ); define( 'WP_DEBUG_DISPLAY', false ); define( 'WP_DEBUG_LOG', true );
define( 'WP_HOME', 'http://127.0.0.1:$PORT' ); define( 'WP_SITEURL', 'http://127.0.0.1:$PORT' );
define( 'DISALLOW_FILE_EDIT', true ); define( 'AUTOMATIC_UPDATER_DISABLED', true );
define( 'AUTH_KEY', 'local-dev-only-1' ); define( 'SECURE_AUTH_KEY', 'local-dev-only-2' ); define( 'LOGGED_IN_KEY', 'local-dev-only-3' ); define( 'NONCE_KEY', 'local-dev-only-4' );
define( 'AUTH_SALT', 'local-dev-only-5' ); define( 'SECURE_AUTH_SALT', 'local-dev-only-6' ); define( 'LOGGED_IN_SALT', 'local-dev-only-7' ); define( 'NONCE_SALT', 'local-dev-only-8' );
if ( ! defined( 'ABSPATH' ) ) { define( 'ABSPATH', __DIR__ . '/' ); }
require_once ABSPATH . 'wp-settings.php';
CFG
    mkdir -p "$WP/wp-content/mu-plugins"; cat > "$WP/wp-content/mu-plugins/local-dev.php" <<'MU'
<?php // LOCAL STAGING ONLY: allow application passwords over plain HTTP on 127.0.0.1.
add_filter( 'wp_is_application_passwords_available', '__return_true' );
MU
    echo "setup done";;
  start)
    cd "$WP" && (php -S 127.0.0.1:$PORT "$ROOT/scripts/wp_router.php" > "$LOG" 2>&1 & echo $! > "$PID"); sleep 1; echo "php server pid $(cat "$PID") on :$PORT";;
  stop) [ -f "$PID" ] && kill "$(cat "$PID")" 2>/dev/null && rm -f "$PID" && echo stopped || echo "not running";;
  status) curl -s -o /dev/null -w "%{http_code}\n" "http://127.0.0.1:$PORT/wp-json/campus/v1/status";;
  *) echo "usage: $0 setup|start|stop|status";;
esac
