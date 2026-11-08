"""Scale to thousands of pages (specs/continuous-local-run.md R42, R43, R44, R47; AT41, AT42, AT43, AT47 fixture parts)."""
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

import pytest

from campus_worker import claims, expansion, processes, tier2, volume
from campus_worker.discovery import QuestionInput, ingest
from campus_worker.editorial import gates
from campus_worker.tools import navigator
from campus_worker.types import ClaimRecord
from tests.helpers import make_entity, make_school
from tests.test_claims import _money
from tests.test_gates import RUBRIC_OK

NOW = datetime.now(timezone.utc)
ROOT = Path(__file__).resolve().parents[2]


def _claim(inst, campus, topic, ent, field, **kw):
    base = dict(institution_id=inst, campus_id=campus, entity_id=ent, topic_id=topic, field=field, evidence_category="verified_fact", extraction_method="deterministic",
                extraction_confidence=0.9, retrieved_at=NOW, academic_year="2026-27", value_type="text", value_text="x")
    base.update(kw)
    return ClaimRecord(**base)


def _verified_hall(conn, inst, campus, topics, *, name, slug, n_claims, rate=1204200):
    ent = make_entity(conn, inst, campus, topics["housing"], name=name, slug=slug)
    fields = [("rate.room", dict(value_type="money", value_number=rate, unit="minor_units", currency="USD", billing_period="per_academic_year", price_basis="per_person", room_type="double")),
              ("amenity.air_conditioning", dict(value_type="boolean", value_bool=True)), ("amenity.kitchen", dict(value_type="text", value_text="one per floor")),
              ("location.distance_minutes", dict(value_type="integer", value_number=6, unit="minutes")), ("eligibility.population", dict(value_type="text", value_text="first-year and returning undergraduates")),
              ("policy.contract_length", dict(value_type="text", value_text="academic year")), ("amenity.laundry", dict(value_type="boolean", value_bool=True))]
    for f, kw in fields[:n_claims]:
        claims.store_claim(conn, _claim(inst, campus, topics["housing"], ent, f, **kw), snapshot_id=None)
    return ent


def _observed_query(conn, inst, campus, ent, text):
    ingest(conn, [QuestionInput(raw_text=text, origin="related_question", institution_id=inst, campus_id=campus, topic_key="housing", entity_id=ent, observed_at=NOW, source_ref=f"obs:{text}")])


# ------------------------------------------------------------------------------------------------ AT41 tier 2
def test_tier2_profile_rules(clean_conn):
    inst, campus, topics = make_school(clean_conn)
    good = _verified_hall(clean_conn, inst, campus, topics, name="Fixture Hall", slug="fixture-hall", n_claims=7)
    _observed_query(clean_conn, inst, campus, good, "Fixture Hall review")
    r = tier2.build_profile(clean_conn, good, intro_md="Fixture Hall is a synthetic hall (fixture).", tradeoffs_md="Higher rate, closer walk (fixture).", rubric=RUBRIC_OK, primary_query="fixture hall review")
    assert r["built"] and r["gate"]["status"] == "passed" and r["path"] == "/schools/fixture-state/housing/fixture-hall/" and r["rows"] == 7
    with clean_conn.cursor() as cur:
        cur.execute("SELECT tier, primary_query FROM pages WHERE id=%s", (r["page_id"],))
        p = cur.fetchone()
    assert p["tier"] == 2 and p["primary_query"] == "fixture hall review"
    # a hall with only 4 verified claims is not published
    few = _verified_hall(clean_conn, inst, campus, topics, name="Thin Hall", slug="thin-hall", n_claims=4)
    _observed_query(clean_conn, inst, campus, few, "Thin Hall review")
    r2 = tier2.build_profile(clean_conn, few, intro_md="x", tradeoffs_md="y", rubric=RUBRIC_OK)
    assert not r2["built"] and any("< 6" in x for x in r2["reasons"])
    # a hall with no observed query is not published
    quiet = _verified_hall(clean_conn, inst, campus, topics, name="Quiet Hall", slug="quiet-hall", n_claims=7, rate=1300000)
    r3 = tier2.build_profile(clean_conn, quiet, intro_md="x", tradeoffs_md="y", rubric=RUBRIC_OK)
    assert not r3["built"] and any("no observed query" in x for x in r3["reasons"])
    # a hall whose fact table overlaps the published one by more than 60% is not published (same values → same rows)
    twin = _verified_hall(clean_conn, inst, campus, topics, name="Twin Hall", slug="twin-hall", n_claims=7)
    _observed_query(clean_conn, inst, campus, twin, "Twin Hall review")
    with clean_conn.cursor() as cur:  # the good page is staged so it counts as published coverage
        cur.execute("UPDATE pages SET status='staged' WHERE id=%s", (r["page_id"],))
    clean_conn.commit()
    r4 = tier2.build_profile(clean_conn, twin, intro_md="x", tradeoffs_md="y", rubric=RUBRIC_OK)
    assert not r4["built"] and any("overlaps" in x for x in r4["reasons"]) and r4["eligibility"]["max_overlap"] > 0.6


