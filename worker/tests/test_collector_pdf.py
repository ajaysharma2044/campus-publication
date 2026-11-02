from campus_worker.collectors.pdf import extract_pdf, find_academic_years, parse_money_minor, table_to_records
from campus_worker.config import FIXTURES_DIR


def test_pdf_pages_tables_footnotes_and_years():
    e = extract_pdf((FIXTURES_DIR / "sources" / "fixture_rate_sheet.pdf").read_bytes())
    assert len(e.pages) == 2
    assert e.academic_years == ["2025-26", "2026-27"]
    assert any("multiple_academic_years" in r for r in e.review_reasons)
    recs = table_to_records(e.pages[0].tables[0])
    assert recs[0]["Room type"] == "Double" and recs[0]["2026–27"] == "$12,042"
    assert any("deposit" in f for f in e.pages[0].footnotes)
    assert any(f.startswith("*") for f in e.pages[1].footnotes)
    assert e.pages[1].academic_years == []  # dining page carries no year; must not inherit page 1's


def test_scanned_or_empty_pdf_routes_to_review():
    import pypdf, io
    w = pypdf.PdfWriter(); w.add_blank_page(width=200, height=200)
    buf = io.BytesIO(); w.write(buf)
    e = extract_pdf(buf.getvalue())
    assert e.needs_review and any("little_or_no_text" in r for r in e.review_reasons)


def test_year_and_money_parsing():
    assert find_academic_years("Rates for 2026–27 and 2026-2027 and 2026/27") == ["2026-27"]
    assert find_academic_years("Founded 1865-1870") == []  # not consecutive years
    assert parse_money_minor("$12,042") == 1204200
    assert parse_money_minor("$ 1,234.5") == 123450
    assert parse_money_minor("TBD") is None
