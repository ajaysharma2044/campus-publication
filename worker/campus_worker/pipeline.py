"""R16 pipeline per page, as a coordinator-run chain (continuous-local-run R16, R25, R37, R38, R45, R8; AT14, AT23, AT25, AT38).

    python -m campus_worker.pipeline run <cluster_id> [--until <stage>] [--notes <json file>] [--links <path,path>] [--draft <path>]
    python -m campus_worker.pipeline publish <version_id> [--siblings <ids>]        SEO gate + local publish for a passed version
    python -m campus_worker.pipeline correct <version_id> [--no-publish]            one correction round for a held version (verifier corrections + SEO gate failures), then gate, SEO gate, publish

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



def _db(conn):
    """The connection the caller holds may have died while an agent ran for minutes (hosted DB idle drop, network blip):
    return it if it still answers, else a fresh connection. Callers reassign `conn = _db(conn)` after every dispatch."""
    try:
        if conn is not None and not conn.closed:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
            return conn
    except Exception:  # noqa: BLE001 — any failure means: reconnect
        pass
    from .config import get_settings
    from .db import connect
    try:
        if conn is not None:
            conn.close()
    except Exception:  # noqa: BLE001
        pass
    return connect(get_settings().database_url)


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


def claims_for_scope(conn, *, institution_id, topic_id, include_estimates: bool = False, place_id=None) -> list[dict]:
    """Current claims for a school + topic with their first source excerpt, for packets and fact tables."""
    cats = ("verified_fact", "not_applicable") + (("estimate",) if include_estimates else ())
    with conn.cursor() as cur:
        if institution_id:
            cur.execute("""SELECT c.* FROM claims c WHERE c.institution_id=%s AND (c.topic_id=%s OR c.topic_id IS NULL) AND c.superseded_by_id IS NULL AND c.conflict_status <> 'open'
                             AND c.evidence_category = ANY(%s) ORDER BY c.field, c.room_type NULLS FIRST, c.audience_applicability""", (institution_id, topic_id, list(cats)))
        else:  # a town scope: claims hang off the town's entities
            cur.execute("""SELECT c.* FROM claims c JOIN entities e ON e.id=c.entity_id WHERE e.place_id=%s AND (c.topic_id=%s OR c.topic_id IS NULL) AND c.superseded_by_id IS NULL
                             AND c.conflict_status <> 'open' AND c.evidence_category = ANY(%s) ORDER BY c.field, c.room_type NULLS FIRST, c.audience_applicability""", (place_id, topic_id, list(cats)))
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
            # a page whose primary query is this cluster's label (strategy query target), never any page of the same school + topic
            cur.execute("""SELECT p.id, p.path, p.status, p.current_version_id, p.primary_query, p.audience, p.page_format, NULL::uuid AS brief_id FROM pages p
                           JOIN intent_clusters c ON c.id=%s WHERE p.institution_id IS NOT DISTINCT FROM c.institution_id AND p.place_id IS NOT DISTINCT FROM c.place_id
                           AND lower(p.primary_query) = lower(c.label) LIMIT 1""", (cluster_id,))
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
    conn = _db(conn)
    stored = []
    if res.status in ("ok", "hold") and res.doc:
        stored = store_research_claims(conn, c, (res.doc.get("output") or {}).get("claims") or [], snapshot_by_page=(packet_extra or {}).get("snapshot_by_page") or {},
                                       entity_id=(packet_extra or {}).get("entity_id"))
    return {"status": res.status, "errors": res.errors, "claims_stored": stored}


_FIELD_PREFIXES = ("rate.", "cost.", "fee.", "deadline.", "eligibility.", "prerequisite.", "agreement.", "accessibility.", "route.", "placement.", "process.", "policy.", "capacity.", "address.", "hours.", "contact.", "amenity.", "timeline.", "housing.")


def canonical_field(field: str) -> str:
    """Keep researcher field names on the claim taxonomy so the critical-claim rule (rate./fee./deadline./eligibility.) keeps its grip:
    a topic prefix is dropped and a segment that names a fee, deadline, rate or eligibility rule moves under that prefix."""
    f = (field or "").strip().lower().replace(" ", "_")
    parts = [x for x in f.split(".") if x]
    if parts and parts[0] in ("housing", "dining", "transfer", "transportation", "costs_aid", "admissions", "town"):
        parts = parts[1:]
    if not parts:
        return f or "fact"
    joined = ".".join(parts)
    head = parts[0]
    if head in ("rate", "cost", "fee", "deadline", "eligibility", "prerequisite", "agreement", "accessibility", "route", "placement", "process", "policy", "capacity", "address", "hours", "contact", "amenity", "timeline"):
        return joined
    rest = "_".join(parts)
    if "fee" in rest or "deposit" in rest:
        return "fee." + rest
    if "deadline" in rest or "due_date" in rest:
        return "deadline." + rest
    if "rate" in rest or "cost" in rest or "price" in rest:
        return "rate." + rest
    if any(k in rest for k in ("eligib", "exception", "exempt", "requirement", "required", "guarantee")):
        return "eligibility." + rest
    if "placement" in rest or "allocation" in rest or "assign" in rest:
        return "placement." + rest
    if "hours" in rest:
        return "hours." + rest
    return joined


def store_research_claims(conn, c: dict, items: list[dict], *, snapshot_by_page: dict, entity_id=None) -> list[dict]:
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
        kw = dict(institution_id=c["institution_id"], campus_id=campus, entity_id=entity_id, topic_id=c["topic_id"], field=canonical_field(it["field"]), value_type=vt,
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
        out.append({"field": canonical_field(it["field"]), "action": r.action, "claim_id": str(r.claim_id), "audience": it.get("audience_applicability"), "superseded_id": str(r.superseded_id) if r.superseded_id else None})
    return out


def _snapshot_family(conn, snapshot_id) -> str | None:
    with conn.cursor() as cur:
        cur.execute("SELECT r.source_family FROM fetch_snapshots s JOIN source_registry r ON r.id=s.source_id WHERE s.id=%s", (str(snapshot_id),))
        row = cur.fetchone()
    return row["source_family"] if row else None


ENTITY_FIELDS = {
    "residence_hall": "room types and their rates (per person, per semester or year, with the academic year), capacity or number of residents, who lives there (first-year, upper-level, program house), address or campus area, dining or meal-plan requirement, accessibility and air conditioning only if stated, year opened only if stated",
    "dining_location": "location and campus area, hours by day as stated, meal-plan acceptance, payment options, dietary offerings only if stated",
    "library": "address or building, hours as stated, who may use it, contact details only if stated",
    "park": "address, hours, amenities, fees or permits as stated",
    "bus_route": "route number and name, endpoints, days of service, headways or first and last trips as stated, fare as stated",
    "town_service": "what the service does, address, hours, phone or email as stated, fees as stated",
}


def ensure_research(conn, cluster_id: UUID, *, settings, runner=dsp.cli_runner, log_path=None, run_id="adhoc") -> dict:
    """LEAN MODE production: an entity cluster with no verified facts gets its official page fetched (robots and access modes honoured)
    and the researcher dispatched on that page before planning. Returns what was collected and stored."""
    from . import lean
    from .collectors.html import collect_html_source, register_source
    from .fetcher import SafeFetcher
    c = _cluster(conn, cluster_id)
    if not c.get("entity_id"):
        return {"status": "not_entity"}
    with conn.cursor() as cur:
        cur.execute("SELECT id, name, entity_type, source_url, source_id, institution_id, campus_id, place_id, attributes FROM entities WHERE id=%s", (c["entity_id"],))
        e = dict(cur.fetchone() or {})
    if not e:
        return {"status": "no_entity_row"}
    attrs = e.get("attributes") or {}
    url = attrs.get("official_url") or attrs.get("url") or e.get("source_url")  # the entity's own page beats the list page it was harvested from
    have = lean.verified_claims_in_scope(conn, institution_id=None, place_id=None, topic_id=None, entity_id=e["id"])
    with conn.cursor() as cur:  # facts harvested from a list page are not research of the entity's own page: do that once
        cur.execute("""SELECT count(*) AS n FROM claims c JOIN claim_sources cs ON cs.claim_id=c.id JOIN fetch_snapshots s ON s.id=cs.snapshot_id JOIN source_registry r ON r.id=s.source_id
                       WHERE c.entity_id=%s AND r.canonical_url=%s""", (e["id"], url))
        from_own_page = int(cur.fetchone()["n"])
    if have and (from_own_page or not url):
        return {"status": "has_facts", "verified_claims": have, "from_own_page": from_own_page}
    if not url:
        return {"status": "no_source_url"}
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM source_registry WHERE canonical_url=%s", (url,))
        row = cur.fetchone()
    try:
        sid = row["id"] if row else register_source(conn, canonical_url=url, institution_id=e.get("institution_id"), campus_id=e.get("campus_id"), place_id=e.get("place_id"),
                                                     source_kind="official_html", publisher=c.get("school_name") or c.get("place_name"))
    except Exception as ex:  # noqa: BLE001 — a domain the registry does not permit stays unfetched
        return {"status": "not_permitted", "detail": str(ex)[:200]}
    conn.commit()
    res = collect_html_source(conn, SafeFetcher(conn), sid)
    conn.commit()
    if res.get("outcome") not in ("ok", "unchanged"):
        return {"status": "fetch_" + str(res.get("outcome")), "detail": res.get("error")}
    with conn.cursor() as cur:
        cur.execute("SELECT id, retained_text FROM fetch_snapshots WHERE source_id=%s AND retained_text IS NOT NULL ORDER BY fetched_at DESC LIMIT 1", (sid,))
        snap = cur.fetchone()
    if not snap or len(snap["retained_text"] or "") < 200:
        return {"status": "no_text", "snapshot_id": str(snap["id"]) if snap else None}
    extra = {"pages": [{"key": "E1", "url": url, "snapshot_id": str(snap["id"]), "text": snap["retained_text"][:30000]}], "snapshot_by_page": {"E1": str(snap["id"])}, "entity_id": e["id"],
             "entity": {"name": e["name"], "type": e["entity_type"]},
             "fields_wanted": [ENTITY_FIELDS.get(e["entity_type"], "every dated, sourced fact about this entity the page states")],
             "rules": ["Only facts the page states about " + e["name"] + "; audience_applicability from the page's own words; source_locator 'E1: <sentence>'; excerpt verbatim; academic_year exactly as stated or null; money in minor units with the basis.",
                       "Fields use the claim taxonomy: rate.<room_type>, capacity.residents, placement.area, eligibility.<rule>, address.street, hours.<day_or_scope>, fee.<name>, contact.<kind>, amenity.<name> (boolean), route.<attribute>."]}
    out = stage_research(conn, cluster_id, runner=runner, log_path=log_path, run_id=run_id, packet_extra=extra)
    out["source_id"] = str(sid); out["snapshot_id"] = str(snap["id"])
    return out


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
    conn = _db(conn)
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
    conn = _db(conn)
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
    observed = competitors_for_cluster(conn, cluster_id, n=10)
    extra = {"draft": {k: draft.get(k) for k in ("headline", "deck", "body_markdown", "fact_table", "next_actions", "claim_refs", "byline")}, "deterministic_findings": [f.as_dict() for f in det_findings],
             "source_text_files": sorted(set(paths.values())),
             "observed_results": [{"url": o.get("url"), "title": o.get("title"), "label": o.get("label")} for o in observed],
             "observed_results_rule": "A sentence that names what currently ranks (a document's observed title, publisher or year) is supported by observed_results, labeled as observed via the search tool; it may not describe such a document's contents.",
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
    conn = _db(conn)
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
            # a failed new version never pulls an already-published (or locally published) version off the site: the page keeps its current version
            cur.execute("""UPDATE pages SET status=CASE WHEN local_published_at IS NOT NULL OR status='published' THEN status ELSE 'held' END, revalidation_required=TRUE, revalidation_reason=%s
                           WHERE id=(SELECT page_id FROM page_versions WHERE id=%s)""",
                        (("gate %s on version %s: " % (gate.status, str(version_id)[:8])) + "; ".join(gate.hard_failures + gate.rubric_failures + gate.major_findings)[:380], version_id))
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


def qa_overflow(out_root: Path, page_path: str | None = None) -> tuple[list[int], int]:
    """scripts/qa_screens.js over the build: (widths where THIS page overflows, widths checked). Without node nothing is checked.
    Problems on other pages of the same build (a hub, a policy page) are not this page's gate failure."""
    node = shutil.which("node")
    if not node:
        return [], 0
    qa_dir = out_root / "qa"
    r = subprocess.run([node, str(REPO_ROOT / "scripts" / "qa_screens.js"), str(out_root), str(qa_dir)], capture_output=True, text=True, timeout=900, cwd=str(REPO_ROOT))
    text = r.stdout + r.stderr
    # qa_screens.js prints "pages×widths: N; problems: M" and one " - <url> @<width>: overflow=<bool> ..." line per problem
    want = (page_path.rstrip("/") + "/index.html") if page_path else None
    widths = sorted({int(w) for url, w in re.findall(r"- (\S+) @(\d{3,4}): overflow=true", text) if not want or url.rstrip("/") in (want, page_path.rstrip("/"))})
    m = re.search(r"pages.widths: (\d+); problems: (\d+)", text)
    checked = 5 if m and int(m.group(1)) > 0 else 0
    if r.returncode != 0 and not m:
        widths = widths or [0]
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
        overflow, checked = qa_overflow(tmp, page["path"]) if run_qa else ([], 5)
        conn = _db(conn)  # the render + screenshot QA can take minutes; the hosted DB may have dropped the connection meanwhile
        backlinks = seo_gate.count_backlinks(html_by_path, page["path"])
        hubs = seo_gate._hubs_for(page["path"])
        siblings = [p for p in html_by_path if p.startswith(hubs[0]) and p not in (page["path"], hubs[0])]
        pin = seo_gate.page_input_from_html(conn, version_id, html, css_bytes=css_bytes, environment=environment, base_url=getattr(settings, "base_url", "") or "",
                                            primary_query=page["primary_query"] or (win_plan or {}).get("primary_query") or "", secondary_questions=(win_plan or {}).get("secondary_questions") or [],
                                            real_faq_questions=(win_plan or {}).get("faq_real_questions") or [], backlinks=backlinks, has_sibling_pages=bool(siblings), qa_overflow_widths=overflow, qa_checked_widths=checked)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    conn = _db(conn)
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
    conn = _db(conn)
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