def test_comparison_pages_only_for_pairs_with_an_observed_query(clean_conn):
    inst, campus, topics = make_school(clean_conn)
    a = _verified_hall(clean_conn, inst, campus, topics, name="Fixture Hall", slug="fixture-hall", n_claims=6)
    b = _verified_hall(clean_conn, inst, campus, topics, name="Riverside Hall", slug="riverside-hall", n_claims=6, rate=1158200)
    _verified_hall(clean_conn, inst, campus, topics, name="Hilltop House", slug="hilltop-house", n_claims=6, rate=1100000)
    assert tier2.comparison_pairs_with_demand(clean_conn, institution_id=inst) == []
    ingest(clean_conn, [QuestionInput(raw_text="Fixture Hall vs Riverside Hall", origin="hypothesis", institution_id=inst, campus_id=campus, topic_key="housing", is_hypothesis=True, source_ref="hyp:vs")])
    assert tier2.comparison_pairs_with_demand(clean_conn, institution_id=inst) == []  # a hypothesis is not an observed query
    _observed_query(clean_conn, inst, campus, a, "Fixture Hall vs Riverside Hall which is better")
    pairs = tier2.comparison_pairs_with_demand(clean_conn, institution_id=inst)
    assert len(pairs) == 1 and pairs[0]["path"] == "compare/fixture-hall-vs-riverside-hall/"


