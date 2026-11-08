"""LEAN MODE (owner decision 2026-11-06, STATE.md): scores order the work, any non-navigational cluster without a strong incumbent gets a page once
its scope has a verified fact; gain minimum 1; tier-2 minimum 4; beat review every 10th page; sweep cap 5000. Spec thresholds stay testable with CAMPUS_LEAN_MODE=0."""
from __future__ import annotations

import json
from datetime import datetime, timezone

import pytest

from campus_worker import claims as cm
from campus_worker import funnel, lanes, lean, quality, sweep
from campus_worker.types import ClaimRecord
from tests.helpers import make_school


@pytest.fixture
def lean_on(monkeypatch):
    monkeypatch.setenv("CAMPUS_LEAN_MODE", "1")
    monkeypatch.delenv("CAMPUS_SWEEP_INTEL_CAP", raising=False)  # the run harness may export an override; the default is what is under test
    yield


def _cluster(conn, inst, campus, topic, label, *, agi, state="watch", niche=10.0, nav=False):
    with conn.cursor() as cur:
        cur.execute("""INSERT INTO intent_clusters (institution_id, campus_id, topic_id, label, answer_key, audience, task, queue_state, d_score, agi, g_est, e_est, niche_score, last_intel_at, independent_occurrences)
                       VALUES (%s,%s,%s,%s,%s,NULL,'decide',%s,1,%s,3,3,%s,now(),1) RETURNING id""", (inst, campus, topic, label, label, state, agi, niche))
        cid = cur.fetchone()["id"]
        cur.execute("""INSERT INTO serp_observations (cluster_id, query_text, observed_at, locale, device, results, direct_answer_quality, missing_contribution, provider)
                       VALUES (%s,%s,now(),'en-US','desktop',%s::jsonb,%s,'x','observed via search tool (fixture)')""",
                    (cid, label, json.dumps([{"position": 1, "url": "https://forum.example.invalid/t/1", "title": label, "publisher": "forum", "result_type": "forum", "dedicated": agi <= 1,
                                              "answer_quality": "navigational_official" if nav else ("complete" if agi <= 1 else "partial"), "freshness": "current" if agi <= 1 else "stale", "freshness_date": None, "evidence_quality": "sourced" if agi <= 1 else "unsourced", "missing_contribution": "verified facts"}]),
                     "navigational_official" if nav else "partial"))
    conn.commit()
    return cid


def _verified_claim(conn, inst, campus, topic):
    rec = ClaimRecord(institution_id=inst, campus_id=campus, entity_id=None, topic_id=topic, field="rate.room", value_type="money", value_number=1204200, unit="minor_units", currency="USD",
                      billing_period="per_academic_year", price_basis="per_person", room_type="double", evidence_category="verified_fact", extraction_method="deterministic", extraction_model="fixture",
                      extraction_confidence=0.95, retrieved_at=datetime.now(timezone.utc), academic_year="2026-27", audience_applicability=[])
    return cm.store_claim(conn, rec, snapshot_id=None).claim_id


def test_lean_funnel_orders_by_score_and_requires_a_verified_fact(clean_conn, lean_on):
    inst, campus, topics = make_school(clean_conn)
    with clean_conn.cursor() as cur:  # lean.production_queue deliberately skips synthetic_fixture schools; this test needs a queue-eligible one
        cur.execute("UPDATE institutions SET identity_status='verified' WHERE id=%s", (inst,))
    clean_conn.commit()
    housing = topics["housing"]
    weak_incumbent = _cluster(clean_conn, inst, campus, housing, "fixture hall laundry", agi=4, niche=30)
    strong_incumbent = _cluster(clean_conn, inst, campus, housing, "fixture hall address", agi=1, niche=50)
    nav = _cluster(clean_conn, inst, campus, housing, "fixture housing portal login", agi=4, state="navigational", niche=60, nav=True)
    assert not funnel.qualify(clean_conn, weak_incumbent).ok and "no verified fact" in funnel.qualify(clean_conn, weak_incumbent).reason
    assert funnel.guard(clean_conn, weak_incumbent, "researcher").ok and not funnel.guard(clean_conn, weak_incumbent, "writer").ok  # research first, then the rest
    _verified_claim(clean_conn, inst, campus, housing)
    g = funnel.qualify(clean_conn, weak_incumbent)
    assert g.ok and g.stage == "lean_funnel"
    assert not funnel.qualify(clean_conn, strong_incumbent).ok and "strong dedicated incumbent" in funnel.qualify(clean_conn, strong_incumbent).reason
    assert not funnel.qualify(clean_conn, nav).ok and "navigational" in funnel.qualify(clean_conn, nav).reason
    q = lean.production_queue(clean_conn, limit=5)
    assert [str(x["cluster_id"]) for x in q] == [str(weak_incumbent)]  # strong incumbent and navigational never enter the queue
    item = lanes.production_item(clean_conn)
    assert item and item["kind"] == "lean_queue_cluster" and item["cluster_id"] == str(weak_incumbent)


