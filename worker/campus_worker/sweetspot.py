"""Niche-first selection and the sweet-spot queue (continuous-local-run R20, R21, R22, R23; AT22).

Deterministic scoring from stored evidence:
  D   demand from recorded evidence points (R20): 0 none · 1 one occurrence · 2 repeated independent (≥2) ·
      3 measured demand (keyword export / Search Console row) · 4 measured + seasonality · 5 strong + first-party
  AGI from agi.py over the cluster's serp intel
  G   answer-gap estimate = AGI, +1 when an official result only partly answers (cap 5)
  E   evidence-advantage estimate from the source map of the cluster's scope/topic:
      0 no source · 2 search-observation-only sources · 3 ≥1 official fetch_permitted/public source family ·
      4 ≥2 independent official families · 5 structured data (api_authorized official API) available
  priority (SPEC §11) is still computed and stored for every cluster, but it is NOT the advance rule here (R22).
Sweet spot when D ≥ 2, AGI ≥ 3, G ≥ 3, E ≥ 3 and at least one result is weak or missing.
niche_score = (AGI + G) × E × min(D, 3); ties: seasonality urgency, then freshness risk.
Head terms with a strong dedicated incumbent (AGI ≤ 1) → watch. Navigational → reject (tagged).
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID

import psycopg

from . import agi as agimod
from .scoring import WEIGHTS

MIN_D, MIN_AGI, MIN_G, MIN_E = 2, 3, 3, 3


@dataclass
class ClusterScore:
    cluster_id: UUID
    d: int
    agi: int
    g: int
    e: int
    w: int
    niche_score: float
    decision: str              # sweet_spot | watch | reject | navigational | needs_intel
    reason: str
    priority: float | None
    best_variant: str | None
    weak_or_missing: bool


def demand_points(conn: psycopg.Connection, cluster_id: UUID) -> dict:
    """Count independent evidence points (R20). Each kind counts once per independent reference."""
    with conn.cursor() as cur:
        cur.execute("""SELECT origin, count(DISTINCT COALESCE(source_ref, id::text)) AS n FROM questions WHERE cluster_id=%s AND NOT is_hypothesis GROUP BY origin""", (cluster_id,))
        by_origin = {r["origin"]: int(r["n"]) for r in cur.fetchall()}
        cur.execute("SELECT count(*) AS n FROM demand_observations WHERE cluster_id=%s AND NOT is_suppressed AND volume_low IS NOT NULL", (cluster_id,))
        measured = cur.fetchone()["n"]
        cur.execute("SELECT count(*) AS n FROM demand_observations WHERE cluster_id=%s AND monthly_breakdown IS NOT NULL", (cluster_id,))
        seasonal = cur.fetchone()["n"]
    independent = sum(by_origin.values())
    first_party = by_origin.get("first_party", 0)
    return {"by_origin": by_origin, "independent": independent, "measured": int(measured), "seasonal": int(seasonal), "first_party": first_party}


def d_score(points: dict) -> int:
    if points["measured"] and points["first_party"]:
        return 5
    if points["measured"] and points["seasonal"]:
        return 4
    if points["measured"]:
        return 3
    if points["independent"] >= 2:
        return 2
    if points["independent"] == 1:
        return 1
    return 0


def e_estimate(conn: psycopg.Connection, *, institution_id: UUID | None, place_id: UUID | None, topic_id: UUID | None) -> tuple[int, str]:
    scope_col, scope_id = ("institution_id", institution_id) if institution_id else ("place_id", place_id)
    with conn.cursor() as cur:
        cur.execute(f"""SELECT p.access_mode, r.source_family FROM source_registry r LEFT JOIN source_permissions p ON p.id=r.permission_id
                        WHERE r.{scope_col}=%s AND r.health <> 'gone'""", (scope_id,))
        rows = cur.fetchall()
    fams_official = {r["source_family"] or "?" for r in rows if r["access_mode"] in ("fetch_permitted", "public_http", "feed", "export_import")}
    api = any(r["access_mode"] == "api_authorized" for r in rows)
    observe_only = any(r["access_mode"] == "search_observation" for r in rows)
    if api and fams_official:
        return 5, "structured data (official API) plus official page families"
    if len(fams_official) >= 2:
        return 4, f"{len(fams_official)} independent official source families"
    if fams_official:
        return 3, "one official source family: verifiable synthesis possible"
    if observe_only:
        return 2, "search-observation sources only"
    return 0, "no registered sources for this scope"


def latest_intel(conn: psycopg.Connection, cluster_id: UUID) -> dict | None:
    """Reassemble a serp_intel-shaped dict from the latest observations per variant."""
    with conn.cursor() as cur:
        cur.execute("""SELECT DISTINCT ON (query_text) query_text, results, direct_answer_quality, observed_at FROM serp_observations
                       WHERE cluster_id=%s ORDER BY query_text, observed_at DESC""", (cluster_id,))
        rows = cur.fetchall()
    if not rows:
        return None
    variants = []
    for r in rows:
        res = r["results"] if isinstance(r["results"], list) else json.loads(r["results"])
        variants.append({"query": r["query_text"], "results": res, "navigational": r["direct_answer_quality"] == "navigational_official"})
    return {"variants": variants, "observed_on": max(r["observed_at"] for r in rows).date().isoformat()}


def score_cluster(conn: psycopg.Connection, cluster_id: UUID, *, intel: dict | None = None) -> ClusterScore:
    with conn.cursor() as cur:
        cur.execute("SELECT institution_id, place_id, topic_id, seasonality_urgency, freshness_risk FROM intent_clusters WHERE id=%s", (cluster_id,))
        c = cur.fetchone()
    pts = demand_points(conn, cluster_id)
    d = d_score(pts)
    e, e_why = e_estimate(conn, institution_id=c["institution_id"], place_id=c["place_id"], topic_id=c["topic_id"])
    intel = intel or latest_intel(conn, cluster_id)
    if intel is None:
        with conn.cursor() as cur:
            cur.execute("SELECT hypothesis_count, independent_occurrences, queue_state, queue_reason FROM intent_clusters WHERE id=%s", (cluster_id,))
            h = cur.fetchone()
        if h["queue_state"] == "watch" and (h["queue_reason"] or "").startswith(("deferred:", "waiting for a second")):
            # the bounded sweep decided this cluster (R41 deferral / R20 single occurrence); scoring without new intel keeps that decision
            cs = ClusterScore(cluster_id, d, 0, 0, e, 0, 0.0, "watch", h["queue_reason"], None, None, False)
            return _persist(conn, cs, pts, {"e_why": e_why})
        if h["hypothesis_count"] > 0 or h["independent_occurrences"] >= 2:
            cs = ClusterScore(cluster_id, d, 0, 0, e, 0, 0.0, "needs_intel", "no search observations yet (R25: observe 2 variants first)", None, None, False)
        else:
            cs = ClusterScore(cluster_id, d, 0, 0, e, 0, 0.0, "watch", "single observed occurrence; waits for a second independent occurrence before search observation", None, None, False)
        return _persist(conn, cs, pts, {"e_why": e_why})
    a = agimod.compute(intel)
    g = min(5, a.agi + (1 if "partial_official" in (a.detail.get("weak_kinds") or sum((v.get("weak_kinds", []) for v in a.detail.get("variants", [])), [])) else 0))
    w = a.agi  # winnability tracks the authority gap (AGI feeds W and G)
    priority = round(20 * (WEIGHTS["demand"] * d + WEIGHTS["answer_gap"] * g + WEIGHTS["winnability"] * w + WEIGHTS["evidence_advantage"] * e + WEIGHTS["commercial"] * 0), 2)
    niche = float((a.agi + g) * e * min(d, 3))
    best_variant = min(intel["variants"], key=lambda v: agimod.compute_variant(v).agi)["query"] if intel.get("variants") else None
    if a.navigational:
        dec, why = "navigational", "pure navigational query (official navigational result); rejected (R21)"
    elif d >= MIN_D and a.agi >= MIN_AGI and g >= MIN_G and e >= MIN_E and a.weak_or_missing:
        dec, why = "sweet_spot", f"D={d} AGI={a.agi} G={g} E={e}; weak/missing result present; niche_score={niche:.0f}"
    elif a.agi <= 1:
        dec, why = "watch", f"strong dedicated incumbent (AGI={a.agi}); head term logged as watch"
    else:
        missing = [k for k, v, m in (("D", d, MIN_D), ("AGI", a.agi, MIN_AGI), ("G", g, MIN_G), ("E", e, MIN_E)) if v < m]
        dec = "watch" if (d >= 1 and a.agi >= 2) else "reject"
        why = f"below threshold on {', '.join(missing) or 'weak/missing-result condition'}: D={d} AGI={a.agi} G={g} E={e}"
    cs = ClusterScore(cluster_id, d, a.agi, g, e, w, niche, dec, why, priority, best_variant, a.weak_or_missing)
    return _persist(conn, cs, pts, {"e_why": e_why, "agi": a.detail})


def _persist(conn, cs: ClusterScore, pts: dict, detail: dict) -> ClusterScore:
    with conn.cursor() as cur:
        cur.execute(
            """UPDATE intent_clusters SET agi=%s, agi_detail=%s::jsonb, demand_points=%s, d_score=%s, g_est=%s, e_est=%s, niche_score=%s,
               queue_state=CASE WHEN queue_state IN ('in_production','done') THEN queue_state ELSE %s END, queue_reason=%s, best_variant=%s, updated_at=now() WHERE id=%s""",
            (cs.agi if cs.decision != "needs_intel" else None, json.dumps(dict(detail, demand=pts, priority=cs.priority), default=str), pts["independent"], cs.d, cs.g, cs.e,
             cs.niche_score if cs.decision != "needs_intel" else None, cs.decision, cs.reason, cs.best_variant, cs.cluster_id),
        )
    conn.commit()
    return cs


def score_all(conn: psycopg.Connection, *, institution_id: UUID | None = None, place_id: UUID | None = None) -> list[ClusterScore]:
    with conn.cursor() as cur:
        if institution_id:
            cur.execute("SELECT id FROM intent_clusters WHERE institution_id=%s", (institution_id,))
        elif place_id:
            cur.execute("SELECT id FROM intent_clusters WHERE place_id=%s", (place_id,))
        else:
            cur.execute("SELECT id FROM intent_clusters")
        ids = [r["id"] for r in cur.fetchall()]
    # each cluster commits on its own, so a dropped connection mid-sweep loses nothing: reconnect and retry that cluster once
    from .db import ensure_conn
    out: list[ClusterScore] = []
    for cid in ids:
        try:
            out.append(score_cluster(conn, cid))
        except psycopg.OperationalError:
            conn = ensure_conn(conn)
            out.append(score_cluster(conn, cid))
    return out


def queue(conn: psycopg.Connection, *, limit: int = 50, institution_id: UUID | None = None, place_id: UUID | None = None) -> list[dict]:
    """The sweet-spot queue: niche_score desc, then seasonality urgency, then freshness risk."""
    where = ["queue_state='sweet_spot'"]
    args: list = []
    if institution_id:
        where.append("institution_id=%s"); args.append(institution_id)
    if place_id:
        where.append("place_id=%s"); args.append(place_id)
    with conn.cursor() as cur:
        cur.execute(f"""SELECT c.id AS cluster_id, c.label, c.best_variant, c.d_score AS d, c.agi, c.g_est AS g, c.e_est AS e, c.niche_score, c.capture_format,
                               c.seasonality_urgency, c.freshness_risk, t.key AS topic_key, c.institution_id, c.place_id, c.entity_id
                        FROM intent_clusters c LEFT JOIN topics t ON t.id=c.topic_id WHERE {' AND '.join(where)}
                        ORDER BY c.niche_score DESC NULLS LAST, c.seasonality_urgency DESC, c.freshness_risk DESC, c.created_at LIMIT %s""", (*args, limit))
        return [dict(r) for r in cur.fetchall()]


def watch_list(conn: psycopg.Connection, *, limit: int = 50) -> list[dict]:
    with conn.cursor() as cur:
        cur.execute("""SELECT id AS cluster_id, label, best_variant, agi, d_score AS d, queue_reason FROM intent_clusters WHERE queue_state='watch'
                       ORDER BY d_score DESC NULLS LAST, created_at LIMIT %s""", (limit,))
        return [dict(r) for r in cur.fetchall()]


def mark(conn: psycopg.Connection, cluster_id: UUID, state: str, reason: str | None = None) -> None:
    with conn.cursor() as cur:
        cur.execute("UPDATE intent_clusters SET queue_state=%s, queue_reason=COALESCE(%s, queue_reason), updated_at=now() WHERE id=%s", (state, reason, cluster_id))
    conn.commit()


def apply_audience_rule(conn: psycopg.Connection, cluster_id: UUID) -> dict:
    """R33/AT45: an audience-specific cluster (parents, alumni, …) becomes its own page only when the audience-guide test
    finds differing rules/steps/facts; otherwise its capture format is 'section' on the shared page."""
    from .briefs import audience_guide_justified
    with conn.cursor() as cur:
        cur.execute("SELECT institution_id, topic_id, entity_id, audience FROM intent_clusters WHERE id=%s", (cluster_id,))
        c = cur.fetchone()
    if not c or not c["audience"] or not c["institution_id"] or not c["topic_id"]:
        return {"cluster_id": str(cluster_id), "audience": c["audience"] if c else None, "decision": "n/a", "reason": "no audience split or no school/topic"}
    ok, why = audience_guide_justified(conn, entity_id=c["entity_id"], institution_id=c["institution_id"], topic_id=c["topic_id"], audience=c["audience"])
    fmt = "guide" if ok else "section"
    with conn.cursor() as cur:
        cur.execute("UPDATE intent_clusters SET capture_format=%s, updated_at=now() WHERE id=%s", (fmt, cluster_id))
    conn.commit()
    return {"cluster_id": str(cluster_id), "audience": c["audience"], "decision": "separate_page" if ok else "merge_as_section", "capture_format": fmt, "reason": why}