def auto_cite(draft: dict, claims: list[dict], *, exclude: set[str] | None = None, prefer: set[str] | None = None, page_audience: str | None = None) -> dict:
    """Deterministic citation repair after an edit: a money or date claim whose value appears in the body or fact table is added to claim_refs,
    and a money/date value cited in prose without a fact-table row gets one (label from the field and audience). Never adds prose."""
    import calendar
    body = draft.get("body_markdown") or ""
    exclude = set(exclude or ())
    prefer = set(prefer or ())
    by_id = {k["id"]: k for k in claims}
    table = []
    for r in (draft.get("fact_table") or []):
        cid = str(r.get("claim_id") or "")
        k = by_id.get(cid)
        if cid in exclude or (k and not audience_matches(k.get("audience"), page_audience)):
            continue  # excluded by the verifier, or scoped to an audience this page is not for
        if k and (not re.search(r"[A-Z]", str(r.get("label") or "")) or "unknown" in str(r.get("value") or "")):
            r = dict(r, label=fact_label(k), value=money_value(k) if k["value_type"] == "money" else r.get("value"))  # earlier auto-generated rows get readable labels and clean values
        table.append(r)
    refs = set(str(x) for x in draft.get("claim_refs") or []) - exclude
    table_text = " ".join(f"{r.get('label', '')} {r.get('value', '')}" for r in table)
    # when several claims share a value (the same date for different audiences), the verifier's preferred claims win and excluded ones never return
    ranked = sorted(claims, key=lambda k: (0 if k["id"] in prefer else 1, 0 if k.get("audience") else 1))
    seen_values: set[str] = set()
    for k in ranked:
        if k["id"] in exclude or (k["id"] not in prefer and not audience_matches(k.get("audience"), page_audience)):
            continue  # a verifier-named claim may carry another audience when its row says so (its label names the audience)
        forms: list[str] = []
        if k["value_type"] == "money" and k["value"].startswith("$"):
            forms.append(k["value"].split(" ")[0])
        elif k["value_type"] == "date" and k["value"]:
            y, m, d = k["value"][:10].split("-")
            forms += [k["value"][:10], f"{calendar.month_name[int(m)]} {int(d)}, {y}"]
        if not forms:
            continue
        in_body = any(f in body for f in forms)
        in_table = any(f in table_text for f in forms)
        value_key = forms[0]
        if (in_body or in_table) and (value_key not in seen_values or k["id"] in prefer):
            refs.add(k["id"])
            seen_values.add(value_key)
        else:
            continue
        if in_body and not in_table:
            table.append({"label": fact_label(k), "value": money_value(k) if k["value_type"] == "money" else k["value"], "claim_id": k["id"]})
            table_text += " " + k["value"]
    # text claims: linked when the body carries the claim's statement (most of its content words in one paragraph)
    body_paras = [re.findall(r"[a-z0-9]+", para.lower()) for para in re.split(r"\n\s*\n", body)]
    stop = {"the", "a", "an", "of", "to", "in", "on", "for", "and", "or", "is", "are", "be", "by", "with", "at", "as", "that", "this", "it", "its", "their", "they", "will", "not", "no", "all", "any"}
    for k in claims:
        if k["id"] in exclude or k["id"] in refs or k["value_type"] != "text" or not k.get("value") or (k["id"] not in prefer and not audience_matches(k.get("audience"), page_audience)):
            continue
        words = [w for w in re.findall(r"[a-z0-9]+", k["value"].lower()) if w not in stop]
        if len(words) < 3:
            continue
        for para in body_paras:
            pset = set(para)
            shared = sum(1 for w in words if w in pset)
            if shared >= 3 and shared / len(words) >= 0.5:
                refs.add(k["id"])  # the verifier re-checks every linked claim; a wrong link comes back as wrong_scope and is excluded next round
                break
    out = dict(draft)
    out["claim_refs"] = sorted(refs)
    out["fact_table"] = table
    return out


