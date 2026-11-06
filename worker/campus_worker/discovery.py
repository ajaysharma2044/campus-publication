"""Question discovery, normalization, deduplication and clustering (SPEC §10).

- normalize(): lowercase, punctuation/stopword trimming, synonym folding that keeps the raw text.
- occurrence_key(): identifies the same underlying post/crosspost so five copies are one occurrence.
- cluster(): groups questions whose *answer* is the same (answer_key). Audience is part of the key
  only for topics where rules differ by audience (AUDIENCE_SPLIT_TOPICS); otherwise variations are
  merged and the audience list is kept on the cluster.
- generate_hypotheses(): bounded school × entity × audience × problem combinations, labeled
  is_hypothesis=True, never counted as observed demand.
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID

import psycopg

SYNONYMS = {
    r"\bdorms?\b": "residence hall",
    r"\bresidence halls?\b": "residence hall",
    r"\bres halls?\b": "residence hall",
    r"\ba/?c\b": "air conditioning",
    r"\bair[- ]conditioned\b": "air conditioning",
    r"\bfreshm[ae]n\b": "first-year",
    r"\bfirst[- ]years?\b": "first-year",
    r"\bfirst[- ]year students?\b": "first-year",
    r"\btransfers?\b": "transfer",
    r"\btransfer students?\b": "transfer",
    r"\bintl\b": "international",
    r"\bgrad students?\b": "graduate",
    r"\bcc\b": "community college",
    r"\bcommunity colleges?\b": "community college",
    r"\bcost|price|rate|fee\b": "cost",
    r"\bhow much (is|does|do|are)\b": "cost",
    r"\bwifi\b": "wi-fi",
}
STOPWORDS = {"the", "a", "an", "is", "are", "do", "does", "in", "at", "of", "for", "to", "i", "my", "me", "there", "any",
             "what", "which", "can", "you", "get", "with", "on", "and", "or", "it", "its", "be", "have", "has", "about", "like"}
AUDIENCE_MARKERS = {
    "transfer": ("transfer",), "international": ("international",), "graduate": ("graduate", "phd", "masters"),
    "first_year": ("first-year",), "parent": ("parent", "my son", "my daughter", "my kid"),
    "commuter": ("commute", "commuter", "commuting"), "adult_learner": ("adult learner", "working adult", "returning adult"),
}
# Topics where eligibility/steps differ by audience often enough that clusters split by audience.
AUDIENCE_SPLIT_TOPICS = {"housing": {"transfer", "graduate", "international", "first_year"},
                         "admissions": {"transfer", "international"}, "costs_aid": {"international", "graduate"},
                         "transfer": set()}


def normalize(text: str) -> str:
    t = text.lower().strip()
    t = re.sub(r"[’']", "", t)
    t = re.sub(r"[^a-z0-9\s/-]", " ", t)
    for pat, rep in SYNONYMS.items():
        t = re.sub(pat, rep, t)
    tokens = [w for w in t.split() if w not in STOPWORDS]
    return " ".join(tokens)


def detect_audience(text: str) -> str | None:
    n = normalize(text)
    for aud, markers in AUDIENCE_MARKERS.items():
        if any(m in n for m in markers):
            return aud
    return None


def occurrence_key(*, source_ref: str | None, normalized: str, origin: str, observed_at: datetime | None) -> str:
    """Same source_ref → same occurrence (crosspost/mirror). Otherwise same normalized text from the
    same origin on the same day is one occurrence, not many."""
    if source_ref:
        return "ref:" + hashlib.sha1(source_ref.encode()).hexdigest()[:16]
    day = observed_at.date().isoformat() if observed_at else "nodate"
    return "txt:" + hashlib.sha1(f"{origin}|{day}|{normalized}".encode()).hexdigest()[:16]


def answer_key(*, institution_id: UUID | None, topic_key: str | None, entity_id: UUID | None, normalized: str, audience: str | None) -> str:
    """Two questions share a cluster when the answer that resolves them is the same."""
    split = audience if (audience and topic_key and audience in AUDIENCE_SPLIT_TOPICS.get(topic_key, set())) else None
    tokens = set(normalized.split())
    if audience and not split:
        # audience does not change the answer for this topic: fold its marker words out of the key
        for m in AUDIENCE_MARKERS.get(audience, ()):
            tokens -= set(m.split())
        tokens -= {"students", "student"}
    core = " ".join(sorted(tokens))
    return hashlib.sha1(f"{institution_id}|{topic_key}|{entity_id}|{core}|{split}".encode()).hexdigest()[:20]


@dataclass
class QuestionInput:
    raw_text: str
    origin: str
    institution_id: UUID | None = None
    campus_id: UUID | None = None
    topic_key: str | None = None
    entity_id: UUID | None = None
    observed_at: datetime | None = None
    source_ref: str | None = None
    constraints: list[str] = field(default_factory=list)
    is_hypothesis: bool = False
    place_id: UUID | None = None          # town scope (continuous-local-run R34); institution_id stays None for town questions
    pattern_key: str | None = None        # R19: which pattern generated a hypothesis
    pattern_version: str | None = None


def _topic_id(cur, key: str | None) -> UUID | None:
    if not key:
        return None
    cur.execute("SELECT id FROM topics WHERE key=%s", (key,))
    r = cur.fetchone()
    return r["id"] if r else None


def ingest(conn: psycopg.Connection, items: list[QuestionInput]) -> dict:
    """Store questions, dedupe occurrences, attach to clusters. Returns counts."""
    out = {"stored": 0, "duplicate_occurrences": 0, "clusters_created": 0, "hypotheses": 0}
    with conn.cursor() as cur:
        for q in items:
            norm = normalize(q.raw_text)
            if not norm:
                continue
            aud = detect_audience(q.raw_text)
            occ = occurrence_key(source_ref=q.source_ref, normalized=norm, origin=q.origin, observed_at=q.observed_at)
            cur.execute("SELECT id FROM questions WHERE occurrence_key=%s AND institution_id IS NOT DISTINCT FROM %s AND place_id IS NOT DISTINCT FROM %s", (occ, q.institution_id, q.place_id))
            if cur.fetchone():
                out["duplicate_occurrences"] += 1
                continue
            tid = _topic_id(cur, q.topic_key)
            akey = answer_key(institution_id=q.institution_id or q.place_id, topic_key=q.topic_key, entity_id=q.entity_id, normalized=norm, audience=aud)
            cur.execute("SELECT id FROM intent_clusters WHERE answer_key=%s", (akey,))
            r = cur.fetchone()
            if r:
                cluster_id = r["id"]
            else:
                split_aud = aud if (aud and q.topic_key and aud in AUDIENCE_SPLIT_TOPICS.get(q.topic_key, set())) else None
                cur.execute(
                    """INSERT INTO intent_clusters (institution_id, campus_id, topic_id, entity_id, label, answer_key, audience, task, place_id, queue_state)
                       VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,'candidate') RETURNING id""",
                    (q.institution_id, q.campus_id, tid, q.entity_id, q.raw_text[:140], akey, split_aud, norm[:120], q.place_id),
                )
                cluster_id = cur.fetchone()["id"]
                out["clusters_created"] += 1
            cur.execute(
                """INSERT INTO questions (institution_id, campus_id, topic_id, entity_id, raw_text, normalized_text, origin, is_hypothesis,
                   audience, constraints, observed_at, source_ref, occurrence_key, cluster_id, place_id, pattern_key, pattern_version)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                (q.institution_id, q.campus_id, tid, q.entity_id, q.raw_text, norm, q.origin, q.is_hypothesis, aud, q.constraints,
                 q.observed_at, q.source_ref, occ, cluster_id, q.place_id, q.pattern_key, q.pattern_version),
            )
            if q.is_hypothesis:
                cur.execute("UPDATE intent_clusters SET hypothesis_count=hypothesis_count+1, updated_at=now() WHERE id=%s", (cluster_id,))
                out["hypotheses"] += 1
            else:
                cur.execute("UPDATE intent_clusters SET observed_count=observed_count+1, independent_occurrences=independent_occurrences+1, updated_at=now() WHERE id=%s", (cluster_id,))
            out["stored"] += 1
    conn.commit()
    return out


