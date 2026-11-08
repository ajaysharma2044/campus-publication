"""Stage 5: one cheaper verification request per page confirms each remaining claim against its quote; claims marked wrong are
removed with the sentences that used them; then the page is rendered to build/site/ through the existing version/publish path."""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from uuid import UUID

import psycopg

from .. import pipeline
from ..cms import publisher
from ..editorial import gates
from .batch_client import BatchRequest
from .check import _sentences
from .util import parse_json_object, slugify

MAX_OUTPUT_TOKENS = 1_500
VERIFY_SYSTEM = """You verify a short reference page against its sources. For each CLAIM you get the exact quote from the official page and the sentence of the page that relies on it. Decide, strictly from the quote:
- "supported": the sentence states only what the quote states (same number, date, rule, scope and audience);
- "unsupported": the sentence says something the quote does not (a different number, a broader scope, an added condition, a different audience) or the quote is about something else.
Return ONE JSON object: {"verdicts": [{"claim_id": "...", "verdict": "supported|unsupported", "note": "<= 20 words"}]} with one entry per claim id, nothing else."""


def build_request(bulk_page: dict, *, model: str) -> BatchRequest:
    d = bulk_page["draft"]
    items = "\n".join(f"CLAIM {c['claim_id']}\n  quote: \"{c['quote']}\"\n  sentence: \"{(c.get('used_for') or '')[:400]}\"" for c in d.get("claims") or [])
    user = f"PAGE: {d.get('h1')}\nANSWER: {d.get('answer')}\n\n{items}\n"
    return BatchRequest(custom_id=f"verify:{bulk_page['id']}", model=model, system=VERIFY_SYSTEM, user=user, max_tokens=MAX_OUTPUT_TOKENS, temperature=0.0)


def apply_verdicts(draft: dict, verdict_text: str | None) -> tuple[dict, dict]:
    doc = parse_json_object(verdict_text or "") or {}
    verdicts = {str(v.get("claim_id")): v for v in (doc.get("verdicts") or []) if isinstance(v, dict)}
    report = {"verdicts": verdicts, "removed": [], "parsed": bool(doc)}
    if not doc:
        report["removed"] = [c["claim_id"] for c in draft.get("claims") or []]
        draft["claims"] = []
        return draft, report
    bad = {cid for cid, v in verdicts.items() if (v.get("verdict") or "").lower() != "supported"}
    bad_sentences = [c.get("used_for") or "" for c in draft.get("claims") or [] if c["claim_id"] in bad and c.get("used_for")]
    draft["claims"] = [c for c in draft.get("claims") or [] if c["claim_id"] not in bad]
    report["removed"] = sorted(bad)
    if bad_sentences:
        def strip(text: str) -> str:
            return " ".join(s for s in _sentences(text) if not any(_same(s, b) for b in bad_sentences))
        draft["answer"] = strip(draft.get("answer") or "")
        for sec in draft.get("sections") or []:
            sec["body_md"] = "\n\n".join(p for p in (strip(para) if not para.lstrip().startswith(("-", "*", "1.")) else "\n".join(l for l in para.split("\n") if not any(_same(l, b) for b in bad_sentences)) for para in (sec.get("body_md") or "").split("\n\n")) if p.strip())
        draft["sections"] = [s for s in draft.get("sections") or [] if s.get("body_md", "").strip()]
        if draft.get("table"):
            draft["table"]["rows"] = [r for r in draft["table"].get("rows") or [] if r.get("claim_id") not in bad]
    return draft, report


def _same(a: str, b: str) -> bool:
    na, nb = re.sub(r"\W+", " ", a.lower()).strip(), re.sub(r"\W+", " ", b.lower()).strip()
    return bool(na) and bool(nb) and (na == nb or na in nb or nb in na)


def body_markdown(draft: dict) -> str:
    parts = [draft["answer"].strip(), ""]
    placed_table = False
    for sec in draft.get("sections") or []:
        parts += [f"## {sec['heading'].strip()}", "", sec["body_md"].strip(), ""]
        if draft.get("table") and not placed_table and any(k in sec["heading"].lower() for k in ("cost", "rate", "price", "glance", "deadline", "date", "fee", "compar")):
            parts += ["[[fact-table]]", ""]
            placed_table = True
    if draft.get("table") and not placed_table:
        parts += ["[[fact-table]]", ""]
    if draft.get("steps"):
        parts += ["## Steps", ""] + [f"{i}. {s}" for i, s in enumerate(draft["steps"], start=1)] + [""]
    if draft.get("not_confirmed"):
        parts += ["## Not confirmed", ""] + [f"- {x}" for x in draft["not_confirmed"]] + [""]
    return "\n".join(parts).strip() + "\n"


