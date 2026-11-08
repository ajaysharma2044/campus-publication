from campus_worker import claims, propagation as prop, queue as q
from tests.helpers import NOW, make_entity, make_school, make_snapshot, make_source
from tests.test_claims import _money


def _page(conn, inst, topic, path="/schools/fixture-state/housing/fixture-hall/"):
    with conn.cursor() as cur:
        cur.execute("INSERT INTO pages (institution_id, topic_id, page_format, slug, path, status) VALUES (%s,%s,'entity_profile','fixture-hall',%s,'published') RETURNING id", (inst, topic, path))
        pid = cur.fetchone()["id"]
    conn.commit()
    return pid


def test_claim_change_flags_pages_and_enqueues_once(clean_conn):
    inst, campus, topics = make_school(clean_conn)
    ent = make_entity(clean_conn, inst, campus, topics["housing"])
    src = make_source(clean_conn, inst, campus, "https://www.example.edu/rates", family="f")
    snap = make_snapshot(clean_conn, src)
    r1 = claims.store_claim(clean_conn, _money(inst, campus, topics["housing"], ent, 1204200), snapshot_id=snap, source_family="f")
    profile = _page(clean_conn, inst, topics["housing"])
    comparison = _page(clean_conn, inst, topics["housing"], "/schools/fixture-state/housing/compare/")
    prop.register(clean_conn, upstream_type="claim", upstream_id=r1.claim_id, downstream_type="page", downstream_id=profile)
    prop.register(clean_conn, upstream_type="claim", upstream_id=r1.claim_id, downstream_type="page", downstream_id=comparison)
    r2 = claims.store_claim(clean_conn, _money(inst, campus, topics["housing"], ent, 1240000), snapshot_id=make_snapshot(clean_conn, src, content_hash="b"), source_family="f")
    out = prop.on_claim_changed(clean_conn, r1.claim_id, r2.claim_id, reason="rate_changed")
    assert set(out["affected_pages"]) == {str(profile), str(comparison)} and all(j["created"] for j in out["jobs"])
    again = prop.on_claim_changed(clean_conn, r1.claim_id, r2.claim_id, reason="rate_changed")
    assert not any(j["created"] for j in again["jobs"])  # idempotent
    with clean_conn.cursor() as cur:
        cur.execute("SELECT count(*) AS n FROM pages WHERE revalidation_required")
        assert cur.fetchone()["n"] == 2
    assert prop.downstream_of(clean_conn, "claim", r2.claim_id)  # edges inherited by new claim
    assert q.counts(clean_conn)["queued"] == 2


def test_source_gone_propagates(clean_conn):
    inst, campus, topics = make_school(clean_conn)
    ent = make_entity(clean_conn, inst, campus, topics["housing"])
    src = make_source(clean_conn, inst, campus, "https://www.example.edu/rates", family="f")
    r1 = claims.store_claim(clean_conn, _money(inst, campus, topics["housing"], ent, 1204200), snapshot_id=make_snapshot(clean_conn, src), source_family="f")
    page = _page(clean_conn, inst, topics["housing"])
    prop.register(clean_conn, upstream_type="claim", upstream_id=r1.claim_id, downstream_type="page", downstream_id=page)
    out = prop.on_source_gone(clean_conn, src)
    assert out["stale_claims"] == [str(r1.claim_id)] and out["propagations"][0]["affected_pages"] == [str(page)]


def test_zero_fact_regression_halts(clean_conn):
    inst, campus, topics = make_school(clean_conn)
    ent = make_entity(clean_conn, inst, campus, topics["housing"])
    sources = []
    for i in range(5):
        s = make_source(clean_conn, inst, campus, f"https://www.example.edu/p{i}", family="f")
        snap = make_snapshot(clean_conn, s)
        claims.store_claim(clean_conn, _money(inst, campus, topics["housing"], ent, 1000 + i, room=f"r{i}"), snapshot_id=snap, source_family="f")
        sources.append(s)
    g = prop.regression_guard(clean_conn, source_ids=sources, extracted_counts={s: 0 for s in sources})
    assert g["halt"] and g["reason"] == "zero_fact_regression"
    ok = prop.regression_guard(clean_conn, source_ids=sources, extracted_counts={s: 1 for s in sources})
    assert not ok["halt"]