def test_spec_mode_keeps_the_sweet_spot_rule(clean_conn, monkeypatch):
    monkeypatch.setenv("CAMPUS_LEAN_MODE", "0")
    inst, campus, topics = make_school(clean_conn)
    cid = _cluster(clean_conn, inst, campus, topics["housing"], "fixture hall laundry", agi=4, niche=30)
    _verified_claim(clean_conn, inst, campus, topics["housing"])
    g = funnel.qualify(clean_conn, cid)
    assert not g.ok and g.stage == "agi_threshold"


def test_lean_minimums_and_spot_check(clean_conn, lean_on):
    inst, campus, topics = make_school(clean_conn)
    cid = _verified_claim(clean_conn, inst, campus, topics["housing"])
    g = quality.check_information_gain(clean_conn, [{"item": "per-person rate", "claim_id": str(cid)}])
    assert g.ok and "minimum 1" in g.reason
    assert lean.TIER2_MIN_CLAIMS_LEAN == 4 and sweep.sweep_cap() == 5000
    assert lean.spot_check_due(0) and not lean.spot_check_due(1) and lean.spot_check_due(9) and not lean.spot_check_due(10) and lean.spot_check_due(19)


def test_lean_coverage_check_and_default_path(clean_conn, lean_on):
    from uuid import UUID
    from campus_worker import pipeline
    from campus_worker.editorial import gates
    inst, campus, topics = make_school(clean_conn)
    housing = topics["housing"]
    with clean_conn.cursor() as cur:
        cur.execute("INSERT INTO pages (institution_id, campus_id, topic_id, page_format, slug, path, audience, status, primary_query) VALUES (%s,%s,%s,'guide','transfer-housing','/schools/fixture-state/housing/transfer-housing/','transfer','staged','is housing guaranteed for transfer students at fixture state') RETURNING id", (inst, campus, housing))
        pid = cur.fetchone()["id"]
    clean_conn.commit()
    vid = gates.create_version(clean_conn, pid, brief_id=None, headline="Is Housing Guaranteed for Fixture State Transfer Students?", deck=None, body_md="## Do transfer students have to live on campus at Fixture State?\n\nYes, for one year (fixture).\n\n[[fact-table]]\n", body_html=None, structured={}, byline="Housing desk", production_note="fixture", claim_ids=[], writer_model="fixture", editor_model=None, verifier_model=None)
    with clean_conn.cursor() as cur:
        cur.execute("UPDATE pages SET current_version_id=%s WHERE id=%s", (vid, pid))
    clean_conn.commit()
    covered = _cluster(clean_conn, inst, campus, housing, "Do transfer students have to live on campus at Fixture State?", agi=4, niche=40)
    fresh = _cluster(clean_conn, inst, campus, housing, "Which Fixture State halls have air conditioning?", agi=4, niche=35)
    assert lean.covered_by_existing_page(clean_conn, cluster_id=covered) == "/schools/fixture-state/housing/transfer-housing/"
    assert lean.covered_by_existing_page(clean_conn, cluster_id=fresh) is None
    assert lean.default_page_path(clean_conn, cluster_id=fresh) == "/schools/fixture-state/housing/which-fixture-state-halls-air-conditioning/"
    poss = _cluster(clean_conn, inst, campus, housing, "Is Fixture State's north campus housing transfers?", agi=4, niche=20)
    assert lean.default_page_path(clean_conn, cluster_id=poss) == "/schools/fixture-state/housing/fixture-state-north-campus-housing-transfers/"
