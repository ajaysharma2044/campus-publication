"""R16 chain on fixtures with a fake agent runner (continuous-local-run AT14 fixture counterpart, AT23, AT38, AT44, AT45 wiring)."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from uuid import UUID

import pytest

from campus_worker import claims as cm
from campus_worker import pipeline
from campus_worker.config import get_settings
from campus_worker.types import ClaimRecord
from tests.agent_fixtures import GENERIC, envelope, cli_stdout
from tests.helpers import make_school

PATH = "/schools/fixture-state/housing/fixture-hall-transfer/"
LINKS = ["/about/methods/", "/about/corrections/", "/schools/fixture-state/housing/riverside-hall/"]


def _claim(conn, inst, campus, topic, field, **kw) -> str:
    base = dict(institution_id=inst, campus_id=campus, entity_id=None, topic_id=topic, field=field, evidence_category="verified_fact", extraction_method="deterministic", extraction_model="fixture",
                extraction_confidence=0.95, retrieved_at=datetime.now(timezone.utc), academic_year="2026-27", audience_applicability=[], billing_period=None, price_basis=None, room_type=None, unit=None, currency=None)
    base.update(kw)
    return str(cm.store_claim(conn, ClaimRecord(**base), snapshot_id=None).claim_id)


def _setup(conn):
    inst, campus, topics = make_school(conn)
    housing = topics["housing"]
    ids = {"rate": _claim(conn, inst, campus, housing, "rate.room", value_type="money", value_number=1204200, unit="minor_units", currency="USD", billing_period="per_academic_year", price_basis="per_person", room_type="double"),
           "elig": _claim(conn, inst, campus, housing, "eligibility.transfer_may_apply", value_type="boolean", value_bool=True, audience_applicability=["transfer"]),
           "deadline": _claim(conn, inst, campus, housing, "deadline.housing_application", value_type="date", value_date=datetime(2026, 5, 15).date(), audience_applicability=["transfer"])}
    with conn.cursor() as cur:
        cur.execute("""INSERT INTO intent_clusters (institution_id, campus_id, topic_id, label, answer_key, audience, task, queue_state, d_score, agi, g_est, e_est, niche_score)
                       VALUES (%s,%s,%s,'fixture hall transfer housing','fixture hall transfer housing','transfer','decide','in_production',2,4,4,4,64) RETURNING id""", (inst, campus, housing))
        cid = cur.fetchone()["id"]
        results = [{"position": i + 1, "url": f"https://forum.example.invalid/t/{i}", "title": f"Fixture Hall thread {i}", "publisher": "forum", "result_type": "forum", "dedicated": False, "answer_quality": "partial",
                    "freshness": "stale", "freshness_date": "2023-01-01", "evidence_quality": "unsourced", "missing_contribution": "verified rates and the transfer rule"} for i in range(3)]
        cur.execute("""INSERT INTO serp_observations (cluster_id, query_text, observed_at, locale, device, results, direct_answer_quality, missing_contribution, provider)
                       VALUES (%s,'fixture hall transfer housing',now(),'en-US','desktop',%s::jsonb,'partial','verified per-person rate','observed via search tool on 2026-11-06 (fixture)')""", (cid, json.dumps(results)))
        doc = {"scope": {"school_slug": "fixture-state", "topic_key": "housing"}, "cluster_map": [], "internal_links": [], "trust_signals": {"sources_section": True, "updated_date": True},
               "win_plans": [{"page_path": PATH, "primary_query": "fixture hall transfer housing", "target_title": "Fixture Hall Transfer Housing: Cost and Eligibility", "h1": "Fixture Hall transfer housing",
                              "contribution": "a verified per-person rate and the transfer rule", "answer_first_intro": "Transfers may apply; a double costs $12,042 per person for 2026-27.", "snippet_formats": ["table", "numbered_steps"],
                              "faq_real_questions": [], "secondary_questions": ["Who can live in Fixture Hall?", "When is the housing application due?"], "beats": [{"url": results[0]["url"], "how": "verified rate with a source"}]}],
               "refresh_cadence": [], "win_criteria": []}
        cur.execute("INSERT INTO strategies (institution_id, place_id, topic_id, version, doc) VALUES (%s,NULL,%s,1,%s::jsonb)", (inst, housing, json.dumps(doc)))
    conn.commit()
    return inst, campus, housing, cid, ids


BODY = """Transfer students may apply to live in Fixture Hall, and a double room costs $12,042 per person for the 2026-27 academic year (synthetic fixture). The housing application for transfers is due 2026-05-15.