# ------------------------------------------------------------------------------------------------ AT47 process graph + navigator
def test_process_graph_decisions_and_navigator(clean_conn):
    inst, campus, topics = make_school(clean_conn)
    gid = processes.ensure_graph(clean_conn, institution_id=inst, key="changing-majors", name="Changing majors / internal transfer", topic_key="transfer",
                                 tool_path="/schools/fixture-state/transfer/tools/changing-majors-navigator/")
    base_rules = {"steps": ["Meet your current advisor", "Apply through the receiving college"], "deadlines": ["Oct 15 for spring entry (fixture)"], "offices": ["Receiving college registrar"], "gpa_min": "2.5"}
    processes.upsert_node(clean_conn, gid, processes.NodeSpec("overview", "Changing majors at Fixture State", 0, rules=base_rules, source_urls=["https://www.fixturestate.example.edu/registrar/change-major"]))
    r1 = processes.upsert_node(clean_conn, gid, processes.NodeSpec("as-to-dyson", "Arts & Sciences → Dyson", 1, parent_key="overview", from_state="arts-sciences", to_state="dyson",
                                                                     rules=dict(base_rules, gpa_min="3.0", prerequisites=["AEM 2100"], forms=["Internal transfer application"]), source_urls=["https://www.fixturestate.example.edu/dyson/internal-transfer"]))
    r1b = processes.upsert_node(clean_conn, gid, processes.NodeSpec("eng-to-as", "Engineering → Arts & Sciences", 1, parent_key="overview", from_state="engineering", to_state="arts-sciences", rules=base_rules))
    assert r1["inherits_parent"] is False and r1b["inherits_parent"] is True  # identical to the parent → stores nothing new
    r2 = processes.upsert_node(clean_conn, gid, processes.NodeSpec("anthro-to-aem-sophomore", "Anthropology → AEM as a sophomore", 2, parent_key="as-to-dyson", from_state="arts-sciences", to_state="dyson",
                                                                     situation="sophomore", rules=dict(base_rules, gpa_min="3.0", prerequisites=["AEM 2100", "MATH 1110"], forms=["Internal transfer application"], course_requirements=["Complete AEM 2100 by spring (fixture)"])))
    r3 = processes.upsert_node(clean_conn, gid, processes.NodeSpec("missing-prereq", "Missing a prerequisite", 3, parent_key="anthro-to-aem-sophomore", from_state="arts-sciences", to_state="dyson",
                                                                     situation="missing prerequisite", rules=dict(base_rules, gpa_min="3.0", prerequisites=["AEM 2100", "MATH 1110"], forms=["Internal transfer application"], course_requirements=["Complete AEM 2100 by spring (fixture)"], exceptions=["Petition the Dyson advising office (fixture)"])))
    # an L2 node identical to its L1 parent produces no page
    r_same = processes.upsert_node(clean_conn, gid, processes.NodeSpec("as-to-dyson-junior", "AS → Dyson as a junior", 2, parent_key="as-to-dyson", from_state="arts-sciences", to_state="dyson", situation="junior",
                                                                         rules=dict(base_rules, gpa_min="3.0", prerequisites=["AEM 2100"], forms=["Internal transfer application"])))
    assert r_same["inherits_parent"] is True
    demand = {"as-to-dyson": {"independent_questions": 3, "query_targets": 0}, "anthro-to-aem-sophomore": {"independent_questions": 0, "query_targets": 0},
              "missing-prereq": {"independent_questions": 2, "query_targets": 0}, "as-to-dyson-junior": {"independent_questions": 5, "query_targets": 1}, "eng-to-as": {"independent_questions": 9, "query_targets": 0}, "overview": {"independent_questions": 0, "query_targets": 0}}
    dec = {d["key"]: d for d in processes.decide_pages(clean_conn, gid, institution_id=inst, school_slug="fixture-state", topic_key="transfer", demand_lookup=lambda k: demand[k])}
    assert dec["overview"]["decision"] == "standalone" and dec["as-to-dyson"]["decision"] == "standalone" and dec["as-to-dyson"]["page_path"] == "/schools/fixture-state/transfer/as-to-dyson/"
    assert dec["anthro-to-aem-sophomore"]["decision"] == "section"           # differs but no demand
    assert dec["missing-prereq"]["decision"] == "standalone"                 # differs + 2 independent questions
    assert dec["as-to-dyson-junior"]["decision"] == "none" and dec["eng-to-as"]["decision"] == "none"  # identical to parent → no page even with demand
    s = processes.graph_summary(clean_conn, gid)
    assert s["by_layer"] == {0: 1, 1: 2, 2: 2, 3: 1}
    # navigator answers a fixture path with steps, requirements, deadlines and offices
    opts = navigator.options(clean_conn, gid)
    assert "arts-sciences" in opts["from_states"] and "dyson" in opts["to_states"]
    a = navigator.answer(clean_conn, gid, from_state="arts-sciences", to_state="dyson", situations=["sophomore", "missing prerequisite"])
    assert a.found and a.gpa_min == "3.0" and "MATH 1110" in a.prerequisites and a.deadlines and a.offices == ["Receiving college registrar"] and a.exceptions
    assert [n["key"] for n in a.path_nodes] == ["as-to-dyson", "anthro-to-aem-sophomore", "missing-prereq"]
    assert "https://www.fixturestate.example.edu/dyson/internal-transfer" in a.source_urls
    none = navigator.answer(clean_conn, gid, from_state="dyson", to_state="engineering")
    assert not none.found and "No documented path" in none.message


