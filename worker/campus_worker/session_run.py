"""In-session research → draft → verify → render run for one Cornell task (no API key, no worker
model service). The language-judgment roles (discovery synthesis, writing, editing, verification
scoring) were performed by the Claude Code session itself; everything else is the existing
deterministic code. Evidence provenance is recorded truthfully as search-snippet attribution
because the primary hosts could not be opened from this session.

    python -m campus_worker.session_run cornell-transfer-housing

Outputs: database rows (sources, snapshots, claims, questions, clusters, opportunity score, brief,
page, page_version with gate findings), a rendered preview page under build/preview, and
docs/research/cornell-transfer-housing-run.md with ids and results.
"""
from __future__ import annotations

import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from uuid import UUID

from . import claims as claimsmod
from . import discovery, scoring
from .collectors.html import record_snapshot, register_source
from .config import REPO_ROOT, get_settings
from .db import connect
from .editorial import checks, gates
from .registry import find_by_external_id
from .render import engine, preview
from .seed import seed_all
from .types import ClaimRecord

NOW = datetime.now(timezone.utc)
TODAY = NOW.date()
CONTENT = REPO_ROOT / "content" / "cornell" / "transfer-housing"
SESSION_MODEL = "session:claude-code (claude-fable-5-1 serving; not the worker provider)"
BLOCKER = ("Primary Cornell pages could not be opened from this session (scl.cornell.edu and other cornell.edu hosts fail DNS under the "
           "environment's network policy). All facts are search-snippet attributions to the named official pages, stored as estimates, "
           "so every cost, eligibility and deadline claim is unverified and the page is held.")

OFFICIAL = {
    "S1": ("https://scl.cornell.edu/residential-life/housing/housing-details/rates-amenities-licenses/housing-rates", "Housing Rates 2026-2027"),
    "S2": ("https://scl.cornell.edu/residential-life/housing/campus-housing/residential-policy", "Residential Policy"),
    "S3": ("https://scl.cornell.edu/residential-life/housing/campus-housing/new-transfer-undergraduates", "New Transfer Undergraduates"),
    "S4": ("https://scl.cornell.edu/residential-life/housing/housing-details/apply-housing/new-undergrad-application-process", "New Undergrad Application Process"),
    "S5": ("https://scl.cornell.edu/residential-life/housing/housing-details/rates-amenities-licenses/housing-license-cancellation-policy", "Housing License Cancellation Policy"),
    "S7": ("https://faq.enrollment.cornell.edu/kb/article/377-as-an-admitted-student-how-do-i-sign-up-for-housing/", "Admitted-student housing FAQ"),
}
SNIPPETS = {
    "S1": "2026-2027 residence hall / program house / West Campus rates per semester, same fall and spring: super single $8,298 ($16,595/yr); single $7,783 ($15,566/yr); double $6,872 ($13,744/yr); triple or one-room quad $6,322 ($12,644/yr); townhouse double $7,783 ($15,566/yr). Housing Rates include gas, electricity, garbage pick-up, and Internet service (up to 200 GB/month). A separate block shows lower cooperative-residence figures.",
    "S2": "Two-year residential requirement for full-time Ithaca first- and second-year students, with a required meal plan. Transfers who have not met the residential requirement elsewhere must live on campus for one academic year; spring transfers for the incoming spring and the following academic year; transfers with two years of on-campus residence at a previous school, or entering as juniors or seniors, are exempt. Individual exemptions via the housing application during open periods, one academic year at a time.",
    "S3": "Transfer students may be placed in the West Campus House System, South Campus Residence Halls, North Campus Residence Halls, and Program Houses; transfer rooms are grouped together whenever possible; in limited situations transfers who qualify as first-year students are placed in first-year residences.",
    "S4": "Transfer students should apply for housing within ten days of receiving a NetID. There is no fee to apply for housing. Confirmations began mid-June; guaranteed waitlist receives weekly updates. Full for the 2026-2027 academic year; room change requests not accepted.",
    "S5": "Effective August 2026, new first-year and transfer students cannot cancel a housing assignment except in specified circumstances. Spring-term cancellation requests due December 1, 2026; later requests carry a $500 fee.",
    "S7": "All first-year students are guaranteed on-campus housing.",
}
QUESTIONS = [
    ("Do transfer students have to live on campus at Cornell?", "official_faq", "transfer"),
    ("Is housing guaranteed for transfer students at Cornell?", "related_question", "transfer"),
    ("Where do Cornell transfer students live, West or North Campus?", "related_question", "transfer"),
    ("When is the Cornell housing application due for transfers?", "search_suggestion", "transfer"),
    ("Can a transfer student cancel Cornell housing and live off campus?", "related_question", "transfer"),
    ("Do I have to buy a meal plan as a transfer at Cornell?", "related_question", "transfer"),
    ("Why were Cornell transfers put in converted lounges?", "competitor_gap", "transfer"),
    ("Is housing guaranteed for first-year students at Cornell?", "official_faq", "first_year"),
]


