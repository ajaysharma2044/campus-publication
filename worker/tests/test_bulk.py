"""Bulk mode (specs/bulk-mode.md): batch pricing, sitemap parsing, extraction that keeps only verbatim quotes, the question map and
ranking, plan/gather, the code checks, verdict application, and an end-to-end run with the fake batch client (B1/B2 shape)."""
from __future__ import annotations

import json
from argparse import Namespace
from datetime import date, datetime, timezone

import pytest

from campus_worker import claims as cm
from campus_worker.bulk import batch_client as bc
from campus_worker.bulk import check, crawl, extract, plan, questions, rank, run, verify
from campus_worker.collectors.html import record_snapshot
from campus_worker.config import get_settings
from campus_worker.types import ClaimRecord
from tests.helpers import make_entity, make_school, make_source

SITEMAP_INDEX = b"""<?xml version="1.0"?><sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><sitemap><loc>https://scl.example.edu/sitemap-1.xml</loc></sitemap></sitemapindex>"""
URLSET = b"""<?xml version="1.0"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
<url><loc>http://scl.example.edu/residential-life/housing/rates</loc><lastmod>2026-10-01</lastmod></url>
<url><loc>https://scl.example.edu/residential-life/housing/rates.pdf</loc></url>
<url><loc>https://other.example.edu/x</loc></url>
<url><loc>https://www.scl.example.edu/residential-life/dining/hours?x=1</loc></url>
<url><loc>https://scl.example.edu/residential-life/housing/rates</loc></url></urlset>"""
PAGE_TEXT = "Housing Rates Housing rates include utilities. A double room costs $6,872 per semester for 2026-27. Barbara Fixture Hall has two elevators. The housing application deadline is May 15, 2026."


def test_batch_pricing_uses_the_batch_discount_and_cached_prefix():
    one = bc.price_minor("claude-sonnet-5-5", input_tokens=1_000_000, output_tokens=0, batch=False)
    assert one == 300 and bc.price_minor("claude-sonnet-5-5", input_tokens=1_000_000, output_tokens=0) == 150
    reqs = [bc.BatchRequest(f"w:{i}", "claude-sonnet-5-5", "S" * 40_000, "u" * 4_000, 1_000) for i in range(10)]
    assert bc.estimate_minor(reqs, cached_prefix=True) < bc.estimate_minor(reqs, cached_prefix=False)
    with pytest.raises(KeyError):
        bc.price_minor("unpriced-model", input_tokens=1, output_tokens=1)


def test_sitemap_parsing_and_url_filter():
    children, pages = crawl.parse_sitemap(SITEMAP_INDEX)
    assert children == ["https://scl.example.edu/sitemap-1.xml"] and pages == []
    children, pages = crawl.parse_sitemap(URLSET)
    assert not children and len(pages) == 5
    urls = crawl.filter_urls(pages, host="scl.example.edu", prefixes=["/residential-life/housing"], max_pages=10)
    assert urls == ["https://scl.example.edu/residential-life/housing/rates"]  # http normalized, pdf skipped, other host skipped, dedupe
    assert crawl.filter_urls(pages, host="scl.example.edu", prefixes=None, max_pages=10) == ["https://scl.example.edu/residential-life/housing/rates", "https://www.scl.example.edu/residential-life/dining/hours"]


def _seed(conn):
    inst, campus, topics = make_school(conn)
    with conn.cursor() as cur:
        cur.execute("UPDATE institutions SET identity_status='verified', city='Fixtown' WHERE id=%s", (inst,))
    hall = make_entity(conn, inst, campus, topics["housing"], name="Barbara Fixture Hall", slug="barbara-fixture-hall")
    with conn.cursor() as cur:
        cur.execute("UPDATE entities SET status='active' WHERE id=%s", (hall,))
    sid = make_source(conn, inst, campus, "https://scl.example.edu/residential-life/housing/rates", family="crawl:housing")
    with conn.cursor() as cur:
        cur.execute("UPDATE source_registry SET crawl_section='housing', title='Housing Rates | Fixture State' WHERE id=%s", (sid,))
    snap = record_snapshot(conn, sid, final_url="https://scl.example.edu/residential-life/housing/rates", status=200, content_type="text/html", content_hash="h1", raw_hash=None, byte_size=len(PAGE_TEXT),
                           etag=None, last_modified=None, confidence=0.9, retained_text=PAGE_TEXT, retained_tables=None, material_change=None, outcome="ok")
    conn.commit()
    return inst, campus, topics, hall, sid, snap


