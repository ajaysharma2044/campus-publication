"""R16 pipeline per page, as a coordinator-run chain (continuous-local-run R16, R25, R37, R38, R45, R8; AT14, AT23, AT25, AT38).

    python -m campus_worker.pipeline run <cluster_id> [--until <stage>] [--notes <json file>] [--links <path,path>] [--draft <path>]
    python -m campus_worker.pipeline publish <version_id> [--links <path,path>]     SEO gate + local publish for a passed version

Stages: plan (planner + information gain, R37) → write → deterministic checks → edit → version → beat_review (R38, one resend) →
verify (verifier dispatch + gates) → seo (rendered-HTML gate + seo agent checklist, R45) → publish (R8). Every stage persists its
result in the database and the dispatch log; the funnel guard refuses expensive stages for unqualified clusters (R25). Pages
in one build link to each other, so `--links` names the sibling paths the writer may link to.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID

import psycopg

from . import funnel, quality, search_intel, seo_gate, strategy, sweetspot
from .agents import dispatch as dsp
from .cms import publisher
from .config import REPO_ROOT
from .editorial import checks, gates
from .editorial.checks import Finding

STAGES = ("search_intel", "opportunity", "strategy", "research", "plan", "write", "edit", "beat_review", "verify", "seo", "publish")
RUNS_DIR = REPO_ROOT / "build" / "runs"
NEARBY_INSTITUTIONS = ("Ithaca College", "Syracuse University", "Columbia University", "Binghamton University", "Tompkins Cortland Community College")
STYLE_PATHS = ["docs/editorial/style.md", "skills/national-college-publishing/references/writing.md"]
_AGENTS: dict | None = None


class StageRefused(Exception):
    pass


def _agents() -> dict:
    global _AGENTS
    if _AGENTS is None:
        _AGENTS = dsp.load_agents()
    return _AGENTS


def _cluster(conn, cluster_id: UUID) -> dict:
    with conn.cursor() as cur:
        cur.execute("""SELECT c.*, t.key AS topic_key, t.label AS topic_label, i.slug AS school_slug, i.canonical_name AS school_name, p.slug AS place_slug, p.name AS place_name
                       FROM intent_clusters c LEFT JOIN topics t ON t.id=c.topic_id LEFT JOIN institutions i ON i.id=c.institution_id LEFT JOIN places p ON p.id=c.place_id WHERE c.id=%s""", (cluster_id,))
        r = cur.fetchone()
    if not r:
        raise LookupError("cluster not found")
    return dict(r)


def _guard(conn, cluster_id: UUID, agent: str, log_path: Path | None) -> None:
    g = funnel.guard(conn, cluster_id, agent, log_path=log_path)
    if not g.ok:
        raise StageRefused(f"{agent} refused by the funnel at stage {g.stage}: {g.reason}")


# ------------------------------------------------------------------------------------------------ inputs from the database
def human_value(r: dict) -> str:
    vt = r.get("value_type")
    if vt == "money" and r.get("value_number") is not None:
        n = int(r["value_number"])
        s = f"${n // 100:,}" + (f".{n % 100:02d}" if n % 100 else "")
        basis = " ".join(x for x in (("per person" if r.get("price_basis") == "per_person" else r.get("price_basis") or ""), {"per_semester": "per semester", "per_academic_year": "per academic year", "one_time": "one time", "per_month": "per month"}.get(r.get("billing_period") or "", r.get("billing_period") or "")) if x)
        return f"{s} {basis}".strip()
    if vt == "boolean":
        return "yes" if r.get("value_bool") else "no"
    if vt == "date":
        return r["value_date"].isoformat() if r.get("value_date") else ""
    if vt in ("integer", "decimal", "duration"):
        n = r.get("value_number")
        n = int(n) if n is not None and float(n).is_integer() else n
        return f"{n}{(' ' + r['unit']) if r.get('unit') else ''}"
    return r.get("value_text") or ""


def claims_for_scope(conn, *, institution_id, topic_id, include_estimates: bool = False) -> list[dict]:
    """Current claims for a school + topic with their first source excerpt, for packets and fact tables."""
    cats = ("verified_fact", "not_applicable") + (("estimate",) if include_estimates else ())
    with conn.cursor() as cur:
        cur.execute("""SELECT c.* FROM claims c WHERE c.institution_id=%s AND (c.topic_id=%s OR c.topic_id IS NULL) AND c.superseded_by_id IS NULL AND c.conflict_status <> 'open'
                         AND c.evidence_category = ANY(%s) ORDER BY c.field, c.room_type NULLS FIRST, c.audience_applicability""", (institution_id, topic_id, list(cats)))
        rows = [dict(r) for r in cur.fetchall()]
        cur.execute("""SELECT cs.claim_id, cs.excerpt, cs.locator, cs.snapshot_id, s.fetched_at, COALESCE(s.final_url, r.canonical_url) AS source_url, r.source_family, r.publisher,
                              r.source_kind, length(s.retained_text) AS text_chars, (s.final_url LIKE '%%#search-snippet%%' OR r.canonical_url LIKE '%%#search-snippet%%') AS is_snippet
                       FROM claim_sources cs JOIN fetch_snapshots s ON s.id=cs.snapshot_id JOIN source_registry r ON r.id=s.source_id
                       WHERE cs.claim_id = ANY(%s) ORDER BY is_snippet, s.fetched_at DESC""", ([r["id"] for r in rows],))
        srcs: dict = {}
        for x in cur.fetchall():
            srcs.setdefault(x["claim_id"], []).append(dict(x))
    out = []
    for r in rows:
        sources = [{"snapshot_id": str(x["snapshot_id"]), "excerpt": (x.get("excerpt") or "")[:500], "locator": (x.get("locator") or "")[:200], "source_url": x.get("source_url"),
                    "publisher": x.get("publisher"), "retrieved_at": x["fetched_at"].date().isoformat() if x.get("fetched_at") else None,
                    "kind": "search snippet (page not opened)" if x.get("is_snippet") else ("opened page, %s chars of text" % (x.get("text_chars") or 0))} for x in srcs.get(r["id"], [])]
        best = sources[0] if sources else {}
        out.append({"id": str(r["id"]), "field": r["field"], "value": human_value(r), "value_type": r["value_type"], "audience": list(r.get("audience_applicability") or []),
                    "academic_year": r.get("academic_year"), "room_type": r.get("room_type"), "status": r["evidence_category"], "is_critical": bool(r.get("is_critical")),
                    "excerpt": best.get("excerpt", ""), "locator": best.get("locator", ""), "source_url": best.get("source_url"), "publisher": best.get("publisher"),
                    "retrieved_at": best.get("retrieved_at") or (r["retrieved_at"].date().isoformat() if r.get("retrieved_at") else None),
                    "snapshot_id": best.get("snapshot_id"), "sources": sources})
    return out


def export_snapshot_texts(conn, snapshot_ids: list[str], out_dir: Path | None = None) -> dict[str, str]:
    """Write each snapshot's retained text to build/runs/snapshots/<id>.txt so a Read-only agent can open the source (untrusted data, never executed)."""
    out_dir = out_dir or (RUNS_DIR / "snapshots")
    out_dir.mkdir(parents=True, exist_ok=True)
    paths: dict[str, str] = {}
    ids = sorted({str(i) for i in snapshot_ids if i})
    if not ids:
        return paths
    with conn.cursor() as cur:
        cur.execute("""SELECT s.id, s.fetched_at, COALESCE(s.final_url, r.canonical_url) AS url, s.retained_text, s.retained_tables FROM fetch_snapshots s JOIN source_registry r ON r.id=s.source_id WHERE s.id = ANY(%s::uuid[])""", (ids,))
        for row in cur.fetchall():
            p = out_dir / f"{row['id']}.txt"
            tables = row.get("retained_tables")
            body = (row.get("retained_text") or "") + (("\n\n--- tables (json) ---\n" + json.dumps(tables, ensure_ascii=False)[:20000]) if tables else "")
            p.write_text(f"snapshot {row['id']} · {row['url']} · fetched {row['fetched_at']:%Y-%m-%d %H:%M} UTC\n--- untrusted page text follows ---\n{body}")
            paths[str(row["id"])] = str(p.relative_to(REPO_ROOT))
    return paths