def _ensure_cornell(conn):
    seed_all(conn)
    inst = find_by_external_id(conn, "ipeds_unitid", "190415")
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM campuses WHERE institution_id=%s AND is_main LIMIT 1", (inst["id"],))
        campus = cur.fetchone()["id"]
        cur.execute("SELECT id FROM topics WHERE key='housing'")
        housing = cur.fetchone()["id"]
        cur.execute("""INSERT INTO source_permissions (domain_pattern, publisher, connector, access_mode, permission_state, retention_policy, rate_limit_per_minute, notes, reviewed_at)
                       VALUES ('*.cornell.edu','Cornell University','official_html','public_http','allowed_with_limits','excerpts_only',6,'session: host unreachable under network policy',now())
                       ON CONFLICT (domain_pattern) DO NOTHING""")
    conn.commit()
    return inst, campus, housing


def _sources_and_snapshots(conn, inst, campus):
    """Register each official page (blocked snapshot) and a search-snippet evidence source for it."""
    snap_by_key = {}
    for key, (url, title) in OFFICIAL.items():
        sid = register_source(conn, canonical_url=url, institution_id=inst, campus_id=campus, source_kind="official_html", publisher="Cornell Student & Campus Life", reliability="official", source_family="cornell-housing-site")
        record_snapshot(conn, sid, final_url=url, status=None, content_type=None, content_hash="", raw_hash=None, byte_size=None, etag=None, last_modified=None,
                        confidence=None, retained_text=None, retained_tables=None, material_change=None, outcome="blocked",
                        error_detail="DNS resolution refused by session network policy (2026-11-04); page not opened")
        snip_url = url + "#search-snippet-2026-11-04"
        snip_id = register_source(conn, canonical_url=snip_url, institution_id=inst, campus_id=campus, source_kind="search_snippet", publisher="search-engine snippet attributed to " + title, reliability="unrated", source_family="search-snippet")
        snap_by_key[key] = record_snapshot(conn, snip_id, final_url=snip_url, status=200, content_type="text/plain", content_hash=__import__("hashlib").sha256(SNIPPETS[key].encode()).hexdigest(),
                                           raw_hash=None, byte_size=len(SNIPPETS[key]), etag=None, last_modified=None, confidence=0.5, retained_text=SNIPPETS[key], retained_tables=None,
                                           material_change=None, outcome="ok")
    return snap_by_key


def _claim(inst, campus, topic, field, **kw):
    base = dict(institution_id=inst, campus_id=campus, entity_id=None, topic_id=topic, field=field, evidence_category="estimate", extraction_method="import",
                extraction_confidence=0.5, retrieved_at=NOW, academic_year="2026-27")
    base.update(kw)
    return ClaimRecord(**base)


