import httpx
from pathlib import Path
from campus_worker.collectors.html import collect_html_source, extract_material
from campus_worker.config import FIXTURES_DIR
from campus_worker.fetcher import SafeFetcher
from tests.helpers import make_school, make_source
from tests.test_fetcher import resolver_factory

SRC = FIXTURES_DIR / "sources"


def _fetcher(conn, body_by_path):
    def handler(req):
        body = body_by_path[req.url.path]
        return httpx.Response(200, headers={"content-type": "text/html"}, content=body)
    return SafeFetcher(conn, transport=httpx.MockTransport(handler), resolver=resolver_factory({}), sleep=lambda s: None)


def test_extract_strips_navigation_and_keeps_tables():
    ex = extract_material((SRC / "fixture_hall_rates_v1.html").read_bytes())
    assert "Home" not in ex.material_text and "Privacy" not in ex.material_text
    assert "$12,042" in ex.material_text
    assert len(ex.tables) == 1 and ex.tables[0]["headers"] == ["Room type", "2025–26", "2026–27"]
    assert ex.tables[0]["rows"][0] == ["Double", "$11,580", "$12,042"]


def test_nav_change_is_not_material_but_rate_change_is(clean_conn):
    inst, campus, _ = make_school(clean_conn)
    sid = make_source(clean_conn, inst, campus, "https://www.example.edu/rates")
    v1 = (SRC / "fixture_hall_rates_v1.html").read_bytes()
    v2 = (SRC / "fixture_hall_rates_v2_navchange.html").read_bytes()
    v3 = (SRC / "fixture_hall_rates_v3_ratechange.html").read_bytes()
    r1 = collect_html_source(clean_conn, _fetcher(clean_conn, {"/rates": v1}), sid)
    assert r1["outcome"] == "ok" and r1["first_fetch"] and r1["tables"] == 1
    r2 = collect_html_source(clean_conn, _fetcher(clean_conn, {"/rates": v2}), sid)
    assert r2["material_change"] is False
    r3 = collect_html_source(clean_conn, _fetcher(clean_conn, {"/rates": v3}), sid)
    assert r3["material_change"] is True
    with clean_conn.cursor() as cur:
        cur.execute("SELECT health, consecutive_failures, last_changed_at IS NOT NULL AS changed FROM source_registry WHERE id=%s", (sid,))
        r = cur.fetchone()
    assert r["health"] == "healthy" and r["consecutive_failures"] == 0 and r["changed"]


def test_denied_access_and_gone_recorded(clean_conn):
    inst, campus, _ = make_school(clean_conn)
    sid = make_source(clean_conn, inst, campus, "https://www.example.edu/private")
    def handler(req):
        return httpx.Response(403)
    f = SafeFetcher(clean_conn, transport=httpx.MockTransport(handler), resolver=resolver_factory({}), sleep=lambda s: None)
    assert collect_html_source(clean_conn, f, sid)["outcome"] == "blocked"
    sid2 = make_source(clean_conn, inst, campus, "https://www.example.edu/removed")
    f2 = SafeFetcher(clean_conn, transport=httpx.MockTransport(lambda r: httpx.Response(404)), resolver=resolver_factory({}), sleep=lambda s: None)
    collect_html_source(clean_conn, f2, sid2)
    with clean_conn.cursor() as cur:
        cur.execute("SELECT health FROM source_registry WHERE id=%s", (sid2,))
        assert cur.fetchone()["health"] == "gone"


def test_retention_policy_hashes_only(clean_conn):
    inst, campus, _ = make_school(clean_conn)
    with clean_conn.cursor() as cur:
        cur.execute("UPDATE source_permissions SET retention_policy='hashes_only' WHERE domain_pattern='*.example.edu'")
    clean_conn.commit()
    sid = make_source(clean_conn, inst, campus, "https://www.example.edu/rates")
    collect_html_source(clean_conn, _fetcher(clean_conn, {"/rates": (SRC / "fixture_hall_rates_v1.html").read_bytes()}), sid)
    with clean_conn.cursor() as cur:
        cur.execute("SELECT retained_text, retained_tables, content_hash FROM fetch_snapshots WHERE source_id=%s", (sid,))
        r = cur.fetchone()
    assert r["retained_text"] is None and r["retained_tables"] is None and len(r["content_hash"]) == 64
