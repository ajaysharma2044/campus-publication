"""D5/D6: incumbent class and queue order for every question from CACHED search observations (14 days; at most the cluster's two
variants), never a new search here: bulk mode runs no search agent, so a question without a cached observation is 'unscanned'
and ordered after the ones with evidence. Underserved questions first (forum-only, outdated, none), then weak, then unscanned,
then strong incumbents; underserved audiences first within each tier. A one-line win note per question goes to the writer."""
from __future__ import annotations

import json
import re
from collections import Counter
from datetime import date, datetime, timezone
from urllib.parse import urlsplit
from uuid import UUID

import psycopg

from .. import search_cache
from ..seo_gate import STOP
from .questions import UNDERSERVED_AUDIENCES

COMMUNITY = ("reddit.com", "quora.com", "collegeconfidential.com", "youtube.com", "facebook.com", "tiktok.com", "niche.com", "unigo.com")
TIER = {"forum_only": 1, "outdated": 1, "none": 1, "weak": 2, "unscanned": 3, "strong_dedicated": 4}
CACHE_DAYS = 14


def _host(url: str | None) -> str:
    try:
        return (urlsplit(url or "").hostname or "").lower()
    except ValueError:
        return ""


def _year(r: dict) -> int | None:
    for k in ("date", "published", "freshness", "year"):
        v = r.get(k)
        if v:
            m = re.search(r"(20\d\d)", str(v))
            if m:
                return int(m.group(1))
    m = re.search(r"\b(20\d\d)\b", (r.get("title") or "") + " " + (r.get("snippet") or ""))
    return int(m.group(1)) if m else None


def _dedicated(r: dict, question: str) -> bool:
    words = [w for w in re.findall(r"[a-z0-9']+", question.lower()) if w not in STOP and len(w) > 2]
    text = ((r.get("title") or "") + " " + (r.get("url") or "")).lower()
    hit = sum(1 for w in words if w in text)
    return bool(words) and hit / len(words) >= 0.6


def classify(results: list[dict], *, question: str, official_domains: tuple[str, ...], today: date) -> tuple[str, dict]:
    top = [r for r in results[:10] if isinstance(r, dict)]
    if not top:
        return "unscanned", {"reason": "no cached observation"}
    community = [r for r in top[:5] if any(_host(r.get("url")).endswith(c) for c in COMMUNITY)]
    official = [r for r in top if any(_host(r.get("url")).endswith(d) for d in official_domains)]
    dedicated = [r for r in top[:5] if _dedicated(r, question) and not any(_host(r.get("url")).endswith(c) for c in COMMUNITY)]
    years = [y for y in (_year(r) for r in top[:5]) if y]
    detail = {"top_hosts": [_host(r.get("url")) for r in top[:5]], "community_in_top5": len(community), "official_in_top10": len(official), "dedicated_in_top5": len(dedicated), "years_top5": years}
    if len(community) >= 3 and not dedicated:
        return "forum_only", detail
    if dedicated:
        ded_years = [y for y in (_year(r) for r in dedicated) if y]
        if ded_years and max(ded_years) <= today.year - 2:
            return "outdated", detail
        if any(any(_host(r.get("url")).endswith(d) for d in official_domains) for r in dedicated[:3]):
            return "strong_dedicated", detail
        return "weak", detail
    if years and max(years) <= today.year - 2:
        return "outdated", detail
    if official:
        return "weak", detail
    return "none", detail


def win_note(cls: str, detail: dict, *, has_costs: bool, has_deadlines: bool, has_steps: bool) -> str:
    what = ", ".join(x for x, ok in (("the current fee table", has_costs), ("dated deadlines", has_deadlines), ("a step list", has_steps)) if ok) or "the dated official facts"
    hosts = ", ".join(detail.get("top_hosts", [])[:3]) or "no observed results"
    years = detail.get("years_top5") or []
    age = f" dated {min(years)}-{max(years)}" if years else ""
    lead = {"forum_only": f"Top results are forum threads{age} ({hosts})", "outdated": f"Top results are stale{age} ({hosts})", "none": f"No dedicated answer in the observed results ({hosts})",
            "weak": f"Only generic pages rank ({hosts})", "strong_dedicated": f"A dedicated official page already ranks ({hosts})", "unscanned": "No cached search observation yet"}[cls]
    return f"{lead}; we win with {what}."


PRACTICAL = (  # owner decision 2026-11-07: practical, high-traffic questions first; (rank, regex on question/answer key/topic/audience/page type)
    (0, r"\b(cost|costs|fee|fees|tuition|price|prices|rate|rates|how much|bill|billing|deposit)\b"),
    (0, r"\b(deadline|deadlines|when is|when are|due date|last day|what date|by when)\b"),
    (1, r"\b(how do i|how to|apply|application|process|steps|register|enroll|change my major|transfer credit|add/drop|add drop|leave of absence)\b"),
    (1, r"\b(dorm|dorms|residence hall|hall|housing|room|rooms|live on campus|roommate|move-in|move in)\b"),
    (2, r"\b(dining|meal plan|meal plans|eatery|cafe|dining hall|food)\b"),
    (2, r"\b(bus|tcat|transit|parking|commute|shuttle|bike|getting around|transportation)\b"),
    (1, r"\btransfer\b"),
    (2, r"\b(parent|parents|family|families)\b"),
)
PRACTICAL_TOPICS = {"costs_aid": 0, "parents_billing": 0, "admissions": 1, "housing": 1, "courses": 1, "dining": 2, "transportation": 2, "town_transit_local": 2, "town_transit_intercity": 2,
                    "transfer": 1, "parents_visitors": 2, "parents_calendar": 2, "parents_prep": 2, "parents_logistics": 2, "daily_life": 3}


