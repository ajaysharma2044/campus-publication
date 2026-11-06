"""Coordinator side of search intelligence (continuous-local-run R13, R15, R20, R26, R36; AT12, AT24, AT36).

run_cluster(): build the packet (variants + cached observations), dispatch the search-intel agent only when at least one
variant is NOT cached, then ingest its serp_intel output: observations → serp_observations + serp_cache, follow-up
questions and community occurrences → observed questions (demand evidence, R20), search calls → ledger. Inside the
cache window a repeat run makes zero search calls and zero dispatches (R26).
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from uuid import UUID

import psycopg

from . import search_cache
from .adapters.search import store_serp_observation
from .agents import dispatch as dsp
from .discovery import QuestionInput, ingest

LABEL = "observed via search tool on "


def variants_for_cluster(conn: psycopg.Connection, cluster_id: UUID, *, max_variants: int = 2) -> list[str]:
    """2 variants (R13, R25): the best observed wording first, then the top hypothesis wording; fallback to the label."""
    with conn.cursor() as cur:
        cur.execute("SELECT label, best_variant FROM intent_clusters WHERE id=%s", (cluster_id,))
        c = cur.fetchone()
        cur.execute("""SELECT raw_text, is_hypothesis, count(*) OVER (PARTITION BY normalized_text) AS n FROM questions WHERE cluster_id=%s
                       ORDER BY is_hypothesis, n DESC, created_at""", (cluster_id,))
        rows = cur.fetchall()
    out: list[str] = []
    for r in rows:
        t = r["raw_text"].strip()
        if t and t.lower() not in {o.lower() for o in out}:
            out.append(t)
        if len(out) >= max_variants:
            break
    if not out and c:
        out = [c["best_variant"] or c["label"]]
    return out[:max_variants]


def build_packet(conn: psycopg.Connection, cluster_id: UUID, *, run_id: str, cache_days: int, place_subs: list[str] | None = None, now: datetime | None = None) -> tuple[dict, list[str], dict[str, dict]]:
    variants = variants_for_cluster(conn, cluster_id)
    cached = search_cache.get_many(conn, variants, days=cache_days, now=now)
    with conn.cursor() as cur:
        cur.execute("""SELECT c.label, c.institution_id, c.place_id, t.key AS topic_key, c.entity_id FROM intent_clusters c LEFT JOIN topics t ON t.id=c.topic_id WHERE c.id=%s""", (cluster_id,))
        c = cur.fetchone()
    packet = dsp.build_packet(
        task_id=f"intel:{str(cluster_id)[:8]}", run_id=run_id, objective=f"Search intelligence for cluster '{c['label']}' (R13): observe the 2 variants below (up to 10 results each), "
        f"follow-up questions, community occurrences incl. site:reddit.com searches for {', '.join(place_subs or ['r/Cornell', 'r/ithaca'])}, seasonality. Reuse cached queries; never re-search them.",
        input_ids=[str(cluster_id)], institution_id=str(c["institution_id"]) if c["institution_id"] else None, place_id=str(c["place_id"]) if c["place_id"] else None,
        constraints=["label every observation 'observed via search tool on <date>'", "no Google scraping, no autocomplete, no paid tools",
                     "community sites: titles, URLs, dates, snippets only (search_observation)", f"cached queries (do not search): {sorted(cached)}"],
        extra={"cluster_id": str(cluster_id), "topic_key": c["topic_key"], "variants": variants,
               "cached_queries": {q: {"observed_at": r["observed_at"].isoformat(), "results": r["results"]} for q, r in cached.items()}},
    )
    return packet, variants, cached


def ingest_intel(conn: psycopg.Connection, cluster_id: UUID, intel: dict, *, cached: dict[str, dict], now: datetime | None = None) -> dict:
    """Persist a serp_intel output: observations, cache, demand evidence, ledger search calls."""
    now = now or datetime.now(timezone.utc)
    observed_on = intel.get("observed_on") or now.date().isoformat()
    label = intel.get("label") or (LABEL + observed_on)
    stored_obs = 0
    demand_items: list[QuestionInput] = []
    with conn.cursor() as cur:
        cur.execute("SELECT institution_id, place_id, campus_id, entity_id, t.key AS topic_key FROM intent_clusters c LEFT JOIN topics t ON t.id=c.topic_id WHERE c.id=%s", (cluster_id,))
        c = cur.fetchone()
    for v in intel.get("variants") or []:
        q = v.get("query") or ""
        results = (v.get("results") or [])[:10]
        was_cached = q in cached
        if not was_cached:
            search_cache.store(conn, q, results=results, follow_up_questions=v.get("follow_up_questions") or [], community_occurrences=v.get("community_occurrences") or [],
                               navigational=bool(v.get("navigational")), observed_at=now)
            search_cache.record_search_call(conn, q, cached=False, cluster_id=cluster_id)
        else:
            search_cache.record_search_call(conn, q, cached=True, cluster_id=cluster_id)
        dq = "navigational_official" if v.get("navigational") else _direct_answer_quality(results)
        missing = next((r.get("missing_contribution") for r in results if r.get("missing_contribution")), None)
        store_serp_observation(conn, cluster_id, query_text=q, locale="en-US", device="desktop", results=[dict(r, label=label) for r in results],
                               direct_answer_quality=dq, missing_contribution=missing, provider=label, observed_at=now)
        stored_obs += 1
        for fq in v.get("follow_up_questions") or []:
            demand_items.append(QuestionInput(raw_text=fq, origin="related_question", institution_id=c["institution_id"], campus_id=c["campus_id"], place_id=c["place_id"],
                                              topic_key=c["topic_key"], entity_id=c["entity_id"], observed_at=now, source_ref=f"search:{observed_on}:{q}:paa:{fq[:60]}"))
        for occ in v.get("community_occurrences") or []:
            demand_items.append(QuestionInput(raw_text=occ.get("title") or q, origin="discussion", institution_id=c["institution_id"], campus_id=c["campus_id"], place_id=c["place_id"],
                                              topic_key=c["topic_key"], entity_id=c["entity_id"], observed_at=_parse_date(occ.get("date"), now),
                                              source_ref=f"search:{occ.get('site', 'web')}:{occ.get('url')}", constraints=[f"site:{occ.get('site', '')}", "search_observation"]))
    for ev in intel.get("demand_evidence") or []:
        if ev.get("kind") in ("official_faq", "keyword_export", "search_console"):
            demand_items.append(QuestionInput(raw_text=ev.get("query") or "", origin={"official_faq": "official_faq", "keyword_export": "search_suggestion", "search_console": "search_console"}[ev["kind"]],
                                              institution_id=c["institution_id"], campus_id=c["campus_id"], place_id=c["place_id"], topic_key=c["topic_key"], entity_id=c["entity_id"],
                                              observed_at=now, source_ref=f"evidence:{ev['kind']}:{ev.get('ref')}"))
    demand = ingest(conn, demand_items) if demand_items else {"stored": 0, "duplicate_occurrences": 0}
    with conn.cursor() as cur:
        cur.execute("UPDATE intent_clusters SET last_intel_at=%s, queue_state=CASE WHEN queue_state IN ('needs_intel','candidate') THEN 'candidate' ELSE queue_state END, updated_at=now() WHERE id=%s", (now, cluster_id))
    conn.commit()
    return {"observations": stored_obs, "demand_evidence_stored": demand["stored"], "demand_duplicates": demand.get("duplicate_occurrences", 0),
            "search_calls_reported": intel.get("search_calls_made"), "label": label}


def _direct_answer_quality(results: list[dict]) -> str | None:
    if not results:
        return "none"
    qualities = [r.get("answer_quality") for r in results[:5]]
    if "complete" in qualities:
        return "complete"
    if "partial" in qualities:
        return "partial"
    return "none"


def _parse_date(s: str | None, default: datetime) -> datetime:
    if not s:
        return default
    for fmt in ("%Y-%m-%d", "%Y-%m", "%Y"):
        try:
            return datetime.strptime(s, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return default


def run_cluster(conn: psycopg.Connection, cluster_id: UUID, *, settings, runner=dsp.cli_runner, run_id: str | None = None, log_path=None,
                place_subs: list[str] | None = None, now: datetime | None = None) -> dict:
    """R26: skip the dispatch entirely when every variant is cached (zero search calls); otherwise dispatch search-intel and ingest."""
    agents = dsp.load_agents()
    packet, variants, cached = build_packet(conn, cluster_id, run_id=run_id or "adhoc", cache_days=settings.quotas.serp_cache_days, place_subs=place_subs, now=now)
    if variants and all(v in cached for v in variants):
        for v in variants:
            search_cache.record_search_call(conn, v, cached=True, cluster_id=cluster_id)
        intel = {"cluster_id": str(cluster_id), "observed_on": max(r["observed_at"] for r in cached.values()).date().isoformat(), "variants":
                 [{"query": v, "results": cached[v]["results"], "follow_up_questions": cached[v].get("follow_up_questions") or [], "navigational": cached[v].get("navigational", False)} for v in variants]}
        with conn.cursor() as cur:
            cur.execute("UPDATE intent_clusters SET last_intel_at=now(), updated_at=now() WHERE id=%s", (cluster_id,))
        conn.commit()
        return {"status": "cached", "dispatched": False, "variants": variants, "intel": intel, "search_calls": 0}
    res = dsp.dispatch(agents["search-intel"], packet, runner=runner, conn=conn, log_path=log_path)
    if res.status not in ("ok", "hold") or not res.doc:
        return {"status": res.status, "dispatched": True, "errors": res.errors, "variants": variants}
    intel = res.doc.get("output") or {}
    ing = ingest_intel(conn, cluster_id, intel, cached=cached, now=now)
    return {"status": "ok", "dispatched": True, "variants": variants, "intel": intel, "ingest": ing, "search_calls": ing["search_calls_reported"]}


def rank_recheck_packet(conn: psycopg.Connection, page_id: UUID, *, run_id: str) -> dict:
    """R15: the analyst re-runs R13 for a published page's target variants and records whether our page appears."""
    with conn.cursor() as cur:
        cur.execute("SELECT path FROM pages WHERE id=%s", (page_id,))
        path = cur.fetchone()["path"]
        cur.execute("SELECT query_norm FROM query_targets WHERE page_path=%s ORDER BY is_primary DESC", (path,))
        queries = [r["query_norm"] for r in cur.fetchall()]
    return dsp.build_packet(task_id=f"recheck:{str(page_id)[:8]}", run_id=run_id, objective=f"Rank re-check (R15) for {path}: observe each target variant and record whether our page appears (position or absent). Label 'observed via search tool on <date>'. No causal claims.",
                            input_ids=[str(page_id)], extra={"page_path": path, "variants": queries[:4]})