def competitors_for_cluster(conn, cluster_id: UUID, n: int = 3) -> list[dict]:
    with conn.cursor() as cur:
        cur.execute("SELECT results, observed_at FROM serp_observations WHERE cluster_id=%s ORDER BY observed_at DESC LIMIT 1", (cluster_id,))
        row = cur.fetchone()
    if not row:
        return []
    results = sorted([r for r in (row["results"] or []) if isinstance(r, dict)], key=lambda r: r.get("position") or 99)[:n]
    out = []
    for r in results:
        summary = (f"{r.get('publisher') or 'unknown publisher'}; type {r.get('result_type')}; dedicated page: {r.get('dedicated')}; freshness {r.get('freshness')}"
                   f"{' (' + str(r.get('freshness_date')) + ')' if r.get('freshness_date') else ''}; academic year stated: {r.get('academic_year_stated') or 'none'}; "
                   f"answer quality {r.get('answer_quality')}; evidence {r.get('evidence_quality')}; lacks: {r.get('missing_contribution') or 'not recorded'}")
        out.append({"url": r.get("url"), "title": r.get("title"), "summary": summary, "says": f"{r.get('title')} — {r.get('answer_quality')} answer; {r.get('missing_contribution') or ''}"[:400],
                    "label": r.get("label") or f"observed via search tool on {row['observed_at']:%Y-%m-%d}"})
    return out


def win_plan_for(conn, *, institution_id, place_id, page_path: str | None, primary_query: str | None) -> dict | None:
    with conn.cursor() as cur:
        cur.execute("SELECT doc FROM strategies WHERE institution_id IS NOT DISTINCT FROM %s AND place_id IS NOT DISTINCT FROM %s ORDER BY version DESC LIMIT 1", (institution_id, place_id))
        row = cur.fetchone()
    if not row:
        return None
    doc = row["doc"] or {}
    for w in doc.get("win_plans") or []:
        if (page_path and w.get("page_path") == page_path) or (primary_query and (w.get("primary_query") or "").strip().lower() == primary_query.strip().lower()):
            plan = dict(w)
            plan["internal_links"] = [l for l in doc.get("internal_links") or [] if w.get("page_path") in (l.get("from"), l.get("to"))]
            plan["trust_signals"] = doc.get("trust_signals") or {}
            return plan
    return None


def _page_for_cluster(conn, cluster_id: UUID) -> dict | None:
    with conn.cursor() as cur:
        cur.execute("""SELECT p.id, p.path, p.status, p.current_version_id, p.primary_query, p.audience, p.page_format, b.id AS brief_id FROM briefs b
                       JOIN page_versions v ON v.brief_id=b.id JOIN pages p ON p.id=v.page_id WHERE b.cluster_id=%s ORDER BY v.created_at DESC LIMIT 1""", (cluster_id,))
        r = cur.fetchone()
        if not r:
            cur.execute("""SELECT p.id, p.path, p.status, p.current_version_id, p.primary_query, p.audience, p.page_format, b.id AS brief_id FROM briefs b
                           JOIN pages p ON p.institution_id IS NOT DISTINCT FROM b.institution_id AND p.topic_id=(SELECT topic_id FROM intent_clusters WHERE id=%s)
                           WHERE b.cluster_id=%s ORDER BY b.created_at DESC LIMIT 1""", (cluster_id, cluster_id))
            r = cur.fetchone()
    return dict(r) if r else None


# ------------------------------------------------------------------------------------------------ stages
def stage_search_intel(conn, cluster_id: UUID, *, settings, runner=dsp.cli_runner, log_path=None, run_id="adhoc") -> dict:
    return search_intel.run_cluster(conn, cluster_id, settings=settings, runner=runner, run_id=run_id, log_path=log_path)


def stage_opportunity(conn, cluster_id: UUID, **_) -> dict:
    cs = sweetspot.score_cluster(conn, cluster_id)
    g = funnel.qualify(conn, cluster_id)
    return {"decision": cs.decision, "scores": {"D": cs.d, "AGI": cs.agi, "G": cs.g, "E": cs.e, "niche_score": cs.niche_score}, "qualified": g.ok, "reason": g.reason}


def stage_strategy(conn, cluster_id: UUID, *, runner=dsp.cli_runner, log_path=None, run_id="adhoc", **_) -> dict:
    _guard(conn, cluster_id, "search-strategist", log_path)
    c = _cluster(conn, cluster_id)
    return strategy.run_strategist(conn, institution_id=c["institution_id"], place_id=c["place_id"], topic_key=c["topic_key"], school_slug=c["school_slug"] or c["place_slug"],
                                   school_name=c["school_name"] or c["place_name"], run_id=run_id, runner=runner, log_path=log_path)


def stage_research(conn, cluster_id: UUID, *, runner=dsp.cli_runner, log_path=None, run_id="adhoc", packet_extra: dict | None = None, **_) -> dict:
    """Researcher: primary-source collection + claim extraction. The coordinator supplies opened snapshots in packet_extra['pages']."""
    _guard(conn, cluster_id, "researcher", log_path)
    c = _cluster(conn, cluster_id)
    agents = _agents()
    packet = dsp.build_packet(task_id=f"research:{str(cluster_id)[:8]}", run_id=run_id, objective=f"Primary-source research for cluster '{c['label']}' ({c['topic_key']}): extract claims from the opened official pages in `pages` only.",
                              input_ids=[str(cluster_id)], institution_id=str(c["institution_id"]) if c["institution_id"] else None, place_id=str(c["place_id"]) if c["place_id"] else None,
                              constraints=["only facts stated in the pages", "money in minor units", "unknown is a value"], turn_budget=agents["researcher"].max_turns, extra=packet_extra or {})
    res = dsp.dispatch(agents["researcher"], packet, runner=runner, conn=conn, log_path=log_path)
    stored = []
    if res.status in ("ok", "hold") and res.doc:
        stored = store_research_claims(conn, c, (res.doc.get("output") or {}).get("claims") or [], snapshot_by_page=(packet_extra or {}).get("snapshot_by_page") or {})
    return {"status": res.status, "errors": res.errors, "claims_stored": stored}