def _store_claims(conn, inst, campus, housing, snaps):
    c = lambda field, **kw: _claim(inst, campus, housing, field, **kw)
    money = lambda room, minor: c("rate.room", value_type="money", value_number=minor, unit="minor_units", currency="USD", billing_period="per_semester", price_basis="per_person", room_type=room)
    items = [
        (money("double", 687200), "S1", "double $6,872 per semester"), (money("single", 778300), "S1", "single $7,783 per semester"),
        (money("triple or one-room quad", 632200), "S1", "triple or one-room quad $6,322 per semester"), (money("super single", 829800), "S1", "super single $8,298 per semester"),
        (c("rate.includes", value_type="text", value_text="gas, electricity, garbage pick-up, internet up to 200 GB/month"), "S1", "Housing Rates include gas, electricity, garbage pick-up, and Internet service (up to 200 GB/month)"),
        (c("eligibility.residency_years_required", value_type="integer", value_number=1, unit="academic_years", audience_applicability=["transfer"]), "S2", "transfers ... must live on campus for one academic year"),
        (c("eligibility.residency_years_required", value_type="integer", value_number=2, unit="academic_years"), "S2", "two-year residential requirement"),
        (c("eligibility.exempt_if", value_type="text", value_text="two years on campus at previous school, or entering as junior/senior", audience_applicability=["transfer"]), "S2", "exempt"),
        (c("eligibility.spring_transfer_rule", value_type="text", value_text="incoming spring plus the following academic year", audience_applicability=["transfer"]), "S2", "spring transfers"),
        (c("eligibility.meal_plan_required", value_type="boolean", value_bool=True), "S2", "with a required meal plan"),
        (c("eligibility.guaranteed_housing", value_type="boolean", value_bool=True, audience_applicability=["first_year"]), "S7", "All first-year students are guaranteed on-campus housing"),
        (c("eligibility.guaranteed_housing", value_type="boolean", value_bool=False, audience_applicability=["transfer"]), "S3", "no guarantee stated; rooms grouped together whenever possible"),
        (c("placement.areas", value_type="text", value_text="West Campus House System; South Campus; North Campus; Program Houses", audience_applicability=["transfer"]), "S3", "may be placed in"),
        (c("deadline.housing_application", value_type="text", value_text="within ten days of receiving NetID", audience_applicability=["transfer"]), "S4", "apply within ten days of receiving your NetID"),
        (c("fee.housing_application", value_type="money", value_number=0, unit="minor_units", currency="USD", billing_period="one_time", price_basis="per_person"), "S4", "There is no fee to apply for housing"),
        (c("deadline.spring_cancellation", value_type="date", value_date=date(2026, 12, 1)), "S5", "Cancellation requests for the spring term are due December 1, 2026"),
        (c("fee.late_cancellation", value_type="money", value_number=50000, unit="minor_units", currency="USD", billing_period="one_time", price_basis="per_person"), "S5", "later requests carry a $500 fee"),
    ]
    results = []
    for rec, key, excerpt in items:
        results.append(claimsmod.store_claim(conn, rec, snapshot_id=snaps[key], excerpt=excerpt, locator="search snippet", source_family="search-snippet"))
    return results


def _discovery(conn, inst, campus):
    items = [discovery.QuestionInput(raw_text=q, origin=o, institution_id=inst, campus_id=campus, topic_key="housing", observed_at=NOW, source_ref=f"websearch:2026-11-04:{i}")
             for i, (q, o, _a) in enumerate(QUESTIONS)]
    out = discovery.ingest(conn, items)
    with conn.cursor() as cur:
        cur.execute("SELECT id, label, audience, observed_count FROM intent_clusters WHERE institution_id=%s ORDER BY observed_count DESC, created_at", (inst,))
        clusters = cur.fetchall()
    return out, clusters


def _score(conn, cluster_id):
    sc = scoring.Score(
        demand=2, answer_gap=4, winnability=3, evidence_advantage=2, commercial=2,
        observations={
            "demand": "repeated independent questions across official FAQ wording, Cornell Sun coverage (2012–2021) and Student Assembly documents; no authorized keyword provider, so D capped at 2",
            "answer_gap": "official answer is split across four pages (residential policy, transfer page, application process, cancellation policy); first-year guarantee is stated, transfer non-guarantee is only implied; secondary coverage is 2008–2021 and partly outdated",
            "winnability": "results mix official pages (navigational) with dated newspaper pieces; a current single-page synthesis is plausible, official pages will outrank for navigational queries",
            "evidence_advantage": "synthesis would be verifiable from primary pages, but those pages were NOT opened in this session — snippet attribution only, so E=2 until opened",
            "commercial": "housing decision with spend implications (room rate, meal plan, $500 fee); no advertiser evidence",
        },
        confidence="low", effort_research=2, effort_build=1, effort_maintain=2,
    )
    dec = scoring.decide(sc)  # E<3 → hold, not advance
    oid = scoring.persist(conn, cluster_id, sc, dec, scorer_model=SESSION_MODEL)
    return sc, dec, oid


