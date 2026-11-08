"""Reader-first site rules (owner decision 2026-11-06): no internals on public pages, official sources with clean titles, one brand,
no staging banner, a homepage of guides and topics, practical topics first in the lean queue, a cap on verifier rounds."""
from __future__ import annotations

import re

from campus_worker import lean
from campus_worker.cms.publisher import clean_source_title
from campus_worker.render import engine, site


def test_site_defaults_have_no_banner_and_one_verify_link():
    ctx = engine.site_defaults(publication_name="Footnote Daily", environment="staging")
    assert ctx["site"]["staging_banner"] is False
    assert ctx["site"]["name"] == "Footnote Daily" and ctx["site"]["working_title"] is False
    labels = [l["label"] for l in ctx["site"]["footer_links"]]
    assert labels.count("How we verify") == 1 and "Editorial methods & automation" not in labels
    assert all(l["label"] != "Tools" for l in ctx["site"]["nav"])


def _shell(template: str, **extra) -> str:
    ctx = engine.site_defaults(publication_name="Footnote Daily", environment="staging")
    ctx.update(canonical_path="/", template_name="home", static_prefix="/static/", noindex=True, current_section="/", ad_slots={}, related=[])
    ctx.update(extra)
    return engine.render(template, **ctx)


def test_home_lists_guides_with_dates_and_a_topic_grid_and_hides_empty_tools():
    guides = [{"href": "/schools/x/housing/a/", "headline": "A guide", "deck": "d", "date": "2026-11-06T10:00:00+00:00", "topic": "Housing", "school": "Fixture State"}]
    grid = [{"label": "Housing", "blurb": "b", "count": 1, "href": "/topics/housing/"}, {"label": "Dining", "blurb": "b", "count": 0, "href": None}]
    html = _shell("home.html", lead={"section": "Housing · Fixture State", "section_href": "/schools/x/housing/", "href": "/schools/x/housing/a/", "headline": "A guide", "deck": "d", "updated": "2026-11-06T10:00:00+00:00"},
                  guides=guides, topic_grid=grid, tools=[], schools=[{"name": "Fixture State", "href": "/schools/x/", "pages": 1}])
    assert "Latest guides" in html and "November 6, 2026" in html
    assert 'href="/topics/housing/"' in html and "Not covered yet" in html
    for internal in ("How this site works", "in the registry", "Tools", "staging-banner", "No human editor", "Recent verified updates"):
        assert internal not in html, internal


def test_article_sources_show_clean_titles_and_no_labels():
    page = {"id": "p1", "headline": "H", "deck": "D", "section": "Housing", "section_href": "/schools/x/housing/", "byline": "Housing desk",
            "published_at": "2026-11-06T10:00:00+00:00", "updated_at": "2026-11-06T10:00:00+00:00", "body_markdown": "Body text here.\n\n[[fact-table]]\n",
            "fact_table": [], "next_actions": [], "production_note": "Produced by the publication's automated system. No human editor reviewed this version.",
            "sources": [{"url": "https://example.edu/housing-rates", "title": "Housing Rates", "retrieved_at": "2026-11-06T10:00:00+00:00", "kind": "official_html", "publisher": "Example"}],
            "held_notice": None, "stale": False, "audience_label": "first year"}
    html = _shell("article.html", page=page, structured_data="", canonical_path="/schools/x/housing/h/", template_name="guide")
    assert ">Housing Rates</a>" in html and "checked November 6, 2026" in html
    assert "official_html" not in html and "No human editor" not in html and "For: first year" not in html
    assert "Substantively updated" not in html


def test_clean_source_title_strips_site_suffix_and_falls_back_to_the_slug():
    assert clean_source_title("Housing Rates | Student & Campus Life | Cornell University", "https://x/housing-rates") == "Housing Rates"
    assert clean_source_title("As an admitted student, how do I sign up for housing? - Frequently Asked Questions", "https://x/377-q/") == "As an admitted student, how do I sign up for housing?"
    assert clean_source_title(None, "https://faq.example.edu/kb/article/377-as-an-admitted-student-how-do-i-sign-up-for-housing/") == "As an admitted student how do i sign up for housing"


def test_topic_tiles_match_pages_by_topic_key_or_audience():
    pages = [{"topic_key": "housing", "audience": "transfer"}, {"topic_key": "dining", "audience": None}]
    by_label = {t["label"]: site.tile_pages(pages, t) for t in site.TOPIC_TILES}
    assert len(by_label["Housing"]) == 1 and len(by_label["Transfer"]) == 1 and len(by_label["Dining"]) == 1
    assert by_label["Parents"] == [] and by_label["Costs"] == []
    assert [t["label"] for t in site.TOPIC_TILES] == ["Housing", "Costs", "Transfer", "Dining", "Getting around", "Parents"]


def test_lean_queue_orders_practical_topics_first_and_caps_verifier_rounds():
    assert lean.topic_rank("costs_aid") < lean.topic_rank("housing") < lean.topic_rank("transfer") < lean.topic_rank("alumni_giving")
    assert lean.MAX_VERIFIER_ROUNDS == 3