def store_research_claims(conn, c: dict, items: list[dict], *, snapshot_by_page: dict) -> list[dict]:
    from datetime import date as _date
    from . import claims as cm
    from .types import ClaimRecord
    out = []
    now = datetime.now(timezone.utc)
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM campuses WHERE institution_id=%s AND is_main LIMIT 1", (c["institution_id"],))
        campus = (cur.fetchone() or {}).get("id")
    for it in items:
        if it.get("evidence_category") not in ("verified_fact", "not_applicable"):
            continue
        vt = it.get("value_type")
        val = it.get("value")
        kw = dict(institution_id=c["institution_id"], campus_id=campus, entity_id=None, topic_id=c["topic_id"], field=it["field"], value_type=vt,
                  evidence_category=it["evidence_category"], extraction_method="model", extraction_model="session:researcher", extraction_confidence=it.get("confidence") or 0.8,
                  retrieved_at=now, academic_year=it.get("academic_year"), audience_applicability=it.get("audience_applicability") or [], billing_period=it.get("billing_period"),
                  price_basis=it.get("price_basis"), room_type=it.get("room_type"), unit=it.get("unit"), currency=it.get("currency"))
        try:
            if vt in ("money", "integer", "decimal", "duration"):
                kw["value_number"] = int(val) if vt in ("money", "integer") else float(val)
                if vt == "money":
                    kw.update(unit="minor_units", currency=it.get("currency") or "USD")
            elif vt == "boolean":
                kw["value_bool"] = bool(val) if not isinstance(val, str) else val.strip().lower() in ("true", "yes", "1")
            elif vt == "date":
                kw["value_date"] = _date.fromisoformat(str(val)[:10])
            else:
                kw["value_text"] = str(val)
            rec = ClaimRecord(**kw)
        except Exception as e:  # noqa: BLE001 — malformed claim items are reported, never stored
            out.append({"field": it.get("field"), "error": f"{type(e).__name__}: {e}"})
            continue
        page_key = (it.get("source_locator") or "")[:2]
        snap = snapshot_by_page.get(page_key)
        family = _snapshot_family(conn, snap) if snap else None
        r = cm.store_claim(conn, rec, snapshot_id=UUID(str(snap)) if snap else None, excerpt=(it.get("excerpt") or "")[:500], locator=(it.get("source_locator") or "")[:300], source_family=family)
        out.append({"field": it["field"], "action": r.action, "claim_id": str(r.claim_id), "audience": it.get("audience_applicability"), "superseded_id": str(r.superseded_id) if r.superseded_id else None})
    return out


def _snapshot_family(conn, snapshot_id) -> str | None:
    with conn.cursor() as cur:
        cur.execute("SELECT r.source_family FROM fetch_snapshots s JOIN source_registry r ON r.id=s.source_id WHERE s.id=%s", (str(snapshot_id),))
        row = cur.fetchone()
    return row["source_family"] if row else None


def stage_plan(conn, cluster_id: UUID, *, claims: list[dict], win_plan: dict | None, competitors: list[dict], page_path: str, audience: str | None,
               notes: list[str], runner=dsp.cli_runner, log_path=None, run_id="adhoc") -> dict:
    """Planner dispatch → information-gain check (R37) → brief + page rows. Returns watch when the gain check fails."""
    _guard(conn, cluster_id, "planner", log_path)
    c = _cluster(conn, cluster_id)
    agents = _agents()
    evidence = [{"id": k["id"], "field": k["field"], "value": k["value"], "audience": k["audience"], "academic_year": k["academic_year"], "status": k["status"], "is_critical": k["is_critical"], "excerpt": k["excerpt"][:240], "source_url": k["source_url"]} for k in claims]
    packet = dsp.build_packet(task_id=f"plan:{str(cluster_id)[:8]}", run_id=run_id, objective=f"Plan one page for cluster '{c['label']}' ({c['topic_key']}, {c['school_name'] or c['place_name']}) from the listed claims only, against the win plan and what the top results already say.",
                              input_ids=[str(cluster_id)], evidence=evidence, institution_id=str(c["institution_id"]) if c["institution_id"] else None, place_id=str(c["place_id"]) if c["place_id"] else None,
                              constraints=["critical_claim_ids and supporting_claim_ids must be ids from `evidence`", "information_gain: ≥3 decision-relevant items none of the top 3 results contain, each tied to one claim id",
                                           "competitors_say: one line per top result from `competitors` (what the packet records, nothing imagined)", "unresolved_facts: every question the claims cannot answer; never invent an answer",
                                           "page_format from the win plan; audience " + (audience or "general")],
                              acceptance_checks=["planner.json validates", "every claim id exists in evidence", "information_gain ≥ 3 verified items"], turn_budget=agents["planner"].max_turns,
                              extra={"page": {"path": page_path, "audience": audience}, "win_plan": win_plan, "competitors": competitors, "notes": notes, "cluster": {"label": c["label"], "audience": c.get("audience")}})
    res = dsp.dispatch(agents["planner"], packet, runner=runner, conn=conn, log_path=log_path)
    out = {"status": res.status, "errors": res.errors}
    if res.status not in ("ok", "hold") or not res.doc:
        return out
    o = res.doc.get("output") or {}
    gain = quality.apply_information_gain(conn, cluster_id, o.get("information_gain") or [], competitors_say=o.get("competitors_say") or [])
    out["information_gain"] = gain.as_dict() if hasattr(gain, "as_dict") else getattr(gain, "__dict__", str(gain))
    if not getattr(gain, "ok", False):
        out["status"] = "watch"
        return out
    allowed = {k["id"] for k in claims}
    crit = [UUID(x) for x in o.get("critical_claim_ids") or [] if x in allowed]
    supp = [UUID(x) for x in o.get("supporting_claim_ids") or [] if x in allowed]
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM campuses WHERE institution_id=%s AND is_main LIMIT 1", (c["institution_id"],))
        campus = (cur.fetchone() or {}).get("id")
        cur.execute("SELECT id FROM opportunity_scores WHERE cluster_id=%s ORDER BY scored_at DESC LIMIT 1", (cluster_id,))
        orow = cur.fetchone()
        cur.execute("""INSERT INTO briefs (institution_id, campus_id, cluster_id, opportunity_id, page_format, audience, reader_decision, verified_answer, unique_contribution,
                       critical_claim_ids, unresolved_facts, exceptions, structure, allowed_subjective_evidence, next_tasks, overlap_page_ids, status)
                       VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb,%s,%s,%s,'draft') RETURNING id""",
                    (c["institution_id"], campus, cluster_id, orow["id"] if orow else None, o.get("page_format") or "guide", o.get("audience") or audience or "general", o["reader_decision"], o["verified_answer"],
                     o["unique_contribution"], crit, o.get("unresolved_facts") or [], o.get("exceptions") or [], json.dumps(o.get("structure") or []), o.get("allowed_subjective_evidence") or [],
                     o.get("next_tasks") or [], []))
        bid = cur.fetchone()["id"]
        slug = page_path.rstrip("/").rsplit("/", 1)[-1]
        cur.execute("""INSERT INTO pages (institution_id, campus_id, topic_id, place_id, page_format, slug, path, audience, status, primary_query, tier)
                       VALUES (%s,%s,%s,%s,%s,%s,%s,%s,'drafting',%s,1) ON CONFLICT (path) DO UPDATE SET status=CASE WHEN pages.status='published' THEN pages.status ELSE 'drafting' END,
                       primary_query=COALESCE(EXCLUDED.primary_query, pages.primary_query) RETURNING id""",
                    (c["institution_id"], campus, c["topic_id"], c["place_id"], o.get("page_format") or "guide", slug, page_path, o.get("audience") or audience, (win_plan or {}).get("primary_query")))
        pid = cur.fetchone()["id"]
    conn.commit()
    out.update(brief_id=str(bid), page_id=str(pid), critical_claim_ids=[str(x) for x in crit], supporting_claim_ids=[str(x) for x in supp], structure=o.get("structure"), verified_answer=o.get("verified_answer"),
               unresolved_facts=o.get("unresolved_facts"), headline_candidates=o.get("headline_candidates"))
    return out


