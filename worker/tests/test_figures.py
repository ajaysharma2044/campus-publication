"""Figures built from the fact table (render/figures.py), the photo slot keyed by page path (render/photos.py), and how
article.html renders both: every number verbatim, nothing invented, no <img> without a rights record."""
from __future__ import annotations

import re
import struct
import zlib
from datetime import date
from pathlib import Path
from uuid import uuid4

import yaml
from bs4 import BeautifulSoup

from campus_worker import seo_gate
from campus_worker.render import engine, figures, photos, site

TODAY = date(2026, 11, 6)
ROWS = [  # the shape of the Cornell transfer-housing fact table
    {"label": "Application fee", "value": "None (2026-27)", "claim_id": "c0"},
    {"label": "Apply by", "value": "Should apply within ten days of receiving your NetID", "claim_id": "c1"},
    {"label": "Admitted-student sign-up deadline, 2026-27", "value": "May 15, 2026 (passed)", "claim_id": "c2"},
    {"label": "Double, per semester", "value": "$6,872 (2026-27)", "claim_id": "c3"},
    {"label": "Double, academic year", "value": "$13,744 (2026-27)", "claim_id": "c4"},
    {"label": "Single, per semester", "value": "$7,783 (2026-27)", "claim_id": "c5"},
    {"label": "Single, academic year", "value": "$15,566 (2026-27)", "claim_id": "c6"},
    {"label": "Triple or one-room quad, per semester", "value": "$6,322 (2026-27)", "claim_id": "c7"},
    {"label": "Penalty-free cancellation deadline, fall 2026", "value": "June 15, 2026 (passed)", "claim_id": "c8"},
    {"label": "Penalty-free cancellation deadline, spring 2027 term", "value": "December 1, 2026", "claim_id": "c9"},
    {"label": "Cancellation fee after the deadline", "value": "$500", "claim_id": "c10"},
    {"label": "Final three halls opened", "value": "August 15, 2022", "claim_id": "c11"},
    {"label": "Which dorms have air conditioning", "value": "Unknown", "claim_id": None},
]


def _visible(svg: str) -> str:
    """The text a reader sees in the SVG (text elements only; not the accessible <desc>)."""
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", " ".join(re.findall(r"<text[^>]*>(.*?)</text>", svg, re.S))))


def _page(**extra) -> dict:
    page = {"id": "p1", "headline": "Transfer housing at Cornell: what it costs and when to apply", "deck": "D", "section": "Housing", "section_href": "/schools/x/housing/",
            "byline": "Housing desk", "published_at": "2026-11-06T10:00:00+00:00", "updated_at": "2026-11-06T10:00:00+00:00",
            "body_markdown": "Body text here.\n\n[[fact-table]]\n\nMore.", "fact_table": ROWS, "fact_table_caption": "Facts", "next_actions": [], "production_note": "n",
            "sources": [], "held_notice": None, "stale": False, "audience_label": None}
    page.update(extra)
    return page


def _render(page: dict) -> str:
    ctx = engine.site_defaults(publication_name="Footnote Daily", environment="staging")
    ctx.update(canonical_path="/schools/x/housing/h/", template_name="guide", static_prefix="/static/", noindex=True, current_section="/", ad_slots={}, related=[],
               structured_data="", today=TODAY)
    return engine.render("article.html", page=page, **ctx)


def _png(path: Path, w: int, h: int) -> Path:
    raw = b"".join(b"\x00" + b"\x80\x80\x80" * w for _ in range(h))
    chunk = lambda t, d: struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)
    path.write_bytes(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))
    return path


# ------------------------------------------------------------------------------------------------ figures
def test_cost_chart_parses_amounts_and_prints_them_verbatim():
    fig = figures.cost_chart(ROWS)
    assert fig["kind"] == "cost" and fig["title"] == "Per-semester amounts at a glance"
    svg, shown = fig["svg"], _visible(fig["svg"])
    for value in ("$6,872 (2026-27)", "$7,783 (2026-27)", "$6,322 (2026-27)"):  # per-semester rows: the whole value, verbatim
        assert value in shown, value
    for other_basis in ("$13,744", "$15,566", "$500"):  # academic-year rows and the fee are another basis: not on this chart
        assert other_basis not in shown, other_basis
    widths = [float(w) for w in re.findall(r'<rect[^>]*width="([\d.]+)"', svg)]
    assert len(widths) == 3 and widths[1] == max(widths) and abs(widths[0] / widths[1] - 6872 / 7783) < 0.01  # bars from zero, proportional
    assert 'viewBox="0 0 360 ' in svg and 'width="100%"' in svg and 'role="img"' in svg and '<title id="fig-cost-title">' in svg
    assert not re.search(r'width="\d+px"', svg) and "var(--navy" in svg and "var(--ink" in svg
    assert "the table gives them" in fig["caption"]
    # cents are never rounded; a long value prints its first amount only, and the caption says so
    fig2 = figures.cost_chart([{"label": "Double room, 2026-27", "value": "$6,872.50 per semester, per person ($13,745/yr)"},
                               {"label": "Single room, 2026-27", "value": "$7,783.25 per semester, per person ($15,566.50/yr)"}])
    shown2 = _visible(fig2["svg"])
    assert "$6,872.50" in shown2 and "$7,783.25" in shown2 and "$13,745" not in shown2 and "first dollar amount" in fig2["caption"]
    # academic-year rows chart when no semester rows exist; a range is never one bar; two bases with one row each is no chart
    assert figures.cost_chart([{"label": "Double room, 2026-27", "value": "$12,042 per academic year, per person"}, {"label": "Single room, 2026-27", "value": "$13,770 per academic year, per person"}])["title"] == "Academic-year amounts at a glance"
    assert figures.cost_chart([{"label": "Double", "value": "$6,322–$6,872 per semester"}, {"label": "Single", "value": "$7,783 per semester"}]) is None
    assert figures.cost_chart([{"label": "Double, per semester", "value": "$6,872"}, {"label": "Double, academic year", "value": "$13,744"}]) is None


