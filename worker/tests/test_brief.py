from campus_worker import claims
from campus_worker.briefs import audience_guide_justified, build_entity_profile_brief, persist_brief
from campus_worker.types import ClaimRecord
from tests.helpers import NOW, make_entity, make_school, make_snapshot, make_source
from tests.test_claims import _money


def _bool(inst, campus, topic, ent, field, val, aud=None):
    return ClaimRecord(institution_id=inst, campus_id=campus, entity_id=ent, topic_id=topic, field=field, value_type="boolean", value_bool=val,
                       audience_applicability=[aud] if aud else [], evidence_category="verified_fact", extraction_method="deterministic", retrieved_at=NOW)


def test_brief_blocks_on_missing_required_evidence_and_lists_unknowns(clean_conn):
    inst, campus, topics = make_school(clean_conn)
    ent = make_entity(clean_conn, inst, campus, topics["housing"])
    b = build_entity_profile_brief(clean_conn, entity_id=ent)
    assert not b.ready and b.blocked_by == ["missing_evidence:rate.room"]
    claims.store_claim(clean_conn, _money(inst, campus, topics["housing"], ent, 1204200), snapshot_id=None)
    claims.store_claim(clean_conn, _bool(inst, campus, topics["housing"], ent, "amenity.air_conditioning", True), snapshot_id=None)
    b = build_entity_profile_brief(clean_conn, entity_id=ent)
    assert b.ready and len(b.critical_claim_ids) == 1 and "$12,042 per academic year per person (2026-27)" in b.verified_answer
    assert any(u.startswith("amenity.kitchen: unknown") for u in b.unresolved_facts)
    assert b.evidence_packet[0]["claim_id"] and "excerpt" not in b.evidence_packet[0]
    bid = persist_brief(clean_conn, b)
    with clean_conn.cursor() as cur:
        cur.execute("SELECT status, array_length(critical_claim_ids,1) AS n FROM briefs WHERE id=%s", (bid,))
        r = cur.fetchone()
    assert r["status"] == "approved" and r["n"] == 1


def test_brief_blocks_on_conflicted_critical_claim(clean_conn):
    inst, campus, topics = make_school(clean_conn)
    ent = make_entity(clean_conn, inst, campus, topics["housing"])
    s1 = make_source(clean_conn, inst, campus, "https://www.example.edu/a", family="a")
    s2 = make_source(clean_conn, inst, campus, "https://www.example.edu/b", family="b")
    claims.store_claim(clean_conn, _money(inst, campus, topics["housing"], ent, 1204200), snapshot_id=make_snapshot(clean_conn, s1), source_family="a")
    claims.store_claim(clean_conn, _money(inst, campus, topics["housing"], ent, 1190000), snapshot_id=make_snapshot(clean_conn, s2), source_family="b")
    b = build_entity_profile_brief(clean_conn, entity_id=ent)
    assert not b.ready and b.blocked_by[0].startswith("critical_claims_conflicted_or_stale")


def test_audience_guide_only_when_rules_differ(clean_conn):
    inst, campus, topics = make_school(clean_conn)
    ent = make_entity(clean_conn, inst, campus, topics["housing"])
    ok, why = audience_guide_justified(clean_conn, entity_id=ent, institution_id=inst, topic_id=topics["housing"], audience="transfer")
    assert not ok and "no transfer-specific" in why
    claims.store_claim(clean_conn, _bool(inst, campus, topics["housing"], ent, "eligibility.guaranteed_housing", True), snapshot_id=None)
    claims.store_claim(clean_conn, _bool(inst, campus, topics["housing"], ent, "eligibility.guaranteed_housing", True, aud="transfer"), snapshot_id=None)
    ok, why = audience_guide_justified(clean_conn, entity_id=ent, institution_id=inst, topic_id=topics["housing"], audience="transfer")
    assert not ok and "match the general rules" in why
    claims.store_claim(clean_conn, _bool(inst, campus, topics["housing"], ent, "eligibility.guaranteed_housing", False, aud="transfer"), snapshot_id=None)
    ok, why = audience_guide_justified(clean_conn, entity_id=ent, institution_id=inst, topic_id=topics["housing"], audience="transfer")
    assert ok and "eligibility.guaranteed_housing" in why