def _brief_row(conn, brief_id) -> dict:
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM briefs WHERE id=%s", (brief_id,))
        b = dict(cur.fetchone())
    return {"reader_decision": b["reader_decision"], "verified_answer": b["verified_answer"], "unique_contribution": b["unique_contribution"], "structure": b["structure"], "audience": b["audience"],
            "page_format": b["page_format"], "critical_claim_ids": [str(x) for x in b["critical_claim_ids"] or []], "unresolved_facts": b["unresolved_facts"], "next_tasks": b["next_tasks"]}


def stage_write(conn, cluster_id: UUID, *, page: dict, brief_id, claims: list[dict], win_plan: dict | None, notes: list[str], link_targets: list[dict],
                prior_draft_path: str | None, resend: dict | None = None, runner=dsp.cli_runner, log_path=None, run_id="adhoc") -> dict:
    _guard(conn, cluster_id, "writer", log_path)
    c = _cluster(conn, cluster_id)
    agents = _agents()
    evidence = [{"id": k["id"], "field": k["field"], "value": k["value"], "audience": k["audience"], "academic_year": k["academic_year"], "room_type": k["room_type"], "status": k["status"],
                 "is_critical": k["is_critical"], "excerpt": k["excerpt"][:300], "source_url": k["source_url"], "retrieved_at": k["retrieved_at"]} for k in claims]
    hubs = seo_gate._hubs_for(page["path"])
    constraints = [
        "State as fact only what a listed claim says, and list every claim you used in claim_refs; no other facts, numbers, dates, names, or history. A fact the claims do not cover is written as not stated on the pages we opened.",
        "Money: per person and per semester with the academic year written exactly as 2026-27; every dollar amount in prose also appears in fact_table, to the dollar.",
        "Write no other academic-year range anywhere (no 2019-20, 2020-2021); refer to older records without a year range.",
        "Headline ≤ 60 characters and containing the content words of the primary query; deck 120–155 characters (it becomes the meta description) and must state the answer.",
        "The first paragraph answers the reader's question in its first two sentences and is ≤ 50 words.",
        "Put the literal line [[fact-table]] on its own line where the fact table belongs; fact_table rows carry label, value, claim_id (null only for a row that says unknown).",
        "Headings: one per secondary question in the win plan, phrased so the question's words appear; include a numbered-steps block and a one-sentence definition where the win plan asks.",
        "Internal links: markdown links only to paths in link_targets (each exists or is published in this same build) and to the hubs " + f"{hubs[0]} and {hubs[1]}; descriptive anchor text; at least three links to link_targets.",
        "No filler phrases (docs/editorial/style.md), no quotations, no invented experiences or consensus, no ratings, no superlatives, no 'best'.",
        "Byline: " + page.get("byline", "Housing desk") + ". Include a short 'What we could not verify' section listing `not_verified` plainly.",
        "next_actions: at least two, each a specific action with a target (an internal path from link_targets or an official URL from the claims' source_url).",
    ]
    extra = {"page": {"path": page["path"], "audience": page.get("audience"), "format": page.get("page_format"), "school": c["school_name"] or c["place_name"]}, "brief": _brief_row(conn, brief_id),
             "win_plan": win_plan, "link_targets": link_targets, "hubs": {"topic_hub": hubs[0], "scope_hub": hubs[1]}, "style_paths": STYLE_PATHS, "not_verified": notes,
             "prior_draft_path": prior_draft_path, "resend": resend}
    packet = dsp.build_packet(task_id=f"write:{str(cluster_id)[:8]}{':r2' if resend else ''}", run_id=run_id, objective=f"Draft the page {page['path']} for {c['school_name'] or c['place_name']} from the brief, the win plan and the listed claims only.",
                              input_ids=[str(brief_id), str(cluster_id)], evidence=evidence, institution_id=str(c["institution_id"]) if c["institution_id"] else None, constraints=constraints,
                              acceptance_checks=["writer.json validates", "every claim_refs id is in evidence", "every $ amount in prose is in fact_table", "[[fact-table]] present", "≥3 links to link_targets"],
                              turn_budget=agents["writer"].max_turns, extra=extra)
    res = dsp.dispatch(agents["writer"], packet, runner=runner, conn=conn, log_path=log_path)
    out = {"status": res.status, "errors": res.errors}
    if res.status in ("ok", "hold") and res.doc:
        out["draft"] = res.doc.get("output") or {}
        out["uncertainties"] = res.doc.get("uncertainties") or []
    return out


def deterministic_findings(conn, *, institution_id, page_id, draft: dict, critical_ids: list[str], approved_ids: set[str], academic_year: str | None) -> list[Finding]:
    with conn.cursor() as cur:
        cur.execute("SELECT canonical_name FROM institutions WHERE id=%s", (institution_id,))
        name = (cur.fetchone() or {}).get("canonical_name") or ""
        cur.execute("""SELECT p.id, v.body_markdown FROM pages p JOIN page_versions v ON v.id=p.current_version_id WHERE p.institution_id=%s AND p.id<>%s AND v.body_markdown IS NOT NULL""", (institution_id, page_id))
        existing = [(str(r["id"]), r["body_markdown"]) for r in cur.fetchall()]
    others = [n for n in NEARBY_INSTITUTIONS if n.lower() != name.lower()]
    return checks.run_all(headline=draft["headline"], deck=draft.get("deck"), body_md=draft["body_markdown"], byline=draft.get("byline") or "Housing desk", fact_table=draft.get("fact_table"),
                          body_claim_ids=[str(x) for x in draft.get("claim_refs") or []], critical_ids=[str(x) for x in critical_ids], approved_ids=approved_ids, institution_name=name,
                          other_institution_names=others, academic_year=academic_year, next_actions=draft.get("next_actions"), existing_bodies=existing)


def stage_edit(conn, cluster_id: UUID, *, draft: dict, det_findings: list[Finding], claims: list[dict], runner=dsp.cli_runner, log_path=None, run_id="adhoc") -> dict:
    _guard(conn, cluster_id, "editor", log_path)
    agents = _agents()
    claim_table = [{"id": k["id"], "field": k["field"], "value": k["value"], "audience": k["audience"], "status": k["status"]} for k in claims]
    extra = {"mode": "substantive_edit", "draft": {k: draft.get(k) for k in ("headline", "deck", "body_markdown", "fact_table", "next_actions", "claim_refs")},
             "deterministic_findings": [f.as_dict() for f in det_findings], "claim_table": claim_table, "style_paths": STYLE_PATHS + ["skills/national-college-publishing/references/editing.md"]}
    packet = dsp.build_packet(task_id=f"edit:{str(cluster_id)[:8]}", run_id=run_id, objective="Substantive edit of the draft: resolve every deterministic finding, keep every claim reference, add no fact, cut machine-prose tells; return the revised draft.",
                              input_ids=[str(cluster_id)], constraints=["no new facts, numbers, dates or sources", "keep [[fact-table]]", "keep the claim ids", "deck 120–155 chars; headline ≤ 60 chars"],
                              acceptance_checks=["editor.json validates", "every deterministic finding addressed or listed in unresolved"], turn_budget=agents["editor"].max_turns, extra=extra)
    res = dsp.dispatch(agents["editor"], packet, runner=runner, conn=conn, log_path=log_path)
    out = {"status": res.status, "errors": res.errors}
    if res.status in ("ok", "hold") and res.doc:
        o = res.doc.get("output") or {}
        revised = dict(draft)
        if o.get("revised_headline"):
            revised["headline"] = o["revised_headline"]
        if o.get("revised_deck") is not None:
            revised["deck"] = o["revised_deck"]
        if o.get("revised_body_markdown"):
            revised["body_markdown"] = o["revised_body_markdown"]
        out.update(draft=revised, findings=o.get("findings") or [], substantive_changes=o.get("substantive_changes") or [], unresolved=o.get("unresolved") or [])
    return out


