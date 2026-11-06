"""Writing quality system + SEO gate (specs/continuous-local-run.md R37, R38, R39, R45; AT37, AT38, AT39, AT44 fixture parts)."""
import json
from pathlib import Path

import pytest

from campus_worker import claims, quality, seo, seo_gate
from campus_worker.editorial import checks
from campus_worker.editorial import gates
from tests.helpers import make_entity, make_school
from tests.test_claims import _money
from tests.test_gates import RUBRIC_OK

ROOT = Path(__file__).resolve().parents[2]
FIX = ROOT / "fixtures" / "synthetic" / "editorial"


# ------------------------------------------------------------------------------------------------ AT39 style guide + filler check
def test_style_guide_exists_and_filler_check_flags_ai_tells_and_passes_clean_text():
    assert (ROOT / "docs" / "editorial" / "style.md").exists()
    tells = (FIX / "draft_filler.md").read_text()
    clean = (FIX / "draft_clean.md").read_text()
    f_tells = checks.check_filler(tells) + checks.check_openings(tells)
    assert f_tells and any("filler" in f.kind for f in f_tells)
    hit = " ".join(f.detail for f in f_tells).lower()
    for phrase in ("navigating", "delve", "important to note", "whether you"):
        assert phrase in hit, phrase
    assert checks.check_filler(clean) == [] and checks.check_openings(clean) == []


# ------------------------------------------------------------------------------------------------ AT37 information gain
def test_information_gain_fewer_than_three_sets_cluster_to_watch(clean_conn):
    from campus_worker.discovery import QuestionInput, ingest
    inst, campus, topics = make_school(clean_conn)
    ent = make_entity(clean_conn, inst, campus, topics["housing"])
    cids = [claims.store_claim(clean_conn, _money(inst, campus, topics["housing"], ent, 1204200 + i, room=f"r{i}"), snapshot_id=None).claim_id for i in range(3)]
    ingest(clean_conn, [QuestionInput(raw_text="fixture hall cost", origin="related_question", institution_id=inst, campus_id=campus, topic_key="housing", source_ref="s1")])
    with clean_conn.cursor() as cur:
        cur.execute("SELECT id FROM intent_clusters WHERE institution_id=%s LIMIT 1", (inst,))
        cluster = cur.fetchone()["id"]
    g = quality.apply_information_gain(clean_conn, cluster, [{"item": "per-person rate", "claim_id": str(cids[0])}, {"item": "deposit rule", "claim_id": str(cids[1])}])
    assert not g.ok and "set to watch" in g.reason
    with clean_conn.cursor() as cur:
        cur.execute("SELECT queue_state, queue_reason FROM intent_clusters WHERE id=%s", (cluster,))
        r = cur.fetchone()
    assert r["queue_state"] == "watch" and "information gain" in r["queue_reason"]
    # three verified claim-linked items pass; an unknown or estimate claim does not count
    g2 = quality.check_information_gain(clean_conn, [{"item": f"fact {i}", "claim_id": str(c)} for i, c in enumerate(cids)] + [{"item": "made up", "claim_id": "00000000-0000-0000-0000-000000000000"}])
    assert g2.ok and len(g2.items) == 3 and g2.missing_claim_ids == ["00000000-0000-0000-0000-000000000000"]


