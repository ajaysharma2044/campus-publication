"""Stage 3: one Message Batches request per page. The shared prefix (style guide, page templates, citation format, output schema)
is one cached system block; the page's question, audience, dossier facts with quotes, win note and link targets are the user turn.
The reply is structured JSON; code validates it (jsonschema) before the check stage."""
from __future__ import annotations

import json
from datetime import date

import jsonschema

from .batch_client import BatchRequest
from .util import parse_json_object

MAX_OUTPUT_TOKENS = 3_500

WRITER_SYSTEM = """You write one reader-first guide page for Footnote Daily, an independent publication about US colleges and their towns. You write from the FACTS block only.

Voice and rules (owner's style guide):
- Lead with the direct, practical answer a student can act on, built from what the sources DO say; a knowledgeable upperclassman explaining it to a friend. The first paragraph answers the question in at most 50 words and contains the key number, date, rule or a plain yes/no when the facts support one.
- Never write "the pages we opened do not say", "not stated", "we could not verify" or any audit language (snapshot, snippet, claim, verifier, rubric, "this publication"). Gaps go only in not_confirmed (at most 3 short bullets, one line each, no apology).
- Every number, date, dollar amount, rule and name you state must come from a fact in FACTS and be listed in "claims" with that fact's id and its quote copied exactly from FACTS. Facts you do not cite may not appear. Do not add outside knowledge, estimates, history, opinions, ratings, reviews or resident experiences.
- Dates as "November 6, 2026". Money exactly as in the fact value (e.g. "$6,872 per person per semester"). Academic years as "2026-27". Mark a dated deadline that is earlier than TODAY as passed.
- Tables for comparisons (rows carry a label, a value and the claim id), numbered steps for processes.
- Internal links: markdown links only to paths in LINK_TARGETS and HUBS, with descriptive anchor text; use at least two, where the text naturally refers to them.
- No filler ("whether you're", "it's important to note", "navigating", "delve", "vibrant", "state-of-the-art", "look no further", "in today's"), no superlatives, no "best".
- One brand: Footnote Daily. No byline, date line or sources section in the body (the page chrome shows them).

Page templates (section headings are yours to phrase so a reader would search them; keep this order):
- question_guide: answer paragraph; details that explain the rule or number; a table of costs or dates when the facts give two or more; numbered steps when the facts describe a process; not_confirmed; next_steps.
- entity_guide: answer paragraph (what it is, who it is for, the one key number); an at-a-glance table; what is there (amenities, hours, location); who lives/uses it and how placement or access works; rules and costs; how to apply or get there; contact; not_confirmed; next_steps.
- process_guide: answer paragraph (the process in one or two sentences with the deadline); numbered steps; deadlines table; exceptions; contact; not_confirmed; next_steps.
- comparison: answer paragraph; a comparison table (one row per item, columns from the facts); the differences that matter; not_confirmed; next_steps.

Return ONE JSON object and nothing else:
{"title": "<= 60 characters, contains every content word of PRIMARY QUERY", "meta": "120-155 characters stating the answer", "h1": "<the question or a plain statement of it>",
 "answer": "<the first paragraph, <= 50 words>", "sections": [{"heading": "...", "body_md": "<markdown: paragraphs, bullet lists, numbered steps; no H1/H2 markup, no tables here>"}],
 "table": {"caption": "...", "rows": [{"label": "...", "value": "...", "claim_id": "<fact id>"}]} | null, "steps": ["...", "..."] | null,
 "next_steps": [{"text": "<specific action>", "target": "<internal path from LINK_TARGETS/HUBS or an official source_url from FACTS>"}] (2-4 items),
 "not_confirmed": ["<one line>"] (0-3 items), "claims": [{"claim_id": "<fact id>", "quote": "<exact quote from FACTS>", "used_for": "<the sentence or row that uses it>"}],
 "internal_links": ["<paths used>"]}"""

DRAFT_SCHEMA = {
    "type": "object",
    "required": ["title", "meta", "h1", "answer", "sections", "next_steps", "claims"],
    "properties": {
        "title": {"type": "string", "minLength": 10, "maxLength": 90}, "meta": {"type": "string", "minLength": 60, "maxLength": 220}, "h1": {"type": "string", "minLength": 5},
        "answer": {"type": "string", "minLength": 20}, "sections": {"type": "array", "items": {"type": "object", "required": ["heading", "body_md"], "properties": {"heading": {"type": "string"}, "body_md": {"type": "string"}}}},
        "table": {"type": ["object", "null"], "properties": {"caption": {"type": "string"}, "rows": {"type": "array", "items": {"type": "object", "required": ["label", "value"], "properties": {"label": {"type": "string"}, "value": {"type": "string"}, "claim_id": {"type": ["string", "null"]}}}}}},
        "steps": {"type": ["array", "null"], "items": {"type": "string"}}, "next_steps": {"type": "array", "minItems": 1, "items": {"type": "object", "required": ["text", "target"]}},
        "not_confirmed": {"type": "array", "maxItems": 5, "items": {"type": "string"}}, "claims": {"type": "array", "items": {"type": "object", "required": ["claim_id", "quote"]}},
        "internal_links": {"type": "array", "items": {"type": "string"}},
    },
}


def user_turn(bulk_page: dict, *, school_name: str, today: date) -> str:
    plan, g = bulk_page["plan"], bulk_page["gathered"]
    facts = "\n".join(f"- id={f['id']} | field={f['field']} | value={f['value']}" + (f" | year={f['academic_year']}" if f.get("academic_year") else "") + (f" | audience={','.join(f['audience'])}" if f.get("audience") else "")
                      + (f" | about={f['entity']}" if f.get("entity") else "") + f" | source={f['source_url']} (fetched {f['fetched_at']})\n  quote: \"{f['quote']}\"" for f in g["facts"])
    links = "\n".join(f"- {l['path']} ({l.get('anchor_hint') or ''})" for l in g.get("link_targets") or [])
    return (f"TODAY: {today.strftime('%B %-d, %Y')}\nSCHOOL: {school_name}\nPAGE TYPE: {plan['page_type']}\nQUESTION: {plan['question']}\nPRIMARY QUERY: {plan.get('primary_query') or plan['question']}\nAUDIENCE: {plan.get('audience') or 'general'}\n"
            f"PATH: {bulk_page['path']}\nWIN NOTE: {plan.get('win_note') or ''}\nHUBS: {', '.join(g.get('hubs') or [])}\nLINK_TARGETS:\n{links or '- (none yet)'}\n\nFACTS:\n{facts}\n")


def build_request(bulk_page: dict, *, model: str, school_name: str, today: date) -> BatchRequest:
    return BatchRequest(custom_id=f"write:{bulk_page['id']}", model=model, system=WRITER_SYSTEM, user=user_turn(bulk_page, school_name=school_name, today=today), max_tokens=MAX_OUTPUT_TOKENS, temperature=0.3)


def parse_draft(text: str | None) -> tuple[dict | None, str | None]:
    doc = parse_json_object(text or "")
    if doc is None:
        return None, "reply is not JSON"
    doc.setdefault("not_confirmed", [])
    doc.setdefault("internal_links", [])
    doc.setdefault("table", None)
    doc.setdefault("steps", None)
    try:
        jsonschema.validate(doc, DRAFT_SCHEMA)
    except jsonschema.ValidationError as e:
        return None, f"schema: {'/'.join(str(p) for p in e.absolute_path)}: {e.message[:160]}"
    return doc, None