def json_ld_for(*, headline: str, deck: str | None, path: str, publication_name: str, base_url: str, published: datetime, modified: datetime, crumbs: list[tuple[str, str]]) -> str:
    article = {"@context": "https://schema.org", "@type": "Article", "headline": headline, "description": deck or "", "datePublished": published.date().isoformat(), "dateModified": modified.date().isoformat(),
               "author": {"@type": "Organization", "name": publication_name}, "publisher": {"@type": "Organization", "name": publication_name}, "mainEntityOfPage": f"{base_url}{path}"}
    crumb = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": f"{base_url}{h}"} for i, (n, h) in enumerate(crumbs)]}
    return json.dumps([article, crumb], ensure_ascii=False)


def create_version(conn, *, page: dict, brief_id, draft: dict, claim_ids: list[str], settings, writer_model: str, editor_model: str, change_summary: str, school_name: str, topic_label: str,
                   sources_used: list[str] | None = None, production_note: str | None = None) -> UUID:
    now = datetime.now(timezone.utc)
    with conn.cursor() as cur:
        cur.execute("SELECT first_published_at, last_material_update_at FROM pages WHERE id=%s", (page["id"],))
        prow = cur.fetchone() or {}
    published = prow.get("first_published_at") or now
    hubs = seo_gate._hubs_for(page["path"])
    crumbs = [("Home", "/"), ("Schools" if page["path"].startswith("/schools/") else "Towns", "/schools/" if page["path"].startswith("/schools/") else "/towns/"), (school_name, hubs[1]), (topic_label, hubs[0]), (draft["headline"], page["path"])]
    structured = {"fact_table": draft.get("fact_table") or [], "fact_table_caption": draft.get("fact_table_caption") or f"{topic_label} at {school_name}: facts from official pages, 2026-27",
                  "fact_table_footnote": draft.get("fact_table_footnote") or "Every row cites a claim verified against a fetched official page; the retrieval date is in Sources.",
                  "next_actions": draft.get("next_actions") or [], "claim_refs": [str(c) for c in claim_ids], "sources_used": sources_used or [],
                  "json_ld": json_ld_for(headline=draft["headline"], deck=draft.get("deck"), path=page["path"], publication_name=settings.publication_name, base_url=getattr(settings, "base_url", "") or "",
                                         published=published, modified=now, crumbs=crumbs)}
    note = production_note or ("Produced by the publication's automated system on %s: claims extracted from fetched official pages (see Sources), drafted by the writer agent, edited by the editor agent, "
                               "reviewed against the top observed results, verified claim by claim by the verifier agent with deterministic checks. No human editor reviewed this version." % now.date().isoformat())
    return gates.create_version(conn, page["id"], brief_id=brief_id, headline=draft["headline"], deck=draft.get("deck"), body_md=draft["body_markdown"], body_html=None, structured=structured,
                                byline=draft.get("byline") or "Housing desk", production_note=note, claim_ids=[UUID(str(c)) for c in claim_ids], writer_model=writer_model, editor_model=editor_model,
                                verifier_model=None, change_summary=change_summary)


def stage_beat_review(conn, cluster_id: UUID, *, version_id: UUID, draft: dict, claims: list[dict], competitors: list[dict], round_no: int, runner=dsp.cli_runner, log_path=None, run_id="adhoc") -> dict:
    """R38: a fresh editor dispatch with no drafting context scores us and the top 3 on six items."""
    agents = _agents()
    claim_table = [{"field": k["field"], "value": k["value"], "audience": k["audience"]} for k in claims]
    extra = quality.beat_review_packet_extra(draft["body_markdown"], draft["headline"], claim_table, competitors)
    packet = dsp.build_packet(task_id=f"beat:{str(cluster_id)[:8]}:r{round_no}", run_id=run_id, objective="Competitor-beat review: score this draft and each listed competitor 0–4 on the six items; return beat_review.",
                              input_ids=[str(version_id)], constraints=["judge only what the packet contains", "no rewrite", "return beat_review with ours and one entry per competitor"],
                              acceptance_checks=["editor.json validates with beat_review"], turn_budget=agents["editor"].max_turns, extra=extra)
    res = dsp.dispatch(agents["editor"], packet, runner=runner, conn=conn, log_path=log_path)
    out = {"status": res.status, "errors": res.errors, "round": round_no}
    if res.status not in ("ok", "hold") or not res.doc:
        return out
    br = (res.doc.get("output") or {}).get("beat_review") or {}
    review = quality.score_review(br.get("ours") or {}, [{"url": x.get("url"), "scores": x.get("scores") or {}} for x in br.get("competitors") or []], round_no=round_no)
    quality.record_review(conn, version_id, review)
    out.update(review=review.as_dict(), outcome=review.outcome, passed=review.passed, findings=(res.doc.get("output") or {}).get("findings") or [], note=br.get("verdict_note"))
    return out


_VERIFIER_HARD = {"unsupported_critical_claim": "unsupported_claim", "unresolved_conflict": "unresolved_conflict", "wrong_school_campus_year": "wrong_school", "invented_quote_or_experience": "invented_quote",
                  "missing_rights": "missing_rights", "incorrect_arithmetic": "incorrect_arithmetic", "deceptive_headline": "deceptive_headline", "superficial_duplicate": "superficial_duplicate",
                  "unsafe_code": "unsafe_code", "broken_interaction": "broken_interaction", "inaccessible_layout": "inaccessible_layout", "ads_obscure_task": "ads_obscure_task",
                  "missing_privacy_behavior": "missing_privacy_behavior", "fake_byline": "fake_byline", "fabricated_consensus": "fabricated_consensus"}
_CHECK_KIND = {"unsupported": "unsupported_claim", "stale": "unsupported_claim", "conflicted": "unresolved_conflict", "arithmetic_error": "incorrect_arithmetic", "wrong_scope": "wrong_school"}


