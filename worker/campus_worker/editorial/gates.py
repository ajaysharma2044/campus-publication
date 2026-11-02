"""Publication gates and versioned drafts (SPEC §17).

Gate policy (configurable): every hard check passes; rubric total ≥ 20/24 with no dimension < 3.
Findings are persisted on the page_version. The rubric is a release rule, not proof of quality.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from uuid import UUID

import psycopg

from ..claims import blocking_claims
from .checks import Finding

RUBRIC_KEYS = ("clarity", "specificity", "structure", "attribution", "usefulness", "prose")
MIN_TOTAL = 20
MIN_EACH = 3
HARD_KINDS = {"unsupported_claim", "fabricated_consensus", "invented_quote", "fake_byline", "incorrect_arithmetic", "wrong_school",
              "superficial_duplicate", "empty", "unresolved_conflict", "missing_rights", "unsafe_code", "broken_interaction",
              "inaccessible_layout", "ads_obscure_task", "missing_privacy_behavior"}


@dataclass
class GateResult:
    passed: bool
    status: str                     # 'passed' | 'failed' | 'held'
    hard_failures: list[str] = field(default_factory=list)
    major_findings: list[str] = field(default_factory=list)
    rubric_total: int | None = None
    rubric_failures: list[str] = field(default_factory=list)
    blocking_claim_ids: list[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return self.__dict__.copy()


def evaluate(findings: list[Finding], rubric: dict | None, *, blocking: list[dict], novel_template: bool = False) -> GateResult:
    hard = [f"{f.kind}: {f.detail}" for f in findings if f.severity == "hard" or f.kind in HARD_KINDS]
    major = [f"{f.kind}: {f.detail}" for f in findings if f.severity == "major"]
    blocked = [str(b["id"]) for b in blocking]
    if blocked:
        hard.append(f"unresolved_conflict/stale critical claims: {blocked[:5]}")
    rubric_fail: list[str] = []
    total = None
    if rubric is not None:
        missing = [k for k in RUBRIC_KEYS if k not in rubric]
        if missing:
            rubric_fail.append(f"rubric missing {missing}")
        else:
            total = sum(int(rubric[k]) for k in RUBRIC_KEYS)
            if total < MIN_TOTAL:
                rubric_fail.append(f"rubric total {total} < {MIN_TOTAL}")
            low = [k for k in RUBRIC_KEYS if int(rubric[k]) < MIN_EACH]
            if low:
                rubric_fail.append(f"rubric below {MIN_EACH}: {low}")
    else:
        rubric_fail.append("no rubric recorded")
    if hard:
        return GateResult(False, "failed", hard, major, total, rubric_fail, blocked)
    if novel_template:
        return GateResult(False, "held", [], major, total, rubric_fail + ["novel template requires owner calibration"], blocked)
    if rubric_fail or len(major) >= 3:
        return GateResult(False, "failed", [], major, total, rubric_fail or ["three or more major findings"], blocked)
    return GateResult(True, "passed", [], major, total, [], blocked)


def content_hash(headline: str, deck: str | None, body_md: str, structured: dict) -> str:
    return hashlib.sha256(json.dumps({"h": headline, "d": deck, "b": body_md, "s": structured}, sort_keys=True).encode()).hexdigest()


def create_version(conn: psycopg.Connection, page_id: UUID, *, brief_id: UUID | None, headline: str, deck: str | None, body_md: str,
                   body_html: str | None, structured: dict, byline: str, production_note: str, claim_ids: list[UUID],
                   writer_model: str | None, editor_model: str | None, verifier_model: str | None, change_summary: str | None = None,
                   is_material_change: bool = True) -> UUID:
    h = content_hash(headline, deck, body_md, structured)
    with conn.cursor() as cur:
        cur.execute("SELECT COALESCE(MAX(version_no),0)+1 AS v FROM page_versions WHERE page_id=%s", (page_id,))
        v = cur.fetchone()["v"]
        cur.execute("SELECT content_hash FROM page_versions WHERE page_id=%s ORDER BY version_no DESC LIMIT 1", (page_id,))
        prev = cur.fetchone()
        if prev and prev["content_hash"] == h:
            cur.execute("SELECT id FROM page_versions WHERE page_id=%s ORDER BY version_no DESC LIMIT 1", (page_id,))
            conn.commit()
            return cur.fetchone()["id"]  # identical content: no new version
        cur.execute(
            """INSERT INTO page_versions (page_id, version_no, brief_id, headline, deck, body_markdown, body_html, structured, byline, production_note,
               content_hash, writer_model, editor_model, verifier_model, is_material_change, change_summary)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s::jsonb,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id""",
            (page_id, v, brief_id, headline, deck, body_md, body_html, json.dumps(structured), byline, production_note, h,
             writer_model, editor_model, verifier_model, is_material_change, change_summary),
        )
        vid = cur.fetchone()["id"]
        for cid in set(claim_ids):
            cur.execute("INSERT INTO page_claims (page_version_id, claim_id, usage) VALUES (%s,%s,'prose') ON CONFLICT DO NOTHING", (vid, cid))
            cur.execute("""INSERT INTO dependencies (upstream_type, upstream_id, downstream_type, downstream_id) VALUES ('claim',%s,'page',%s)
                           ON CONFLICT DO NOTHING""", (cid, page_id))
        cur.execute("UPDATE pages SET status = CASE WHEN status='planned' THEN 'drafting' ELSE status END WHERE id=%s", (page_id,))
    conn.commit()
    return vid


def record_gate(conn: psycopg.Connection, version_id: UUID, findings: list[Finding], rubric: dict | None, result: GateResult) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """UPDATE page_versions SET gate_status=%s, gate_findings=%s::jsonb, rubric=%s::jsonb WHERE id=%s""",
            (result.status, json.dumps([f.as_dict() for f in findings] + [{"kind": "gate", "severity": "info", "detail": json.dumps(result.as_dict())}]),
             json.dumps(dict(rubric or {}, total=result.rubric_total)), version_id),
        )
        cur.execute("SELECT page_id FROM page_versions WHERE id=%s", (version_id,))
        page_id = cur.fetchone()["page_id"]
        if result.passed:
            cur.execute("UPDATE pages SET current_version_id=%s, status=CASE WHEN status IN ('planned','drafting','held') THEN 'staged' ELSE status END, revalidation_required=FALSE, revalidation_reason=NULL WHERE id=%s", (version_id, page_id))
        elif result.status == "held":
            cur.execute("UPDATE pages SET status='held' WHERE id=%s AND status IN ('planned','drafting')", (page_id,))
    conn.commit()


def gate_version(conn: psycopg.Connection, version_id: UUID, findings: list[Finding], rubric: dict | None, *, novel_template: bool = False) -> GateResult:
    with conn.cursor() as cur:
        cur.execute("SELECT claim_id FROM page_claims WHERE page_version_id=%s", (version_id,))
        claim_ids = [r["claim_id"] for r in cur.fetchall()]
    blocking = blocking_claims(conn, claim_ids)
    result = evaluate(findings, rubric, blocking=blocking, novel_template=novel_template)
    record_gate(conn, version_id, findings, rubric, result)
    return result
