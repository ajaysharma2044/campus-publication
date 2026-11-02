"""Deterministic editorial checks (SPEC §16, §17, §31 'Writing').

Each check returns a list of Finding(kind, severity, detail). severity 'hard' is a hard failure.
These are release rules, not proof of quality; the model-based editor and verifier add judgment.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from difflib import SequenceMatcher

BANNED_OPENINGS = (
    r"^navigating the (world|landscape|maze) of",
    r"^whether you['’]?re (a |an )?\w+ or (a |an )?\w+",
    r"^nestled in the heart of",
    r"^in today['’]?s (fast-paced|ever-changing|competitive)",
    r"^when it comes to",
    r"^(choosing|finding) the (right|perfect) \w+ (can be|is) (a )?(daunting|overwhelming|exciting)",
    r"^(welcome|congratulations)[!,.]",
    r"^are you (a |an )?\w+ (student|parent) (looking|wondering)",
)
FILLER_PHRASES = (
    "vibrant", "unique experience for every student", "state-of-the-art", "world-class", "top-notch", "a plethora of",
    "it is important to note", "in conclusion", "look no further", "the perfect choice", "truly", "unparalleled",
    "best of both worlds", "home away from home", "whether you are", "endless opportunities", "something for everyone",
    "exciting journey", "dive into", "delve into", "game-changer", "seamless", "elevate your",
)
CONSENSUS_PATTERNS = (
    r"\bstudents (all )?agree\b", r"\buniversally (loved|praised|hated)\b", r"\beveryone (loves|hates|says)\b",
    r"\b(most|all) students (love|hate|prefer|say)\b", r"\bresidents rave\b", r"\bconsistently rated\b",
    r"\b\d(\.\d)?[/ ]?(out of )?5 stars?\b", r"\baverage rating\b", r"\bwhen i (lived|stayed|visited)\b",
    r"\bi (spoke|talked) (to|with)\b", r"\bone student told (me|us)\b", r"\bour (reporter|correspondent) (found|visited|tested)\b",
    r"\bwe (tested|visited|toured|stayed)\b", r"\bin my experience\b",
)
QUOTE_PATTERN = re.compile(r"[“\"][^”\"]{25,}[”\"]\s*(,|—|-)?\s*(said|says|according to|told)\b", re.I)
BYLINE_HUMAN_PATTERN = re.compile(r"^\s*by\s+[A-Z][a-z]+(\s+[A-Z]\.)?\s+[A-Z][a-z]+", re.M | re.I)
SUPERLATIVE_PATTERN = re.compile(r"\b(the )?(best|worst|cheapest|most affordable|#1|number one|top[- ]rated|ultimate|definitive|complete guide)\b", re.I)
MONEY_PATTERN = re.compile(r"\$\s?(\d{1,3}(?:,\d{3})+|\d+)(?:\.(\d{2}))?")
YEAR_PATTERN = re.compile(r"\b(20\d{2})[–\-/](\d{2}|20\d{2})\b")
ALLOWED_BYLINES = ("Publication desk", "Housing desk", "Admissions desk", "Costs and aid desk", "Transfer desk", "Tools desk")


@dataclass
class Finding:
    kind: str
    severity: str  # 'hard' | 'major' | 'minor'
    detail: str

    def as_dict(self) -> dict:
        return {"kind": self.kind, "severity": self.severity, "detail": self.detail}


def _paragraphs(md: str) -> list[str]:
    return [p.strip() for p in re.split(r"\n\s*\n", md) if p.strip() and not p.strip().startswith(("#", "|", "-", "*", ">"))]


def check_openings(body_md: str) -> list[Finding]:
    out = []
    paras = _paragraphs(body_md)
    if not paras:
        return [Finding("empty", "hard", "no body paragraphs")]
    first = paras[0].lower()
    for pat in BANNED_OPENINGS:
        if re.search(pat, first):
            out.append(Finding("filler", "major", f"banned empty opening: '{paras[0][:80]}'"))
            break
    return out


def check_filler(body_md: str) -> list[Finding]:
    low = body_md.lower()
    hits = [p for p in FILLER_PHRASES if p in low]
    out = []
    if hits:
        sev = "major" if len(hits) >= 3 else "minor"
        out.append(Finding("filler", sev, f"generic phrasing: {', '.join(hits[:6])}"))
    return out


def check_fabrication(body_md: str) -> list[Finding]:
    out = []
    for pat in CONSENSUS_PATTERNS:
        m = re.search(pat, body_md, re.I)
        if m:
            out.append(Finding("fabricated_consensus", "hard", f"invented consensus/experience phrasing: '{m.group(0)}'"))
    if QUOTE_PATTERN.search(body_md):
        out.append(Finding("invented_quote", "hard", "attributed quotation present; quotes require a stored, rights-cleared source excerpt"))
    return out


def check_byline(byline: str) -> list[Finding]:
    if byline in ALLOWED_BYLINES:
        return []
    if BYLINE_HUMAN_PATTERN.match(byline) or re.match(r"^[A-Z][a-z]+ [A-Z][a-z]+$", byline.strip()):
        return [Finding("fake_byline", "hard", f"byline '{byline}' looks like a person; no human reporter exists for this page")]
    return [Finding("fake_byline", "major", f"byline '{byline}' is not an approved desk credit")]


def check_headline(headline: str, deck: str | None, body_md: str) -> list[Finding]:
    out = []
    if SUPERLATIVE_PATTERN.search(headline):
        out.append(Finding("deceptive_headline", "major", f"unsupported superlative/clickbait in headline: '{headline}'"))
    if len(headline) > 110:
        out.append(Finding("headline", "minor", "headline longer than 110 characters"))
    if headline.rstrip().endswith("?") and "?" not in body_md[:600] and not re.search(r"\b(yes|no)\b", body_md[:400], re.I):
        out.append(Finding("headline", "minor", "question headline whose answer is not given early in the body"))
    return out


def check_money_in_prose_matches_table(body_md: str, fact_table: list[dict] | None) -> list[Finding]:
    """Any dollar amount in prose must appear in the fact table (or claims) — catches outdated prose
    beside an updated table (SPEC §31)."""
    if not fact_table:
        return []
    table_values = set()
    for row in fact_table:
        for m in MONEY_PATTERN.finditer(str(row.get("value", ""))):
            table_values.add(m.group(1).replace(",", ""))
    prose = "\n".join(_paragraphs(body_md))
    out = []
    for m in MONEY_PATTERN.finditer(prose):
        if m.group(1).replace(",", "") not in table_values:
            out.append(Finding("prose_table_mismatch", "major", f"amount {m.group(0)} in prose does not appear in the fact table"))
    return out


def check_claim_refs(body_claim_ids: list[str], critical_ids: list[str], approved_ids: set[str]) -> list[Finding]:
    out = []
    unknown = [c for c in body_claim_ids if c not in approved_ids]
    if unknown:
        out.append(Finding("unsupported_claim", "hard", f"draft references claims not in the approved evidence packet: {unknown[:5]}"))
    missing_critical = [c for c in critical_ids if c not in body_claim_ids]
    if missing_critical:
        out.append(Finding("missing_critical", "major", f"critical claims from the brief are not used: {missing_critical[:5]}"))
    return out


def check_arithmetic(body_md: str) -> list[Finding]:
    """Verify simple inline sums like '$X + $Y = $Z' or 'X × 2 = Y' present in prose or tables."""
    out = []
    for m in re.finditer(r"\$?([\d,]+(?:\.\d+)?)\s*\+\s*(?:[A-Za-z ]{0,30}?)\$?([\d,]+(?:\.\d+)?)\s*=\s*\$?([\d,]+(?:\.\d+)?)", body_md):
        a, b, c = (float(x.replace(",", "")) for x in m.groups())
        if abs(a + b - c) > 0.005:
            out.append(Finding("incorrect_arithmetic", "hard", f"'{m.group(0)}' does not add up"))
    for m in re.finditer(r"\$?([\d,]+(?:\.\d+)?)\s*[×x\*]\s*(\d+)\s*=\s*\$?([\d,]+(?:\.\d+)?)", body_md):
        a, n, c = float(m.group(1).replace(",", "")), int(m.group(2)), float(m.group(3).replace(",", ""))
        if abs(a * n - c) > 0.005:
            out.append(Finding("incorrect_arithmetic", "hard", f"'{m.group(0)}' is wrong"))
    return out


def check_scope(body_md: str, headline: str, *, institution_name: str, other_institution_names: list[str], academic_year: str | None) -> list[Finding]:
    out = []
    text = headline + "\n" + body_md
    for other in other_institution_names:
        if other and other.lower() != institution_name.lower() and re.search(r"\b" + re.escape(other) + r"\b", text, re.I):
            out.append(Finding("wrong_school", "hard", f"mentions another institution '{other}' without a scoped comparison record"))
    if academic_year:
        for m in YEAR_PATTERN.finditer(text):
            found = f"{m.group(1)}-{m.group(2)[-2:]}"
            if found != academic_year:
                out.append(Finding("wrong_year", "major", f"academic year {found} appears but the brief is scoped to {academic_year}"))
    return out


def check_next_action(next_actions: list[dict] | None) -> list[Finding]:
    if not next_actions:
        return [Finding("missing_next_action", "major", "no next action for the reader")]
    bad = [a for a in next_actions if re.search(r"you may also like|read more|click here|related", a.get("text", ""), re.I)]
    if bad:
        return [Finding("weak_link_text", "minor", "link text does not explain the action")]
    return []


def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def check_duplicate_audience(body_md: str, existing_bodies: list[tuple[str, str]], *, threshold: float = 0.82) -> list[Finding]:
    """Flag label-swapped audience rewrites: near-identical text to an existing page."""
    out = []
    norm = re.sub(r"\b(first-year|transfer|international|graduate|freshman|freshmen|commuter)\b", "AUD", body_md, flags=re.I)
    for page_id, other in existing_bodies:
        other_norm = re.sub(r"\b(first-year|transfer|international|graduate|freshman|freshmen|commuter)\b", "AUD", other, flags=re.I)
        s = similarity(norm[:6000], other_norm[:6000])
        if s >= threshold:
            out.append(Finding("superficial_duplicate", "hard", f"{int(s * 100)}% similar to page {page_id} after audience-label normalization"))
    return out


def check_length_padding(body_md: str) -> list[Finding]:
    paras = _paragraphs(body_md)
    out = []
    if len(paras) >= 6:
        sims = [similarity(paras[i], paras[j]) for i in range(len(paras)) for j in range(i + 1, len(paras))]
        if sims and sum(1 for s in sims if s > 0.7) >= 2:
            out.append(Finding("repetition", "major", "repeated paragraphs (summary restated)"))
    return out


def run_all(*, headline: str, deck: str | None, body_md: str, byline: str, fact_table: list[dict] | None, body_claim_ids: list[str],
            critical_ids: list[str], approved_ids: set[str], institution_name: str, other_institution_names: list[str],
            academic_year: str | None, next_actions: list[dict] | None, existing_bodies: list[tuple[str, str]]) -> list[Finding]:
    f: list[Finding] = []
    f += check_openings(body_md)
    f += check_filler(body_md)
    f += check_fabrication(body_md)
    f += check_byline(byline)
    f += check_headline(headline, deck, body_md)
    f += check_money_in_prose_matches_table(body_md, fact_table)
    f += check_claim_refs(body_claim_ids, critical_ids, approved_ids)
    f += check_arithmetic(body_md)
    f += check_scope(body_md, headline, institution_name=institution_name, other_institution_names=other_institution_names, academic_year=academic_year)
    f += check_next_action(next_actions)
    f += check_duplicate_audience(body_md, existing_bodies)
    f += check_length_padding(body_md)
    return f