PROBLEMS_BY_TOPIC = {
    "housing": ["cost", "air conditioning", "eligibility", "roommate", "distance to classes", "deadline"],
    "transfer": ["which credits transfer", "articulation agreement", "application deadline", "gpa requirement"],
    "transportation": ["parking permit cost", "bus route", "commute time", "evening schedule"],
    "costs_aid": ["net cost", "fafsa deadline", "payment plan", "scholarship eligibility"],
    "programs": ["program length", "prerequisites", "job placement", "online option"],
}


def generate_hypotheses(conn: psycopg.Connection, *, institution_id: UUID, campus_id: UUID | None, topic_key: str,
                        entity_names: list[tuple[UUID | None, str]], audiences: list[str], limit: int = 40) -> dict:
    """Bounded exploratory combinations, labeled hypotheses. Skips topics not applicable to the school."""
    from .registry import topic_applicability

    if topic_applicability(conn, institution_id, topic_key) == "not_applicable":
        return {"stored": 0, "skipped_reason": "topic_not_applicable"}
    items = []
    for entity_id, name in entity_names or [(None, "")]:
        for prob in PROBLEMS_BY_TOPIC.get(topic_key, ["cost", "eligibility"]):
            for aud in (audiences or [None]):
                text = f"{name} {prob}".strip() + (f" for {aud.replace('_', ' ')} students" if aud else "")
                items.append(QuestionInput(raw_text=text, origin="hypothesis", institution_id=institution_id, campus_id=campus_id,
                                           topic_key=topic_key, entity_id=entity_id, is_hypothesis=True, source_ref=f"hyp:{text}"))
                if len(items) >= limit:
                    break
            if len(items) >= limit:
                break
        if len(items) >= limit:
            break
    res = ingest(conn, items)
    res["generated"] = len(items)
    return res