def test_timeline_marks_passed_dates_and_keeps_history_out():
    fig = figures.deadline_timeline(ROWS, TODAY)
    svg, shown = fig["svg"], _visible(fig["svg"])
    assert fig["kind"] == "timeline" and "May 15, 2026 (passed)" in shown and shown.count("(passed)") == 2  # June gets the mark; May's own is not doubled
    assert "June 15, 2026 (passed)" in shown and "December 1, 2026" in shown and "December 1, 2026 (passed)" not in shown
    assert shown.index("May 15") < shown.index("June 15") < shown.index("December 1")  # earliest first
    assert "August 15, 2022" not in shown and "halls opened" not in shown  # a historical date is not a deadline
    assert svg.count('class="badge badge--passed"') == 4 and svg.count('class="badge"') == 2  # an axis dot and a list badge per row
    assert "Today" in shown and "November 6, 2026" in fig["caption"] and 'role="img"' in svg and 'viewBox="0 0 360 ' in svg
    with_year = figures.deadline_timeline(ROWS + [{"label": "Spring housing payment due", "value": "January 15, 2027"}], TODAY)
    assert "2027" in _visible(with_year["svg"])  # a year boundary inside the range gets a year mark
    assert figures.deadline_timeline(ROWS[:3], TODAY) is None  # one dated row is not a timeline
    assert figures.first_date("Sept. 1, 2026 or 2026-09-15") == date(2026, 9, 1) and figures.first_date("August 2022") is None


def test_steps_diagram_escapes_markup_and_caps_at_six():
    fig = figures.steps_diagram(["Apply <early> & pay the fee", "Wait", "", {"text": "Third"}, "Fourth", "Fifth", "Sixth", "Seventh"])
    assert fig["kind"] == "steps" and "&lt;early&gt; &amp; pay" in fig["svg"] and "<early>" not in fig["svg"]
    shown = _visible(fig["svg"])
    assert fig["svg"].count('class="badge"') == 6 and "Third" in shown and "Seventh" not in shown
    assert figures.steps_diagram([]) is None and figures.steps_diagram(["", "  "]) is None


def test_figures_for_page_returns_at_most_two_and_none_for_an_empty_table():
    assert figures.figures_for_page({"fact_table": []}, TODAY) == []
    assert figures.figures_for_page({"fact_table": [{"label": "Residents", "value": "311"}, {"label": "Location", "value": "North Campus"}]}, TODAY) == []
    figs = figures.figures_for_page({"fact_table": ROWS, "steps": ["Apply", "Wait"]}, TODAY)
    assert [f["kind"] for f in figs] == ["cost", "timeline"] and all(set(f) == {"kind", "title", "svg", "caption"} for f in figs)
    assert [f["kind"] for f in figures.figures_for_page({"fact_table": [], "steps": ["Apply", "Wait"]}, TODAY)] == ["steps"]


# ------------------------------------------------------------------------------------------------ article.html
def test_article_renders_figures_after_the_table_and_no_img_without_a_photo():
    page = _page()
    page["figures"] = figures.figures_for_page(page, TODAY)
    html = _render(page)
    assert html.count('<figure class="figure figure--') == 2 and 'class="figure figure--cost"' in html and 'class="figure figure--timeline"' in html
    assert html.index("</table>") < html.index('class="figure figure--cost"') < html.index("<p>More.</p>")
    assert "<img" not in html and "placeholders" not in html
    assert "Per-semester amounts at a glance" in html and "$6,872 (2026-27)" in html and "<figcaption><b class=\"figure__title\">" in html
    assert 'class="figure' not in _render(_page())  # a context without figures renders none


# ------------------------------------------------------------------------------------------------ photo slot
class _FakeConn:
    """Enough of a connection for seo_gate.page_input_from_html's path lookup."""
    def __init__(self, path): self.path = path
    def cursor(self): return self
    def __enter__(self): return self
    def __exit__(self, *a): return False
    def execute(self, *a, **k): pass
    def fetchone(self): return {"path": self.path}


