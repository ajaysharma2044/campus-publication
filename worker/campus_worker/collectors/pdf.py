"""Official PDF / table collector (SPEC §08).

Uses pdfplumber. Preserves page numbers, tables per page, footnote lines, and detected academic
years so a rate table's "2026–27" column is never silently attached to a different year. Produces
an extraction confidence; low confidence routes to review instead of becoming facts.
"""
from __future__ import annotations

import hashlib
import io
import re
from dataclasses import dataclass, field

import pdfplumber

ACADEMIC_YEAR_RE = re.compile(r"\b(20\d{2})\s*[–—/-]\s*(20)?(\d{2})\b")
FOOTNOTE_RE = re.compile(r"^\s*(?:[\*†‡§]\s?|\(?\d{1,2}\)?[\.\)]?\s)(?=\S)")
MONEY_RE = re.compile(r"\$\s?\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?")


@dataclass
class PdfPage:
    number: int
    text: str
    tables: list[list[list[str | None]]]
    footnotes: list[str]
    academic_years: list[str]


@dataclass
class PdfExtraction:
    pages: list[PdfPage]
    content_hash: str
    confidence: float
    academic_years: list[str]
    needs_review: bool
    review_reasons: list[str] = field(default_factory=list)


def normalize_academic_year(m: re.Match) -> str:
    start = int(m.group(1))
    end2 = int(m.group(3))
    return f"{start}-{end2:02d}"


def find_academic_years(text: str) -> list[str]:
    years = []
    for m in ACADEMIC_YEAR_RE.finditer(text):
        ay = normalize_academic_year(m)
        s, e = int(ay[:4]), int(ay[:2] + ay[5:])
        if e - s == 1 and ay not in years:
            years.append(ay)
    return years


def extract_pdf(data: bytes) -> PdfExtraction:
    pages: list[PdfPage] = []
    reasons: list[str] = []
    total_chars = 0
    table_cells = 0
    empty_cells = 0
    with pdfplumber.open(io.BytesIO(data)) as pdf:
        for i, p in enumerate(pdf.pages, start=1):
            text = p.extract_text() or ""
            total_chars += len(text)
            tables = []
            for t in p.extract_tables() or []:
                clean = [[(c.strip() if isinstance(c, str) else c) for c in row] for row in t]
                for row in clean:
                    for c in row:
                        table_cells += 1
                        if c in (None, ""):
                            empty_cells += 1
                tables.append(clean)
            footnotes = [ln.strip() for ln in text.splitlines() if FOOTNOTE_RE.match(ln) and len(ln.strip()) > 8]
            pages.append(PdfPage(i, text, tables, footnotes, find_academic_years(text)))
    all_years = []
    for pg in pages:
        for y in pg.academic_years:
            if y not in all_years:
                all_years.append(y)
    if not pages:
        reasons.append("no_pages")
    if total_chars < 200:
        reasons.append("little_or_no_text_layer (scanned? OCR not trusted as fact)")
    if table_cells and empty_cells / table_cells > 0.4:
        reasons.append("sparse_tables (layout parse may have split cells)")
    if len(all_years) > 1:
        reasons.append(f"multiple_academic_years {all_years} (claims must be scoped per year)")
    confidence = 0.0 if not pages else min(1.0, 0.3 + min(total_chars, 2000) / 4000 + (0.2 if table_cells and empty_cells / max(table_cells, 1) < 0.2 else 0))
    needs_review = confidence < 0.6 or any(r.startswith(("no_pages", "little_or_no", "sparse")) for r in reasons)
    material = "\n".join(pg.text for pg in pages)
    return PdfExtraction(pages, hashlib.sha256(material.encode()).hexdigest(), round(confidence, 3), all_years, needs_review, reasons)


def table_to_records(table: list[list[str | None]]) -> list[dict[str, str]]:
    """First non-empty row is the header; subsequent rows become dicts. Cells kept as text."""
    rows = [r for r in table if any(c not in (None, "") for c in r)]
    if len(rows) < 2:
        return []
    headers = [(h or f"col{i}").strip() for i, h in enumerate(rows[0])]
    out = []
    for r in rows[1:]:
        out.append({headers[i]: (r[i] or "").strip() for i in range(min(len(headers), len(r)))})
    return out


def parse_money_minor(text: str) -> int | None:
    m = MONEY_RE.search(text or "")
    if not m:
        return None
    digits = m.group(0).replace("$", "").replace(",", "").strip()
    whole, _, cents = digits.partition(".")
    return int(whole) * 100 + (int(cents.ljust(2, "0")[:2]) if cents else 0)
