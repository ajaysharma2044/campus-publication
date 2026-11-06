"""Unthrottled production + live ramp (specs/continuous-local-run.md R8; AT9)."""
import dataclasses
from datetime import datetime, timedelta, timezone

import pytest

from campus_worker import ramp
from campus_worker.adapters.cms import InMemoryCMS
from campus_worker.cms import publisher
from campus_worker.config import get_settings
from campus_worker.editorial import gates
from tests.helpers import make_school
from tests.test_gates import RUBRIC_OK


def _gated_pages(conn, n: int, *, scores, start: int = 0):
    with conn.cursor() as cur:
        cur.execute("SELECT i.id, t.id AS topic FROM institutions i, topics t WHERE i.slug='fixture-state' AND t.key='housing'")
        row = cur.fetchone()
    if row:
        inst, topics = row["id"], {"housing": row["topic"]}
    else:
        inst, campus, topics = make_school(conn)
    out = []
    for j in range(n):
        i = start + j
        with conn.cursor() as cur:
            cur.execute("INSERT INTO pages (institution_id, topic_id, page_format, slug, path) VALUES (%s,%s,'guide',%s,%s) RETURNING id",
                        (inst, topics["housing"], f"fixture-{i}", f"/schools/fixture-state/housing/fixture-{i}/"))
            pid = cur.fetchone()["id"]
        conn.commit()
        vid = gates.create_version(conn, pid, brief_id=None, headline=f"Fixture page {i}: what the rate includes", deck="Deck.", body_md="Body paragraph.\n\n## More\n\nText " * 20,
                                   body_html=None, structured={"fact_table": [], "next_actions": []}, byline="Housing desk", production_note="synthetic fixture",
                                   claim_ids=[], writer_model="m", editor_model=None, verifier_model=None)
        gates.gate_version(conn, vid, [], RUBRIC_OK)
        ramp.mark_ready(conn, pid, niche_score=scores[j])
        out.append((pid, vid, scores[j]))
    return out


def test_parse_ramp_and_rates():
    st = ramp.parse_ramp("5x14,15")
    assert [(s.per_day, s.days) for s in st] == [(5, 14), (15, None)]
    assert ramp.rate_for_day(st, 0) == 5 and ramp.rate_for_day(st, 13) == 5 and ramp.rate_for_day(st, 14) == 15 and ramp.rate_for_day(st, 400) == 15
    assert ramp.rate_for_day(ramp.parse_ramp("2x3,4x3,9"), 6) == 9 and ramp.rate_for_day(ramp.parse_ramp("3"), 99) == 3
    with pytest.raises(ValueError):
        ramp.parse_ramp("5,15x2")  # only the last stage may be open-ended
    with pytest.raises(ValueError):
        ramp.parse_ramp("abc")


def test_no_live_domain_all_ready_pages_publish_locally_without_quota(clean_conn, tmp_path):
    settings = dataclasses.replace(get_settings(), environment="development", live_domain=None)
    assert not settings.is_live
    pages = _gated_pages(clean_conn, 10, scores=[float(i) for i in range(10)])
    cms = InMemoryCMS()
    results = [publisher.publish_local(clean_conn, cms, vid, settings=settings, out_root=tmp_path) for _, vid, _ in pages]
    assert len(results) == 10 and all((tmp_path / f"schools/fixture-state/housing/fixture-{i}/index.html").exists() for i in range(10))
    assert len(cms.posts) == 10 and all(p["status"] == "draft" for p in cms.posts.values())
    with clean_conn.cursor() as cur:
        cur.execute("SELECT count(*) AS n FROM pages WHERE local_published_at IS NOT NULL AND status='staged'")
        assert cur.fetchone()["n"] == 10
        cur.execute("SELECT count(*) AS n FROM live_releases")
        assert cur.fetchone()["n"] == 0  # nothing is public; nothing waited
    # with no live domain release_live is a no-op, not an error
    assert publisher.release_live(clean_conn, cms, settings=settings)["released"] == []


def test_live_domain_ramp_releases_exactly_five_in_niche_order_and_production_continues(clean_conn):
    settings = dataclasses.replace(get_settings(), environment="production", live_domain="example.org", auto_publish_enabled=True)
    settings = dataclasses.replace(settings, quotas=dataclasses.replace(settings.quotas, live_ramp="5x14,15"))
    assert settings.is_live
    scores = [3.0, 9.0, 1.0, 7.0, 5.0, 8.0, 2.0, 6.0, 4.0, 10.0]
    pages = _gated_pages(clean_conn, 10, scores=scores)
    cms = InMemoryCMS()
    now = datetime.now(timezone.utc)
    r = publisher.release_live(clean_conn, cms, settings=settings, now=now)
    assert len(r["released"]) == 5 and r["still_ready"] == 5
    assert [float(x["niche_score"]) for x in r["released"]] == [10.0, 9.0, 8.0, 7.0, 6.0]
    assert r["allowance"]["rate"] == 5 and r["allowance"]["remaining"] == 0
    assert len(cms.posts) == 5 and all(p["status"] == "publish" for p in cms.posts.values())
    # a second call the same day releases nothing more; pages stay ready, not failed
    r2 = publisher.release_live(clean_conn, cms, settings=settings, now=now)
    assert r2["released"] == [] and r2["still_ready"] == 5
    # production continues while pages wait: an 11th page passes its gates and becomes ready
    _gated_pages(clean_conn, 1, scores=[0.5], start=10)
    assert len(ramp.ready_queue(clean_conn)) == 6
    # day 15: rate is 15, so everything left goes live
    r3 = publisher.release_live(clean_conn, cms, settings=settings, now=now + timedelta(days=14))
    assert r3["allowance"]["rate"] == 15 and len(r3["released"]) == 6 and r3["still_ready"] == 0
    with clean_conn.cursor() as cur:
        cur.execute("SELECT count(*) AS n FROM live_releases WHERE kind='new'")
        assert cur.fetchone()["n"] == 11


def test_indexing_hold_freezes_rate(clean_conn):
    settings = dataclasses.replace(get_settings(), environment="production", live_domain="example.org")
    now = datetime.now(timezone.utc)
    ramp.ensure_live_since(clean_conn, now.date() - timedelta(days=20))
    assert ramp.allowance(clean_conn, "5x14,15", now=now)["rate"] == 15
    h = ramp.set_indexing_hold(clean_conn, live_pages_checked=10, unindexed=3, current_rate=5)
    assert h["hold"] is True and "30%" in h["reason"]
    a = ramp.allowance(clean_conn, "5x14,15", now=now)
    assert a["rate"] == 5 and a["hold"] is True
    h2 = ramp.set_indexing_hold(clean_conn, live_pages_checked=10, unindexed=2, current_rate=5)
    assert h2["hold"] is False and ramp.allowance(clean_conn, "5x14,15", now=now)["rate"] == 15