def publish(conn: psycopg.Connection, bulk_page: dict, *, institution_id: UUID, settings, model: str, run_id: str) -> dict:
    d, plan = bulk_page["draft"], bulk_page["plan"]
    with conn.cursor() as cur:
        cur.execute("SELECT canonical_name, slug, identity_status FROM institutions WHERE id=%s", (institution_id,))
        inst = cur.fetchone()
        if inst["identity_status"] != "verified":   # SPEC §07: nothing publishes for a school whose identity is not verified against the official NCES file
            raise PermissionError(f"institution identity {inst['identity_status']}: publishing waits for NCES verification")
        cur.execute("SELECT id, label FROM topics WHERE key=%s", (plan.get("topic_key") or "housing",))
        topic = cur.fetchone()
        cur.execute("SELECT id FROM campuses WHERE institution_id=%s AND is_main LIMIT 1", (institution_id,))
        campus = (cur.fetchone() or {}).get("id")
        page_format = {"entity_guide": "entity_profile", "process_guide": "guide", "comparison": "comparison"}.get(plan["page_type"], "guide")
        slug = bulk_page["path"].rstrip("/").rsplit("/", 1)[-1]
        cur.execute("""INSERT INTO pages (institution_id, campus_id, topic_id, entity_id, page_format, slug, path, audience, status, tier, primary_query)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'drafting', 1, %s)
                       ON CONFLICT (path) DO UPDATE SET primary_query=COALESCE(pages.primary_query, EXCLUDED.primary_query) RETURNING id""",
                    (institution_id, campus, topic["id"], UUID(plan["entity_id"]) if plan.get("entity_id") else None, page_format, slug, bulk_page["path"],
                     None if (plan.get("audience") or "general") == "general" else plan["audience"], (plan.get("primary_query") or plan["question"])[:300]))
        page_id = cur.fetchone()["id"]
    conn.commit()
    claim_ids = [c["claim_id"] for c in d.get("claims") or []]
    fact_table = [{"label": r["label"], "value": r["value"], "claim_id": r.get("claim_id")} for r in ((d.get("table") or {}).get("rows") or [])]
    draft = {"headline": d["title"][:60] if len(d["title"]) > 60 else d["title"], "deck": d["meta"], "body_markdown": body_markdown(d), "fact_table": fact_table, "fact_table_caption": (d.get("table") or {}).get("caption"),
             "next_actions": [{"text": str(n["text"])[:140], "target": str(n["target"])} for n in (d.get("next_steps") or [])][:6], "claim_refs": claim_ids, "byline": "Housing desk" if plan.get("topic_key") == "housing" else "Campus desk"}
    note = (f"Bulk mode (specs/bulk-mode.md), run {run_id}: written by {model} in one Message Batches request from the school dossier; code checks (quotes verbatim on the source page, "
            "every number backed by a quote, SEO basics, overlap) and one verification request per page; no correction rounds, no human editor.")
    page = {"id": page_id, "path": bulk_page["path"], "audience": None if (plan.get("audience") or "general") == "general" else plan["audience"], "page_format": page_format, "byline": draft["byline"]}
    with conn.cursor() as cur:
        cur.execute("SELECT COALESCE(s.final_url, r.canonical_url) AS url FROM claim_sources cs JOIN fetch_snapshots s ON s.id=cs.snapshot_id JOIN source_registry r ON r.id=s.source_id WHERE cs.claim_id = ANY(%s::uuid[]) AND r.source_kind LIKE 'official%%'", (claim_ids,))
        sources_used = sorted({r["url"] for r in cur.fetchall()})
    version_id = pipeline.create_version(conn, page=page, brief_id=None, draft=draft, claim_ids=claim_ids, settings=settings, writer_model=f"batch:{model}", editor_model="none:bulk", change_summary=f"bulk mode {run_id}",
                                         school_name=inst["canonical_name"], topic_label=topic["label"], sources_used=sources_used, production_note=note)
    checks = bulk_page.get("checks") or {}
    verdicts = bulk_page.get("verdicts") or {}
    findings = [{"kind": "bulk_check", "severity": "info", "detail": json.dumps({k: checks.get(k) for k in ("seo", "overlap_max", "removed_claims", "removed_sentences")}, default=str)[:4000]},
                {"kind": "bulk_verify", "severity": "info", "detail": json.dumps({"removed": verdicts.get("removed"), "count": len(verdicts.get("verdicts") or {})}, default=str)[:2000]}]
    rubric = {"bulk": True, "claims_verified": len(claim_ids), "claims_removed": len(verdicts.get("removed") or []) + len(checks.get("removed_claims") or []), "total": None}
    with conn.cursor() as cur:
        cur.execute("UPDATE page_versions SET gate_status='passed', gate_findings=%s::jsonb, rubric=%s::jsonb, verifier_model=%s WHERE id=%s", (json.dumps(findings), json.dumps(rubric), f"batch:{model}", version_id))
        cur.execute("UPDATE pages SET current_version_id=%s, status=CASE WHEN status IN ('planned','drafting','held') THEN 'staged' ELSE status END, revalidation_required=FALSE, revalidation_reason=NULL WHERE id=%s", (version_id, page_id))
    conn.commit()
    out = publisher.publish_local(conn, None, version_id, settings=settings)
    with conn.cursor() as cur:
        cur.execute("UPDATE bulk_pages SET page_id=%s, version_id=%s, stage='published', updated_at=now() WHERE id=%s", (page_id, version_id, bulk_page["id"]))
        cur.execute("UPDATE bulk_questions SET status='done', updated_at=now() WHERE id=%s", (bulk_page["question_id"],))
    conn.commit()
    return {"page_id": str(page_id), "version_id": str(version_id), "path": bulk_page["path"], "site_path": out.get("site_path") if isinstance(out, dict) else None}