def test_extract_keeps_only_verbatim_quotes_and_creates_entities(clean_conn):
    inst, campus, topics, hall, sid, snap = _seed(clean_conn)
    cfg = {"sections": [{"key": "housing", "topic": "housing"}]}
    topic_by_section = extract.section_topic(clean_conn, cfg)
    snaps = extract.pending_snapshots(clean_conn, institution_id=inst, place_ids=[], limit=10)
    assert [s["id"] for s in snaps] == [snap]
    reqs = extract.build_requests(snaps, model="claude-sonnet-5-5", topic_by_section=topic_by_section)
    assert reqs[0].custom_id == f"extract:{snap}" and "PAGE TEXT" in reqs[0].user
    reply = json.dumps({"claims": [
        {"field": "rate.room.double", "value_type": "money", "value": 687200, "currency": "USD", "billing_period": "per_semester", "price_basis": "per_person", "academic_year": "2026-27", "audience": [],
         "entity_name": None, "entity_type": None, "quote": "A double room costs $6,872 per semester for 2026-27.", "is_critical": True, "confidence": 0.9},
        {"field": "amenity.elevator", "value_type": "text", "value": "two elevators", "entity_name": "Barbara Fixture Hall", "entity_type": "residence_hall", "quote": "Barbara Fixture Hall has two elevators.", "confidence": 0.9},
        {"field": "fee.housing_application", "value_type": "money", "value": 0, "quote": "There is no fee to apply for housing", "confidence": 0.9},   # not on the page → dropped
        {"field": "deadline.housing_application", "value_type": "date", "value": "2026-05-15", "academic_year": "2026-27", "quote": "The housing application deadline is May 15, 2026.", "confidence": 0.95}],
        "entities": [{"name": "Fixture Dining Room", "entity_type": "dining_location"}], "processes": []})
    client = bc.FakeBatchClient(lambda r: reply)
    bid = client.submit(reqs)
    stats = extract.process_results(clean_conn, list(client.results(bid)), model="claude-sonnet-5-5", topic_by_section=topic_by_section, batch_id=bid, default_institution_id=inst)
    assert stats["claims_stored"] == 3 and stats["claims_dropped_no_quote"] == 1
    with clean_conn.cursor() as cur:
        cur.execute("SELECT field, entity_id, value_number, value_date FROM claims WHERE institution_id=%s ORDER BY field", (inst,))
        rows = cur.fetchall()
        cur.execute("SELECT count(*) AS n FROM claim_sources cs JOIN claims c ON c.id=cs.claim_id WHERE c.institution_id=%s AND cs.snapshot_id=%s AND cs.excerpt <> ''", (inst, snap))
        assert cur.fetchone()["n"] == 3
        cur.execute("SELECT name FROM entities WHERE institution_id=%s ORDER BY name", (inst,))
        names = [r["name"] for r in cur.fetchall()]
        cur.execute("SELECT extracted_at IS NOT NULL AS done FROM fetch_snapshots WHERE id=%s", (snap,))
        assert cur.fetchone()["done"]
    assert [r["field"] for r in rows] == ["amenity.elevator", "deadline.housing_application", "rate.room.double"]
    assert rows[0]["entity_id"] == hall and rows[2]["value_number"] == 687200 and str(rows[1]["value_date"]) == "2026-05-15"
    assert "Fixture Dining Room" in names
    assert extract.unextracted_count(clean_conn, institution_id=inst, place_ids=[]) == 0


