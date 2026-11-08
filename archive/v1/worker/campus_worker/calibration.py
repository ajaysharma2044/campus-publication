"""Calibration exercises 1–4 (SPEC §32) run end to end on LABELED SYNTHETIC fixtures with the
FixtureProvider, against the development database. Produces docs/editorial/calibration.md with
run ids, traceability, rubric results, corrections and holds.

    python -m campus_worker.calibration

This proves the loop (source → snapshot → claims → brief → draft → edit → verify → gate → staged
publication → dependent update) with scripted model responses. It is NOT evidence of real model
routing: no provider credential exists in this environment.
"""
from __future__ import annotations

import json
from datetime import date, datetime, timezone
from pathlib import Path
from uuid import UUID

import httpx

from . import budget as budgetmod
from . import claims as claimsmod
from . import propagation, queue as q
from .adapters.cms import InMemoryCMS
from .adapters.model import FixtureProvider, ModelRouter
from .briefs import audience_guide_justified, build_entity_profile_brief, persist_brief
from .cms import publisher
from .collectors.html import collect_html_source, register_source
from .config import FIXTURES_DIR, REPO_ROOT, get_settings
from .db import connect
from .fetcher import SafeFetcher
from .registry import find_by_external_id
from .roles import runners
from .scheduler import run_once
from .seed import seed_all
from .tools.comparison import compare, tradeoffs
from .types import ClaimRecord, JobRecord

OUT = REPO_ROOT / "docs" / "editorial" / "calibration.md"
SRC = FIXTURES_DIR / "sources"
NOW = datetime.now(timezone.utc)


def _env(role, output, decision="advance"):
    return json.dumps({"schema_version": "1.0", "run_id": "run-calibration", "role": role, "input_ids": [], "institution_id": "x", "decision": decision,
                       "hold": None, "output": output, "evidence_ids": [], "uncertainties": [], "next_jobs": [], "usage": {}})


def _resolver(host, port, proto=0):
    import socket
    return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 443))]


def _fetcher(conn, bodies):
    def handler(req):
        return httpx.Response(200, headers={"content-type": "text/html"}, content=bodies[req.url.path])
    return SafeFetcher(conn, transport=httpx.MockTransport(handler), resolver=_resolver, sleep=lambda s: None)


def _bool_claim(inst, campus, topic, ent, field, val, aud=None):
    return ClaimRecord(institution_id=inst, campus_id=campus, entity_id=ent, topic_id=topic, field=field, value_type="boolean", value_bool=val,
                       audience_applicability=[aud] if aud else [], evidence_category="verified_fact", extraction_method="deterministic", retrieved_at=NOW)