def test_photo_slot_needs_a_rights_record_and_passes_the_gate_image_check(tmp_path):
    images = tmp_path / "images"
    images.mkdir()
    _png(images / "hall.png", 32, 20)
    entry = {"file": "hall.png", "alt": "Hall front", "credit": "Photo: J. Doe", "license": "CC BY 4.0", "caption": "The hall"}
    credits = {"pages": {"/schools/x/housing/h/": entry}}
    img = photos.page_photo("/schools/x/housing/h", credits=credits, photos_dir=images)  # trailing slash optional
    assert img == {"src": "/static/img/photos/hall.png", "file": "hall.png", "alt": "Hall front", "credit": "Photo: J. Doe", "caption": "The hall", "rights": "CC BY 4.0",
                   "source_url": None, "width": 32, "height": 20}
    assert photos.page_photo("/schools/x/housing/h/", credits={"pages": {"/schools/x/housing/h/": dict(entry, license="")}}, photos_dir=images) is None  # no rights record
    assert photos.page_photo("/schools/x/housing/h/", credits={"pages": {"/schools/x/housing/h/": dict(entry, file="../hall.png")}}, photos_dir=images) is None
    assert photos.page_photo("/schools/x/housing/other/", credits=credits, photos_dir=images) is None
    out = tmp_path / "site"
    assert photos.copy_photo(img, out, photos_dir=images) == out / "static" / "img" / "photos" / "hall.png"
    assert (out / "static/img/photos/hall.png").read_bytes() == (images / "hall.png").read_bytes()
    from PIL import Image  # test-only: a real JPEG header for the pure-Python size reader
    Image.new("RGB", (48, 30)).save(images / "quad.jpg", "JPEG")
    assert photos.image_size(images / "quad.jpg") == (48, 30) and photos.image_size(images / "hall.png") == (32, 20)
    # rendered: alt, width, height and data-rights, which is exactly what the SEO gate's image check reads
    html = _render(_page(image=img))
    tag = BeautifulSoup(html, "lxml").find("article").find_all("img")
    assert len(tag) == 1 and tag[0]["alt"] == "Hall front" and tag[0]["width"] == "32" and tag[0]["height"] == "20" and tag[0]["data-rights"] == "CC BY 4.0"
    assert "The hall · Photo: J. Doe" in html
    pin = seo_gate.page_input_from_html(_FakeConn("/schools/x/housing/h/"), uuid4(), html, css_bytes=0, environment="staging", base_url="", primary_query="transfer housing cornell",
                                        secondary_questions=[], real_faq_questions=[], backlinks=1, has_sibling_pages=False, qa_overflow_widths=[], qa_checked_widths=5)
    assert pin.images == [{"alt": "Hall front", "width": "32", "height": "20", "rights_recorded": True, "bytes": 0}]
    assert next(i for i in seo_gate.evaluate(pin).items if i.name == "images").ok


def test_render_version_adds_figures_and_a_credited_photo(clean_conn, tmp_path, monkeypatch):
    from campus_worker.editorial import gates
    from tests.helpers import make_school

    inst, campus, topics = make_school(clean_conn)
    path = "/schools/fixture-state/housing/transfer-housing/"
    with clean_conn.cursor() as cur:
        cur.execute("INSERT INTO pages (institution_id, topic_id, page_format, slug, path) VALUES (%s,%s,'guide','transfer-housing',%s) RETURNING id", (inst, topics["housing"], path))
        pid = cur.fetchone()["id"]
    clean_conn.commit()
    vid = gates.create_version(clean_conn, pid, brief_id=None, headline="Transfer housing at Fixture State: costs and deadlines", deck="d", body_md="Body text here.\n\n[[fact-table]]\n",
                               body_html=None, structured={"fact_table": ROWS}, byline="Housing desk", production_note="n", claim_ids=[], writer_model="m", editor_model=None, verifier_model=None)
    with clean_conn.cursor() as cur:
        cur.execute("UPDATE page_versions SET gate_status='passed' WHERE id=%s", (vid,))
    clean_conn.commit()
    images = tmp_path / "images"
    images.mkdir()
    _png(images / "hall.png", 32, 20)
    (images / "credits.yml").write_text(yaml.safe_dump({"pages": {path: {"file": "hall.png", "alt": "Hall front", "credit": "Photo: J. Doe", "license": "CC BY 4.0"}}}))
    monkeypatch.setattr(photos, "PHOTOS_DIR", images)
    monkeypatch.setattr(photos, "CREDITS_FILE", images / "credits.yml")
    html = site.render_version(clean_conn, vid, out_root=tmp_path / "site").read_text()
    assert 'class="figure figure--cost"' in html and 'class="figure figure--timeline"' in html and "$6,872 (2026-27)" in html
    assert 'data-rights="CC BY 4.0"' in html and 'src="/static/img/photos/hall.png"' in html and (tmp_path / "site/static/img/photos/hall.png").exists()
    (images / "credits.yml").write_text("{}\n")  # no entry for the path: no image at all, never a placeholder
    html2 = site.render_version(clean_conn, vid, out_root=tmp_path / "site2").read_text()
    assert "<img" not in html2 and 'class="figure figure--cost"' in html2