def _store(conn, inst, campus, topic, snap, *, field, entity_id=None, **kw):
    rec = ClaimRecord(institution_id=inst, campus_id=campus, entity_id=entity_id, topic_id=topic, field=field, evidence_category="verified_fact", extraction_method="manual",
                      retrieved_at=datetime.now(timezone.utc), is_critical=cm.is_critical_field(field), **kw)
    return cm.store_claim(conn, rec, snapshot_id=snap, excerpt=kw.pop("_quote", None) if "_quote" in kw else None).claim_id


def _seed_claims(conn):
    inst, campus, topics, hall, sid, snap = _seed(conn)
    housing = topics["housing"]
    quotes = {"rate.room.double": "A double room costs $6,872 per semester for 2026-27.", "amenity.elevator": "Barbara Fixture Hall has two elevators.", "deadline.housing_application": "The housing application deadline is May 15, 2026.",
              "deadline.cancellation_fall": "The housing application deadline is May 15, 2026.", "deadline.cancellation_spring": "The housing application deadline is May 15, 2026.",
              "policy.residency": "Barbara Fixture Hall has two elevators.", "policy.meal_plan": "Barbara Fixture Hall has two elevators.", "eligibility.first_year": "Barbara Fixture Hall has two elevators."}
    ids = {}
    for field, kw in (("rate.room.double", dict(value_type="money", value_number=687200, unit="minor_units", currency="USD", billing_period="per_semester", price_basis="per_person", academic_year="2026-27", room_type="double", entity_id=hall)),
                      ("amenity.elevator", dict(value_type="text", value_text="two elevators", entity_id=hall)),
                      ("deadline.housing_application", dict(value_type="date", value_date=date(2026, 5, 15), academic_year="2026-27")),
                      ("deadline.cancellation_fall", dict(value_type="date", value_date=date(2026, 6, 15), academic_year="2026-27")),
                      ("deadline.cancellation_spring", dict(value_type="date", value_date=date(2026, 12, 1), academic_year="2026-27")),
                      ("policy.residency", dict(value_type="text", value_text="two years on campus", academic_year="2026-27")),
                      ("policy.meal_plan", dict(value_type="text", value_text="meal plan required", academic_year="2026-27")),
                      ("eligibility.first_year", dict(value_type="text", value_text="first-year students", academic_year="2026-27"))):
        rec = ClaimRecord(institution_id=inst, campus_id=campus, topic_id=housing, field=field, evidence_category="verified_fact", extraction_method="manual", retrieved_at=datetime.now(timezone.utc),
                          is_critical=cm.is_critical_field(field), **kw)
        ids[field] = cm.store_claim(conn, rec, snapshot_id=snap, excerpt=quotes[field], locator="test").claim_id
    conn.commit()
    return inst, campus, topics, hall, snap, ids


def test_question_map_ranking_plan_and_gather(clean_conn):
    inst, campus, topics, hall, snap, ids = _seed_claims(clean_conn)
    qstats = questions.build(clean_conn, slug="fixture-state")
    assert qstats["total"] >= 3 and qstats["generated"] >= 3
    with clean_conn.cursor() as cur:
        cur.execute("SELECT question, audience, page_type, primary_query, answer_key FROM bulk_questions WHERE institution_id=%s ORDER BY question", (inst,))
        qs = cur.fetchall()
    texts = [q["question"] for q in qs]
    assert any(t.startswith("Barbara Fixture Hall at Fixture State University") for t in texts)                       # entity guide (2 facts)
    assert any("housing deadlines for 2026-27" in t for t in texts) and any("housing rules" in t for t in texts)          # hubs: 3 deadline claims, 3 policy/eligibility claims
    assert all(q["primary_query"] for q in qs) and any(q["primary_query"] == "Fixture State housing deadlines" for q in qs)
    assert any(q["page_type"] == "entity_guide" for q in qs) and not any("for parents" in t for t in texts)              # audience variants need 5+ facts
    r = rank.rank_all(clean_conn, institution_id=inst, official_domains=("example.edu",), today=date(2026, 11, 6))
    assert r["ranked"] == len(qs) and r["by_class"].get("unscanned") == len(qs)
    out = plan.plan_pages(clean_conn, institution_id=inst, limit=3, run_id="t1")
    assert len(out["planned"]) == 3 and all(p["path"].startswith("/schools/fixture-state/housing/") for p in out["planned"])
    with clean_conn.cursor() as cur:
        cur.execute("SELECT * FROM bulk_pages WHERE run_id='t1' ORDER BY created_at")
        pages = [dict(x) for x in cur.fetchall()]
    g = plan.gather(clean_conn, pages[0], institution_id=inst)
    assert g["fact_count"] >= 1 and all(f["quote"] for f in g["facts"]) and g["hubs"] == ["/schools/fixture-state/housing/", "/schools/fixture-state/"]
    # a second plan skips paths already planned
    again = plan.plan_pages(clean_conn, institution_id=inst, limit=3, run_id="t2")
    assert all(p["path"] not in {q["path"] for q in out["planned"]} for p in again["planned"])


