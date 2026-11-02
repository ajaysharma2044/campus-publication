"""Database connection and migration runner.

Migrations are plain SQL files in campus_worker/migrations/NNNN_name.sql, applied forward-only
inside a transaction, recorded in schema_migrations with a sha256 checksum. Each has a matching
NNNN_name.down.sql documenting the recovery approach (SPEC §28); down scripts are applied only by
explicit `migrate-down --to N` and are not assumed to be data-safe.
"""
from __future__ import annotations

import hashlib
import re
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

import psycopg
from psycopg.rows import dict_row

from .config import get_settings

MIGRATIONS_DIR = Path(__file__).parent / "migrations"
_FILE_RE = re.compile(r"^(\d{4})_([a-z0-9_]+)\.sql$")


def connect(database_url: str | None = None) -> psycopg.Connection:
    url = database_url or get_settings().database_url
    return psycopg.connect(url, row_factory=dict_row, autocommit=False)


@contextmanager
def transaction(conn: psycopg.Connection) -> Iterator[psycopg.Cursor]:
    with conn.cursor() as cur:
        try:
            yield cur
            conn.commit()
        except Exception:
            conn.rollback()
            raise


def _ensure_table(conn: psycopg.Connection) -> None:
    with transaction(conn) as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                checksum TEXT NOT NULL,
                applied_at TIMESTAMPTZ NOT NULL DEFAULT now()
            )
            """
        )


def list_migrations() -> list[tuple[int, str, Path]]:
    out = []
    for p in sorted(MIGRATIONS_DIR.glob("*.sql")):
        m = _FILE_RE.match(p.name)
        if m:
            out.append((int(m.group(1)), m.group(2), p))
    return out


def applied_versions(conn: psycopg.Connection) -> dict[int, str]:
    _ensure_table(conn)
    with conn.cursor() as cur:
        cur.execute("SELECT version, checksum FROM schema_migrations ORDER BY version")
        return {r["version"]: r["checksum"] for r in cur.fetchall()}


def migrate(conn: psycopg.Connection, target: int | None = None) -> list[int]:
    """Apply pending migrations up to target (inclusive). Returns applied versions."""
    applied = applied_versions(conn)
    done = []
    for version, name, path in list_migrations():
        if target is not None and version > target:
            break
        sql = path.read_text()
        checksum = hashlib.sha256(sql.encode()).hexdigest()
        if version in applied:
            if applied[version] != checksum:
                raise RuntimeError(
                    f"migration {version:04d}_{name} was modified after being applied "
                    f"(checksum mismatch). Write a new migration instead."
                )
            continue
        with transaction(conn) as cur:
            cur.execute(sql)
            cur.execute(
                "INSERT INTO schema_migrations (version, name, checksum) VALUES (%s, %s, %s)",
                (version, name, checksum),
            )
        done.append(version)
    return done


def migrate_down(conn: psycopg.Connection, to: int) -> list[int]:
    """Apply down scripts for versions > `to`, newest first. Explicit, logged, not data-safe."""
    applied = sorted(applied_versions(conn).keys(), reverse=True)
    reverted = []
    for version in applied:
        if version <= to:
            break
        matches = [p for v, n, p in list_migrations() if v == version]
        if not matches:
            raise RuntimeError(f"no migration file for applied version {version}")
        down = matches[0].with_suffix(".down.sql")
        if not down.exists():
            raise RuntimeError(f"no down script for {matches[0].name}; restore from backup instead")
        with transaction(conn) as cur:
            cur.execute(down.read_text())
            cur.execute("DELETE FROM schema_migrations WHERE version = %s", (version,))
        reverted.append(version)
    return reverted


def reset_database(conn: psycopg.Connection) -> None:
    """Drop and recreate the public schema. TEST DATABASES ONLY."""
    with transaction(conn) as cur:
        cur.execute("DROP SCHEMA public CASCADE; CREATE SCHEMA public;")


def main(argv: list[str]) -> int:
    if not argv or argv[0] not in {"migrate", "migrate-down", "status"}:
        print("usage: python -m campus_worker.db migrate|migrate-down --to N|status")
        return 2
    conn = connect()
    try:
        if argv[0] == "migrate":
            done = migrate(conn)
            print("applied:", done if done else "nothing pending")
        elif argv[0] == "migrate-down":
            to = int(argv[argv.index("--to") + 1])
            print("reverted:", migrate_down(conn, to))
        else:
            applied = applied_versions(conn)
            for v, n, _ in list_migrations():
                print(f"{v:04d} {n:40s} {'applied' if v in applied else 'pending'}")
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
