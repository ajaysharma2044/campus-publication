"""Stage 4 (code): every number, date and dollar amount in the prose must appear in a cited quote that is verbatim on its source page;
the R45 basics (title ≤ 60 with key words, meta length, one H1, answer first, 2+ internal links); no banned filler or internal terms;
overlap < 60% with any existing page. Failing claims are removed with the sentences that used them; if the answer survives, the
page continues, otherwise it is skipped with the reason."""
from __future__ import annotations

import re
from difflib import SequenceMatcher

from ..editorial.checks import FILLER_PHRASES
from ..seo_gate import _contains_query, _words
from .util import norm_text, quote_in_text

INTERNAL_TERMS = ("pages we opened", "could not verify", "not stated on the pages", "snapshot", "snippet", "claim id", "verifier", "rubric", "this publication's", "automated system", "no human editor")
NUMBER_RE = re.compile(r"\$[\d,]+(?:\.\d{2})?|\b(?:January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2}, 20\d{2}\b|\b20\d\d-\d\d\b|\b\d{1,3}(?:,\d{3})+\b|\b\d+(?:\.\d+)?%|\b(?!20\d\d\b)\d{2,}\b")
OVERLAP_MAX = 0.60
ANSWER_MAX_WORDS = 50   # the SEO gate's answer-first rule; the lead is split to fit it, never the rule loosened


def _sentences(text: str) -> list[str]:
    return [s for s in re.split(r"(?<=[.!?])\s+(?=[A-Z0-9\"“(])", text.strip()) if s.strip()]


def _tokens(text: str) -> set[str]:
    return {norm_text(m.group(0)) for m in NUMBER_RE.finditer(text or "")}


def check_draft(draft: dict, gathered: dict, *, question: str, hubs: list[str], existing_bodies: list[str], source_texts: dict[str, str]) -> tuple[dict, dict]:
    facts = {f["id"]: f for f in gathered["facts"]}
    report = {"removed_claims": [], "removed_sentences": [], "seo": {}, "banned": [], "status": "ok", "reasons": []}
    # 1. claims: known id, quote verbatim on the source page (or identical to the stored excerpt)
    kept_claims, allowed_tokens = [], {norm_text(f["academic_year"]) for f in facts.values() if f.get("academic_year")}  # year labels are scope, not facts
    for c in draft.get("claims") or []:
        f = facts.get(str(c.get("claim_id")))
        if not f:
            report["removed_claims"].append({"claim_id": c.get("claim_id"), "reason": "not in the gathered facts"})
            continue
        quote = str(c.get("quote") or "")
        src = source_texts.get(f["snapshot_id"], "")
        if not (norm_text(quote) == norm_text(f["quote"]) or quote_in_text(quote, src) or quote_in_text(quote, f["quote"])):
            report["removed_claims"].append({"claim_id": f["id"], "reason": "quote not verbatim on its source"})
            continue
        kept_claims.append({"claim_id": f["id"], "quote": f["quote"], "used_for": c.get("used_for") or ""})
        allowed_tokens |= _tokens(f["quote"]) | _tokens(f["value"])
        if f.get("academic_year"):
            allowed_tokens.add(norm_text(f["academic_year"]))
    draft["claims"] = kept_claims
    # 2. numbers in prose must be covered by a kept quote/value; a sentence with an uncovered number is dropped
    def clean_block(text: str, where: str) -> str:
        out = []
        for s in _sentences(text):
            bad = [t for t in _tokens(s) if t not in allowed_tokens]
            low = s.lower()
            banned = [p for p in FILLER_PHRASES + INTERNAL_TERMS if p in low]
            if bad or banned:
                report["removed_sentences"].append({"where": where, "sentence": s[:160], "numbers": bad, "banned": banned})
                continue
            out.append(s)
        return " ".join(out)
    draft["answer"] = clean_block(draft.get("answer") or "", "answer")
    for i, sec in enumerate(draft.get("sections") or []):
        paras = []
        for para in (sec.get("body_md") or "").split("\n\n"):
            if para.lstrip().startswith(("-", "*", "1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.")):
                lines = []
                for line in para.split("\n"):
                    bad = [t for t in _tokens(line) if t not in allowed_tokens]
                    if bad or any(p in line.lower() for p in FILLER_PHRASES + INTERNAL_TERMS):
                        report["removed_sentences"].append({"where": f"section {i}", "sentence": line[:160], "numbers": bad})
                        continue
                    lines.append(line)
                paras.append("\n".join(lines))
            else:
                paras.append(clean_block(para, f"section {i}"))
        sec["body_md"] = "\n\n".join(p for p in paras if p.strip())
    draft["sections"] = [s for s in draft.get("sections") or [] if s.get("body_md", "").strip()]
    # 2b. a lead over the word cap is split at a sentence boundary: the opening sentences stay the answer, the rest open the first section
    report["answer_split"] = _split_answer(draft)
    if draft.get("table"):
        rows = []
        for r in draft["table"].get("rows") or []:
            cid = str(r.get("claim_id") or "")
            if cid in facts and all(t in allowed_tokens | _tokens(facts[cid]["value"]) for t in _tokens(str(r.get("value")))):
                rows.append({"label": str(r["label"])[:120], "value": str(r["value"])[:200], "claim_id": cid})
            else:
                report["removed_sentences"].append({"where": "table", "sentence": f"{r.get('label')}: {r.get('value')}", "numbers": ["uncited row"]})
        draft["table"]["rows"] = rows
        if not rows:
            draft["table"] = None
    if draft.get("steps"):
        draft["steps"] = [s for s in draft["steps"] if not [t for t in _tokens(s) if t not in allowed_tokens]]
    # 3. SEO basics
    answer_words = _words(draft.get("answer") or "")
    links = set(re.findall(r"\]\((/[^)\s]+)\)", " ".join(s.get("body_md") or "" for s in draft.get("sections") or []) + " " + (draft.get("answer") or "")))
    targets = {l["path"] for l in gathered.get("link_targets") or []} | set(hubs)
    seo = {"title_ok": 10 <= len(draft.get("title") or "") <= 60 and _contains_query(draft.get("title") or "", question), "meta_ok": 120 <= len(draft.get("meta") or "") <= 155,
           "h1_ok": bool(draft.get("h1")), "answer_first_ok": 8 <= answer_words <= 50 and bool(re.search(r"\d|\byes\b|\bno\b|\bmust\b|\bis\b|\bare\b|\bcosts?\b|\brequire", draft.get("answer") or "", re.I)),
           "internal_links": len(links & targets), "links_ok": len(links & targets) >= 2}
    if not seo["links_ok"] and targets:
        extra = [t for t in list(dict.fromkeys(list(hubs) + [l["path"] for l in gathered.get("link_targets") or []])) if t not in links][: max(0, 2 - len(links & targets))]
        if extra:
            draft["sections"].append({"heading": "Related guides", "body_md": "\n".join(f"- [{_anchor(t, gathered, hubs)}]({t})" for t in extra)})
            seo["internal_links"] = len(links & targets) + len(extra)
            seo["links_ok"] = seo["internal_links"] >= 2
    if seo["meta_ok"] is False and draft.get("meta"):
        draft["meta"] = _fit_meta(draft["meta"], draft.get("answer") or "")
        seo["meta_ok"] = 120 <= len(draft["meta"]) <= 155
    report["seo"] = seo
    # 4. overlap with existing pages
    body_text = norm_text(" ".join([draft.get("answer") or ""] + [s.get("body_md") or "" for s in draft.get("sections") or []]))
    report["overlap_max"] = max((SequenceMatcher(None, body_text, norm_text(b)).ratio() for b in existing_bodies if b), default=0.0)
    # 5. decide
    if not draft["answer"] or _words(draft["answer"]) < 8:
        report["reasons"].append("the answer paragraph did not survive the number check")
    if not kept_claims:
        report["reasons"].append("no claim survived")
    if not seo["title_ok"]:
        report["reasons"].append("title fails the key-word or length rule")
    if not seo["answer_first_ok"]:
        report["reasons"].append("answer paragraph is not a direct answer (length or content)")
    if report["overlap_max"] >= OVERLAP_MAX:
        report["reasons"].append(f"overlap {report['overlap_max']:.2f} with an existing page")
    report["status"] = "skip" if report["reasons"] else "ok"
    draft["not_confirmed"] = [str(x)[:200] for x in (draft.get("not_confirmed") or [])][:3]
    return draft, report