def cluster_summary(conn: psycopg.Connection, cluster_id: UUID) -> dict:
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM intent_clusters WHERE id=%s", (cluster_id,))
        c = dict(cur.fetchone())
        cur.execute("SELECT raw_text, origin, is_hypothesis, audience FROM questions WHERE cluster_id=%s ORDER BY created_at", (cluster_id,))
        c["questions"] = cur.fetchall()
    return c


# ---------------------------------------------------------------------------- open-ended discovery (continuous-local-run R46)
AUTO_TOPIC_MIN_INDEPENDENT = 3
_WORD = re.compile(r"[a-z][a-z-]+")
_SKIP = STOPWORDS | {"cornell", "ithaca", "university", "college", "student", "students", "how", "when", "where", "why", "is", "does", "do", "much", "many", "best", "good"}


def _topic_name_from_questions(texts: list[str]) -> tuple[str, str]:
    """Deterministic name: the most frequent 1–3 content words across the cluster's questions, in first-seen order."""
    counts: dict[str, int] = {}
    order: list[str] = []
    for t in texts:
        for w in _WORD.findall(normalize(t)):
            if w in _SKIP or len(w) < 3:
                continue
            if w not in counts:
                order.append(w)
            counts[w] = counts.get(w, 0) + 1
    top = sorted(order, key=lambda w: (-counts[w], order.index(w)))[:3]
    if not top:
        top = ["uncategorized"]
    key = "auto_" + "_".join(top)
    label = " ".join(top).capitalize() + " (auto-created)"
    return key[:60], label[:120]


def auto_create_topics(conn: psycopg.Connection, *, run_id: str | None = None, min_independent: int = AUTO_TOPIC_MIN_INDEPENDENT) -> list[dict]:
    """R46: a cluster with >= 3 independent observed questions and no topic becomes a new topic, named from its
    questions, logged as a digest event, and attached to the cluster and its questions. Idempotent."""
    created = []
    with conn.cursor() as cur:
        cur.execute(
            """SELECT c.id, c.institution_id, c.place_id, c.independent_occurrences FROM intent_clusters c
               WHERE c.topic_id IS NULL AND c.independent_occurrences >= %s ORDER BY c.created_at""", (min_independent,))
        clusters = cur.fetchall()
        for c in clusters:
            cur.execute("SELECT raw_text FROM questions WHERE cluster_id=%s AND NOT is_hypothesis ORDER BY created_at", (c["id"],))
            texts = [r["raw_text"] for r in cur.fetchall()]
            key, label = _topic_name_from_questions(texts)
            scope = "town" if (c["place_id"] and not c["institution_id"]) else "school"
            cur.execute(
                """INSERT INTO topics (key, label, description, sort_order, scope, auto_created, created_from, freshness_risk)
                   VALUES (%s,%s,%s,900,%s,TRUE,%s,'medium') ON CONFLICT (key) DO UPDATE SET label=topics.label RETURNING id, (xmax = 0) AS inserted""",
                (key, label, "auto-created from " + "; ".join(t[:80] for t in texts[:3]), scope, str(c["id"])),
            )
            r = cur.fetchone()
            cur.execute("UPDATE intent_clusters SET topic_id=%s, updated_at=now() WHERE id=%s", (r["id"], c["id"]))
            cur.execute("UPDATE questions SET topic_id=%s WHERE cluster_id=%s", (r["id"], c["id"]))
            if r["inserted"]:
                cur.execute("INSERT INTO digest_events (run_id, kind, detail) VALUES (%s,'topic_created',%s::jsonb)",
                            (run_id, __import__("json").dumps({"key": key, "label": label, "cluster_id": str(c["id"]), "questions": texts[:5], "independent": c["independent_occurrences"]})))
            created.append({"cluster_id": str(c["id"]), "topic_key": key, "label": label, "new": bool(r["inserted"])})
    conn.commit()
    return created