def test_incumbent_classification():
    today = date(2026, 11, 6)
    forum = [{"url": "https://www.reddit.com/r/x/1", "title": "a", "date": "2018"}, {"url": "https://quora.com/q", "title": "b"}, {"url": "https://reddit.com/r/y", "title": "c"}, {"url": "https://scl.cornell.edu/other"}]
    assert rank.classify(forum, question="Is housing guaranteed for transfers at Cornell?", official_domains=("cornell.edu",), today=today)[0] == "forum_only"
    strong = [{"url": "https://scl.cornell.edu/housing-rates", "title": "Housing Rates 2026-27 | Cornell", "date": "2026"}]
    assert rank.classify(strong, question="Cornell housing rates", official_domains=("cornell.edu",), today=today)[0] == "strong_dedicated"
    old = [{"url": "https://blog.example.com/cornell-housing-rates", "title": "Cornell housing rates explained", "date": "2019"}]
    assert rank.classify(old, question="Cornell housing rates", official_domains=("cornell.edu",), today=today)[0] == "outdated"
    assert rank.classify([], question="x", official_domains=(), today=today)[0] == "unscanned"
    assert "we win with" in rank.win_note("forum_only", {"top_hosts": ["reddit.com"], "years_top5": [2018]}, has_costs=True, has_deadlines=False, has_steps=False)


def _gathered():
    return {"facts": [{"id": "c1", "field": "rate.room.double", "value": "$6,872 per person per semester", "academic_year": "2026-27", "audience": [], "entity": "Barbara Fixture Hall", "is_critical": True,
                       "quote": "A double room costs $6,872 per semester for 2026-27.", "source_url": "https://scl.example.edu/rates", "fetched_at": "2026-11-06", "snapshot_id": "s1", "content_hash": "h1"},
                      {"id": "c2", "field": "deadline.housing_application", "value": "May 15, 2026", "academic_year": "2026-27", "audience": [], "entity": None, "is_critical": True,
                       "quote": "The housing application deadline is May 15, 2026.", "source_url": "https://scl.example.edu/rates", "fetched_at": "2026-11-06", "snapshot_id": "s1", "content_hash": "h1"}],
            "link_targets": [{"path": "/schools/fixture-state/housing/transfer-housing/", "anchor_hint": "transfer housing"}], "hubs": ["/schools/fixture-state/housing/", "/schools/fixture-state/"], "sources_hash": "x"}