def _brief_and_page(conn, inst, campus, housing, cluster_id, oid, claim_results):
    critical = [r.claim_id for r in claim_results]
    with conn.cursor() as cur:
        cur.execute("SELECT id, field, is_critical FROM claims WHERE id = ANY(%s)", (critical,))
        rows = cur.fetchall()
    crit_ids = [r["id"] for r in rows if r["is_critical"]]
    supp_ids = [r["id"] for r in rows if not r["is_critical"]]
    with conn.cursor() as cur:
        cur.execute(
            """INSERT INTO briefs (institution_id, campus_id, cluster_id, opportunity_id, page_format, audience, reader_decision, verified_answer, unique_contribution,
               critical_claim_ids, unresolved_facts, exceptions, structure, allowed_subjective_evidence, next_tasks, overlap_page_ids, status)
               VALUES (%s,%s,%s,%s,'guide','transfer',%s,%s,%s,%s,%s,%s,%s::jsonb,%s,%s,%s,'draft') RETURNING id""",
            (inst, campus, cluster_id, oid,
             "As an incoming Cornell transfer: must I live on campus, will I get a room, where, by when, and what will it cost?",
             "Transfers without prior residency live on campus one academic year (spring entrants: spring + next year); juniors/seniors or two-year prior residents exempt; housing not guaranteed for transfers (it is for first-years); placement across West/South/North/Program Houses; apply within ten days of NetID; 2026-27 double $6,872 per semester per person. ALL SNIPPET-ATTRIBUTED, UNVERIFIED.",
             "One page that separates the transfer rule from the first-year rule (years required, guarantee, placement, deadline) and prices it on a per-person, per-semester basis with what the rate includes.",
             crit_ids, ["primary pages not opened (network policy)", "whether the 'full for 2026-27' notice still stands", "number of transfers assigned in 2026", "whether any transfer guarantee was adopted after 2020"],
             ["cooperative-residence rate block on the rates page is a different scope"],
             json.dumps([{"heading": "Do transfers have to live on campus?"}, {"heading": "Is housing guaranteed?"}, {"heading": "Where transfers actually live"}, {"heading": "What it costs"}, {"heading": "Deadlines that matter"}, {"heading": "What we could not verify"}]),
             [], ["open primary pages S1–S7 and re-verify", "meal-plan cost comparison", "West vs South Campus profile pair"], []),
        )
        bid = cur.fetchone()["id"]
        cur.execute("""INSERT INTO pages (institution_id, campus_id, topic_id, page_format, slug, path, audience, status) VALUES (%s,%s,%s,'guide','transfer-housing','/schools/cornell-university/housing/transfer-housing/','transfer','drafting')
                       ON CONFLICT (path) DO UPDATE SET status='drafting' RETURNING id""", (inst, campus, housing))
        pid = cur.fetchone()["id"]
    conn.commit()
    return bid, pid, crit_ids, supp_ids