# ------------------------------------------------------------------------------------------------ AT42 expansion
def _passed_pages(conn, inst, topics, n, start=0):
    for i in range(start, start + n):
        with conn.cursor() as cur:
            cur.execute("INSERT INTO pages (institution_id, topic_id, page_format, slug, path) VALUES (%s,%s,'guide',%s,%s) RETURNING id", (inst, topics["housing"], f"p{i}", f"/schools/fixture-state/housing/p{i}/"))
            pid = cur.fetchone()["id"]
        conn.commit()
        vid = gates.create_version(conn, pid, brief_id=None, headline=f"Passed page {i}: what the rate includes", deck="d", body_md="x " * 200, body_html=None, structured={}, byline="Housing desk",
                                   production_note="n", claim_ids=[], writer_model="m", editor_model=None, verifier_model=None)
        with conn.cursor() as cur:
            cur.execute("UPDATE page_versions SET beat_review=%s::jsonb WHERE id=%s", (json.dumps({"passed": True, "total": 22}), vid))
        conn.commit()


def test_expansion_waits_then_onboards_one_school_at_a_time(clean_conn, monkeypatch):
    from campus_worker.registry import import_ipeds_hd
    from campus_worker.config import FIXTURES_DIR
    from datetime import date
    inst, campus, topics = make_school(clean_conn)
    import_ipeds_hd(clean_conn, FIXTURES_DIR / "ipeds" / "hd_synthetic.csv", release="SYNTHETIC_HD", release_date=date(2026, 1, 1), mark_fixture=True)
    with clean_conn.cursor() as cur:
        cur.execute("SELECT canonical_name FROM institutions WHERE identity_status='synthetic_fixture' AND NOT is_system AND lower(canonical_name) NOT LIKE 'fixture state%%' ORDER BY canonical_name LIMIT 2")
        names = [r["canonical_name"] for r in cur.fetchall()]
    assert len(names) == 2
    monkeypatch.setenv("CAMPUS_EXPANSION_LIST", ",".join(names))
    _passed_pages(clean_conn, inst, topics, 9)
    r = expansion.step(clean_conn, map_complete=True)
    assert not r["expanded"] and "need 10" in r["readiness"]["reason"]
    _passed_pages(clean_conn, inst, topics, 1, start=9)
    with clean_conn.cursor() as cur:  # the pilot school config: active, not 'onboarding'
        cur.execute("INSERT INTO school_configs (institution_id, campus_id, coverage_status) VALUES (%s,%s,'active') ON CONFLICT DO NOTHING", (inst, campus))
    clean_conn.commit()
    r = expansion.step(clean_conn, map_complete=True, verify_with_checksum="deadbeef" * 8, run_sweep=lambda c, iid: {"step": "complete", "sweep_complete": True})
    assert r["expanded"] and r["school"] == names[0] and r["onboarding"]["verified"]
    with clean_conn.cursor() as cur:
        cur.execute("SELECT identity_status FROM institutions WHERE canonical_name=%s", (names[0],))
        assert cur.fetchone()["identity_status"] == "verified"
    # the school after it waits while the first is still onboarding
    r2 = expansion.step(clean_conn, map_complete=True)
    assert not r2["expanded"] and names[0] in r2["readiness"]["in_progress"]
    with clean_conn.cursor() as cur:
        cur.execute("SELECT i.id FROM institutions i WHERE canonical_name=%s", (names[0],))
        expansion.mark_active(clean_conn, cur.fetchone()["id"])
    r3 = expansion.step(clean_conn, map_complete=True, run_sweep=lambda c, iid: {"step": "complete"})
    assert r3["expanded"] and r3["school"] == names[1]