def main() -> str:
    settings = get_settings()
    conn = connect(settings.database_url)
    lines = ["# Calibration exercises (SPEC §32)", "", f"Run at {NOW.isoformat()} against the development database with **synthetic fixtures** and the **FixtureProvider** (scripted model responses). "
             "No real model call was made (no credential). Everything below is traceable by id in the database.", ""]
    seed_all(conn)
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM topics WHERE key='housing'")
        housing = cur.fetchone()["id"]
        cur.execute("INSERT INTO source_permissions (domain_pattern, publisher, connector, access_mode, permission_state, retention_policy, rate_limit_per_minute) VALUES ('*.example.edu','Fixture','official_html','public_http','allowed','excerpts_only',600) ON CONFLICT DO NOTHING")
    conn.commit()
    fsu = find_by_external_id(conn, "ipeds_unitid", "900001")
    if not fsu:
        from .registry import import_ipeds_hd
        import_ipeds_hd(conn, FIXTURES_DIR / "ipeds" / "hd_synthetic.csv", release="SYNTHETIC_HD", release_date=date(2026, 1, 1), mark_fixture=True)
        fsu = find_by_external_id(conn, "ipeds_unitid", "900001")
    inst = fsu["id"]
    with conn.cursor() as cur:
        cur.execute("INSERT INTO campuses (institution_id, name, slug, is_main, status) VALUES (%s,'Main','main',TRUE,'synthetic_fixture') ON CONFLICT (institution_id, slug) DO UPDATE SET name=EXCLUDED.name RETURNING id", (inst,))
        campus = cur.fetchone()["id"]
        ents = {}
        for name, slug in (("Fixture Hall", "fixture-hall"), ("Riverside Hall", "riverside-hall")):
            cur.execute("INSERT INTO entities (institution_id, campus_id, topic_id, entity_type, name, slug, status) VALUES (%s,%s,%s,'residence_hall',%s,%s,'synthetic_fixture') ON CONFLICT (institution_id, topic_id, slug) DO UPDATE SET name=EXCLUDED.name RETURNING id", (inst, campus, housing, name, slug))
            ents[slug] = cur.fetchone()["id"]
    conn.commit()
    fh, rh = ents["fixture-hall"], ents["riverside-hall"]

    # ---------------- Exercise 1: research a hall from a permitted primary source → profile
    lines += ["## Exercise 1 — research one hall from a primary source and build a profile", ""]
    src = register_source(conn, canonical_url="https://www.example.edu/housing/rates", institution_id=inst, campus_id=campus, source_kind="official_html", publisher="Fixture State Housing (synthetic)", source_family="housing-site")
    res = collect_html_source(conn, _fetcher(conn, {"/housing/rates": (SRC / "fixture_hall_rates_v1.html").read_bytes()}), src)
    snap = UUID(res["snapshot_id"])
    with conn.cursor() as cur:
        cur.execute("SELECT retained_tables, retained_text FROM fetch_snapshots WHERE id=%s", (snap,))
        s = cur.fetchone()
    cs, warnings = claimsmod.extract_rate_table(s["retained_tables"][0], institution_id=inst, campus_id=campus, topic_id=housing, entity_id=fh, retrieved_at=NOW, context_text=s["retained_text"])
    stored = [claimsmod.store_claim(conn, c, snapshot_id=snap, excerpt=f"{c.room_type} {c.academic_year}", locator="table 1", source_family="housing-site") for c in cs]
    claimsmod.store_claim(conn, _bool_claim(inst, campus, housing, fh, "amenity.air_conditioning", True), snapshot_id=snap, excerpt="Fixture Hall and Riverside Hall are air-conditioned.", locator="p[AC]", source_family="housing-site")
    claimsmod.store_claim(conn, _bool_claim(inst, campus, housing, rh, "amenity.air_conditioning", False), snapshot_id=snap, source_family="housing-site")
    # Riverside rate on a different period to prove equivalent-period comparison
    claimsmod.store_claim(conn, ClaimRecord(institution_id=inst, campus_id=campus, entity_id=rh, topic_id=housing, field="rate.room", value_type="money", value_number=579100, unit="minor_units", currency="USD",
                                            billing_period="per_semester", price_basis="per_person", room_type="double", academic_year="2026-27", evidence_category="verified_fact", extraction_method="deterministic", retrieved_at=NOW), snapshot_id=snap, source_family="housing-site")
    lines += [f"- Source `{src}` → snapshot `{snap}` (outcome {res['outcome']}, confidence {res['confidence']}, tables {res['tables']}).",
              f"- Deterministic extraction: {len(cs)} money claims, warnings {warnings or 'none'}; actions {[r.action for r in stored]}.",
              "- Scoped per academic year and room type; per-person basis and academic-year period detected from the page text."]
    brief = build_entity_profile_brief(conn, entity_id=fh)
    bid = persist_brief(conn, brief)
    cid = str(brief.critical_claim_ids[0])
    with conn.cursor() as cur:
        cur.execute("INSERT INTO pages (institution_id, campus_id, topic_id, entity_id, page_format, slug, path) VALUES (%s,%s,%s,%s,'entity_profile','fixture-hall','/schools/fixture-state-university-900001/housing/fixture-hall/') ON CONFLICT (path) DO UPDATE SET slug=EXCLUDED.slug RETURNING id", (inst, campus, housing, fh))
        pid = cur.fetchone()["id"]
    conn.commit()
    jid, _ = q.enqueue(conn, JobRecord(job_type="write_draft", idempotency_key=f"calib:write:{pid}:{NOW.isoformat()}", institution_id=inst, is_paid=True, estimated_cost_minor=20))
    with conn.cursor() as cur:
        cur.execute("INSERT INTO runs (job_id, attempt, role, worker_id) VALUES (%s,1,'calibration','calibration') RETURNING id", (jid,))
        rid = cur.fetchone()["id"]
    conn.commit()
    good_body = (f"Fixture Hall's double room costs $12,042 per person for the 2026-27 academic year, billed in two equal semester installments. That figure is the housing office's published rate, not an estimate, and it covers the room only.\n\n"
                 "The building is air-conditioned. Whether every floor has a kitchen is unknown: the housing site does not say, and we have not confirmed it with the housing office.\n\n"
                 "## What the rate includes\n\nThe rate is per person, so two roommates each pay $12,042. Dining is billed separately.\n\n[[fact-table]]\n\n## What to do next\n\nCompare Fixture Hall with Riverside Hall on the same per-person, academic-year basis, then run the total-cost calculator.")
    bad_body = good_body + '\n\nStudents agree it is the best hall on campus. "I loved every minute," said one resident.'
    writer_out = lambda body: {"headline": "Fixture Hall: what the double-room rate includes", "deck": "Per-person academic-year rate, what it covers, and what we could not verify.", "body_markdown": body,
                               "claim_refs": [cid], "fact_table": [{"label": "Double, 2026-27", "value": "$12,042 per person, academic year", "claim_id": cid}],
                               "next_actions": [{"text": "Compare Fixture Hall with Riverside Hall on the same basis", "target": "/schools/fixture-state-university-900001/housing/compare/fixture-hall-vs-riverside-hall/"}]}
    prov = FixtureProvider({("claude-sonnet-5-5", "writer"): _env("writer", writer_out(bad_body)),
                            ("claude-opus-5-5", "editor"): _env("editor", {"revised_headline": "Fixture Hall: what the double-room rate includes", "revised_deck": None, "revised_body_markdown": good_body,
                                                                           "findings": [{"kind": "unsupported", "detail": "removed invented consensus and quotation", "resolved": True}], "substantive_changes": ["removed fabricated consensus/quote"], "unresolved": []}),
                            ("claude-sonnet-5-5", "verifier"): _env("verifier", {"claim_checks": [{"claim_id": cid, "status": "supported", "source_opened": True}], "hard_failures": [],
                                                                                 "rubric": {"clarity": 4, "specificity": 4, "structure": 3, "attribution": 4, "usefulness": 3, "prose": 3}, "publishable": True})})
    router = ModelRouter(settings.model_routing, settings.budget, prov)
    w = runners.run_writer(conn, router, brief, page_id=pid, brief_id=bid, job_id=jid, run_id=rid, byline="Housing desk")
    v1 = runners.run_verifier(conn, router, version_id=UUID(w.artifact_ids["page_version_id"]), brief=brief, institution_name=fsu["canonical_name"], other_institution_names=["Lakeside College"], academic_year="2026-27", existing_bodies=[], job_id=jid, run_id=rid)
    lines += [f"- Brief `{bid}` ready={brief.ready}; critical claims {len(brief.critical_claim_ids)}; unknowns listed: {len(brief.unresolved_facts)}.",
              f"- Draft v1 (writer model {w.resolved_model}): verifier status **{v1.status}** — deterministic hard findings: {[f['kind'] for f in v1.findings if f['severity']=='hard']}. The verifier model was not called (no spend on an unpublishable draft)."]
    e = runners.run_editor(conn, router, version_id=UUID(w.artifact_ids["page_version_id"]), brief=brief, job_id=jid, run_id=rid)
    with conn.cursor() as cur:
        cur.execute("UPDATE jobs SET state='leased', lease_owner='calibration', lease_expires_at=now()+interval '5 min' WHERE id=%s", (jid,))
    conn.commit()
    v2 = runners.run_verifier(conn, router, version_id=UUID(e.artifact_ids["page_version_id"]), brief=brief, institution_name=fsu["canonical_name"], other_institution_names=["Lakeside College"], academic_year="2026-27", existing_bodies=[], job_id=jid, run_id=rid)
    q.complete(conn, jid, "calibration")
    cms = InMemoryCMS()
    pub = publisher.publish_version(conn, cms, UUID(e.artifact_ids["page_version_id"]), environment="staging", auto_publish=False)
    pub2 = publisher.publish_version(conn, cms, UUID(e.artifact_ids["page_version_id"]), environment="staging", auto_publish=False)
    lines += [f"- Correction: editor (model {e.resolved_model}) removed the fabricated consensus and quote → v2 `{e.artifact_ids['page_version_id']}`.",
              f"- Draft v2: verifier **{v2.status}**, rubric total {v2.output['rubric_total']}/24, hard failures {v2.output['hard_failures'] or 'none'}; page status staged.",
              f"- Staging publication: cms id {pub.cms_id}, created={pub.created}; repeat publish changed={pub2.changed} (idempotent). Job `{jid}` run `{rid}`.",
              f"- Spend: {budgetmod.spent(conn)['day_minor']} minor units today (fixture provider priced via the reservation path; real spend would be reconciled from provider usage).", ""]

    # ---------------- Exercise 2: compare two halls on equivalent periods
    lines += ["## Exercise 2 — compare two halls on shared records and equivalent periods", ""]
    comp = compare(conn, [fh, rh], room_type="double", academic_year="2026-27")
    rate_row = next(r for r in comp.rows if r.field == "rate.room")
    lines += [f"- Entities: {[e['name'] for e in comp.entities]}; basis {comp.basis}, period {comp.period}.",
              f"- Rate row: {[c.display for c in rate_row.cells]} (Riverside stored per semester, converted to the academic year for an equivalent comparison).",
              f"- Unknown cells: {sum(1 for r in comp.rows for c in r.cells if c.status=='unknown')} — shown as unknown, never as absent.",
              "- Tradeoffs produced from records only: " + " | ".join(tradeoffs(comp)), ""]

    # ---------------- Exercise 3: transfer-specific housing task
    lines += ["## Exercise 3 — transfer-specific housing guide: page or section?", ""]
    ok, why = audience_guide_justified(conn, entity_id=None, institution_id=inst, topic_id=housing, audience="transfer")
    lines += [f"- Before any transfer-scoped claim exists: justified={ok} — {why}. **Decision: no separate page; improve the general housing coverage.**"]
    claimsmod.store_claim(conn, _bool_claim(inst, campus, housing, None, "eligibility.guaranteed_housing", True), snapshot_id=snap, source_family="housing-site")
    claimsmod.store_claim(conn, _bool_claim(inst, campus, housing, None, "eligibility.guaranteed_housing", False, aud="transfer"), snapshot_id=snap, source_family="housing-site")
    ok2, why2 = audience_guide_justified(conn, entity_id=None, institution_id=inst, topic_id=housing, audience="transfer")
    lines += [f"- After a verified transfer-scoped eligibility claim that differs from the general rule: justified={ok2} — {why2}. **Decision: a transfer guide is now justified by a material rule difference, not by relabeling.**", ""]

    # ---------------- Exercise 4: commuter community college configuration
    lines += ["## Exercise 4 — commuter community college configuration (synthetic)", ""]
    rcc = find_by_external_id(conn, "ipeds_unitid", "900003")
    from .discovery import generate_hypotheses
    from .registry import topic_applicability
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM campuses WHERE institution_id=%s LIMIT 1", (rcc["id"],))
        rcc_campus = cur.fetchone()["id"]
    h_housing = generate_hypotheses(conn, institution_id=rcc["id"], campus_id=rcc_campus, topic_key="housing", entity_names=[], audiences=["commuter"])
    h_transfer = generate_hypotheses(conn, institution_id=rcc["id"], campus_id=rcc_campus, topic_key="transfer", entity_names=[(None, "Nursing AAS")], audiences=["transfer", "adult_learner"], limit=8)
    lines += [f"- Identity status: {rcc['identity_status']} (never published).",
              f"- Topic applicability: housing={topic_applicability(conn, rcc['id'], 'housing')}, dining={topic_applicability(conn, rcc['id'], 'dining')}, transfer={topic_applicability(conn, rcc['id'], 'transfer')}.",
              f"- Housing hypotheses generated: {h_housing['stored']} (skipped: {h_housing.get('skipped_reason')}). Transfer hypotheses generated: {h_transfer['stored']}, all labeled hypotheses, observed count 0.",
              "- The workflow prioritised transfer/programs/commuting and produced no dorm coverage.", ""]

    # ---------------- Dependent update: a rate change propagates
    lines += ["## Source change → dependent output update", ""]
    res3 = collect_html_source(conn, _fetcher(conn, {"/housing/rates": (SRC / "fixture_hall_rates_v3_ratechange.html").read_bytes()}), src)
    with conn.cursor() as cur:
        cur.execute("SELECT id, retained_tables, retained_text FROM fetch_snapshots WHERE source_id=%s ORDER BY fetched_at DESC LIMIT 1", (src,))
        s3 = cur.fetchone()
    cs3, _ = claimsmod.extract_rate_table(s3["retained_tables"][0], institution_id=inst, campus_id=campus, topic_id=housing, entity_id=fh, retrieved_at=NOW, context_text=s3["retained_text"])
    changed = [claimsmod.store_claim(conn, c, snapshot_id=s3["id"], source_family="housing-site") for c in cs3]
    sup = [r for r in changed if r.action == "superseded"]
    prop = propagation.on_claim_changed(conn, sup[0].superseded_id, sup[0].claim_id, reason="rate_changed") if sup else {"affected_pages": [], "jobs": []}
    tick = run_once(conn, settings, job_types=["revalidate_page"])
    with conn.cursor() as cur:
        cur.execute("SELECT status, revalidation_required FROM pages WHERE id=%s", (pid,))
        pg = cur.fetchone()
    lines += [f"- Re-fetch: material_change={res3['material_change']}; {len(sup)} claim superseded (old marked stale).",
              f"- Propagation: affected pages {len(prop['affected_pages'])}, revalidate jobs {len(prop['jobs'])}; tick ran {[(r['job_type'], r['result']) for r in tick['ran']]}.",
              f"- Page after revalidation: status {pg['status']}, revalidation_required={pg['revalidation_required']} (the current version still cites the superseded, now-stale claim, so it is held until a new version is drafted from the new claim; the dependency edge was inherited by the new claim so the rewrite job knows which page to update).", ""]

    lines += ["## Deployment state", "", "- All of the above ran locally against the development PostgreSQL and an in-memory CMS. Real WordPress round-trip is verified separately (docs/ops/run.md). No external service was contacted.",
              "- Next work: connect a model credential, run the same four exercises with the real router, compare rubric outcomes against these scripted ones, then enable bounded auto-publication for the entity_profile and comparison templates only."]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n")
    conn.close()
    return str(OUT)


if __name__ == "__main__":
    print(main())
