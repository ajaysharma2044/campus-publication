from datetime import datetime, timezone
from uuid import uuid4
from campus_worker import claims
from campus_worker.collectors.html import extract_material
from campus_worker.config import FIXTURES_DIR
from campus_worker.types import ClaimRecord
from tests.helpers import NOW, make_entity, make_school, make_snapshot, make_source

SRC = FIXTURES_DIR / "sources"


def _money(inst, campus, topic, entity, minor, *, ay="2026-27", room="double", period="per_academic_year", basis="per_person"):
    return ClaimRecord(institution_id=inst, campus_id=campus, entity_id=entity, topic_id=topic, field="rate.room", value_type="money",
                       value_number=minor, unit="minor_units", currency="USD", billing_period=period, price_basis=basis, room_type=room,
                       academic_year=ay, evidence_category="verified_fact", extraction_method="deterministic", retrieved_at=NOW)


def test_rate_table_extraction_scopes_years_and_preserves_unknowns():
    ex = extract_material((SRC / "fixture_hall_rates_v1.html").read_bytes())
    inst, topic = uuid4(), uuid4()
    cs, warnings = claims.extract_rate_table(ex.tables[0], institution_id=inst, campus_id=None, topic_id=topic, entity_id=None,
                                             retrieved_at=NOW, context_text=ex.material_text)
    assert len(cs) == 6 and warnings == []
    by = {(c.room_type, c.academic_year): c.value_number for c in cs}
    assert by[("double", "2026-27")] == 1204200 and by[("double", "2025-26")] == 1158000
    assert all(c.billing_period == "per_academic_year" and c.price_basis == "per_person" for c in cs)
    # a table with no period or basis words must say unknown, not guess
    cs2, w2 = claims.extract_rate_table({"headers": ["Room", "2026–27"], "rows": [["Single", "$900"]]}, institution_id=inst, campus_id=None,
                                        topic_id=topic, entity_id=None, retrieved_at=NOW)
    assert cs2[0].billing_period == "unknown" and cs2[0].price_basis == "unknown"
    assert "billing_period_unknown" in w2 and "price_basis_unknown" in w2


def test_same_value_from_second_source_confirms_not_duplicates(clean_conn):
    inst, campus, topics = make_school(clean_conn)
    ent = make_entity(clean_conn, inst, campus, topics["housing"])
    s1 = make_source(clean_conn, inst, campus, "https://www.example.edu/rates", family="housing-site")
    s2 = make_source(clean_conn, inst, campus, "https://www.example.edu/rates-print", family="housing-site")
    snap1, snap2 = make_snapshot(clean_conn, s1), make_snapshot(clean_conn, s2)
    r1 = claims.store_claim(clean_conn, _money(inst, campus, topics["housing"], ent, 1204200), snapshot_id=snap1, source_family="housing-site")
    r2 = claims.store_claim(clean_conn, _money(inst, campus, topics["housing"], ent, 1204200), snapshot_id=snap2, source_family="housing-site")
    assert r1.action == "created" and r2.action == "confirmed" and r1.claim_id == r2.claim_id
    assert len(claims.current_claims_for_entity(clean_conn, ent)) == 1


def test_different_year_is_a_different_claim_not_a_conflict(clean_conn):
    inst, campus, topics = make_school(clean_conn)
    ent = make_entity(clean_conn, inst, campus, topics["housing"])
    r1 = claims.store_claim(clean_conn, _money(inst, campus, topics["housing"], ent, 1158000, ay="2025-26"), snapshot_id=None)
    r2 = claims.store_claim(clean_conn, _money(inst, campus, topics["housing"], ent, 1204200, ay="2026-27"), snapshot_id=None)
    assert r1.action == r2.action == "created"
    # per-person vs per-unit are different scopes too
    r3 = claims.store_claim(clean_conn, _money(inst, campus, topics["housing"], ent, 1860000, room="apartment", basis="per_unit"), snapshot_id=None)
    r4 = claims.store_claim(clean_conn, _money(inst, campus, topics["housing"], ent, 930000, room="apartment", basis="per_person"), snapshot_id=None)
    assert r3.action == r4.action == "created"


