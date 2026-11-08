"""Planner → writer → editor → verifier on synthetic evidence with the FixtureProvider.
This proves the contract plumbing, gating and persistence — NOT real model routing (no key)."""
import json
from campus_worker import claims
from campus_worker.adapters.model import FixtureProvider, ModelRouter
from campus_worker.briefs import build_entity_profile_brief, persist_brief
from campus_worker.config import Budget, ModelRouting
from campus_worker.roles import runners
from campus_worker.types import ClaimRecord
from tests.helpers import NOW, make_entity, make_school
from tests.test_claims import _money


def _env(role, output, decision="advance"):
    return json.dumps({"schema_version": "1.0", "run_id": "run-fixture-1", "role": role, "input_ids": [], "institution_id": "x", "decision": decision,
                       "hold": None, "output": output, "evidence_ids": [], "uncertainties": [], "next_jobs": [], "usage": {}})


def _setup(conn):
    inst, campus, topics = make_school(conn)
    ent = make_entity(conn, inst, campus, topics["housing"])
    r = claims.store_claim(conn, _money(inst, campus, topics["housing"], ent, 1204200), snapshot_id=None)
    claims.store_claim(conn, ClaimRecord(institution_id=inst, campus_id=campus, entity_id=ent, topic_id=topics["housing"], field="amenity.air_conditioning",
                                         value_type="boolean", value_bool=True, evidence_category="verified_fact", extraction_method="deterministic", retrieved_at=NOW), snapshot_id=None)
    with conn.cursor() as cur:
        cur.execute("INSERT INTO pages (institution_id, topic_id, entity_id, page_format, slug, path) VALUES (%s,%s,%s,'entity_profile','fixture-hall','/schools/fixture-state/housing/fixture-hall/') RETURNING id", (inst, topics["housing"], ent))
        pid = cur.fetchone()["id"]
        cur.execute("INSERT INTO jobs (job_type, idempotency_key) VALUES ('write','e2e-1') RETURNING id")
        jid = cur.fetchone()["id"]
        cur.execute("INSERT INTO runs (job_id, attempt, role) VALUES (%s,1,'writer') RETURNING id", (jid,))
        rid = cur.fetchone()["id"]
    conn.commit()
    return inst, campus, topics, ent, str(r.claim_id), pid, jid, rid


def _good_body(cid):
    return (f"Fixture Hall's double room costs $12,042 per person for the 2026-27 academic year, billed in two semester installments. "
            f"That figure is the published rate, not an estimate.\n\nThe building is air-conditioned. Whether every floor has a kitchen is unknown; "
            f"the housing site does not say, and we have not confirmed it with the housing office.\n\n## What the rate includes\n\n"
            f"The rate is per person, so two roommates each pay $12,042. It covers the room only; dining is billed separately.\n\n"
            f"## What to do next\n\nCompare Fixture Hall with Riverside Hall on the same per-person, academic-year basis, then run the total-cost calculator.")


def _writer_output(cid, body=None, headline="Fixture Hall: what the double-room rate includes", byline_hint=None):
    return {"headline": headline, "deck": "Per-person academic-year rate, what it covers, and what we could not verify.",
            "body_markdown": body or _good_body(cid), "claim_refs": [cid],
            "fact_table": [{"label": "Double, 2026-27", "value": "$12,042 per person, academic year", "claim_id": cid}],
            "next_actions": [{"text": "Compare Fixture Hall with Riverside Hall", "target": "/schools/fixture-state/housing/compare/"}]}


def _editor_output(body, headline="Fixture Hall: what the double-room rate includes"):
    return {"revised_headline": headline, "revised_deck": None, "revised_body_markdown": body,
            "findings": [{"kind": "specificity", "detail": "named the billing installments", "resolved": True}], "substantive_changes": ["tightened opening"], "unresolved": []}


def _verifier_output(cid, rubric=None, hard=None):
    return {"claim_checks": [{"claim_id": cid, "status": "supported", "source_opened": True}], "hard_failures": hard or [],
            "rubric": rubric or {"clarity": 4, "specificity": 4, "structure": 3, "attribution": 4, "usefulness": 3, "prose": 3}, "publishable": not hard}