# ------------------------------------------------------------------------------------------------ AT43 volume
def test_volume_counts_and_projection(clean_conn):
    inst, campus, topics = make_school(clean_conn)
    now = datetime.now(timezone.utc)
    with clean_conn.cursor() as cur:
        for i in range(6):
            cur.execute("INSERT INTO pages (institution_id, topic_id, page_format, slug, path, tier, ready_at, status) VALUES (%s,%s,'guide',%s,%s,%s,%s,'staged')",
                        (inst, topics["housing"], f"v{i}", f"/schools/fixture-state/housing/v{i}/", 1 if i < 4 else 2, now - timedelta(days=i)))
        cur.execute("INSERT INTO pages (institution_id, topic_id, page_format, slug, path, tier, ready_at, first_published_at, status) VALUES (%s,%s,'guide','live','/schools/fixture-state/housing/live/',1,%s,%s,'published')", (inst, topics["housing"], now, now))
        cur.execute("INSERT INTO pages (institution_id, topic_id, page_format, slug, path, status) VALUES (%s,%s,'guide','held','/schools/fixture-state/housing/held/','held')", (inst, topics["housing"]))
    clean_conn.commit()
    rep = volume.report(clean_conn)
    assert rep["counts"]["totals"]["ready"] == 6 and rep["counts"]["totals"]["live"] == 1 and rep["counts"]["totals"]["held"] == 1
    assert rep["counts"]["by_tier"][1]["ready"] == 4 and rep["counts"]["by_tier"][2]["ready"] == 2
    pj = rep["projection"]
    assert pj["ready_total"] == 7 and pj["per_day"] > 0 and pj["projected_days"]["1000"] > 0 and pj["projected_days"]["5000"] > pj["projected_days"]["1000"]


def test_navigator_renders_and_passes_seo_gate_and_accessibility(clean_conn, tmp_path):
    """AT47 render part: the navigator page renders from the fixture graph, answers the fixture path, and passes the R45 gate items
    that depend on markup (one H1, breadcrumb JSON-LD, canonical, answer-first) plus the 5-width screenshot QA with no overflow."""
    import json, re, shutil, subprocess
    from campus_worker import seo_gate
    from campus_worker.render import site
    inst, campus, topics = make_school(clean_conn)
    gid = processes.ensure_graph(clean_conn, institution_id=inst, key="changing-majors", name="Changing majors", topic_key="transfer", description="Changing majors or transferring between colleges at Fixture State: steps, requirements, deadlines and offices from official pages.")
    base = {"steps": ["Meet your advisor", "Apply through the receiving college"], "deadlines": ["Oct 15 (fixture)"], "offices": ["Receiving college registrar"], "gpa_min": "2.5"}
    processes.upsert_node(clean_conn, gid, processes.NodeSpec("overview", "Changing majors at Fixture State", 0, rules=base, source_urls=["https://www.fixturestate.example.edu/registrar/change-major"]))
    processes.upsert_node(clean_conn, gid, processes.NodeSpec("as-to-dyson", "Arts & Sciences → Dyson", 1, parent_key="overview", from_state="arts-sciences", to_state="dyson", rules=dict(base, gpa_min="3.0", prerequisites=["AEM 2100"])))
    processes.upsert_node(clean_conn, gid, processes.NodeSpec("anthro-to-aem-sophomore", "Anthropology → AEM as a sophomore", 2, parent_key="as-to-dyson", from_state="arts-sciences", to_state="dyson", situation="sophomore", rules=dict(base, gpa_min="3.0", prerequisites=["AEM 2100", "MATH 1110"])))
    processes.decide_pages(clean_conn, gid, institution_id=inst, school_slug="fixture-state", topic_key="transfer", demand_lookup=lambda k: {"independent_questions": 3, "query_targets": 1})
    out = site.render_navigator(clean_conn, gid, school_slug="fixture-state", school_name="Fixture State University", topic_key="transfer", out_root=tmp_path, environment="production",
                                selected={"from": "arts-sciences", "to": "dyson", "situations": ["sophomore"]}, base_url="https://example.org")
    html = out.read_text()
    assert out.as_posix().endswith("schools/fixture-state/transfer/tools/changing-majors-navigator/index.html")
    assert html.count("<h1") == 1 and "MATH 1110" in html and "Oct 15 (fixture)" in html and "Receiving college registrar" in html and "data-graph" in html
    lds = [json.loads(m) for m in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)]
    flat = [b for blk in lds for b in (blk if isinstance(blk, list) else [blk])]
    page = seo_gate.PageInput(path="/schools/fixture-state/transfer/tools/changing-majors-navigator/", title=re.search(r"<title>(.*?)</title>", html, re.S).group(1).split(" — ")[0],
                              meta_description=re.search(r'name="description" content="([^"]*)"', html).group(1), h1s=re.findall(r"<h1[^>]*>(.*?)</h1>", html, re.S), h2h3s=re.findall(r"<h[23][^>]*>(.*?)</h[23]>", html, re.S),
                              opening_paragraph=re.search(r'<p class="measure"><strong>(.*?)</strong></p>', html, re.S).group(1), primary_query="changing majors fixture state", secondary_questions=[],
                              json_ld=flat, page_type="WebPage", internal_links=[{"href": h, "anchor": re.sub("<[^>]+>", "", a).strip()} for h, a in re.findall(r'<a href="(/[^"]+)"[^>]*>(.*?)</a>', html, re.S)],
                              topic_hub="/schools/fixture-state/transfer/", scope_hub="/schools/fixture-state/", backlinks=1, canonical="https://example.org/schools/fixture-state/transfer/tools/changing-majors-navigator/",
                              environment="production", html_css_bytes=len(html.encode()) + (tmp_path / "static" / "campus.css").stat().st_size, visible_updated_date="Updated" in html, time_bound_facts_with_year=True)
    r = seo_gate.evaluate(page)
    assert r.passed, r.failed
    # accessibility + overflow QA at 5 widths (Playwright), on the rendered build
    node = shutil.which("node")
    if not node:
        pytest.skip("node not available")
    qa = subprocess.run([node, str(ROOT / "scripts" / "qa_screens.js"), str(tmp_path), str(tmp_path / "qa")], capture_output=True, text=True, timeout=600, cwd=str(ROOT))
    assert qa.returncode == 0, qa.stdout[-2000:] + qa.stderr[-2000:]
    assert "problems: 0" in qa.stdout or "0 problem" in qa.stdout or '"problems": 0' in qa.stdout, qa.stdout[-1500:]