def test_conflicting_critical_claim_blocks_until_resolved(clean_conn):
    inst, campus, topics = make_school(clean_conn)
    ent = make_entity(clean_conn, inst, campus, topics["housing"])
    s1 = make_source(clean_conn, inst, campus, "https://www.example.edu/rates", family="housing-site")
    s2 = make_source(clean_conn, inst, campus, "https://www.example.edu/brochure.pdf", family="brochure", kind="official_pdf")
    snap1, snap2 = make_snapshot(clean_conn, s1), make_snapshot(clean_conn, s2)
    r1 = claims.store_claim(clean_conn, _money(inst, campus, topics["housing"], ent, 1204200), snapshot_id=snap1, source_family="housing-site")
    r2 = claims.store_claim(clean_conn, _money(inst, campus, topics["housing"], ent, 1190000), snapshot_id=snap2, source_family="brochure")
    assert r2.action == "conflict" and r2.conflict_id is not None
    blocked = claims.blocking_claims(clean_conn, [r1.claim_id, r2.claim_id])
    assert {b["id"] for b in blocked} == {r1.claim_id, r2.claim_id}
    claims.resolve_conflict(clean_conn, r2.conflict_id, winner_claim_id=r1.claim_id, resolution="rates page is the responsible official source; brochure is an estimate")
    assert claims.blocking_claims(clean_conn, [r1.claim_id]) == []
    cur_claims = claims.current_claims_for_entity(clean_conn, ent)
    assert len(cur_claims) == 1 and cur_claims[0]["evidence_category"] == "verified_fact"


def test_same_family_update_supersedes_and_marks_old_stale(clean_conn):
    inst, campus, topics = make_school(clean_conn)
    ent = make_entity(clean_conn, inst, campus, topics["housing"])
    s1 = make_source(clean_conn, inst, campus, "https://www.example.edu/rates", family="housing-site")
    snap1 = make_snapshot(clean_conn, s1, content_hash="a")
    snap2 = make_snapshot(clean_conn, s1, content_hash="b")
    r1 = claims.store_claim(clean_conn, _money(inst, campus, topics["housing"], ent, 1204200), snapshot_id=snap1, source_family="housing-site")
    r2 = claims.store_claim(clean_conn, _money(inst, campus, topics["housing"], ent, 1240000), snapshot_id=snap2, source_family="housing-site")
    assert r2.action == "superseded" and r2.superseded_id == r1.claim_id
    with clean_conn.cursor() as cur:
        cur.execute("SELECT evidence_category, superseded_by_id FROM claims WHERE id=%s", (r1.claim_id,))
        old = cur.fetchone()
    assert old["evidence_category"] == "stale" and old["superseded_by_id"] == r2.claim_id


def test_source_gone_downgrades_sole_source_claims(clean_conn):
    inst, campus, topics = make_school(clean_conn)
    ent = make_entity(clean_conn, inst, campus, topics["housing"])
    s1 = make_source(clean_conn, inst, campus, "https://www.example.edu/rates", family="housing-site")
    snap1 = make_snapshot(clean_conn, s1)
    r1 = claims.store_claim(clean_conn, _money(inst, campus, topics["housing"], ent, 1204200), snapshot_id=snap1, source_family="housing-site")
    assert claims.mark_stale_for_source(clean_conn, s1) == [r1.claim_id]


def test_verified_fact_upgrades_or_supersedes_a_snippet_estimate(clean_conn):
    """continuous-local-run S4: once the primary page is opened, snippet estimates become verified (same value) or are superseded (different value); never a conflict."""
    from tests.helpers import make_school, make_entity, make_source, make_snapshot
    inst, campus, topics = make_school(clean_conn)
    ent = make_entity(clean_conn, inst, campus, topics["housing"])
    snip = make_source(clean_conn, inst, campus, "https://www.fixturestate.example.edu/rates#search-snippet", family="search-snippet", kind="search_snippet")
    official = make_source(clean_conn, inst, campus, "https://www.fixturestate.example.edu/rates", family="fixture-housing-site")
    s1, s2 = make_snapshot(clean_conn, snip), make_snapshot(clean_conn, official, content_hash="h2")
    est = _money(inst, campus, topics["housing"], ent, 687200, period="per_semester").model_copy(update={"evidence_category": "estimate", "extraction_method": "import"})
    r0 = claims.store_claim(clean_conn, est, snapshot_id=s1, source_family="search-snippet")
    assert r0.action == "created"
    fact = _money(inst, campus, topics["housing"], ent, 687200, period="per_semester")
    r1 = claims.store_claim(clean_conn, fact, snapshot_id=s2, source_family="fixture-housing-site")
    assert r1.action == "verified" and r1.claim_id == r0.claim_id
    with clean_conn.cursor() as cur:
        cur.execute("SELECT evidence_category, conflict_status FROM claims WHERE id=%s", (r0.claim_id,))
        row = cur.fetchone()
    assert row["evidence_category"] == "verified_fact" and row["conflict_status"] == "none"
    est2 = _money(inst, campus, topics["housing"], ent, 778300, period="per_semester", room="single").model_copy(update={"evidence_category": "estimate", "extraction_method": "import"})
    r2 = claims.store_claim(clean_conn, est2, snapshot_id=s1, source_family="search-snippet")
    fact2 = _money(inst, campus, topics["housing"], ent, 780000, period="per_semester", room="single")
    r3 = claims.store_claim(clean_conn, fact2, snapshot_id=s2, source_family="fixture-housing-site")
    assert r3.action == "superseded" and r3.superseded_id == r2.claim_id
    assert claims.blocking_claims(clean_conn, [r3.claim_id]) == []
