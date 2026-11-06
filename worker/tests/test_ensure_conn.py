"""A hosted DB drops idle connections while an agent runs; ensure_conn returns a live one (STATE.md loop fixes)."""
from campus_worker import db as dbmod


def test_live_connection_is_kept(conn):
    assert dbmod.ensure_conn(conn, None) is conn


def test_closed_connection_is_replaced(conn, migrated_url):
    conn.close()
    fresh = dbmod.ensure_conn(conn, migrated_url)
    try:
        assert fresh is not conn and not fresh.closed
        with fresh.cursor() as cur:
            cur.execute("SELECT 1 AS one")
            assert cur.fetchone()["one"] == 1
    finally:
        fresh.close()