# ------------------------------------------------------------------------------------------------ AT38 competitor-beat review
def test_beat_review_loses_once_then_held(clean_conn):
    inst, campus, topics = make_school(clean_conn)
    with clean_conn.cursor() as cur:
        cur.execute("INSERT INTO pages (institution_id, topic_id, page_format, slug, path) VALUES (%s,%s,'guide','g','/schools/fixture-state/housing/g/') RETURNING id", (inst, topics["housing"]))
        pid = cur.fetchone()["id"]
    clean_conn.commit()
    vid = gates.create_version(clean_conn, pid, brief_id=None, headline="Fixture guide: what the rate includes", deck="d", body_md="x " * 200, body_html=None, structured={}, byline="Housing desk",
                               production_note="n", claim_ids=[], writer_model="m", editor_model=None, verifier_model=None)
    comps = [{"url": "https://a.example.invalid", "scores": {k: 3 for k in quality.BEAT_ITEMS}}, {"url": "https://b.example.invalid", "scores": {k: 2 for k in quality.BEAT_ITEMS}}]
    r1 = quality.score_review({k: 3 for k in quality.BEAT_ITEMS}, comps, round_no=1)      # ties the best competitor → not a beat
    assert not r1.passed and r1.outcome == "resend_to_writer"
    quality.record_review(clean_conn, vid, r1)
    r2 = quality.score_review(dict({k: 4 for k in quality.BEAT_ITEMS}, local_knowledge=2), comps, round_no=quality.previous_round(clean_conn, vid) + 1)  # one item < 3
    assert not r2.passed and r2.outcome == "held" and "local_knowledge" in r2.weakest_items
    quality.record_review(clean_conn, vid, r2)
    with clean_conn.cursor() as cur:
        cur.execute("SELECT p.status, v.beat_review FROM pages p JOIN page_versions v ON v.page_id=p.id WHERE v.id=%s", (vid,))
        row = cur.fetchone()
    assert row["status"] == "held" and row["beat_review"]["round"] == 2 and len(row["beat_review"]["history"]) == 2
    ok = quality.score_review({k: 4 for k in quality.BEAT_ITEMS}, comps, round_no=1)
    assert ok.passed and ok.outcome == "passed" and ok.our_total == 24
    extra = quality.beat_review_packet_extra("draft", "h", [], [{"url": "u", "title": "t", "summary": "s"}])
    assert extra["mode"] == "beat_review" and "draft_markdown" in extra and "drafting" not in json.dumps(extra).lower().replace("drafting conversation", "")


# ------------------------------------------------------------------------------------------------ AT44 SEO gate
def _good_page(**over) -> seo_gate.PageInput:
    base = dict(path="/schools/fixture-state/housing/fixture-hall/", title="Fixture Hall: rooms, cost and what to know", meta_description="Fixture Hall double rooms cost $12,042 per person for 2026-27. Who can live there, what the rate includes, and what we could not verify.",
                h1s=["Fixture Hall: rooms, cost and what to know"], h2h3s=["Is Fixture Hall good for transfers?", "What it costs", "Where it is"], opening_paragraph="Fixture Hall double rooms cost $12,042 per person for the 2026-27 year and are open to first-year and returning undergraduates.",
                primary_query="fixture hall review", secondary_questions=["is fixture hall good for transfers"], json_ld=[{"@type": "Article"}, {"@type": "BreadcrumbList"}], page_type="Article",
                internal_links=[{"href": "/schools/fixture-state/housing/riverside-hall/", "anchor": "Riverside Hall rooms and cost"}, {"href": "/schools/fixture-state/housing/compare/fixture-hall-vs-riverside-hall/", "anchor": "Fixture Hall vs Riverside Hall"},
                                {"href": "/schools/fixture-state/housing/eligibility/", "anchor": "Who can live on campus"}, {"href": "/schools/fixture-state/housing/", "anchor": "Housing at Fixture State"}, {"href": "/schools/fixture-state/", "anchor": "Fixture State University"}],
                topic_hub="/schools/fixture-state/housing/", scope_hub="/schools/fixture-state/", backlinks=2, canonical="https://example.org/schools/fixture-state/housing/fixture-hall/", noindex=False, environment="production",
                images=[], html_css_bytes=60_000, qa_overflow_widths=[], qa_checked_widths=5, visible_updated_date=True, time_bound_facts_with_year=True)
    base.update(over)
    return seo_gate.PageInput(**base)


