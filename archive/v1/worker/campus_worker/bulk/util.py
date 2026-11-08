"""Small shared helpers for bulk mode."""
from __future__ import annotations

import json
import re
import unicodedata
from datetime import date, datetime

STOP = {"a", "an", "the", "of", "at", "in", "on", "for", "to", "is", "are", "do", "does", "did", "what", "when", "where", "how", "can", "i", "my", "and", "or",
        "be", "with", "by", "it", "its", "there", "any", "have", "has", "will", "should", "you", "your", "much", "many", "who", "which"}


def slugify(text: str, *, max_words: int = 8, keep_stop: bool = False) -> str:
    t = unicodedata.normalize("NFKD", text or "").encode("ascii", "ignore").decode()
    t = re.sub(r"[’']s\b", "", t.lower())
    words = [w for w in re.findall(r"[a-z0-9]+", t) if keep_stop or w not in STOP]
    return "-".join(words[:max_words]) or "page"


def norm_text(s: str) -> str:
    """Whitespace- and quote-insensitive form used to check a quote is verbatim on a page."""
    s = unicodedata.normalize("NFKC", s or "")
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"').replace(" ", " ").replace("–", "-").replace("—", "-")
    return re.sub(r"\s+", " ", s).strip().lower()


def quote_in_text(quote: str, text: str) -> bool:
    q, t = norm_text(quote), norm_text(text)
    return bool(q) and len(q) >= 12 and q in t


def parse_json_object(text: str) -> dict | None:
    """The first JSON object in a model reply (replies may wrap it in prose or a code fence)."""
    if not text:
        return None
    s = text.strip()
    if s.startswith("```"):
        s = re.sub(r"^```(?:json)?\s*", "", s)
        s = re.sub(r"\s*```$", "", s)
    try:
        return json.loads(s)
    except json.JSONDecodeError:
        pass
    i = s.find("{")
    while i >= 0:
        depth = 0
        for j in range(i, len(s)):
            if s[j] == "{":
                depth += 1
            elif s[j] == "}":
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(s[i:j + 1])
                    except json.JSONDecodeError:
                        break
        i = s.find("{", i + 1)
    return None


def json_default(o):
    if isinstance(o, (datetime, date)):
        return o.isoformat()
    return str(o)


def money_text(minor: int | None, period: str | None = None, basis: str | None = None) -> str:
    if minor is None:
        return ""
    s = f"${minor / 100:,.2f}" if minor % 100 else f"${minor // 100:,}"
    tail = " ".join(x for x in ({"per_semester": "per semester", "per_academic_year": "per academic year", "per_month": "per month", "per_year": "per year", "one_time": "one time",
                                 "per_term": "per term", "per_week": "per week", "per_day": "per day"}.get(period or "", ""),
                                {"per_person": "per person", "per_unit": "per unit", "per_bed": "per bed"}.get(basis or "", "")) if x)
    return f"{s} {tail}".strip()


def long_date(d: date | datetime | str | None) -> str:
    if not d:
        return ""
    if isinstance(d, str):
        d = datetime.fromisoformat(d[:19])
    return d.strftime("%B %-d, %Y")