def stage_verify(conn, cluster_id: UUID, *, version_id: UUID, draft: dict, claims: list[dict], det_findings: list[Finding], runner=dsp.cli_runner, log_path=None, run_id="adhoc") -> dict:
    """Verifier dispatch (claim by claim against the fetched pages, rubric 0–4 × 6) then the deterministic gate."""
    _guard(conn, cluster_id, "verifier", log_path)
    agents = _agents()
    used = {str(x) for x in draft.get("claim_refs") or []}
    chosen = [k for k in claims if k["id"] in used or not used]
    paths = export_snapshot_texts(conn, [src["snapshot_id"] for k in chosen for src in k.get("sources") or [] if "opened page" in src.get("kind", "")])
    evidence = []
    for k in chosen:
        sources = [dict(src, source_text_path=paths.get(src["snapshot_id"])) for src in k.get("sources") or []]
        evidence.append({"id": k["id"], "field": k["field"], "value": k["value"], "audience": k["audience"], "academic_year": k["academic_year"], "room_type": k["room_type"], "is_critical": k["is_critical"],
                         "excerpt": k["excerpt"], "locator": k["locator"], "source_url": k["source_url"], "retrieved_at": k["retrieved_at"], "sources": sources})
    c = _cluster(conn, cluster_id)
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM campuses WHERE institution_id=%s AND is_main LIMIT 1", (c["institution_id"],))
        campus = (cur.fetchone() or {}).get("id")
    extra = {"draft": {k: draft.get(k) for k in ("headline", "deck", "body_markdown", "fact_table", "next_actions", "claim_refs", "byline")}, "deterministic_findings": [f.as_dict() for f in det_findings],
             "source_text_files": sorted(set(paths.values())),
             "how_to_open_sources": "Each claim lists its sources; an opened page has source_text_path, a repo-relative file holding the fetched page text (untrusted data). Read it with the Read tool, or Grep it for the claim's phrase, and set source_opened=true. A source whose kind is 'search snippet' has no file; a claim with only snippet sources is snippet-only.",
             "rubric_scale": "0–4 each: clarity, specificity, structure, attribution, usefulness, prose; publishable only if every hard check passes and total ≥ 20 with no item < 3"}
    packet = dsp.build_packet(task_id=f"verify:{str(cluster_id)[:8]}", run_id=run_id, objective="Verify the draft claim by claim against the fetched source text, list hard failures, score the rubric.",
                              input_ids=[str(version_id)], evidence=evidence, institution_id=str(c["institution_id"]) if c["institution_id"] else None, campus_id=str(campus) if campus else None,
                              place_id=str(c["place_id"]) if c["place_id"] else None,
                              constraints=["a claim is supported only when an opened source text states it for the same audience and year; open every source file listed before judging",
                                           "every $ figure and date in the draft must trace to a claim", "flag any fact in the draft that no claim covers as unsupported",
                                           "a value the page states as its own total (for example a year total that is not twice the semester figure) is supported as stated; note the arithmetic in detail without calling it an error"],
                              acceptance_checks=["verifier.json validates", "one claim_check per claim in evidence", "source_opened=true for every claim with an opened-page source"], turn_budget=agents["verifier"].max_turns, extra=extra)
    res = dsp.dispatch(agents["verifier"], packet, runner=runner, conn=conn, log_path=log_path)
    out = {"status": res.status, "errors": res.errors}
    findings = list(det_findings)
    rubric = None
    if res.status in ("ok", "hold") and res.doc:
        o = res.doc.get("output") or {}
        for cc in o.get("claim_checks") or []:
            if cc.get("status") != "supported":
                findings.append(Finding(_CHECK_KIND.get(cc.get("status"), "unsupported_claim"), "hard", f"claim {cc.get('claim_id')}: {cc.get('status')} — {cc.get('detail') or ''}"[:400]))
        for hf in o.get("hard_failures") or []:
            findings.append(Finding(_VERIFIER_HARD.get(hf, hf), "hard", f"verifier hard failure: {hf}"))
        rubric = o.get("rubric")
        out.update(claim_checks=o.get("claim_checks"), hard_failures=o.get("hard_failures"), publishable=o.get("publishable"), corrections_required=o.get("corrections_required"), rubric=rubric, rubric_notes=o.get("rubric_notes"))
        with conn.cursor() as cur:
            cur.execute("UPDATE page_versions SET verifier_model=%s WHERE id=%s", (f"agent:verifier/{agents['verifier'].model}", version_id))
        conn.commit()
    else:
        findings.append(Finding("verifier_unavailable", "hard", f"verifier dispatch {res.status}: {'; '.join(res.errors)[:200]}"))
    gate = gates.gate_version(conn, version_id, findings, rubric)
    if not gate.passed:
        with conn.cursor() as cur:
            cur.execute("UPDATE pages SET status='held', revalidation_required=TRUE, revalidation_reason=%s WHERE id=(SELECT page_id FROM page_versions WHERE id=%s) AND status<>'published'",
                        (("gate %s: " % gate.status) + "; ".join(gate.hard_failures + gate.rubric_failures + gate.major_findings)[:400], version_id))
        conn.commit()
    out["gate"] = gate.as_dict()
    return out


def render_build(conn, version_ids: list[UUID], *, settings, out_root: Path, environment: str = "staging") -> dict[str, str]:
    """Render the shell plus the given versions into out_root; returns html by path."""
    from .render import site
    site.render_shell(conn, out_root=out_root, environment=environment, publication_name=settings.publication_name, base_url=getattr(settings, "base_url", "") or "")
    html_by_path: dict[str, str] = {}
    for vid in version_ids:
        p = site.render_version(conn, vid, out_root=out_root, environment=environment, publication_name=settings.publication_name, base_url=getattr(settings, "base_url", "") or "")
        html_by_path["/" + p.parent.relative_to(out_root).as_posix() + "/"] = p.read_text()
    for p in out_root.rglob("index.html"):
        path = "/" + p.parent.relative_to(out_root).as_posix().strip(".") + "/"
        path = path.replace("//", "/")
        html_by_path.setdefault(path, p.read_text())
    return html_by_path


def qa_overflow(out_root: Path) -> tuple[list[int], int]:
    """scripts/qa_screens.js over the build: (widths with overflow, widths checked). Without node nothing is checked."""
    node = shutil.which("node")
    if not node:
        return [], 0
    qa_dir = out_root / "qa"
    r = subprocess.run([node, str(REPO_ROOT / "scripts" / "qa_screens.js"), str(out_root), str(qa_dir)], capture_output=True, text=True, timeout=900, cwd=str(REPO_ROOT))
    widths = sorted({int(w) for w in re.findall(r"overflow[^\n]*?(\d{3,4})px", r.stdout + r.stderr)})
    checked = len(set(re.findall(r"\b(360|390|768|1024|1280|1440)\b", r.stdout))) or 5
    if r.returncode != 0 and not widths:
        widths = [0]
    return widths, checked


def stage_seo(conn, cluster_id: UUID | None, *, version_id: UUID, settings, win_plan: dict | None, sibling_version_ids: list[UUID], runner=dsp.cli_runner, log_path=None, run_id="adhoc",
              environment: str = "staging", run_qa: bool = True) -> dict:
    """R45: deterministic gate on the rendered HTML (with the sibling pages of this build present) plus the seo agent's checklist against the win plan."""
    with conn.cursor() as cur:
        cur.execute("SELECT p.id AS page_id, p.path, p.primary_query, p.institution_id FROM page_versions v JOIN pages p ON p.id=v.page_id WHERE v.id=%s", (version_id,))
        page = dict(cur.fetchone())
    tmp = Path(tempfile.mkdtemp(prefix="seo-gate-", dir=str(RUNS_DIR if RUNS_DIR.exists() else None)))
    try:
        html_by_path = render_build(conn, [version_id] + [v for v in sibling_version_ids if v != version_id], settings=settings, out_root=tmp, environment=environment)
        html = html_by_path[page["path"]]
        css_bytes = (tmp / "static" / "campus.css").stat().st_size if (tmp / "static" / "campus.css").exists() else 0
        overflow, checked = qa_overflow(tmp) if run_qa else ([], 5)
        backlinks = seo_gate.count_backlinks(html_by_path, page["path"])
        hubs = seo_gate._hubs_for(page["path"])
        siblings = [p for p in html_by_path if p.startswith(hubs[0]) and p not in (page["path"], hubs[0])]
        pin = seo_gate.page_input_from_html(conn, version_id, html, css_bytes=css_bytes, environment=environment, base_url=getattr(settings, "base_url", "") or "",
                                            primary_query=page["primary_query"] or (win_plan or {}).get("primary_query") or "", secondary_questions=(win_plan or {}).get("secondary_questions") or [],
                                            real_faq_questions=(win_plan or {}).get("faq_real_questions") or [], backlinks=backlinks, has_sibling_pages=bool(siblings), qa_overflow_widths=overflow, qa_checked_widths=checked)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    titles, descs = seo_gate.site_uniques(conn, exclude_page_id=page["page_id"])
    other = strategy.primary_query_conflict(conn, pin.path, pin.primary_query) if pin.primary_query else None
    det = seo_gate.evaluate(pin, existing_titles=titles, existing_descriptions=descs, other_page_for_primary=other)
    seo_gate.record(conn, version_id, det)
    out = {"seo_gate": det.as_dict(), "page_input": {"title": pin.title, "meta_description": pin.meta_description, "h1s": pin.h1s, "h2h3s": pin.h2h3s, "opening_paragraph": pin.opening_paragraph,
                                                     "internal_links": pin.internal_links, "json_ld_types": [b.get("@type") for b in pin.json_ld], "backlinks": pin.backlinks, "html_css_bytes": pin.html_css_bytes}}
    agents = _agents()
    extra = {"page": out["page_input"] | {"path": pin.path, "primary_query": pin.primary_query, "secondary_questions": pin.secondary_questions}, "deterministic_gate": det.as_dict(), "win_plan": win_plan}
    packet = dsp.build_packet(task_id=f"seo:{str(version_id)[:8]}", run_id=run_id, objective="Checklist of this rendered page against the strategist's win plan and R45: title, meta, URL, headings, structured data, internal links, snippet formatting; findings and proposed changes.",
                              input_ids=[str(version_id)], constraints=["no fabricated rankings or volumes", "proposed changes name the exact target"], acceptance_checks=["seo.json validates"],
                              turn_budget=agents["seo"].max_turns, extra=extra)
    res = dsp.dispatch(agents["seo"], packet, runner=runner, conn=conn, log_path=log_path)
    out["agent"] = {"status": res.status, "errors": res.errors}
    if res.status in ("ok", "hold") and res.doc:
        checklist = res.doc.get("output") or {}
        out["agent"]["checklist"] = checklist
        with conn.cursor() as cur:
            cur.execute("UPDATE page_versions SET seo_gate = COALESCE(seo_gate, '{}'::jsonb) || jsonb_build_object('agent_checklist', %s::jsonb) WHERE id=%s",
                        (json.dumps({"summary": checklist.get("summary"), "findings": checklist.get("findings"), "proposed_changes": checklist.get("proposed_changes"), "win_plan_page": (win_plan or {}).get("page_path")}), version_id))
        conn.commit()
    return out


