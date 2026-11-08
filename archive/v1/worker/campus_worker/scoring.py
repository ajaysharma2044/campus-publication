"""Opportunity scoring and the page/section/tool/nothing decision (SPEC §11, §12).

Priority = 20 × (.25D + .25G + .20W + .20E + .10M), each 0–5 or None. If any component is None the
priority is None (unassessed) — never a silently imputed 0. Advance requires priority ≥ threshold
AND E ≥ 3 AND G ≥ 3, unless a documented editorial exception is recorded. These thresholds are
configurable hypotheses, not calibrated probabilities.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from uuid import UUID

import psycopg

ANCHORS = {
    "demand": {0: "no observed evidence", 1: "a single observed question", 2: "repeated independent questions",
               3: "measured demand from an authorized provider", 4: "measured demand with seasonality", 5: "strong demand with first-party corroboration"},
    "answer_gap": {0: "complete existing answer in inspected results", 1: "minor omissions", 2: "scattered partial answers",
                   3: "meaningful missing step or exception", 4: "answers outdated or conflicting", 5: "no adequate current answer"},
    "winnability": {0: "official result fully satisfies navigational intent", 1: "dominated by strong authoritative pages",
                    2: "mixed strong results", 3: "results thin or generic", 4: "weak, outdated results", 5: "no competent competing answer"},
    "evidence_advantage": {0: "no reliable evidence available", 1: "secondary evidence only", 2: "partial primary evidence",
                           3: "verifiable useful synthesis of primary sources", 4: "primary evidence plus original structure/tool",
                           5: "distinctive verified information or method"},
    "commercial": {0: "no commercial evidence", 1: "informational only", 2: "adjacent purchase decision",
                   3: "decision with spend implications", 4: "active comparison shopping", 5: "verified advertiser interest"},
}
WEIGHTS = {"demand": 0.25, "answer_gap": 0.25, "winnability": 0.20, "evidence_advantage": 0.20, "commercial": 0.10}
DEFAULT_THRESHOLD = 65.0
MIN_E = 3
MIN_G = 3
DECISIONS = ("advance", "update", "improve_section", "new_tool", "merge", "watch", "reject", "hold")


@dataclass
class Score:
    demand: int | None
    answer_gap: int | None
    winnability: int | None
    evidence_advantage: int | None
    commercial: int | None
    observations: dict[str, str] = field(default_factory=dict)  # per-component justification (required for non-null)
    confidence: str | None = None
    effort_research: int | None = None
    effort_build: int | None = None
    effort_maintain: int | None = None

    def validate(self) -> list[str]:
        errs = []
        for k in WEIGHTS:
            v = getattr(self, k)
            if v is not None and not (0 <= v <= 5):
                errs.append(f"{k} out of range")
            if v is not None and not self.observations.get(k):
                errs.append(f"{k} scored without an observation")
        return errs

    def priority(self) -> float | None:
        vals = {k: getattr(self, k) for k in WEIGHTS}
        if any(v is None for v in vals.values()):
            return None
        return round(20 * sum(WEIGHTS[k] * vals[k] for k in WEIGHTS), 2)


@dataclass
class Decision:
    decision: str
    rationale: str
    editorial_exception: bool = False
    exception_rationale: str | None = None
    existing_coverage_checked: list[UUID] = field(default_factory=list)


def decide(score: Score, *, threshold: float = DEFAULT_THRESHOLD, existing_coverage: list[UUID] | None = None,
           has_distinct_task: bool = True, has_sufficient_evidence: bool | None = None,
           exception: tuple[str, str] | None = None) -> Decision:
    """Deterministic decision from the score and coverage facts. `exception` = (decision, rationale)
    for a documented editorial override; it is recorded, never hidden in the score."""
    existing = existing_coverage or []
    p = score.priority()
    if exception:
        return Decision(exception[0], "editorial exception", True, exception[1], existing)
    if p is None:
        return Decision("hold", "unassessed component(s); score incomplete", existing_coverage_checked=existing)
    if (score.evidence_advantage or 0) < MIN_E or has_sufficient_evidence is False:
        return Decision("hold" if (score.answer_gap or 0) >= MIN_G else "watch",
                        f"evidence advantage {score.evidence_advantage} below {MIN_E}; research before drafting", existing_coverage_checked=existing)
    if existing and not has_distinct_task:
        return Decision("improve_section" if (score.answer_gap or 0) >= MIN_G else "update",
                        "existing coverage answers the same task; improve rather than duplicate", existing_coverage_checked=existing)
    if (score.answer_gap or 0) < MIN_G:
        return Decision("watch", f"answer gap {score.answer_gap} below {MIN_G}; existing results adequate", existing_coverage_checked=existing)
    if p >= threshold:
        return Decision("advance", f"priority {p} ≥ {threshold} with E={score.evidence_advantage}, G={score.answer_gap}", existing_coverage_checked=existing)
    if p >= threshold - 15:
        return Decision("watch", f"priority {p} below {threshold}; revisit when demand/evidence improves", existing_coverage_checked=existing)
    return Decision("reject", f"priority {p} well below {threshold}", existing_coverage_checked=existing)


def persist(conn: psycopg.Connection, cluster_id: UUID, score: Score, decision: Decision, *, scorer_model: str | None = None) -> UUID:
    errs = score.validate()
    if errs:
        raise ValueError("; ".join(errs))
    if decision.editorial_exception and not decision.exception_rationale:
        raise ValueError("editorial exception requires a rationale")
    with conn.cursor() as cur:
        cur.execute(
            """INSERT INTO opportunity_scores (cluster_id, demand, answer_gap, winnability, evidence_advantage, commercial, priority,
               confidence, effort_research, effort_build, effort_maintain, observations, decision, decision_rationale,
               editorial_exception, exception_rationale, existing_coverage_checked, scorer_model)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb,%s,%s,%s,%s,%s,%s) RETURNING id""",
            (cluster_id, score.demand, score.answer_gap, score.winnability, score.evidence_advantage, score.commercial, score.priority(),
             score.confidence, score.effort_research, score.effort_build, score.effort_maintain, json.dumps(score.observations),
             decision.decision, decision.rationale, decision.editorial_exception, decision.exception_rationale,
             decision.existing_coverage_checked, scorer_model),
        )
        oid = cur.fetchone()["id"]
        state = {"advance": "researching", "update": "stale", "improve_section": "partially_answered", "watch": "unknown",
                 "reject": "unknown", "hold": "unknown", "new_tool": "researching", "merge": "partially_answered"}[decision.decision]
        cur.execute("UPDATE intent_clusters SET coverage_state=%s, updated_at=now() WHERE id=%s", (state, cluster_id))
    conn.commit()
    return oid


def opportunity_queue(conn: psycopg.Connection, *, limit: int = 20) -> list[dict]:
    with conn.cursor() as cur:
        cur.execute(
            """SELECT DISTINCT ON (o.cluster_id) o.id, o.cluster_id, c.label, c.institution_id, o.priority, o.decision, o.scored_at
               FROM opportunity_scores o JOIN intent_clusters c ON c.id=o.cluster_id
               ORDER BY o.cluster_id, o.scored_at DESC""")
        rows = cur.fetchall()
    rows = [r for r in rows if r["decision"] in ("advance", "new_tool", "update", "improve_section")]
    rows.sort(key=lambda r: (-(r["priority"] or 0), r["scored_at"]))
    return rows[:limit]