def _fact_table(claim_results):
    by = {}
    for r in claim_results:
        by.setdefault(r.claim_id, r)
    ids = [str(r.claim_id) for r in claim_results]
    rows = [
        {"label": "Residency required (transfer without prior residency)", "value": "1 academic year; spring entrants: spring + following year", "status": "estimate", "claim_id": ids[5]},
        {"label": "Residency required (first-year)", "value": "2 academic years", "status": "estimate", "claim_id": ids[6]},
        {"label": "Exempt transfers", "value": "2 years on campus at previous school, or entering as junior/senior", "status": "estimate", "claim_id": ids[7]},
        {"label": "Housing guaranteed — transfers", "value": "Not stated as guaranteed; waitlist with weekly updates", "status": "estimate", "claim_id": ids[11]},
        {"label": "Housing guaranteed — first-years", "value": "Yes", "status": "estimate", "claim_id": ids[10]},
        {"label": "Where transfers may be placed", "value": "West Campus House System; South Campus; North Campus; Program Houses", "status": "estimate", "claim_id": ids[12]},
        {"label": "Housing application deadline (transfer)", "value": "Within 10 days of receiving NetID; no fee", "status": "estimate", "claim_id": ids[13]},
        {"label": "Double room, 2026-27", "value": "$6,872 per semester, per person ($13,744/yr)", "status": "estimate", "claim_id": ids[0], "numeric": True},
        {"label": "Single room, 2026-27", "value": "$7,783 per semester, per person ($15,566/yr)", "status": "estimate", "claim_id": ids[1], "numeric": True},
        {"label": "Triple / one-room quad, 2026-27", "value": "$6,322 per semester, per person ($12,644/yr)", "status": "estimate", "claim_id": ids[2], "numeric": True},
        {"label": "Super single, 2026-27", "value": "$8,298 per semester, per person ($16,595/yr)", "status": "estimate", "claim_id": ids[3], "numeric": True},
        {"label": "Rate includes", "value": "gas, electricity, garbage pick-up, internet up to 200 GB/month; not the meal plan", "status": "estimate", "claim_id": ids[4]},
        {"label": "Meal plan required with residency", "value": "Yes", "status": "estimate", "claim_id": ids[9]},
        {"label": "Spring cancellation deadline / late fee", "value": "December 1, 2026; $500 after", "status": "estimate", "claim_id": ids[15], "numeric": True},
        {"label": "Which dorms have air conditioning", "value": "Unknown — not researched from a primary source yet", "status": "unknown"},
    ]
    return rows