def stage_publish(conn, cluster_id: UUID | None, *, version_id: UUID, settings, cms=None, out_root=None, sibling_version_ids: list[UUID] | None = None, **_) -> dict:
    """R8: every version that passed every gate (editorial + beat review + seo) publishes locally at once; live goes through the ramp."""
    from .render import site
    with conn.cursor() as cur:
        cur.execute("SELECT gate_status, (seo_gate->>'passed')::boolean AS seo_ok, (beat_review->>'passed')::boolean AS beat_ok, page_id FROM page_versions WHERE id=%s", (version_id,))
        v = cur.fetchone()
    if v["gate_status"] != "passed":
        return {"published": False, "reason": f"editorial gate {v['gate_status']}"}
    if not v["seo_ok"]:
        return {"published": False, "reason": "seo gate not passed"}
    if v["beat_ok"] is False:
        return {"published": False, "reason": "competitor-beat review not passed"}
    res = publisher.publish_local(conn, cms, version_id, settings=settings, out_root=out_root)
    site.render_shell(conn, out_root=out_root or site.OUT_DEFAULT, environment="staging", publication_name=settings.publication_name, base_url=getattr(settings, "base_url", "") or "")
    if cluster_id:
        sweetspot.mark(conn, cluster_id, "done", "published locally (R8)")
    if settings.is_live:
        res["live"] = publisher.release_live(conn, cms, settings=settings)
    return {"published": True, **res}


# ------------------------------------------------------------------------------------------------ orchestration
def run_r16(conn, cluster_id: UUID, *, settings, runner=dsp.cli_runner, log_path=None, run_id="adhoc", notes: list[str] | None = None, link_targets: list[dict] | None = None,
            prior_draft_path: str | None = None, until: str = "verify", page_path: str | None = None, audience: str | None = None, byline: str = "Housing desk", report_path: Path | None = None) -> dict:
    """plan → write → checks → edit → version → beat review (one resend) → verify. SEO and publish run per build with `stage_seo`/`stage_publish`
    once every sibling page of the build has a passed version (their links must resolve)."""
    c = _cluster(conn, cluster_id)
    report: dict = {"cluster_id": str(cluster_id), "label": c["label"], "run_id": run_id, "started": datetime.now(timezone.utc).isoformat(timespec="seconds"), "stages": {}}
    rp = report_path or (RUNS_DIR / "pipeline" / f"{str(cluster_id)[:8]}.json")
    rp.parent.mkdir(parents=True, exist_ok=True)

    def save(stage: str, data: dict) -> None:
        report["stages"][stage] = data
        rp.write_text(json.dumps(report, indent=1, default=str))

    try:
        existing = _page_for_cluster(conn, cluster_id)
        plan_path = page_path or (existing or {}).get("path")
        win = win_plan_for(conn, institution_id=c["institution_id"], place_id=c["place_id"], page_path=plan_path, primary_query=c["label"])
        if not plan_path and win:
            plan_path = win.get("page_path")
        if not plan_path:
            raise StageRefused("no page path: neither an existing page nor a strategy win plan names this cluster")
        claims = claims_for_scope(conn, institution_id=c["institution_id"], topic_id=c["topic_id"])
        competitors = competitors_for_cluster(conn, cluster_id)
        report.update(page_path=plan_path, claims=len(claims), competitors=len(competitors), win_plan=bool(win))
        plan = stage_plan(conn, cluster_id, claims=claims, win_plan=win, competitors=competitors, page_path=plan_path, audience=audience or (existing or {}).get("audience") or c.get("audience"), notes=notes or [],
                          runner=runner, log_path=log_path, run_id=run_id)
        save("plan", plan)
        if plan.get("status") != "ok" or not plan.get("page_id"):
            report["outcome"] = plan.get("status")
            return report
        with conn.cursor() as cur:
            cur.execute("SELECT id, path, audience, page_format FROM pages WHERE id=%s", (plan["page_id"],))
            page = dict(cur.fetchone())
        page["byline"] = byline
        approved = {k["id"] for k in claims}
        crit = plan["critical_claim_ids"]
        rounds, draft, version_id, det = 0, None, None, []
        resend = None
        while True:
            rounds += 1
            w = stage_write(conn, cluster_id, page=page, brief_id=UUID(plan["brief_id"]), claims=claims, win_plan=win, notes=notes or [], link_targets=link_targets or [], prior_draft_path=prior_draft_path, resend=resend,
                            runner=runner, log_path=log_path, run_id=run_id)
            save(f"write_r{rounds}", {k: v for k, v in w.items() if k != "draft"} | {"headline": (w.get("draft") or {}).get("headline")})
            if w.get("status") not in ("ok", "hold") or not w.get("draft"):
                report["outcome"] = "writer_" + str(w.get("status"))
                return report
            draft = dict(w["draft"], byline=byline)
            det = deterministic_findings(conn, institution_id=c["institution_id"], page_id=page["id"], draft=draft, critical_ids=crit, approved_ids=approved, academic_year="2026-27")
            save(f"checks_r{rounds}", {"findings": [f.as_dict() for f in det]})
            e = stage_edit(conn, cluster_id, draft=draft, det_findings=det, claims=claims, runner=runner, log_path=log_path, run_id=run_id)
            save(f"edit_r{rounds}", {k: v for k, v in e.items() if k != "draft"})
            if e.get("status") in ("ok", "hold") and e.get("draft"):
                draft = dict(e["draft"], byline=byline)
                det = deterministic_findings(conn, institution_id=c["institution_id"], page_id=page["id"], draft=draft, critical_ids=crit, approved_ids=approved, academic_year="2026-27")
                save(f"checks_after_edit_r{rounds}", {"findings": [f.as_dict() for f in det]})
            prev_vid = version_id
            version_id = create_version(conn, page=page, brief_id=UUID(plan["brief_id"]), draft=draft, claim_ids=[x for x in draft.get("claim_refs") or [] if x in approved], settings=settings,
                                        writer_model=f"agent:writer/{_agents()['writer'].model}", editor_model=f"agent:editor/{_agents()['editor'].model}",
                                        change_summary=("beat-review resend" if resend else "initial pipeline draft"), school_name=c["school_name"] or c["place_name"] or "", topic_label=c["topic_label"] or "",
                                        sources_used=sorted({k["source_url"] for k in claims if k.get("source_url")}))
            if prev_vid and prev_vid != version_id:
                with conn.cursor() as cur:
                    cur.execute("UPDATE page_versions SET beat_review=(SELECT beat_review FROM page_versions WHERE id=%s) WHERE id=%s", (prev_vid, version_id))
                conn.commit()
            report["version_id"] = str(version_id)
            if until == "write":
                report["outcome"] = "stopped_after_write"
                return report
            round_no = quality.previous_round(conn, version_id) + 1
            b = stage_beat_review(conn, cluster_id, version_id=version_id, draft=draft, claims=claims, competitors=competitors, round_no=round_no, runner=runner, log_path=log_path, run_id=run_id)
            save(f"beat_review_r{round_no}", b)
            if b.get("passed"):
                break
            if b.get("outcome") == "resend_to_writer" and rounds < 2:
                resend = {"reason": (b.get("review") or {}).get("reason"), "weak_items": (b.get("review") or {}).get("weak_items"), "our_scores": (b.get("review") or {}).get("ours"),
                          "competitors": (b.get("review") or {}).get("competitors"), "findings": b.get("findings"), "note": b.get("note")}
                continue
            report["outcome"] = "held_by_beat_review" if b.get("outcome") == "held" else f"beat_review_{b.get('status')}"
            return report
        if until == "beat_review":
            report["outcome"] = "stopped_after_beat_review"
            return report
        v = stage_verify(conn, cluster_id, version_id=version_id, draft=draft, claims=claims, det_findings=det, runner=runner, log_path=log_path, run_id=run_id)
        save("verify", v)
        report["outcome"] = "gate_" + v["gate"]["status"]
        return report
    except StageRefused as e:
        report["outcome"] = "refused"
        report["refused"] = str(e)
        rp.write_text(json.dumps(report, indent=1, default=str))
        return report