def test_full_loop_passes_gates_and_stages_page(clean_conn):
    inst, campus, topics, ent, cid, pid, jid, rid = _setup(clean_conn)
    brief = build_entity_profile_brief(clean_conn, entity_id=ent)
    bid = persist_brief(clean_conn, brief)
    prov = FixtureProvider({
        ("claude-sonnet-5-5", "planner"): _env("planner", {"page_format": "entity_profile", "audience": "first_year", "reader_decision": brief.reader_decision,
                                                           "verified_answer": brief.verified_answer, "unique_contribution": brief.unique_contribution,
                                                           "critical_claim_ids": [cid], "structure": brief.structure, "next_tasks": brief.next_tasks}),
        ("claude-sonnet-5-5", "writer"): _env("writer", _writer_output(cid)),
        ("claude-opus-5-5", "editor"): _env("editor", _editor_output(_good_body(cid).replace("That figure is the published rate", "That figure is the housing office's published rate"))),
        ("claude-sonnet-5-5", "verifier"): _env("verifier", _verifier_output(cid)),
    })
    router = ModelRouter(ModelRouting(), Budget(), prov)
    p = runners.run_planner(clean_conn, router, brief, job_id=jid, run_id=rid)
    assert p.status == "ok" and p.resolved_model == "claude-sonnet-5-5"
    w = runners.run_writer(clean_conn, router, brief, page_id=pid, brief_id=bid, job_id=jid, run_id=rid, byline="Housing desk")
    assert w.status == "ok" and "page_version_id" in w.artifact_ids
    e = runners.run_editor(clean_conn, router, version_id=w.artifact_ids["page_version_id"], brief=brief, job_id=jid, run_id=rid)
    assert e.status == "ok" and e.resolved_model == "claude-opus-5-5"
    v = runners.run_verifier(clean_conn, router, version_id=e.artifact_ids["page_version_id"], brief=brief, institution_name="Fixture State University",
                             other_institution_names=["Lakeside College"], academic_year="2026-27", existing_bodies=[], job_id=jid, run_id=rid)
    assert v.status == "ok" and v.output["passed"] and v.output["rubric_total"] == 21
    with clean_conn.cursor() as cur:
        cur.execute("SELECT status, current_version_id FROM pages WHERE id=%s", (pid,))
        page = cur.fetchone()
        cur.execute("SELECT version_no, gate_status, writer_model, editor_model, verifier_model FROM page_versions WHERE id=%s", (page["current_version_id"],))
        ver = cur.fetchone()
        cur.execute("SELECT resolved_model FROM runs WHERE id=%s", (rid,))
        run = cur.fetchone()
    assert page["status"] == "staged" and ver["gate_status"] == "passed" and ver["version_no"] == 2
    assert (ver["writer_model"], ver["editor_model"], ver["verifier_model"]) == ("claude-sonnet-5-5", "claude-opus-5-5", "claude-sonnet-5-5")
    assert run["resolved_model"]  # traceable


def test_fabricated_draft_fails_before_verifier_model_is_paid(clean_conn):
    inst, campus, topics, ent, cid, pid, jid, rid = _setup(clean_conn)
    brief = build_entity_profile_brief(clean_conn, entity_id=ent)
    bad_body = _good_body(cid) + '\n\nStudents agree it is the best dorm. "I loved every minute," said one resident.'
    prov = FixtureProvider({("claude-sonnet-5-5", "writer"): _env("writer", _writer_output(cid, body=bad_body))})
    router = ModelRouter(ModelRouting(), Budget(), prov)
    w = runners.run_writer(clean_conn, router, brief, page_id=pid, brief_id=None, job_id=jid, run_id=rid, byline="Housing desk")
    v = runners.run_verifier(clean_conn, router, version_id=w.artifact_ids["page_version_id"], brief=brief, institution_name="Fixture State University",
                             other_institution_names=[], academic_year="2026-27", existing_bodies=[], job_id=jid, run_id=rid)
    assert v.status == "failed" and any(f["kind"] in ("fabricated_consensus", "invented_quote") for f in v.findings)
    assert [c["tag"] for c in prov.calls] == ["writer"]  # verifier model never called
    with clean_conn.cursor() as cur:
        cur.execute("SELECT status FROM pages WHERE id=%s", (pid,))
        assert cur.fetchone()["status"] == "drafting"


def test_missing_evidence_holds_without_any_model_call(clean_conn):
    inst, campus, topics = make_school(clean_conn)
    ent = make_entity(clean_conn, inst, campus, topics["housing"])  # no claims at all
    brief = build_entity_profile_brief(clean_conn, entity_id=ent)
    prov = FixtureProvider()
    router = ModelRouter(ModelRouting(), Budget(), prov)
    with clean_conn.cursor() as cur:
        cur.execute("INSERT INTO pages (institution_id, topic_id, entity_id, page_format, slug, path) VALUES (%s,%s,%s,'entity_profile','x','/x/') RETURNING id", (inst, topics["housing"], ent))
        pid = cur.fetchone()["id"]
    clean_conn.commit()
    w = runners.run_writer(clean_conn, router, brief, page_id=pid, brief_id=None, job_id=None, run_id=None)
    assert w.status == "held" and w.hold_reason == "missing_evidence" and prov.calls == []


def test_low_rubric_fails_gate_and_findings_persist(clean_conn):
    inst, campus, topics, ent, cid, pid, jid, rid = _setup(clean_conn)
    brief = build_entity_profile_brief(clean_conn, entity_id=ent)
    prov = FixtureProvider({("claude-sonnet-5-5", "writer"): _env("writer", _writer_output(cid)),
                            ("claude-sonnet-5-5", "verifier"): _env("verifier", _verifier_output(cid, rubric={"clarity": 4, "specificity": 2, "structure": 4, "attribution": 4, "usefulness": 4, "prose": 4}))})
    router = ModelRouter(ModelRouting(), Budget(), prov)
    w = runners.run_writer(clean_conn, router, brief, page_id=pid, brief_id=None, job_id=jid, run_id=rid, byline="Housing desk")
    v = runners.run_verifier(clean_conn, router, version_id=w.artifact_ids["page_version_id"], brief=brief, institution_name="Fixture State University",
                             other_institution_names=[], academic_year="2026-27", existing_bodies=[], job_id=jid, run_id=rid)
    assert v.status == "failed" and "below 3" in v.output["rubric_failures"][0]
    with clean_conn.cursor() as cur:
        cur.execute("SELECT gate_status, rubric, jsonb_array_length(gate_findings) AS n FROM page_versions WHERE id=%s", (w.artifact_ids["page_version_id"],))
        r = cur.fetchone()
    assert r["gate_status"] == "failed" and r["rubric"]["total"] == 22 and r["n"] >= 1
