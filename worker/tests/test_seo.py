from datetime import datetime, timezone
from campus_worker import seo


def test_url_policy():
    assert seo.classify_url("/schools/cornell-university/housing/mews-hall/").indexable
    assert seo.classify_url("/schools/cornell-university/housing/compare/mews-hall-vs-court-kay-bauer/").indexable
    assert seo.classify_url("/tools/total-cost/").indexable
    d = seo.classify_url("/tools/total-cost/?period=per_semester&occupants=2")
    assert not d.indexable and d.canonical == "/tools/total-cost/"
    assert not seo.classify_url("/search/?q=mews").indexable
    assert not seo.classify_url("/schools/cornell-university/housing/mews-hall").indexable  # no trailing slash
    assert not seo.classify_url("/schools/Cornell_University/").indexable
    assert not seo.classify_url("/random/junk/path/here/").indexable


def test_sitemap_only_published_passed_pages(clean_conn):
    with clean_conn.cursor() as cur:
        cur.execute("INSERT INTO pages (page_format, slug, path, status) VALUES ('guide','a','/schools/x/housing/a/','published') RETURNING id")
        a = cur.fetchone()["id"]
        cur.execute("INSERT INTO page_versions (page_id, version_no, headline, body_markdown, content_hash, gate_status) VALUES (%s,1,'A','b','h1','passed') RETURNING id", (a,))
        va = cur.fetchone()["id"]
        cur.execute("UPDATE pages SET current_version_id=%s, first_published_at=now() WHERE id=%s", (va, a))
        cur.execute("INSERT INTO pages (page_format, slug, path, status) VALUES ('guide','b','/schools/x/housing/b/','staged') RETURNING id")
        b = cur.fetchone()["id"]
        cur.execute("INSERT INTO page_versions (page_id, version_no, headline, body_markdown, content_hash, gate_status) VALUES (%s,1,'B','b','h2','passed') RETURNING id", (b,))
        cur.execute("UPDATE pages SET current_version_id=(SELECT id FROM page_versions WHERE page_id=%s) WHERE id=%s", (b, b))
        cur.execute("INSERT INTO pages (page_format, slug, path, status, redirect_to_path) VALUES ('guide','c','/schools/x/housing/c/','redirected','/schools/x/housing/a/')")
    clean_conn.commit()
    xml = seo.sitemap_xml(clean_conn, "https://example.org")
    assert "/schools/x/housing/a/" in xml and "/housing/b/" not in xml and "/housing/c/" not in xml and "<lastmod>" in xml
    assert seo.robots_txt("https://example.org", "staging").startswith("User-agent: *\nDisallow: /")
    assert "Sitemap:" in seo.robots_txt("https://example.org", "production")


def test_structured_data_must_match_visible_content():
    pub = datetime(2026, 10, 29, tzinfo=timezone.utc)
    ld = {"@type": "Article", "headline": "H", "description": "D", "datePublished": "2026-10-29", "dateModified": "2026-10-29", "author": {"@type": "Organization", "name": "desk"}}
    assert seo.validate_structured_data(ld, visible_headline="H", visible_description="D", published=pub, modified=pub).ok
    bad = dict(ld, headline="Clickbait", author={"@type": "Person", "name": "Jane Doe"}, aggregateRating={"ratingValue": 5})
    r = seo.validate_structured_data(bad, visible_headline="H", visible_description="D", published=pub, modified=pub)
    assert not r.ok and len(r.errors) == 3
    stale = dict(ld, dateModified="2026-11-02")  # freshness theater
    assert "dateModified" in seo.validate_structured_data(stale, visible_headline="H", visible_description="D", published=pub, modified=pub).errors[0]


def test_internal_links_broken_and_orphans(clean_conn):
    with clean_conn.cursor() as cur:
        cur.execute("INSERT INTO pages (page_format, slug, path, status) VALUES ('guide','a','/schools/x/housing/a/','published'), ('guide','b','/schools/x/housing/b/','published'), ('guide','old','/schools/x/housing/old/','redirected')")
        cur.execute("UPDATE pages SET redirect_to_path='/schools/x/housing/a/' WHERE path='/schools/x/housing/old/'")
    clean_conn.commit()
    html = {"/schools/x/housing/a/": '<a href="/schools/x/housing/b/">b</a> <a href="/schools/x/housing/missing/">m</a> <a href="/schools/x/housing/old/">o</a>',
            "/schools/x/housing/b/": '<a href="/about/methods/">m</a>'}
    r = seo.check_internal_links(clean_conn, html)
    assert {b["href"] for b in r["broken"]} == {"/schools/x/housing/missing/", "/schools/x/housing/old/"}
    assert r["orphans"] == ["/schools/x/housing/a/"]


def test_title_description_truncate_truthfully():
    t, d = seo.title_and_description("Mews Hall: what the double-room rate includes and who can live there in 2026-27", "deck", "The Campus Ledger")
    assert len(t) <= 70 and t.endswith("…") or "—" in t
    assert d == "deck"