@pytest.mark.parametrize("over,expect", [
    ({"title": "Fixture Hall: rooms, cost, location, amenities, policies and everything else to know"}, "title_length"),
    ({"meta_description": "Short."}, "meta_length"),
    ({"h1s": ["A", "B"]}, "one_h1"),
    ({"json_ld": [{"@type": "Article"}]}, "structured_data_breadcrumb"),
    ({"internal_links": [{"href": "/schools/fixture-state/housing/", "anchor": "Housing at Fixture State"}, {"href": "/schools/fixture-state/", "anchor": "Fixture State University"}]}, "internal_links_three_contextual"),
    ({"backlinks": 0}, "not_orphan"),
    ({"path": "/Schools/Fixture State/housing/x/"}, "url_policy"),
    ({"opening_paragraph": "In today's world there are many things to consider when thinking about residence halls and the many wonderful options that students may wish to explore during their time on campus as part of their journey toward finding a place to live that fits them, their friends, their budget, their schedule and their hopes for the coming academic year and beyond."}, "answer_first"),
    ({"json_ld": [{"@type": "Article"}, {"@type": "BreadcrumbList"}, {"@type": "FAQPage"}], "real_faq_questions": []}, "structured_data_faq_only_real"),
    ({"html_css_bytes": 200_000}, "performance_size"),
    ({"qa_overflow_widths": [360]}, "performance_no_overflow"),
    ({"noindex": True}, "indexable"),
    ({"title": "Riverside Hall review"}, "title_contains_primary_query"),
])
def test_seo_gate_fails_each_item_individually(over, expect):
    r = seo_gate.evaluate(_good_page(**over))
    assert not r.passed and expect in r.failed, (r.failed, expect)


def test_seo_gate_duplicate_meta_and_cannibalization_and_compliant_page(clean_conn):
    assert seo_gate.evaluate(_good_page()).passed
    r = seo_gate.evaluate(_good_page(), existing_descriptions={_good_page().meta_description})
    assert "meta_unique" in r.failed
    r2 = seo_gate.evaluate(_good_page(), other_page_for_primary="/schools/fixture-state/housing/other/")
    assert "no_cannibalization" in r2.failed
    # first page under a hub is exempt from the non-hub backlink rule but still must not be an orphan
    r3 = seo_gate.evaluate(_good_page(backlinks=1, has_sibling_pages=False))
    assert r3.passed
    # record holds the page with the item named
    inst, campus, topics = make_school(clean_conn)
    with clean_conn.cursor() as cur:
        cur.execute("INSERT INTO pages (institution_id, topic_id, page_format, slug, path, status) VALUES (%s,%s,'guide','g','/schools/fixture-state/housing/g/','staged') RETURNING id", (inst, topics["housing"]))
        pid = cur.fetchone()["id"]
    clean_conn.commit()
    vid = gates.create_version(clean_conn, pid, brief_id=None, headline="G: what the rate includes", deck="d", body_md="x " * 200, body_html=None, structured={}, byline="Housing desk",
                               production_note="n", claim_ids=[], writer_model="m", editor_model=None, verifier_model=None)
    seo_gate.record(clean_conn, vid, seo_gate.evaluate(_good_page(h1s=["A", "B"])))
    with clean_conn.cursor() as cur:
        cur.execute("SELECT status, revalidation_reason FROM pages WHERE id=%s", (pid,))
        row = cur.fetchone()
    assert row["status"] == "held" and "one_h1" in row["revalidation_reason"] and not seo_gate.passed_record(clean_conn, vid)
    seo_gate.record(clean_conn, vid, seo_gate.evaluate(_good_page()))
    assert seo_gate.passed_record(clean_conn, vid)


def test_towns_url_policy_and_title_limit():
    assert seo.classify_url("/towns/ithaca-ny/town-transit-local/route-30/").indexable
    assert seo.classify_url("/towns/ithaca-ny/").indexable and not seo.classify_url("/towns/Ithaca/x/").indexable
    title, desc = seo.title_and_description("Fixture Hall: rooms, cost and what to know for transfer students in 2026-27", "deck", "Footnote Daily")
    assert len(title) <= 60 + len(" — Footnote Daily") + 2


def test_seo_gate_treats_typographic_apostrophes_as_the_same_words():
    from campus_worker import seo_gate
    assert seo_gate._contains_query("What is Cornell’s current housing policy for transfer students?", "What is Cornell's current housing policy for transfer students?")
    assert seo_gate._contains_query("Is Housing Guaranteed for Cornell Transfer Students?", "Is housing guaranteed for transfer students at Cornell?")