def _split_answer(draft: dict) -> int:
    """Writers sometimes run the lead past the cap. Keep the longest run of opening sentences within it and move the rest to the top
    of the first section, so the page keeps every checked sentence. Returns how many sentences moved (0 = untouched)."""
    answer = draft.get("answer") or ""
    sents = _sentences(answer)
    if _words(answer) <= ANSWER_MAX_WORDS or len(sents) < 2:
        return 0
    lead: list[str] = []
    for s in sents:
        if lead and _words(" ".join(lead + [s])) > ANSWER_MAX_WORDS:
            break
        lead.append(s)
    rest = sents[len(lead):]
    if not rest:
        return 0
    draft["answer"] = " ".join(lead)
    secs = draft.get("sections") or []
    if secs:
        secs[0]["body_md"] = (" ".join(rest) + "\n\n" + (secs[0].get("body_md") or "")).strip()
    else:
        draft["sections"] = [{"heading": "The details", "body_md": " ".join(rest)}]
    return len(rest)


def _anchor(path: str, gathered: dict, hubs: list[str]) -> str:
    for l in gathered.get("link_targets") or []:
        if l["path"] == path and l.get("anchor_hint"):
            return l["anchor_hint"][:80]
    parts = [p for p in path.split("/") if p]
    return (parts[-1] if parts else path).replace("-", " ").capitalize() + (" guides" if path in hubs else "")


def _fit_meta(meta: str, answer: str) -> str:
    m = meta.strip()
    if len(m) > 155:
        cut = m[:152].rsplit(" ", 1)[0].rstrip(",;:")
        return cut + "..." if not cut.endswith(".") else cut
    if len(m) < 120:
        extra = answer.strip()
        return (m + " " + extra)[:155].rsplit(" ", 1)[0].rstrip(",;:") + "." if extra else m
    return m