# ---------------------------------------------------------------------------------------------- batch mode (R27, R41)
def run_batch(conn: psycopg.Connection, cluster_ids: list[UUID], *, settings, runner=dsp.cli_runner, run_id: str | None = None, log_path=None,
              place_subs: list[str] | None = None, now: datetime | None = None, max_turns: int | None = None) -> dict:
    """One search-intel dispatch for up to 25 clusters. Clusters whose variants are all cached are served from the cache
    and excluded from the packet (zero search calls for them). The agent returns {"batch": [serp_intel, ...]}."""
    if not cluster_ids:
        return {"status": "empty", "dispatched": False, "results": {}}
    if len(cluster_ids) > 25:
        raise ValueError("batch size is at most 25 (R27/R41)")
    agents = dsp.load_agents()
    items, cached_by, results = [], {}, {}
    for cid in cluster_ids:
        packet, variants, cached = build_packet(conn, cid, run_id=run_id or "adhoc", cache_days=settings.quotas.serp_cache_days, place_subs=place_subs, now=now)
        if variants and all(v in cached for v in variants):
            for v in variants:
                search_cache.record_search_call(conn, v, cached=True, cluster_id=cid)
            with conn.cursor() as cur:
                cur.execute("UPDATE intent_clusters SET last_intel_at=now(), updated_at=now() WHERE id=%s", (cid,))
            conn.commit()
            results[str(cid)] = {"status": "cached", "variants": variants}
            continue
        cached_by[str(cid)] = cached
        items.append({"cluster_id": str(cid), "label": packet["objective"].split("'")[1] if "'" in packet["objective"] else "", "topic_key": packet.get("topic_key"),
                      "variants": variants, "cached_queries": packet.get("cached_queries", {}), "institution_id": packet.get("institution_id"), "place_id": packet.get("place_id")})
    if not items:
        return {"status": "cached", "dispatched": False, "results": results, "search_calls": 0}
    packet = dsp.build_packet(
        task_id=f"intel-batch:{str(cluster_ids[0])[:8]}+{len(items)}", run_id=run_id or "adhoc",
        objective=(f"Search intelligence (R13) for {len(items)} clusters in ONE pass. For each cluster observe its listed variants (up to 10 results each), "
                   f"record follow-up questions, community occurrences incl. site:reddit.com searches for {', '.join(place_subs or ['r/Cornell', 'r/ithaca'])}, and seasonality. "
                   "Reuse cached queries; never re-search them. Return output = {\"batch\": [one serp_intel object per cluster, cluster_id as given]}."),
        input_ids=[str(c) for c in cluster_ids],
        constraints=["label every observation 'observed via search tool on <date>'", "no Google scraping, no autocomplete, no paid tools",
                     "community sites: titles, URLs, dates, snippets only (search_observation)", "skip nothing: every cluster in the packet gets an object, even with empty results"],
        extra={"clusters": items, "batch_mode": True},
    )
    spec = agents["search-intel"]
    if max_turns:
        from dataclasses import replace
        spec = replace(spec, max_turns=max_turns)
    res = dsp.dispatch(spec, packet, runner=runner, conn=conn, log_path=log_path)
    if res.status not in ("ok", "hold") or not res.doc:
        return {"status": res.status, "dispatched": True, "errors": res.errors, "results": results}
    out = res.doc.get("output") or {}
    batch = out.get("batch") if isinstance(out, dict) and "batch" in out else [out]
    by_id = {str(b.get("cluster_id")): b for b in batch if isinstance(b, dict)}
    missing = []
    for it in items:
        cid = it["cluster_id"]
        intel = by_id.get(cid)
        if not intel:
            missing.append(cid)
            continue
        ing = ingest_intel(conn, UUID(cid), intel, cached=cached_by.get(cid, {}), now=now)
        results[cid] = {"status": "ok", "ingest": ing}
    return {"status": "ok" if not missing else "partial", "dispatched": True, "results": results, "missing": missing,
            "search_calls": out.get("search_calls_made") if isinstance(out, dict) else None, "turns": res.turns, "duration_s": res.duration_s}
