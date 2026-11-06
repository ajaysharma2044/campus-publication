"""Authority Gap Index (continuous-local-run R21; AT21). Deterministic, computed from serp_intel results.

For the top 5 observed results of each variant each result is scored for strength in [0, 1]:
  dedicated page about exactly this question 0.35 · complete answer 0.30 · current 0.20 · evidence/sources 0.15
(partial answers earn half of "complete"; unknown freshness earns half of "current"; a result that is not dedicated to the
question is capped at 0.6 of its strength). Positions 4–5 are weighted 0.8.
AGI = round(5 × (1 − strongest weighted result)), clamped to 0–5:
  high when results are mostly forums, outdated pages, thin aggregators or partly-answering official pages;
  low when a dedicated, current, complete page already ranks.
Pure navigational queries (an official navigational result at position 1, or the variant flagged navigational) are
tagged navigational and rejected. AGI feeds W and G (sweetspot.py).
"""
from __future__ import annotations

from dataclasses import dataclass, field

W_DEDICATED, W_COMPLETE, W_CURRENT, W_SOURCED = 0.35, 0.30, 0.20, 0.15
NON_DEDICATED_CAP = 0.6
WEAK_TYPES = {"forum"}


@dataclass
class AgiResult:
    agi: int
    navigational: bool
    weak_or_missing: bool              # at least one weak result, or fewer than 5 results (R22 condition)
    strongest: float
    detail: dict = field(default_factory=dict)
    per_result: list[dict] = field(default_factory=list)


def result_strength(r: dict) -> float:
    s = 0.0
    if r.get("dedicated"):
        s += W_DEDICATED
    aq = r.get("answer_quality")
    if aq == "complete":
        s += W_COMPLETE
    elif aq == "partial":
        s += W_COMPLETE / 2
    fr = r.get("freshness")
    if fr == "current":
        s += W_CURRENT
    elif fr == "unknown":
        s += W_CURRENT / 2
    if r.get("evidence_quality") == "sourced":
        s += W_SOURCED
    if not r.get("dedicated"):
        s *= NON_DEDICATED_CAP  # a page that is not about exactly this question cannot be a strong incumbent
    return round(min(1.0, s), 3)


def is_weak(r: dict) -> tuple[bool, str | None]:
    t = r.get("result_type")
    if t in WEAK_TYPES:
        return True, "forum"
    if r.get("freshness") == "stale":
        return True, "outdated"
    if t == "aggregator" and r.get("answer_quality") != "complete":
        return True, "thin_aggregator"
    if t == "official" and r.get("answer_quality") == "partial":
        return True, "partial_official"
    if r.get("answer_quality") == "none":
        return True, "no_answer"
    return False, None


def compute_variant(variant: dict) -> AgiResult:
    results = sorted(variant.get("results") or [], key=lambda r: r.get("position", 99))[:5]
    nav = bool(variant.get("navigational"))
    if results and results[0].get("result_type") == "official" and results[0].get("answer_quality") == "navigational_official":
        nav = True
    per, strongest, weak_any, weak_kinds = [], 0.0, False, []
    for r in results:
        s = result_strength(r)
        w = 1.0 if r.get("position", 99) <= 3 else 0.8
        weak, kind = is_weak(r)
        weak_any = weak_any or weak
        if kind:
            weak_kinds.append(kind)
        per.append({"position": r.get("position"), "url": r.get("url"), "strength": s, "weighted": round(s * w, 3), "weak": weak, "weak_kind": kind, "type": r.get("result_type")})
        strongest = max(strongest, s * w)
    agi = max(0, min(5, int(5 * (1 - strongest) + 0.5)))  # half-up, never banker's rounding
    missing = len(results) < 5
    return AgiResult(agi=agi, navigational=nav, weak_or_missing=(weak_any or missing), strongest=round(strongest, 3),
                     detail={"results_seen": len(results), "weak_kinds": weak_kinds, "missing_results": missing, "nav_reason": "official navigational result at position 1" if nav else None},
                     per_result=per)


def compute(serp_intel: dict) -> AgiResult:
    """Cluster-level AGI = the minimum over variants (the most-answered variant bounds the gap); navigational if any variant is."""
    variants = serp_intel.get("variants") or []
    if not variants:
        return AgiResult(agi=0, navigational=False, weak_or_missing=False, strongest=1.0, detail={"error": "no variants"})
    per = [compute_variant(v) for v in variants]
    best = min(per, key=lambda a: a.agi)
    return AgiResult(agi=best.agi, navigational=any(a.navigational for a in per), weak_or_missing=any(a.weak_or_missing for a in per), strongest=max(a.strongest for a in per),
                     detail={"variants": [{"query": v.get("query"), "agi": a.agi, "navigational": a.navigational, **a.detail} for v, a in zip(variants, per)]},
                     per_result=[r for a in per for r in a.per_result])