def practical_rank(q: dict) -> int:
    """0 = costs/deadlines, 1 = how-to/dorms/transfer, 2 = dining/transit/parents, 3 = other practical topics, 5 = the rest."""
    text = " ".join(str(q.get(k) or "") for k in ("question", "answer_key", "page_type")).lower()
    aud = (q.get("audience") or "").lower()
    best = 5
    for rank, pat in PRACTICAL:
        if re.search(pat, text) or (rank == 1 and aud == "transfer") or (rank == 2 and aud == "parent"):
            best = min(best, rank)
    if q.get("page_type") == "process_guide":
        best = min(best, 1)
    best = min(best, PRACTICAL_TOPICS.get(q.get("topic_key") or "", 5))
    return best


def rank_all(conn: psycopg.Connection, *, institution_id: UUID, official_domains: tuple[str, ...] = ("cornell.edu",), today: date | None = None, practical_first: bool = True) -> dict:
    today = today or datetime.now(timezone.utc).date()
    with conn.cursor() as cur:
        cur.execute("""SELECT q.id, q.question, q.audience, q.cluster_id, q.entity_id, q.answer_key, q.incumbent_detail, q.page_type, t.key AS topic_key, c.best_variant, c.label, c.agi, c.d_score
                       FROM bulk_questions q LEFT JOIN topics t ON t.id=q.topic_id LEFT JOIN intent_clusters c ON c.id=q.cluster_id WHERE q.institution_id=%s AND q.status <> 'done'""", (institution_id,))
        qs = [dict(r) for r in cur.fetchall()]
        cur.execute("""SELECT entity_id, bool_or(value_type='money') AS costs, bool_or(value_date IS NOT NULL OR field LIKE 'deadline.%%') AS deadlines, bool_or(field LIKE 'process.%%') AS steps
                       FROM claims WHERE institution_id=%s AND superseded_by_id IS NULL GROUP BY entity_id""", (institution_id,))
        facts = {r["entity_id"]: r for r in cur.fetchall()}
    inst_facts = facts.get(None) or {"costs": False, "deadlines": False, "steps": False}
    classes = Counter()
    ranked = []
    for q in qs:
        queries = [q["question"]] + [x for x in (q.get("best_variant"), q.get("label")) if x and x != q["question"]]
        cached = search_cache.get_many(conn, queries[:3], days=CACHE_DAYS)
        results = []
        for c in cached.values():
            results = c.get("results") or results
            if results:
                break
        if not results and q.get("cluster_id"):
            with conn.cursor() as cur:
                cur.execute("SELECT results FROM serp_observations WHERE cluster_id=%s ORDER BY observed_at DESC LIMIT 1", (q["cluster_id"],))
                row = cur.fetchone()
                results = (row or {}).get("results") or []
        cls, detail = classify(results, question=q["question"], official_domains=official_domains, today=today)
        if q.get("agi") is not None and int(q["agi"]) <= 1 and cls in ("unscanned", "none", "weak"):
            cls, detail = "strong_dedicated", detail | {"agi": q["agi"]}
        f = facts.get(q.get("entity_id")) or inst_facts
        note = win_note(cls, detail, has_costs=bool(f.get("costs")), has_deadlines=bool(f.get("deadlines")), has_steps=bool(f.get("steps")))
        aud_rank = 0 if (q.get("audience") or "general") in UNDERSERVED_AUDIENCES else 1
        demand = float(q.get("d_score") or 0)
        pr = practical_rank(q) if practical_first else 0
        ranked.append((pr, TIER[cls], aud_rank, -demand, q["question"], q["id"], cls, detail, note))
        classes[cls] += 1
    ranked.sort(key=lambda t: t[:5])
    with conn.cursor() as cur:
        for i, (_pr, tier, _aud, _dem, _q, qid, cls, detail, note) in enumerate(ranked, start=1):
            cur.execute("UPDATE bulk_questions SET incumbent_class=%s, incumbent_detail=incumbent_detail || %s::jsonb, win_note=%s, tier=%s, order_rank=%s, updated_at=now() WHERE id=%s",
                        (cls, json.dumps(detail, default=str), note, tier, i, qid))
    conn.commit()
    return {"ranked": len(ranked), "by_class": dict(classes), "underserved_first": sum(1 for t in ranked if t[1] == 1), "practical_first": practical_first, "practical_0_2": sum(1 for t in ranked if t[0] <= 2)}