def test_check_draft_removes_uncited_numbers_bad_quotes_and_adds_links():
    draft = {"title": "How much does Barbara Fixture Hall cost in 2026-27?", "meta": "A double in Barbara Fixture Hall is $6,872 per person per semester in 2026-27, and the housing application deadline was May 15, 2026 for new students.",
             "h1": "How much does Barbara Fixture Hall cost?", "answer": "A double in Barbara Fixture Hall is $6,872 per person per semester in 2026-27. Singles run about $7,900. The deadline was May 15, 2026.",
             "sections": [{"heading": "Details", "body_md": "Rates include utilities. Roughly 311 students live here."}],
             "table": {"caption": "Rates", "rows": [{"label": "Double", "value": "$6,872 per person per semester", "claim_id": "c1"}, {"label": "Single", "value": "$7,900", "claim_id": "c1"}]},
             "steps": None, "next_steps": [{"text": "Read the rates page.", "target": "https://scl.example.edu/rates"}], "not_confirmed": ["Single rates."],
             "claims": [{"claim_id": "c1", "quote": "A double room costs $6,872 per semester for 2026-27.", "used_for": "A double in Barbara Fixture Hall is $6,872 per person per semester in 2026-27."},
                        {"claim_id": "c2", "quote": "The deadline is May 15, 2026 for everyone.", "used_for": "The deadline was May 15, 2026."}, {"claim_id": "zz", "quote": "x", "used_for": "y"}], "internal_links": []}
    out, rep = check.check_draft(draft, _gathered(), question="How much does Barbara Fixture Hall cost in 2026-27?", hubs=_gathered()["hubs"], existing_bodies=["something else entirely"], source_texts={"s1": PAGE_TEXT})
    assert {r["claim_id"] for r in rep["removed_claims"]} == {"c2", "zz"}            # paraphrased quote and unknown id are out
    assert "Singles run about $7,900" not in out["answer"] and "May 15, 2026" not in out["answer"] and "$6,872" in out["answer"]
    assert "311" not in out["sections"][0]["body_md"] and len(out["table"]["rows"]) == 1
    assert rep["seo"]["links_ok"] and any(s["heading"] == "Related guides" for s in out["sections"])
    assert rep["status"] == "ok" and rep["seo"]["title_ok"] and rep["seo"]["answer_first_ok"]
    dup, rep2 = check.check_draft(json.loads(json.dumps(draft)), _gathered(), question="How much does Barbara Fixture Hall cost in 2026-27?", hubs=_gathered()["hubs"], existing_bodies=[draft["answer"] + " " + draft["sections"][0]["body_md"]], source_texts={"s1": PAGE_TEXT})
    assert rep2["overlap_max"] > 0.6 and rep2["status"] == "skip"


def test_apply_verdicts_removes_unsupported_claims_and_body_shape():
    draft = {"title": "t", "meta": "m", "h1": "H", "answer": "A double is $6,872 per semester. The deadline was May 15, 2026.", "sections": [{"heading": "Costs", "body_md": "A double is $6,872 per semester. Utilities are included."}],
             "table": {"caption": "Rates", "rows": [{"label": "Double", "value": "$6,872", "claim_id": "c1"}, {"label": "Deadline", "value": "May 15, 2026", "claim_id": "c2"}]}, "steps": ["Apply.", "Wait."],
             "not_confirmed": ["Single rates."], "claims": [{"claim_id": "c1", "quote": "q1", "used_for": "A double is $6,872 per semester."}, {"claim_id": "c2", "quote": "q2", "used_for": "The deadline was May 15, 2026."}], "next_steps": []}
    out, rep = verify.apply_verdicts(draft, json.dumps({"verdicts": [{"claim_id": "c1", "verdict": "supported"}, {"claim_id": "c2", "verdict": "unsupported", "note": "wrong year"}]}))
    assert rep["removed"] == ["c2"] and "May 15" not in out["answer"] and len(out["table"]["rows"]) == 1
    body = verify.body_markdown(out)
    assert body.startswith("A double is $6,872 per semester.") and "## Costs" in body and "[[fact-table]]" in body and "## Steps" in body and body.rstrip().endswith("- Single rates.")
    out2, rep2 = verify.apply_verdicts(json.loads(json.dumps(draft)), "not json")
    assert out2["claims"] == [] and rep2["parsed"] is False


