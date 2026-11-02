from campus_worker.editorial import gates
from campus_worker.editorial.checks import Finding

RUBRIC_OK = {"clarity": 4, "specificity": 3, "structure": 4, "attribution": 4, "usefulness": 3, "prose": 3}  # 21


def test_gate_policy():
    assert gates.evaluate([], RUBRIC_OK, blocking=[]).passed
    r = gates.evaluate([], dict(RUBRIC_OK, prose=2), blocking=[])
    assert not r.passed and "below 3" in r.rubric_failures[0]
    r = gates.evaluate([], {k: 3 for k in RUBRIC_OK}, blocking=[])  # 18
    assert not r.passed and "total 18" in r.rubric_failures[0]
    r = gates.evaluate([Finding("fake_byline", "hard", "x")], RUBRIC_OK, blocking=[])
    assert r.status == "failed" and r.hard_failures
    r = gates.evaluate([], RUBRIC_OK, blocking=[{"id": "c1"}])
    assert not r.passed and "unresolved_conflict" in r.hard_failures[0]
    r = gates.evaluate([], RUBRIC_OK, blocking=[], novel_template=True)
    assert r.status == "held"
    r = gates.evaluate([Finding("filler", "major", "a"), Finding("filler", "major", "b"), Finding("headline", "major", "c")], RUBRIC_OK, blocking=[])
    assert not r.passed


def test_versioning_dedupes_identical_content_and_links_claims(clean_conn):
    from tests.helpers import make_school, make_entity
    from tests.test_claims import _money
    from campus_worker import claims
    inst, campus, topics = make_school(clean_conn)
    ent = make_entity(clean_conn, inst, campus, topics["housing"])
    r = claims.store_claim(clean_conn, _money(inst, campus, topics["housing"], ent, 1204200), snapshot_id=None)
    with clean_conn.cursor() as cur:
        cur.execute("INSERT INTO pages (institution_id, topic_id, entity_id, page_format, slug, path) VALUES (%s,%s,%s,'entity_profile','fixture-hall','/schools/fixture/housing/fixture-hall/') RETURNING id", (inst, topics["housing"], ent))
        pid = cur.fetchone()["id"]
    clean_conn.commit()
    kw = dict(brief_id=None, headline="H", deck="D", body_md="B" * 300, body_html=None, structured={"claim_refs": [str(r.claim_id)]}, byline="Housing desk",
              production_note="n", claim_ids=[r.claim_id], writer_model="m", editor_model=None, verifier_model=None)
    v1 = gates.create_version(clean_conn, pid, **kw)
    v2 = gates.create_version(clean_conn, pid, **kw)
    assert v1 == v2
    v3 = gates.create_version(clean_conn, pid, **dict(kw, body_md="C" * 300))
    assert v3 != v1
    with clean_conn.cursor() as cur:
        cur.execute("SELECT count(*) AS n FROM dependencies WHERE upstream_id=%s AND downstream_id=%s", (r.claim_id, pid))
        assert cur.fetchone()["n"] == 1
    res = gates.gate_version(clean_conn, v3, [], RUBRIC_OK)
    assert res.passed
    with clean_conn.cursor() as cur:
        cur.execute("SELECT status, current_version_id FROM pages WHERE id=%s", (pid,))
        p = cur.fetchone()
    assert p["status"] == "staged" and p["current_version_id"] == v3