def reverify(conn, version_id: UUID, *, settings, runner=dsp.cli_runner, log_path=None, run_id="adhoc") -> dict:
    """Re-run deterministic checks + the verifier + the gate on a stored version (after its sources became openable or claims changed)."""
    with conn.cursor() as cur:
        cur.execute("""SELECT v.headline, v.deck, v.body_markdown, v.structured, v.byline, v.brief_id, p.id AS page_id, p.institution_id, p.topic_id, b.cluster_id, b.critical_claim_ids
                       FROM page_versions v JOIN pages p ON p.id=v.page_id LEFT JOIN briefs b ON b.id=v.brief_id WHERE v.id=%s""", (version_id,))
        v = dict(cur.fetchone())
        cur.execute("SELECT claim_id FROM page_claims WHERE page_version_id=%s", (version_id,))
        used = [str(r["claim_id"]) for r in cur.fetchall()]
    st = v["structured"] or {}
    draft = {"headline": v["headline"], "deck": v["deck"], "body_markdown": v["body_markdown"], "fact_table": st.get("fact_table"), "next_actions": st.get("next_actions"), "claim_refs": st.get("claim_refs") or used, "byline": v["byline"]}
    claims = claims_for_scope(conn, institution_id=v["institution_id"], topic_id=v["topic_id"])
    approved = {k["id"] for k in claims}
    det = deterministic_findings(conn, institution_id=v["institution_id"], page_id=v["page_id"], draft=draft, critical_ids=[str(x) for x in v.get("critical_claim_ids") or []], approved_ids=approved, academic_year="2026-27")
    out = stage_verify(conn, v["cluster_id"], version_id=version_id, draft=draft, claims=claims, det_findings=det, runner=runner, log_path=log_path, run_id=run_id)
    out["deterministic_findings"] = [f.as_dict() for f in det]
    rp = RUNS_DIR / "pipeline" / f"reverify-{str(version_id)[:8]}.json"
    rp.parent.mkdir(parents=True, exist_ok=True)
    rp.write_text(json.dumps(out, indent=1, default=str))
    return out


def main(argv: list[str]) -> int:
    from .config import get_settings
    from .db import connect
    if len(argv) < 2 or argv[0] not in ("run", "publish", "verify"):
        print(__doc__)
        return 2
    settings = get_settings()
    conn = connect(settings.database_url)
    run_id = os.environ.get("CAMPUS_RUN_ID", "adhoc")
    log_path = dsp.DISPATCH_LOG_DEFAULT
    links = [{"path": p, "anchor_hint": p.rstrip("/").rsplit("/", 1)[-1].replace("-", " ")} for p in (argv[argv.index("--links") + 1].split(",") if "--links" in argv else []) if p]
    try:
        if argv[0] == "run":
            cid = UUID(argv[1])
            stage = argv[argv.index("--stage") + 1] if "--stage" in argv else None
            if stage == "search_intel":
                out = stage_search_intel(conn, cid, settings=settings, run_id=run_id, log_path=log_path)
            elif stage == "opportunity":
                out = stage_opportunity(conn, cid)
            elif stage == "strategy":
                out = stage_strategy(conn, cid, run_id=run_id, log_path=log_path)
            else:
                notes = json.loads(Path(argv[argv.index("--notes") + 1]).read_text()) if "--notes" in argv else []
                out = run_r16(conn, cid, settings=settings, log_path=log_path, run_id=run_id, notes=notes, link_targets=links, prior_draft_path=(argv[argv.index("--draft") + 1] if "--draft" in argv else None),
                              until=(argv[argv.index("--until") + 1] if "--until" in argv else "verify"), page_path=(argv[argv.index("--path") + 1] if "--path" in argv else None),
                              audience=(argv[argv.index("--audience") + 1] if "--audience" in argv else None), byline=(argv[argv.index("--byline") + 1] if "--byline" in argv else "Housing desk"))
        elif argv[0] == "verify":
            out = reverify(conn, UUID(argv[1]), settings=settings, log_path=log_path, run_id=run_id)
        else:
            vid = UUID(argv[1])
            sib = [UUID(x) for x in argv[argv.index("--siblings") + 1].split(",")] if "--siblings" in argv else []
            with conn.cursor() as cur:
                cur.execute("SELECT p.path, p.institution_id, p.place_id FROM page_versions v JOIN pages p ON p.id=v.page_id WHERE v.id=%s", (vid,))
                prow = cur.fetchone()
            win = win_plan_for(conn, institution_id=prow["institution_id"], place_id=prow["place_id"], page_path=prow["path"], primary_query=None)
            out = {"seo": stage_seo(conn, None, version_id=vid, settings=settings, win_plan=win, sibling_version_ids=sib, log_path=log_path, run_id=run_id)}
            if out["seo"]["seo_gate"]["passed"]:
                from .adapters.cms import WordPressAdapter
                cms = WordPressAdapter.from_settings(settings)
                out["publish"] = stage_publish(conn, None, version_id=vid, settings=settings, cms=cms if cms.capability().state in ("connected", "fixture") else None)
        print(json.dumps(out, indent=1, default=str)[:12000])
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
