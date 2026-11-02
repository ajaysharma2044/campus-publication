from campus_worker import claims
from campus_worker.tools.calculator import LineItem, calculate
from campus_worker.tools.comparison import compare, tradeoffs
from campus_worker.types import ClaimRecord
from tests.helpers import NOW, make_entity, make_school
from tests.test_claims import _money


def test_calculator_equivalent_periods_deposits_unknowns():
    items = [LineItem("Room", 1204200, "per_academic_year"), LineItem("Meal plan", 295000, "per_semester"),
             LineItem("Deposit", 25000, "one_time", refundable_deposit=True), LineItem("Parking", None, "per_academic_year", mandatory=False),
             LineItem("Insurance", 1500, "per_month", mandatory=False, is_assumption=True)]
    r = calculate(items)
    assert r.mandatory_total_minor == 1204200 + 2 * 295000 and r.deposits_minor == 25000
    assert r.optional_total_minor == 9 * 1500 and r.unknown_items == ["Parking"] and not r.complete
    sem = calculate(items, target_period="per_semester")
    assert sem.mandatory_total_minor == 602100 + 295000
    assert any(i.status == "assumption" for i in r.items)


def test_calculator_per_unit_requires_occupants_and_unknown_period():
    it = [LineItem("Apartment", 1860000, "per_academic_year", "per_unit")]
    r = calculate(it)
    assert r.unknown_items == ["Apartment"] and "occupants" in r.items[0].note
    r2 = calculate(it, assumptions={"occupants_per_unit": 2})
    assert r2.mandatory_total_minor == 930000
    r3 = calculate([LineItem("Fee", 1000, "unknown")])
    assert r3.items[0].status == "not_convertible" and r3.mandatory_total_minor == 0
    assert calculate([LineItem("Neg", -5, "per_month")]).errors


def test_comparison_uses_shared_records_and_no_winner(clean_conn):
    inst, campus, topics = make_school(clean_conn)
    a = make_entity(clean_conn, inst, campus, topics["housing"], name="Fixture Hall", slug="fixture-hall")
    b = make_entity(clean_conn, inst, campus, topics["housing"], name="Riverside Hall", slug="riverside-hall")
    claims.store_claim(clean_conn, _money(inst, campus, topics["housing"], a, 1204200), snapshot_id=None)
    claims.store_claim(clean_conn, _money(inst, campus, topics["housing"], b, 579100, period="per_semester"), snapshot_id=None)  # same yearly basis after conversion
    for ent, val in ((a, True), (b, False)):
        claims.store_claim(clean_conn, ClaimRecord(institution_id=inst, campus_id=campus, entity_id=ent, topic_id=topics["housing"], field="amenity.air_conditioning",
                                                   value_type="boolean", value_bool=val, evidence_category="verified_fact", extraction_method="deterministic", retrieved_at=NOW), snapshot_id=None)
    comp = compare(clean_conn, [a, b])
    rate = next(r for r in comp.rows if r.field == "rate.room")
    assert [c.raw for c in rate.cells] == [1204200, 1158200] and rate.differs
    ac = next(r for r in comp.rows if r.field == "amenity.air_conditioning")
    assert ac.differs and [c.display for c in ac.cells] == ["Yes", "No"]
    kitchen = next(r for r in comp.rows if r.field == "amenity.kitchen")
    assert all(c.status == "unknown" for c in kitchen.cells) and not kitchen.differs
    t = tradeoffs(comp)
    assert any("$460 less" in x for x in t) and not any("better" in x.lower() for x in t)
    assert comp.notes and "Unknown does not mean" in comp.notes[-1]


def test_comparison_no_eligible_results(clean_conn):
    import pytest
    inst, campus, topics = make_school(clean_conn)
    a = make_entity(clean_conn, inst, campus, topics["housing"])
    with pytest.raises(ValueError):
        compare(clean_conn, [a])