## Who can live in Fixture Hall?

Transfer students may apply, according to the fixture housing page. The rate is the same per person for transfer and continuing students.

[[fact-table]]

## When is the housing application due?

1. Receive your fixture NetID.
2. Submit the housing application by 2026-05-15.
3. Watch for the assignment email.

Read [how we verify these facts](/about/methods/), and [report an error](/about/corrections/) if a figure looks wrong. Compare the rate with [Riverside Hall](/schools/fixture-state/housing/riverside-hall/), or browse [housing at Fixture State](/schools/fixture-state/housing/) and the [Fixture State University hub](/schools/fixture-state/).

## What we could not verify

The fixture pages do not state whether a deposit is charged.
"""


def _runner_for(ids: dict):
    def runner(agent, prompt):
        role = agent.role
        if role == "planner":
            out = {"page_format": "guide", "audience": "transfer", "reader_decision": "Whether to apply for Fixture Hall as a transfer student.", "verified_answer": "Transfers may apply; a double costs $12,042 per person for 2026-27 (fixture).",
                   "unique_contribution": "A per-person rate table with the transfer rule and the deadline.", "critical_claim_ids": [ids["rate"], ids["deadline"]], "supporting_claim_ids": [ids["elig"]],
                   "structure": [{"heading": "Who can live in Fixture Hall?", "purpose": "eligibility", "claim_ids": [ids["elig"]]}, {"heading": "When is the housing application due?", "purpose": "deadline", "claim_ids": [ids["deadline"]]}],
                   "next_tasks": ["compare with Riverside Hall"], "information_gain": [{"item": "per-person rate", "claim_id": ids["rate"]}, {"item": "transfer may apply", "claim_id": ids["elig"]}, {"item": "application deadline", "claim_id": ids["deadline"]}],
                   "competitors_say": [{"url": f"https://forum.example.invalid/t/{i}", "says": "stale forum thread"} for i in range(3)], "unresolved_facts": ["deposit"], "headline_candidates": ["Fixture Hall Transfer Housing: Cost and Eligibility"]}
        elif role == "writer":
            out = {"headline": "Fixture Hall Transfer Housing: Cost and Eligibility", "deck": "Transfer students may apply to Fixture Hall; a double costs $12,042 per person for 2026-27, and the application is due 2026-05-15 (fixture).",
                   "body_markdown": BODY, "claim_refs": [ids["rate"], ids["elig"], ids["deadline"]],
                   "fact_table": [{"label": "Double room, 2026-27", "value": "$12,042 per person per academic year", "claim_id": ids["rate"]}, {"label": "Transfers may apply", "value": "yes", "claim_id": ids["elig"]},
                                  {"label": "Application deadline (transfer)", "value": "2026-05-15", "claim_id": ids["deadline"]}],
                   "next_actions": [{"text": "Compare the rate with Riverside Hall", "target": "/schools/fixture-state/housing/riverside-hall/"}, {"text": "Apply through the fixture housing portal", "target": "https://housing.fixturestate.example.edu/apply"}],
                   "sources_used": ["https://housing.fixturestate.example.edu/rates/"]}
        elif role == "editor" and '"mode": "beat_review"' in prompt:
            scores = {k: 4 for k in ("answers_first_two_sentences", "specificity", "completeness", "accuracy_against_sources", "scannability", "local_knowledge")}
            out = {"findings": [], "beat_review": {"ours": scores, "competitors": [{"url": f"https://forum.example.invalid/t/{i}", "scores": {k: 2 for k in scores}} for i in range(3)], "verdict_note": "fixture"}}
        elif role == "editor":
            out = {"revised_headline": "Fixture Hall Transfer Housing: Cost and Eligibility", "revised_deck": None, "revised_body_markdown": BODY, "findings": [{"kind": "prose", "detail": "fixture finding", "resolved": True}], "substantive_changes": ["none needed (fixture)"], "unresolved": []}
        elif role == "verifier":
            out = {"claim_checks": [{"claim_id": c, "status": "supported", "detail": "fixture", "source_opened": True} for c in ids.values()], "hard_failures": [],
                   "rubric": {"clarity": 4, "specificity": 4, "structure": 4, "attribution": 4, "usefulness": 4, "prose": 4}, "publishable": True, "corrections_required": []}
        else:
            out = GENERIC
        return 0, cli_stdout(role, text=json.dumps(envelope(role, out))), ""
    return runner


def test_r16_chain_plans_writes_edits_reviews_verifies_seo_gates_and_publishes_locally(clean_conn, tmp_path):
    inst, campus, housing, cid, ids = _setup(clean_conn)
    settings = get_settings()
    log = tmp_path / "dispatch.jsonl"
    report = pipeline.run_r16(clean_conn, cid, settings=settings, runner=_runner_for(ids), log_path=log, run_id="run-fixture-pipeline", notes=["deposit not stated (fixture)"],
                              link_targets=[{"path": p} for p in LINKS], until="verify", report_path=tmp_path / "report.json")
    assert report["outcome"] == "gate_passed", report
    vid = UUID(report["version_id"])
    assert report["stages"]["plan"]["information_gain"]["ok"] and report["stages"]["beat_review_r1"]["passed"]
    assert report["stages"]["verify"]["gate"]["status"] == "passed"
    assert report["stages"]["checks_after_edit_r1"]["findings"] == [], report["stages"]["checks_after_edit_r1"]
    agents = [json.loads(l)["agent"] for l in log.read_text().splitlines()]
    assert agents == ["planner", "writer", "editor", "editor", "verifier"]
    win = pipeline.win_plan_for(clean_conn, institution_id=inst, place_id=None, page_path=PATH, primary_query=None)
    seo = pipeline.stage_seo(clean_conn, cid, version_id=vid, settings=settings, win_plan=win, sibling_version_ids=[], runner=_runner_for(ids), log_path=log, run_qa=False)
    assert seo["seo_gate"]["passed"], seo["seo_gate"]["failed"]
    assert seo["page_input"]["backlinks"] >= 1 and len(seo["page_input"]["internal_links"]) >= 5
    with clean_conn.cursor() as cur:
        cur.execute("SELECT seo_gate->'agent_checklist'->>'summary' AS s, (seo_gate->>'passed')::boolean AS ok FROM page_versions WHERE id=%s", (vid,))
        r = cur.fetchone()
    assert r["ok"] and r["s"] == GENERIC["summary"]
    pub = pipeline.stage_publish(clean_conn, cid, version_id=vid, settings=settings, cms=None, out_root=tmp_path / "site")
    assert pub["published"], pub
    with clean_conn.cursor() as cur:
        cur.execute("SELECT status, local_published_at, current_version_id FROM pages WHERE path=%s", (PATH,))
        p = cur.fetchone()
        cur.execute("SELECT queue_state FROM intent_clusters WHERE id=%s", (cid,))
        q = cur.fetchone()["queue_state"]
    assert p["status"] == "staged" and p["local_published_at"] is not None and p["current_version_id"] == vid and q == "done"
    site = tmp_path / "site"
    assert (site / "schools/fixture-state/housing/fixture-hall-transfer/index.html").exists() and (site / "schools/fixture-state/housing/index.html").exists()
    assert (site / "schools/fixture-state/index.html").exists() and (site / "about/methods/index.html").exists() and (site / "index.html").exists()
    hub = (site / "schools/fixture-state/housing/index.html").read_text()
    assert PATH in hub and "Fixture Hall Transfer Housing" in hub


def test_funnel_refuses_expensive_stages_for_an_unqualified_cluster(clean_conn, tmp_path):
    inst, campus, housing, cid, ids = _setup(clean_conn)
    with clean_conn.cursor() as cur:
        cur.execute("UPDATE intent_clusters SET queue_state='watch', agi=1 WHERE id=%s", (cid,))
    clean_conn.commit()
    log = tmp_path / "dispatch.jsonl"
    calls = []

    def runner(agent, prompt):
        calls.append(agent.role)
        return 0, cli_stdout(agent.role), ""
    report = pipeline.run_r16(clean_conn, cid, settings=get_settings(), runner=runner, log_path=log, run_id="run-fixture-refuse", report_path=tmp_path / "r.json")
    assert report["outcome"] == "refused" and "planner" in report["refused"] and calls == []
    entries = [json.loads(l) for l in log.read_text().splitlines()]
    assert entries and entries[-1]["status"] == "refused_by_funnel" and entries[-1]["agent"] == "planner"


def test_year_check_allows_iso_dates_and_fact_table_labeled_cycles():
    from campus_worker.editorial import checks
    body = "The application is due 2026-05-15. The 2027-28 selection for rising juniors happens in Fall 2026, the page says. Rates are for 2026-27."
    plain = [f for f in checks.check_scope(body, "h", institution_name="Fixture State University", other_institution_names=[], academic_year="2026-27") if f.kind == "wrong_year"]
    assert [f.detail for f in plain] == ["academic year 2027-28 appears but the brief is scoped to 2026-27"]
    labeled = [f for f in checks.check_scope(body, "h", institution_name="Fixture State University", other_institution_names=[], academic_year="2026-27", labeled_years={"2027-28"}) if f.kind == "wrong_year"]
    assert labeled == []
    out = checks.run_all(headline="Fixture State housing deadlines by student type", deck=None, body_md=body, byline="Housing desk", fact_table=[{"label": "2027-28 selection (rising juniors)", "value": "Fall 2026", "claim_id": "x"}],
                         body_claim_ids=["x"], critical_ids=[], approved_ids={"x"}, institution_name="Fixture State University", other_institution_names=[], academic_year="2026-27",
                         next_actions=[{"text": "Apply in the portal", "target": "https://example.invalid/apply"}], existing_bodies=[])
    assert not [f for f in out if f.kind == "wrong_year"]


def test_auto_cite_adds_claim_refs_and_fact_rows_for_values_in_prose():
    from campus_worker import pipeline
    claims = [{"id": "c-fee", "field": "fee.late_cancellation", "value": "$500 per person one time", "value_type": "money", "audience": [], "academic_year": "2026-27"},
              {"id": "c-date", "field": "deadline.spring_cancellation", "value": "2026-12-01", "value_type": "date", "audience": [], "academic_year": "2026-27"},
              {"id": "c-other", "field": "deadline.fall_cancellation", "value": "2026-06-15", "value_type": "date", "audience": [], "academic_year": "2026-27"}]
    draft = {"body_markdown": "Requests after December 1, 2026 cost $500.", "fact_table": [], "claim_refs": []}
    out = pipeline.auto_cite(draft, claims)
    assert out["claim_refs"] == ["c-date", "c-fee"]
    assert {r["claim_id"] for r in out["fact_table"]} == {"c-date", "c-fee"} and all(r["label"] for r in out["fact_table"])


def test_researcher_field_names_stay_on_the_claim_taxonomy():
    from campus_worker import pipeline
    from campus_worker.claims import is_critical_field
    assert pipeline.canonical_field("housing.cancellation.late_request_fee") == "fee.cancellation_late_request_fee"
    assert pipeline.canonical_field("housing.cancellation.penalty_free_deadline_fall") == "deadline.cancellation_penalty_free_deadline_fall"
    assert pipeline.canonical_field("housing.rate.fall_semester") == "rate.fall_semester"
    assert pipeline.canonical_field("housing.placement.random_auto_allocation") == "placement.random_auto_allocation"
    assert pipeline.canonical_field("eligibility.exempt_if") == "eligibility.exempt_if" and pipeline.canonical_field("capacity.residents") == "capacity.residents"
    assert is_critical_field(pipeline.canonical_field("housing.cancellation.late_request_fee"))


def test_auto_cite_links_text_claims_the_body_states_and_labels_rows_readably():
    from campus_worker import pipeline
    claims = [{"id": "c-place", "field": "placement.random_auto_allocation", "value": "Placement is by random auto-allocation based on preferences; students do not rank halls", "value_type": "text", "audience": [], "academic_year": None},
              {"id": "c-fee", "field": "fee.cancellation_late_request_fee", "value": "$500 per person one time", "value_type": "money", "audience": ["returning_junior_senior"], "academic_year": "2026-27"}]
    draft = {"body_markdown": "Rooms are assigned by random auto-allocation based on your preferences, and students do not rank halls.\n\nLate requests cost $500.", "fact_table": [], "claim_refs": []}
    out = pipeline.auto_cite(draft, claims)
    assert set(out["claim_refs"]) == {"c-place", "c-fee"}
    row = [r for r in out["fact_table"] if r["claim_id"] == "c-fee"][0]
    assert row["label"] == "Cancellation late request fee (returning junior senior), 2026-27" and row["value"] == "$500 per person"