def test_fake_end_to_end_run_publishes_pages_and_reports(clean_conn, tmp_path, monkeypatch):
    inst, campus, topics, hall, snap, ids = _seed_claims(clean_conn)
    questions.build(clean_conn, slug="fixture-state")
    rank.rank_all(clean_conn, institution_id=inst, official_domains=("example.edu",), today=date(2026, 11, 6))
    from campus_worker.render import site
    monkeypatch.setattr(site, "OUT_DEFAULT", tmp_path / "site")
    monkeypatch.setattr(run, "RUNS_DIR", tmp_path / "runs")
    monkeypatch.setenv("CAMPUS_API_DAILY_CAP_USD", "25")
    args = Namespace(school="fixture-state", run_id="fake-run", limit=4, chunk=500, dry_run=False, fake=True, resume=False, deploy=False, include_existing=False)
    assert run.cmd_run(args, get_settings(), conn=clean_conn) == 0
    report = json.loads((tmp_path / "runs" / "fake-run.json").read_text())
    assert report["outcome"] == "completed" and len(report["published"]) >= 1 and report["cost_minor"] >= 0 and report["mode"] == "fake"
    with clean_conn.cursor() as cur:
        cur.execute("SELECT stage, count(*) AS n FROM bulk_pages WHERE run_id='fake-run' GROUP BY stage")
        stages = {r["stage"]: r["n"] for r in cur.fetchall()}
        cur.execute("SELECT p.path, v.gate_status, v.rubric, v.body_markdown FROM pages p JOIN page_versions v ON v.id=p.current_version_id WHERE p.institution_id=%s", (inst,))
        pages = cur.fetchall()
    assert stages.get("published", 0) >= 1
    assert all(p["gate_status"] == "passed" and p["rubric"].get("bulk") for p in pages)
    assert any((tmp_path / "site" / p["path"].strip("/") / "index.html").exists() for p in pages)
    # resume: nothing left to do, no new pages, report still written
    assert run.cmd_run(Namespace(**{**vars(args), "resume": True}), get_settings(), conn=clean_conn) == 0


def test_spend_cap_refuses_a_batch_over_the_daily_cap(clean_conn, monkeypatch):
    monkeypatch.setenv("CAMPUS_API_DAILY_CAP_USD", "0.01")
    reqs = [bc.BatchRequest("w:1", "claude-sonnet-5-5", "S" * 4000, "u" * 4000, 2000)]
    with pytest.raises(run.SpendCapExceeded):
        run._submit(clean_conn, bc.FakeBatchClient(), kind="write", requests=reqs, run_id="cap", log=lambda m: None)
    monkeypatch.setenv("CAMPUS_API_DAILY_CAP_USD", "25")
    bid = run._submit(clean_conn, bc.FakeBatchClient(), kind="write", requests=reqs, run_id="cap", log=lambda m: None)
    with clean_conn.cursor() as cur:
        cur.execute("SELECT status, est_cost_minor FROM bulk_batches WHERE id=%s", (bid,))
        row = cur.fetchone()
    assert row["status"] == "in_progress" and row["est_cost_minor"] >= 1


def test_a_disallowed_path_does_not_switch_the_domain_off(clean_conn):
    """One robots-disallowed URL (a /search/ hit from a sitemap) must not record robots_allows=false for the whole domain pattern."""
    from campus_worker import permissions
    from campus_worker.fetcher import SafeFetcher
    permissions.seed_defaults(clean_conn)
    f = SafeFetcher(clean_conn)
    f._robots["scl.cornell.edu"] = "User-agent: *\nDisallow: /search/\n"
    assert f.robots_ok("https://scl.cornell.edu/search/x") is False
    assert permissions.check_url(clean_conn, "https://scl.cornell.edu/residential-life/housing/").allowed
    assert f.robots_ok("https://scl.cornell.edu/residential-life/housing/") is True
    f._robots["closed.cornell.edu"] = "User-agent: *\nDisallow: /\n"
    assert f.robots_ok("https://closed.cornell.edu/anything") is False
    assert permissions.check_url(clean_conn, "https://closed.cornell.edu/other").reason == "robots_disallow_recorded"