def money_value(k: dict) -> str:
    """'$500' plus the basis the claim states ('per person', 'per semester'); never 'unknown' or 'one time' noise."""
    amount = k["value"].split(" ")[0] if k.get("value") else ""
    rest = k["value"][len(amount):] if k.get("value") else ""
    parts = [w for w in rest.replace("one time", "").replace("unknown", "").split(" per ") if w.strip()]
    basis = " ".join("per " + x.strip() for x in parts)
    return (amount + (" " + basis if basis else "")).strip()


def audience_matches(claim_audience: list | None, page_audience: str | None) -> bool:
    """A claim scoped to an audience is linked only on a page for that audience (a juniors-and-seniors fee never lands on a first-year page)."""
    if not claim_audience or not page_audience:
        return True
    norm = lambda x: set(re.findall(r"[a-z]+", str(x).lower().replace("_", " ")))
    pa = norm(page_audience) - {"students", "student", "undergraduate", "undergraduates"}
    for a in claim_audience:
        ca = norm(a) - {"students", "student", "undergraduate", "undergraduates"}
        if not pa or not ca or pa & ca:
            return True
    return False


def fact_label(k: dict) -> str:
    """A readable fact-table label from a claim's field and scope: 'Late cancellation fee (returning juniors and seniors), 2026-27'."""
    leaf = k["field"].split(".", 1)[-1].replace("_", " ")
    prefix = k["field"].split(".")[0]
    words = [w for w in leaf.split() if w not in (prefix, "cancellation cancellation")]
    text = " ".join(words)
    if prefix in ("fee",) and "fee" not in text:
        text += " fee"
    if prefix == "deadline" and "deadline" not in text:
        text += " deadline"
    text = text[:1].upper() + text[1:]
    if k.get("audience"):
        text += " (" + ", ".join(a.replace("_", " ") for a in k["audience"]) + ")"
    if k.get("academic_year"):
        text += f", {k['academic_year']}"
    return text[:90]


