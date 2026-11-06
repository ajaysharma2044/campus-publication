"""Writing quality system (continuous-local-run R37, R38; AT37, AT38).

Information gain (R37): before drafting, the planner lists what the top 3 observed results already say and the brief
requires ≥ 3 verified, decision-relevant items none of them contain, each tied to a claim id; otherwise the cluster is
set to watch instead of producing a thinner copy.

Competitor-beat review (R38): after editing, a fresh editor dispatch (no drafting context) scores the draft 0–4 on six
items against the top 3 results: answers in the first 2 sentences, specificity, completeness, accuracy against sources,
scannability, local knowledge. The draft must beat every competitor on the total and score ≥ 3 on each item, or it goes
back to the writer once with the findings; a second failure holds the page. Runs in addition to the rubric and gates.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID

import psycopg

from . import sweetspot

MIN_GAIN_ITEMS = 3
BEAT_ITEMS = ("answers_first_two_sentences", "specificity", "completeness", "accuracy_against_sources", "scannability", "local_knowledge")
MIN_ITEM_SCORE = 3
MAX_RESENDS = 1


# ------------------------------------------------------------------------------------------------ information gain (R37)
@dataclass
class GainCheck:
    ok: bool
    items: list[dict]
    missing_claim_ids: list[str]
    reason: str


def check_information_gain(conn: psycopg.Connection, items: list[dict], *, competitors_say: list[dict] | None = None) -> GainCheck:
    """items: [{item, claim_id}]. Each claim id must exist and be a current verified_fact (or an estimate flagged as such is NOT enough)."""
    ids = [str(i.get("claim_id") or "") for i in items]
    valid: list[dict] = []
    missing: list[str] = []
    with conn.cursor() as cur:
        for it in items:
            cid = str(it.get("claim_id") or "")
            if not it.get("item") or not cid:
                missing.append(cid or "(no claim id)")
                continue
            try:
                cur.execute("SELECT evidence_category, superseded_by_id FROM claims WHERE id=%s::uuid", (cid,))
                r = cur.fetchone()
            except psycopg.Error:
                conn.rollback()
                r = None
            if r and r["evidence_category"] == "verified_fact" and r["superseded_by_id"] is None:
                valid.append(it)
            else:
                missing.append(cid)
    if len(valid) >= MIN_GAIN_ITEMS:
        return GainCheck(True, valid, missing, f"{len(valid)} verified, claim-linked items beyond the top 3 results")
    return GainCheck(False, valid, missing, f"only {len(valid)} verified claim-linked items (need {MIN_GAIN_ITEMS}); cluster set to watch instead of a thinner copy")


def apply_information_gain(conn: psycopg.Connection, cluster_id: UUID, items: list[dict], *, competitors_say: list[dict] | None = None,
                           version_id: UUID | None = None) -> GainCheck:
    g = check_information_gain(conn, items, competitors_say=competitors_say)
    if not g.ok:
        sweetspot.mark(conn, cluster_id, "watch", "R37 information gain: " + g.reason)
    if version_id:
        with conn.cursor() as cur:
            cur.execute("UPDATE page_versions SET information_gain=%s::jsonb WHERE id=%s",
                        (json.dumps({"ok": g.ok, "items": g.items, "competitors_say": competitors_say or [], "reason": g.reason}), version_id))
        conn.commit()
    return g


# ------------------------------------------------------------------------------------------------ competitor-beat review (R38)
@dataclass
class BeatReview:
    passed: bool
    our_scores: dict
    our_total: int
    competitors: list[dict]           # [{url, total, scores}]
    weakest_items: list[str]
    outcome: str                      # 'passed' | 'resend_to_writer' | 'held'
    round: int
    reason: str

    def as_dict(self) -> dict:
        return dict(self.__dict__, reviewed_at=datetime.now(timezone.utc).isoformat())


def score_review(our_scores: dict, competitors: list[dict], *, round_no: int) -> BeatReview:
    """Pure decision from the editor's scores. competitors: [{url, scores:{item:int}}]."""
    missing = [i for i in BEAT_ITEMS if i not in our_scores]
    if missing:
        return BeatReview(False, our_scores, 0, [], missing, "resend_to_writer" if round_no < 2 else "held", round_no, f"review incomplete: missing {missing}")
    ours = {k: int(our_scores[k]) for k in BEAT_ITEMS}
    total = sum(ours.values())
    comps = [{"url": c.get("url"), "scores": c.get("scores", {}), "total": sum(int(c.get("scores", {}).get(k, 0)) for k in BEAT_ITEMS)} for c in competitors]
    weak = [k for k in BEAT_ITEMS if ours[k] < MIN_ITEM_SCORE]
    beats_all = all(total > c["total"] for c in comps) if comps else True
    passed = beats_all and not weak
    if passed:
        return BeatReview(True, ours, total, comps, [], "passed", round_no, f"total {total} beats every competitor ({[c['total'] for c in comps]}); every item ≥ {MIN_ITEM_SCORE}")
    outcome = "resend_to_writer" if round_no < 1 + MAX_RESENDS else "held"
    why = []
    if not beats_all:
        why.append(f"total {total} does not beat every competitor ({[c['total'] for c in comps]})")
    if weak:
        why.append(f"items below {MIN_ITEM_SCORE}: {weak}")
    return BeatReview(False, ours, total, comps, weak, outcome, round_no, "; ".join(why))


def record_review(conn: psycopg.Connection, version_id: UUID, review: BeatReview) -> None:
    with conn.cursor() as cur:
        cur.execute("SELECT beat_review FROM page_versions WHERE id=%s", (version_id,))
        prev = (cur.fetchone() or {}).get("beat_review") or {}
        history = list(prev.get("history") or [])
        history.append(review.as_dict())
        cur.execute("UPDATE page_versions SET beat_review=%s::jsonb WHERE id=%s", (json.dumps({"passed": review.passed, "outcome": review.outcome, "round": review.round, "history": history}), version_id))
        if review.outcome == "held":
            cur.execute("UPDATE pages SET status='held', revalidation_reason=%s WHERE id=(SELECT page_id FROM page_versions WHERE id=%s) AND status<>'published'",
                        ("beat review failed twice: " + review.reason, version_id))
    conn.commit()


def previous_round(conn: psycopg.Connection, version_id: UUID) -> int:
    with conn.cursor() as cur:
        cur.execute("SELECT beat_review FROM page_versions WHERE id=%s", (version_id,))
        prev = (cur.fetchone() or {}).get("beat_review") or {}
    return int(prev.get("round") or 0)


def beat_review_packet_extra(draft_md: str, headline: str, claim_table: list[dict], competitors: list[dict]) -> dict:
    """What the fresh editor dispatch sees: the draft, the claim table and the top-3 competitor summaries — never the drafting conversation."""
    return {"mode": "beat_review", "items": list(BEAT_ITEMS), "scale": "0-4 per item", "headline": headline, "draft_markdown": draft_md[:12000],
            "claim_table": claim_table[:60], "competitors": [{"url": c.get("url"), "title": c.get("title"), "summary": (c.get("summary") or "")[:800]} for c in competitors[:3]],
            "rule": "score us and each competitor on every item; we must beat every competitor on the total and score ≥3 on each item"}
