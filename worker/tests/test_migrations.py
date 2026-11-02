from campus_worker import db as dbmod


def test_migrations_apply_and_are_idempotent(migrated_url):
    conn = dbmod.connect(migrated_url)
    try:
        assert dbmod.migrate(conn) == []  # nothing pending after session fixture
        applied = dbmod.applied_versions(conn)
        assert 1 in applied
    finally:
        conn.close()


def test_every_migration_has_down_script():
    for _, _, path in dbmod.list_migrations():
        assert path.with_suffix(".down.sql").exists(), path.name


def test_modified_migration_is_rejected(migrated_url, monkeypatch, tmp_path):
    conn = dbmod.connect(migrated_url)
    try:
        with conn.cursor() as cur:
            cur.execute("UPDATE schema_migrations SET checksum='tampered' WHERE version=1")
        conn.commit()
        try:
            import pytest
            with pytest.raises(RuntimeError, match="checksum"):
                dbmod.migrate(conn)
        finally:
            # restore the real checksum
            import hashlib
            for v, n, p in dbmod.list_migrations():
                if v == 1:
                    real = hashlib.sha256(p.read_text().encode()).hexdigest()
            with conn.cursor() as cur:
                cur.execute("UPDATE schema_migrations SET checksum=%s WHERE version=1", (real,))
            conn.commit()
    finally:
        conn.close()