def run_cornell_transfer_housing() -> dict:
    settings = get_settings()
    conn = connect(settings.database_url)
    report = {"run_at": NOW.isoformat(), "blocker": BLOCKER}
    inst_row, campus, housing = _ensure_cornell(conn)
    inst = inst_row["id"]
    snaps = _sources_and_snapshots(conn, inst, campus)
    claim_results = _store_claims(conn, inst, campus, housing, snaps)
    report["claims"] = {"stored": len(claim_results), "actions": sorted({r.action for r in claim_results})}
    disc, clusters = _discovery(conn, inst, campus)
    report["discovery"] = dict(disc, clusters=[{"id": str(c["id"]), "label": c["label"], "audience": c["audience"]} for c in clusters])
    target = next(c for c in clusters if "guaranteed for transfer" in c["label"])
    sc, dec, oid = _score(conn, target["id"])
    report["opportunity"] = {"cluster_id": str(target["id"]), "priority": sc.priority(), "decision": dec.decision, "rationale": dec.rationale, "opportunity_id": str(oid)}
    bid, pid, crit_ids, supp_ids = _brief_and_page(conn, inst, campus, housing, target["id"], oid, claim_results)
    body = (CONTENT / "draft.md").read_text()
    headline = "Cornell housing for transfer students: what is required, what is guaranteed, what it costs"
    deck = "Transfers follow a different residency rule from first-years, are not promised a room, and have ten days from their NetID to apply. The 2026-27 rates, per person and per semester."
    fact_table = _fact_table(claim_results)
    next_actions = [{"text": "Compare a West Campus and a South Campus hall on the same per-person basis", "target": "/schools/cornell-university/housing/"},
                    {"text": "Add the required meal plan in the total-cost calculator", "target": "/tools/total-cost/"},
                    {"text": "Read Cornell's residential policy page for your exact situation", "target": OFFICIAL["S2"][0]}]
    structured = {"fact_table": fact_table, "fact_table_caption": "Transfer housing at Cornell — snippet-attributed facts, 2026-27 (unverified)",
                  "fact_table_footnote": "Every value is a search-engine snippet attributed to the named Cornell page; the page itself has not been opened by this publication. Nothing here is verified.",
                  "next_actions": next_actions, "claim_refs": [str(c) for c in crit_ids + supp_ids],
                  "sources_used": [f"{k}: {u}" for k, (u, _t) in OFFICIAL.items()]}
    all_ids = crit_ids + supp_ids
    vid = gates.create_version(conn, pid, brief_id=bid, headline=headline, deck=deck, body_md=body, body_html=None, structured=structured, byline="Housing desk",
                               production_note="Researched, written, edited and checked inside a Claude Code session on 2026-11-04 from search-snippet attributions to Cornell's official housing pages; deterministic checks applied; no human editor reviewed this version; primary pages not yet opened.",
                               claim_ids=all_ids, writer_model=SESSION_MODEL, editor_model=SESSION_MODEL, verifier_model=SESSION_MODEL, change_summary="initial in-session draft")
    det = checks.run_all(headline=headline, deck=deck, body_md=body, byline="Housing desk", fact_table=fact_table, body_claim_ids=[str(c) for c in all_ids],
                         critical_ids=[str(c) for c in crit_ids], approved_ids={str(c) for c in all_ids}, institution_name="Cornell University",
                         other_institution_names=["Columbia University", "Syracuse University", "Ithaca College"], academic_year="2026-27", next_actions=next_actions, existing_bodies=[])
    # Session verifier rubric (judgment performed in-session; recorded as such). Attribution scored 2 because no claim was checked against an opened source.
    rubric = {"clarity": 4, "specificity": 4, "structure": 4, "attribution": 2, "usefulness": 4, "prose": 4}
    gate = gates.gate_version(conn, vid, det, rubric)
    report["draft"] = {"page_id": str(pid), "version_id": str(vid), "brief_id": str(bid), "deterministic_findings": [f.as_dict() for f in det],
                       "rubric": dict(rubric, total=sum(rubric.values())), "gate": gate.as_dict()}
    with conn.cursor() as cur:
        cur.execute("UPDATE pages SET status='held', revalidation_required=TRUE, revalidation_reason=%s WHERE id=%s", ("primary sources unopened (network policy)", pid))
    conn.commit()
    # Render the held draft into the preview site, clearly labeled.
    ctx = preview.base_ctx("/schools/cornell-university/housing/transfer-housing/", "guide", "/topics/housing/")
    ctx.update(page={"id": str(pid), "headline": headline, "deck": deck, "section": "Cornell University · Housing · for transfer students", "section_href": "/schools/cornell-university/housing/",
                     "byline": "Housing desk", "published_at": NOW, "updated_at": NOW, "audience_label": "incoming transfer students", "body_markdown": body,
                     "fact_table": fact_table, "fact_table_caption": structured["fact_table_caption"], "fact_table_footnote": structured["fact_table_footnote"],
                     "next_actions": next_actions, "production_note": structured and "Researched, written, edited and checked inside a Claude Code session on 2026-11-04 from search-snippet attributions to Cornell's official housing pages. No human editor reviewed this version. Primary pages not yet opened.",
                     "sources": [{"url": u, "title": t + " (snippet-attributed; page not opened)", "publisher": "Cornell Student & Campus Life", "retrieved_at": NOW, "kind": "search snippet"} for k, (u, t) in OFFICIAL.items()],
                     "held_notice": BLOCKER, "stale": False},
               related=[{"text": "Cornell housing hub (coverage pending)", "href": "/schools/cornell-university/housing/"}], structured_data="")
    html = engine.render("article.html", **ctx)
    out = preview.OUT_DEFAULT / "schools" / "cornell-university" / "housing" / "transfer-housing" / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html)
    report["preview_path"] = str(out)
    conn.close()
    (REPO_ROOT / "docs" / "research" / "cornell-transfer-housing-run.json").write_text(json.dumps(report, indent=2, default=str))
    return report


if __name__ == "__main__":
    r = run_cornell_transfer_housing()
    print(json.dumps({k: r[k] for k in ("claims", "opportunity", "preview_path")}, indent=2, default=str))
    print("gate:", r["draft"]["gate"]["status"], "| hard:", r["draft"]["gate"]["hard_failures"][:1], "| rubric:", r["draft"]["rubric"]["total"])
    print("deterministic findings:", [(f["kind"], f["severity"]) for f in r["draft"]["deterministic_findings"]])