def sibling_link_targets(conn, *, institution_id, place_id, exclude_path: str | None = None) -> list[dict]:
    """Pages in the same school or town with a passed current version (they are in the build), plus the policy pages: the targets a new
    page may link to, so the R45 three-contextual-links rule can be met as the scope grows."""
    with conn.cursor() as cur:
        cur.execute("""SELECT p.path, v.headline FROM pages p JOIN page_versions v ON v.id=p.current_version_id
                       WHERE p.institution_id IS NOT DISTINCT FROM %s AND p.place_id IS NOT DISTINCT FROM %s AND v.gate_status='passed' AND p.status NOT IN ('redirected','retired')
                       ORDER BY p.local_published_at DESC NULLS LAST, v.created_at DESC""", (institution_id, place_id))
        out = [{"path": r["path"], "anchor_hint": r["headline"]} for r in cur.fetchall() if r["path"] != exclude_path]
    return out + [{"path": "/about/methods/", "anchor_hint": "how we verify these facts"}, {"path": "/about/corrections/", "anchor_hint": "report an error"}]


def latest_verifier_corrections(version_id: UUID) -> dict:
    """The last verifier reply saved for this version (per-dispatch output files), so a correction round never re-dispatches to learn what to fix."""
    outdir = RUNS_DIR / "agent-output"
    best = None
    for f in sorted(outdir.glob("*-verifier-*.json"), reverse=True):
        try:
            d = json.loads(f.read_text())
        except json.JSONDecodeError:
            continue
        doc = d.get("doc") or {}
        if str(version_id) in (doc.get("input_ids") or []):
            best = doc
            break
    o = (best or {}).get("output") or {}
    return {"corrections": o.get("corrections_required") or [], "hard_failures": o.get("hard_failures") or [], "not_supported": [c for c in (o.get("claim_checks") or []) if c.get("status") != "supported"],
            "rubric": o.get("rubric"), "rubric_notes": o.get("rubric_notes") or {}}


