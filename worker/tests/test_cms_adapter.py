import pytest
from campus_worker.adapters.cms import InMemoryCMS, PublishRequest, WordPressAdapter
from campus_worker.adapters.base import NotConnected
from campus_worker.cms import publisher
from campus_worker.editorial import gates
from tests.helpers import make_entity, make_school
from tests.test_gates import RUBRIC_OK


def _staged_version(conn):
    from campus_worker import claims
    from tests.test_claims import _money
    inst, campus, topics = make_school(conn)
    ent = make_entity(conn, inst, campus, topics["housing"])
    r = claims.store_claim(conn, _money(inst, campus, topics["housing"], ent, 1204200), snapshot_id=None)
    with conn.cursor() as cur:
        cur.execute("INSERT INTO pages (institution_id, topic_id, entity_id, page_format, slug, path) VALUES (%s,%s,%s,'entity_profile','fixture-hall','/schools/fixture-state/housing/fixture-hall/') RETURNING id", (inst, topics["housing"], ent))
        pid = cur.fetchone()["id"]
    conn.commit()
    vid = gates.create_version(conn, pid, brief_id=None, headline="Fixture Hall: what the rate includes", deck="Deck.", body_md="Body paragraph.\n\n## More\n\nText " * 20,
                               body_html=None, structured={"claim_refs": [str(r.claim_id)], "fact_table": [{"label": "Double", "value": "$12,042", "claim_id": str(r.claim_id)}], "next_actions": [{"text": "Compare", "target": "/x/"}]},
                               byline="Housing desk", production_note="auto", claim_ids=[r.claim_id], writer_model="m", editor_model=None, verifier_model=None)
    return pid, vid


def test_repeat_publish_is_idempotent(clean_conn):
    pid, vid = _staged_version(clean_conn)
    cms = InMemoryCMS()
    with pytest.raises(publisher.NotPublishable):
        publisher.publish_version(clean_conn, cms, vid, environment="staging", auto_publish=False, new_pages_per_day=1)
    gates.gate_version(clean_conn, vid, [], RUBRIC_OK)
    o1 = publisher.publish_version(clean_conn, cms, vid, environment="staging", auto_publish=False, new_pages_per_day=1)
    assert o1.created and o1.changed and o1.status == "draft" and cms.writes == 1
    o2 = publisher.publish_version(clean_conn, cms, vid, environment="staging", auto_publish=False, new_pages_per_day=1)
    assert not o2.created and not o2.changed and cms.writes == 1 and len(cms.posts) == 1
    with clean_conn.cursor() as cur:
        cur.execute("SELECT status, cms_external_id, cms_content_hash FROM pages WHERE id=%s", (pid,))
        p = cur.fetchone()
    assert p["status"] == "staged" and p["cms_external_id"] == "1" and p["cms_content_hash"]
    # sanitised HTML reached the CMS; markdown converted; no script
    assert "<h2>More</h2>" in cms.posts[str(pid)]["content_html"] and "<script" not in cms.posts[str(pid)]["content_html"]
    assert cms.posts[str(pid)]["meta"]["byline"] == "Housing desk"


def test_production_auto_publish_respects_daily_quota(clean_conn):
    pid, vid = _staged_version(clean_conn)
    gates.gate_version(clean_conn, vid, [], RUBRIC_OK)
    cms = InMemoryCMS()
    o = publisher.publish_version(clean_conn, cms, vid, environment="production", auto_publish=True, new_pages_per_day=1)
    assert o.status == "publish"
    with clean_conn.cursor() as cur:
        cur.execute("INSERT INTO pages (page_format, slug, path) VALUES ('guide','g2','/schools/fixture-state/housing/g2/') RETURNING id")
        p2 = cur.fetchone()["id"]
    clean_conn.commit()
    v2 = gates.create_version(clean_conn, p2, brief_id=None, headline="Second page today", deck="d", body_md="x " * 200, body_html=None, structured={}, byline="Housing desk",
                              production_note="n", claim_ids=[], writer_model="m", editor_model=None, verifier_model=None)
    gates.gate_version(clean_conn, v2, [], RUBRIC_OK)
    with pytest.raises(publisher.QuotaExceeded):
        publisher.publish_version(clean_conn, cms, v2, environment="production", auto_publish=True, new_pages_per_day=1)
    assert len(cms.posts) == 1


def test_move_page_registers_redirect(clean_conn):
    pid, vid = _staged_version(clean_conn)
    gates.gate_version(clean_conn, vid, [], RUBRIC_OK)
    cms = InMemoryCMS()
    publisher.publish_version(clean_conn, cms, vid, environment="staging", auto_publish=False, new_pages_per_day=1)
    publisher.move_page(clean_conn, cms, pid, "/schools/fixture-state/housing/fixture-tower/", "fixture-tower")
    assert cms.posts["__redirects__"]["map"]["/schools/fixture-state/housing/fixture-hall/"] == "/schools/fixture-state/housing/fixture-tower/"
    o = publisher.publish_version(clean_conn, cms, vid, environment="staging", auto_publish=False, new_pages_per_day=1)
    assert o.changed and len([k for k in cms.posts if k != "__redirects__"]) == 1  # same post, new path, no duplicate


def test_wordpress_adapter_unconnected_without_credentials(monkeypatch):
    monkeypatch.delenv("CAMPUS_WP_APP_PASSWORD", raising=False)
    a = WordPressAdapter(None, None, None)
    assert a.capability().state == "unconnected"
    with pytest.raises(NotConnected):
        a.upsert(PublishRequest("x", "campus_guide", "t", "s", "/p/", "<p>x</p>"))