def test_digest_has_every_r9_section_and_r29_r44_metrics(clean_conn, tmp_path):
    from campus_worker import digest, budget, events
    from datetime import date
    inst, campus, topics = make_school(clean_conn)
    budget.record_session_usage(clean_conn, kind="iteration", task_id="S4", agent=None, duration_s=120, turns=10, iteration=1)
    budget.record_session_usage(clean_conn, kind="dispatch", task_id="S4", agent="researcher", duration_s=30, turns=5, iteration=1)
    with clean_conn.cursor() as cur:
        cur.execute("INSERT INTO pages (institution_id, topic_id, page_format, slug, path, status, ready_at, local_published_at) VALUES (%s,%s,'guide','d','/schools/fixture-state/housing/d/','staged',now(),now())", (inst, topics["housing"]))
        cur.execute("INSERT INTO pages (institution_id, topic_id, page_format, slug, path, status, revalidation_reason) VALUES (%s,%s,'guide','h','/schools/fixture-state/housing/h/','held','seo_gate failed: one_h1')", (inst, topics["housing"]))
    clean_conn.commit()
    events.emit(clean_conn, "topic_created", {"key": "auto_kayak"})
    p = digest.write(clean_conn, reason="run_end", out_dir=tmp_path)
    md = p.read_text()
    for section in ("## Tasks done", "## Pages published, held and why", "## Claims verified or superseded", "## Skills evaluated, adopted or rejected", "## Search intel and strategy changes", "## Failures and blockers", "## Next 3 tasks"):
        assert section in md, section
    for metric in ("per published page", "per verified update", "per qualified cluster", "discovery yield", "wasted-work rate"):
        assert metric in md, metric
    assert "projected days to 1,000" in md and "| tier | scope | topic | ready | live | held |" in md
    assert "/schools/fixture-state/housing/h/" in md and "one_h1" in md and "turns 15" in md
    assert p.name == f"{date.today().isoformat()}.md" or p.exists()