def page_claim_verdicts(conn, page_id: UUID) -> dict[str, str]:
    """The verifier's latest verdict per claim across every version of this page (from the saved verifier replies), so a claim once found
    wrong-scope or unsupported stays off the page in later rounds unless a later verdict supports it."""
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM page_versions WHERE page_id=%s", (page_id,))
        vids = {str(r["id"]) for r in cur.fetchall()}
    verdicts: dict[str, tuple[str, str]] = {}
    for f in sorted((RUNS_DIR / "agent-output").glob("*-verifier-*.json")):
        try:
            d = json.loads(f.read_text())
        except json.JSONDecodeError:
            continue
        doc = d.get("doc") or {}
        if not (set(doc.get("input_ids") or []) & vids):
            continue
        stamp = f.name[:16]
        for cc in (doc.get("output") or {}).get("claim_checks") or []:
            cid = str(cc.get("claim_id") or "")
            if cid and (cid not in verdicts or verdicts[cid][0] <= stamp):
                verdicts[cid] = (stamp, cc.get("status") or "")
    return {cid: st for cid, (stamp, st) in verdicts.items()}


def correct(conn, version_id: UUID, *, settings, runner=dsp.cli_runner, log_path=None, run_id="adhoc", siblings: list[UUID] | None = None, publish: bool = True) -> dict:
    """One correction round for a held version: the editor applies the verifier's corrections and the SEO gate's failures (title words,
    links to sibling pages), a new version is created (beat review carried), checked, re-verified when facts changed or the verifier had
    hard failures (otherwise the previous rubric is carried), then SEO-gated with the siblings and published locally."""
    from . import lean
    with conn.cursor() as cur:
        cur.execute("""SELECT v.headline, v.deck, v.body_markdown, v.structured, v.byline, v.brief_id, v.rubric, v.gate_status, v.seo_gate, p.id AS page_id, p.path, p.audience, p.page_format,
                              p.institution_id, p.place_id, p.topic_id, p.primary_query, b.cluster_id, b.critical_claim_ids
                       FROM page_versions v JOIN pages p ON p.id=v.page_id LEFT JOIN briefs b ON b.id=v.brief_id WHERE v.id=%s""", (version_id,))
        v = dict(cur.fetchone())
    c = _cluster(conn, v["cluster_id"]) if v.get("cluster_id") else {"school_name": "", "place_name": "", "topic_label": ""}
    st = v["structured"] or {}
    draft = {"headline": v["headline"], "deck": v["deck"], "body_markdown": v["body_markdown"], "fact_table": list(st.get("fact_table") or []), "next_actions": st.get("next_actions"), "claim_refs": list(st.get("claim_refs") or []), "byline": v["byline"]}
    claims = claims_for_scope(conn, institution_id=v["institution_id"], topic_id=v["topic_id"], place_id=v["place_id"])
    approved = {k["id"] for k in claims}
    crit = [str(x) for x in v.get("critical_claim_ids") or []]
    page = {"id": v["page_id"], "path": v["path"], "audience": v["audience"], "page_format": v["page_format"], "byline": v["byline"]}
    vc = latest_verifier_corrections(version_id) if v["gate_status"] != "passed" else {"corrections": [], "hard_failures": [], "not_supported": [], "rubric": v["rubric"]}
    seo_failed = list(((v.get("seo_gate") or {}).get("failed")) or [])
    links = sibling_link_targets(conn, institution_id=v["institution_id"], place_id=v["place_id"], exclude_path=v["path"])
    det = deterministic_findings(conn, institution_id=v["institution_id"], page_id=v["page_id"], draft=draft, critical_ids=crit, approved_ids=approved, academic_year="2026-27")
    findings = list(det)
    findings += [Finding("attribution", "major", "Verifier correction (every source opened): " + x) for x in vc["corrections"]]
    findings += [Finding("unsupported", "major", f"Verifier marked claim {w['claim_id'][:8]} {w['status']}: {w.get('detail') or ''} — remove or reword the sentence so it states only what that claim's source says, or drop the claim.") for w in vc["not_supported"]]
    if vc.get("rubric") and int(vc["rubric"].get("usefulness", 4)) < 3:
        findings.append(Finding("usefulness", "major", "Verifier scored usefulness below 3: " + str(vc.get("rubric_notes", {}).get("usefulness") or "lead with the facts the reader decides on; cut what the page cannot answer to one short list.")))
    if "title_contains_primary_query" in seo_failed:
        findings.append(Finding("headline", "major", f"SEO gate: the headline must contain the content words of the primary query '{v['primary_query']}' and stay ≤ 60 characters."))
    if "internal_links_three_contextual" in seo_failed or any(f in seo_failed for f in ("internal_links_hub_uplinks",)):
        findings.append(Finding("structure", "major", "SEO gate: add at least three contextual markdown links, each to one of these existing pages with descriptive anchor text, where the text naturally refers to them: " + "; ".join(f"{l['path']} ({l['anchor_hint']})" for l in links) + f". Also link the hubs {seo_gate._hubs_for(v['path'])[0]} and {seo_gate._hubs_for(v['path'])[1]}."))
    if "headings_cover_secondary_questions" in seo_failed:
        findings.append(Finding("headline", "major", "SEO gate: every planned secondary question's content words must appear in some H2/H3; see the version's seo_gate record for the missing ones."))
    for extra_fail in [f for f in seo_failed if f not in ("title_contains_primary_query", "internal_links_three_contextual", "internal_links_hub_uplinks", "headings_cover_secondary_questions")]:
        findings.append(Finding("structure", "minor", f"SEO gate item failed: {extra_fail} (see the version's seo_gate record)"))
    findings.append(Finding("attribution", "major", "Any fact you add must be one of the claims in claim_table (cite its id in claim_refs and give it a fact_table row when it is a date or money value); if no claim covers it, write that the opened pages do not state it."))
    findings.append(Finding("prose", "major", "After applying the corrections, re-read the whole page top to bottom: merge choppy one-line paragraphs, keep one idea per paragraph, keep every section's first sentence the answer, and cut repetition. No new facts."))
    report: dict = {"version_id": str(version_id), "corrections": vc["corrections"], "seo_failed": seo_failed}
    asks = [x for x in vc["corrections"] if re.search(r"\b(add|extract|record)\b.*\bclaim", x, re.I) or "as a claim" in x.lower()]
    if asks and v.get("cluster_id"):
        # the verifier found facts on the opened pages that no claim carries: one researcher pass on those pages, scoped to the asks, before the editor
        snaps = sorted({src["snapshot_id"] for k in claims for src in (k.get("sources") or []) if "opened page" in src.get("kind", "")})
        with conn.cursor() as cur:
            cur.execute("SELECT s.id, COALESCE(s.final_url, r.canonical_url) AS url, s.retained_text FROM fetch_snapshots s JOIN source_registry r ON r.id=s.source_id WHERE s.id = ANY(%s::uuid[]) AND s.retained_text IS NOT NULL", (snaps,))
            pages = [dict(r) for r in cur.fetchall()]
        entity_id = None
        with conn.cursor() as cur:
            cur.execute("SELECT entity_id FROM intent_clusters WHERE id=%s", (v["cluster_id"],))
            entity_id = (cur.fetchone() or {}).get("entity_id")
        keyed = {f"P{i + 1}": pg for i, pg in enumerate(pages[:8])}
        extra = {"pages": [{"key": k, "url": pg["url"], "snapshot_id": str(pg["id"]), "text": pg["retained_text"][:20000]} for k, pg in keyed.items()], "snapshot_by_page": {k: str(pg["id"]) for k, pg in keyed.items()},
                 "entity_id": entity_id, "fields_wanted": asks, "rules": ["Extract only the facts the verifier's asks name, from these pages; source_locator '<key>: <sentence>'; excerpt verbatim; audience from the page's words; money in minor units with its basis; dates as dates."]}
        r = stage_research(conn, v["cluster_id"], runner=runner, log_path=log_path, run_id=run_id, packet_extra=extra)
        conn = _db(conn)
        report["research"] = {"asks": asks, "status": r.get("status"), "claims_stored": [(x.get("field"), x.get("action")) for x in r.get("claims_stored") or []]}
        claims = claims_for_scope(conn, institution_id=v["institution_id"], topic_id=v["topic_id"], place_id=v["place_id"])
        approved = {k["id"] for k in claims}
    e = stage_edit(conn, v["cluster_id"], draft=draft, det_findings=findings, claims=claims, runner=runner, log_path=log_path, run_id=run_id)
    conn = _db(conn)
    report["edit"] = {k: val for k, val in e.items() if k != "draft"}
    rp = RUNS_DIR / "pipeline" / f"correct-{str(version_id)[:8]}.json"
    rp.parent.mkdir(parents=True, exist_ok=True)
    if e.get("status") not in ("ok", "hold") or not e.get("draft"):
        report["outcome"] = "editor_" + str(e.get("status"))
        rp.write_text(json.dumps(report, indent=1, default=str))
        return report
    draft2 = dict(e["draft"], byline=v["byline"], fact_table=draft["fact_table"], next_actions=draft["next_actions"])
    ids_in_body = set(re.findall(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", draft2["body_markdown"]))
    draft2["claim_refs"] = sorted((set(draft["claim_refs"]) | ids_in_body) & approved)
    # the verifier's claim verdicts are deterministic instructions: wrong-scope/unsupported claims leave the page; claims it names as replacements are preferred
    by_prefix = {k["id"][:8]: k["id"] for k in claims}
    excluded = {w["claim_id"] for w in vc["not_supported"] if w.get("status") in ("wrong_scope", "unsupported", "stale", "conflicted")}
    excluded |= {cid for cid, st in page_claim_verdicts(conn, v["page_id"]).items() if st in ("wrong_scope", "unsupported", "stale", "conflicted")}  # verdicts from earlier rounds hold
    preferred: set[str] = set()
    for x in vc["corrections"]:
        for pfx in re.findall(r"\b([0-9a-f]{8})\b", x):
            full = by_prefix.get(pfx)
            if not full:
                continue
            if re.search(r"\b(remove|drop|delete)\b", x, re.I) and re.search(r"\b(row|claim)s? for " + pfx, x, re.I):
                excluded.add(full)
            else:
                preferred.add(full)  # a claim the verifier names in a correction is the one it wants on the page
    draft2 = auto_cite(draft2, claims, exclude=excluded, prefer=preferred, page_audience=v.get("audience"))
    report["claims_excluded"] = sorted(x[:8] for x in excluded); report["claims_preferred"] = sorted(x[:8] for x in preferred)
    figs = lambda b: set(re.findall(r"\$[\d,]+|\b20\d\d-\d\d-\d\d\b|\b\d{1,2},\d{3}\b", b))
    facts_changed = figs(draft["body_markdown"]) != figs(draft2["body_markdown"]) or set(draft2["claim_refs"]) != set(draft["claim_refs"])
    det2 = deterministic_findings(conn, institution_id=v["institution_id"], page_id=v["page_id"], draft=draft2, critical_ids=crit, approved_ids=approved, academic_year="2026-27")
    report["checks_after_edit"] = [f.as_dict() for f in det2]
    new_vid = create_version(conn, page=page, brief_id=v["brief_id"], draft=draft2, claim_ids=list(draft2["claim_refs"]), settings=settings, writer_model="agent:writer/sonnet", editor_model="agent:editor/opus",
                             change_summary="correction round: " + "; ".join((vc["corrections"] + seo_failed)[:4])[:300], school_name=c.get("school_name") or c.get("place_name") or "", topic_label=c.get("topic_label") or "",
                             sources_used=sorted({k["source_url"] for k in claims if k.get("source_url")}))
    with conn.cursor() as cur:
        cur.execute("UPDATE page_versions SET beat_review=(SELECT beat_review FROM page_versions WHERE id=%s) WHERE id=%s AND beat_review IS NULL", (version_id, new_vid))
    conn.commit()
    report["new_version_id"] = str(new_vid)
    need_verifier = facts_changed or bool(vc["hard_failures"]) or bool(vc["not_supported"]) or v["gate_status"] != "passed"
    if need_verifier:
        ver = stage_verify(conn, v["cluster_id"], version_id=new_vid, draft=draft2, claims=claims, det_findings=det2, runner=runner, log_path=log_path, run_id=run_id)
        conn = _db(conn)
        report["verify"] = {k: val for k, val in ver.items() if k != "claim_checks"} | {"not_supported": [cc for cc in (ver.get("claim_checks") or []) if cc.get("status") != "supported"]}
        gate_ok = ver["gate"]["status"] == "passed"
    else:
        rubric = {k: v["rubric"][k] for k in ("clarity", "specificity", "structure", "attribution", "usefulness", "prose")}
        g = gates.gate_version(conn, new_vid, det2, rubric)
        report["gate_carried"] = g.as_dict()
        gate_ok = g.passed
    report["outcome"] = "gate_passed" if gate_ok else "gate_failed"
    if gate_ok and publish:
        win = win_plan_for(conn, institution_id=v["institution_id"], place_id=v["place_id"], page_path=v["path"], primary_query=None) or (lean.synthetic_win_plan(conn, cluster_id=v["cluster_id"], page_path=v["path"]) if v.get("cluster_id") else None)
        sib = siblings if siblings is not None else [UUID(x) for x in _sibling_version_ids(conn, institution_id=v["institution_id"], place_id=v["place_id"], exclude_page_id=v["page_id"])]
        seo = stage_seo(conn, v["cluster_id"], version_id=new_vid, settings=settings, win_plan=win, sibling_version_ids=sib, runner=runner, log_path=log_path, run_id=run_id)
        conn = _db(conn)
        report["seo"] = {"passed": seo["seo_gate"]["passed"], "failed": seo["seo_gate"]["failed"], "agent": (seo.get("agent") or {}).get("status")}
        if seo["seo_gate"]["passed"]:
            from .adapters.cms import WordPressAdapter
            cms = WordPressAdapter.from_settings(settings)
            report["publish"] = stage_publish(conn, v["cluster_id"], version_id=new_vid, settings=settings, cms=cms if cms.capability().state in ("connected", "fixture") else None)
            report["outcome"] = "published" if report["publish"].get("published") else "publish_" + str(report["publish"].get("reason"))
        else:
            report["outcome"] = "seo_held"
    rp.write_text(json.dumps(report, indent=1, default=str))
    return report


def _sibling_version_ids(conn, *, institution_id, place_id, exclude_page_id) -> list[str]:
    with conn.cursor() as cur:
        cur.execute("""SELECT p.current_version_id FROM pages p JOIN page_versions v ON v.id=p.current_version_id WHERE p.institution_id IS NOT DISTINCT FROM %s AND p.place_id IS NOT DISTINCT FROM %s
                       AND p.id<>%s AND v.gate_status='passed' AND p.status NOT IN ('redirected','retired')""", (institution_id, place_id, exclude_page_id))
        return [str(r["current_version_id"]) for r in cur.fetchall()]


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
        from . import lean
        if lean.enabled() and not win:
            # no strategist win plan for most lean-mode clusters: the planner works from the claims and this minimal plan
            win = lean.synthetic_win_plan(conn, cluster_id=cluster_id, page_path=plan_path or lean.default_page_path(conn, cluster_id=cluster_id))
            plan_path = plan_path or win["page_path"]
        if lean.enabled() and not existing:
            covered = lean.covered_by_existing_page(conn, cluster_id=cluster_id)
            if covered:
                sweetspot.mark(conn, cluster_id, "done", f"covered by {covered} (an existing page carries this question; no duplicate page)")
                conn.commit()
                raise StageRefused(f"covered by existing page {covered}")
            if not plan_path:
                plan_path = lean.default_page_path(conn, cluster_id=cluster_id)
        if not plan_path:
            raise StageRefused("no page path: neither an existing page nor a strategy win plan names this cluster")
        if lean.enabled() and c.get("entity_id"):
            r = ensure_research(conn, cluster_id, settings=settings, runner=runner, log_path=log_path, run_id=run_id)
            conn = _db(conn)
            save("research", r)
        claims = claims_for_scope(conn, institution_id=c["institution_id"], topic_id=c["topic_id"], place_id=c["place_id"])
        competitors = competitors_for_cluster(conn, cluster_id)
        if not link_targets:
            link_targets = sibling_link_targets(conn, institution_id=c["institution_id"], place_id=c["place_id"], exclude_path=plan_path)
        report.update(page_path=plan_path, claims=len(claims), competitors=len(competitors), win_plan=bool(win))
        plan = stage_plan(conn, cluster_id, claims=claims, win_plan=win, competitors=competitors, page_path=plan_path, audience=audience or (existing or {}).get("audience") or c.get("audience"), notes=notes or [],
                          runner=runner, log_path=log_path, run_id=run_id)
        conn = _db(conn)
        save("plan", plan)
        if plan.get("status") != "ok" or not plan.get("page_id"):
            report["outcome"] = plan.get("status")
            return report
        with conn.cursor() as cur:
            cur.execute("SELECT id, path, audience, page_format FROM pages WHERE id=%s", (plan["page_id"],))
            page = dict(cur.fetchone())
        page["byline"] = byline
        sweetspot.mark(conn, cluster_id, "in_production", "R16 pipeline started (brief %s)" % plan["brief_id"][:8])  # the production lane must not restart it
        conn.commit()
        approved = {k["id"] for k in claims}
        crit = plan["critical_claim_ids"]
        rounds, draft, version_id, det = 0, None, None, []
        resend = None
        while True:
            rounds += 1
            w = stage_write(conn, cluster_id, page=page, brief_id=UUID(plan["brief_id"]), claims=claims, win_plan=win, notes=notes or [], link_targets=link_targets or [], prior_draft_path=prior_draft_path, resend=resend,
                            runner=runner, log_path=log_path, run_id=run_id)
            conn = _db(conn)
            save(f"write_r{rounds}", {k: v for k, v in w.items() if k != "draft"} | {"headline": (w.get("draft") or {}).get("headline")})
            if w.get("status") not in ("ok", "hold") or not w.get("draft"):
                report["outcome"] = "writer_" + str(w.get("status"))
                return report
            draft = dict(w["draft"], byline=byline)
            det = deterministic_findings(conn, institution_id=c["institution_id"], page_id=page["id"], draft=draft, critical_ids=crit, approved_ids=approved, academic_year="2026-27")
            save(f"checks_r{rounds}", {"findings": [f.as_dict() for f in det]})
            e = stage_edit(conn, cluster_id, draft=draft, det_findings=det, claims=claims, runner=runner, log_path=log_path, run_id=run_id)
            conn = _db(conn)
            save(f"edit_r{rounds}", {k: v for k, v in e.items() if k != "draft"})
            if e.get("status") in ("ok", "hold") and e.get("draft"):
                draft = auto_cite(dict(e["draft"], byline=byline), claims, page_audience=page.get("audience"))
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
            from . import lean
            if lean.enabled() and not lean.spot_check_due(lean.pages_produced(conn) - 1):
                # LEAN MODE: the competitor-beat review is a 1-in-10 spot check; this page gets the editor pass only
                with conn.cursor() as cur:
                    cur.execute("UPDATE page_versions SET beat_review=%s::jsonb WHERE id=%s", (json.dumps({"passed": None, "outcome": "lean_spot_check_skipped", "round": 0, "history": []}), version_id))
                conn.commit()
                save(f"beat_review_r{rounds}", {"status": "skipped", "outcome": "lean_spot_check_skipped", "passed": None})
                break
            round_no = quality.previous_round(conn, version_id) + 1
            b = stage_beat_review(conn, cluster_id, version_id=version_id, draft=draft, claims=claims, competitors=competitors, round_no=round_no, runner=runner, log_path=log_path, run_id=run_id)
            conn = _db(conn)
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
        conn = _db(conn)
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
    if len(argv) < 2 or argv[0] not in ("run", "publish", "verify", "correct"):
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
        elif argv[0] == "correct":
            out = correct(conn, UUID(argv[1]), settings=settings, log_path=log_path, run_id=run_id, publish="--no-publish" not in argv)
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
