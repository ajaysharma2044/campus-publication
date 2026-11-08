"""Demand engine (specs/continuous-local-run.md R18–R24, R33–R36, R41, R45, R46; AT19–AT24, AT33–AT35, AT40 fixture part, AT45, AT46 fixture part)."""
import json
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

import httpx
import pytest

from campus_worker import agi, discovery, events, expand, funnel, harvest, lanes, permissions, search_cache, search_intel, sweep, sweetspot, taxonomy
from campus_worker.agents import dispatch as dsp
from campus_worker.collectors import class_roster, first_party, reddit, stackexchange
from campus_worker.config import get_settings
from campus_worker.discovery import QuestionInput
from campus_worker.fetcher import FetchRefused, SafeFetcher
from campus_worker.seed import seed_all
from tests.agent_fixtures import cli_stdout, envelope
from tests.helpers import make_entity, make_school
from tests.test_fetcher import resolver_factory

ROOT = Path(__file__).resolve().parents[2]
FIX = ROOT / "fixtures" / "synthetic"


def _intel(name: str) -> dict:
    return json.loads((FIX / "serp" / f"{name}.json").read_text())


def _place(conn, slug="ithaca-ny"):
    seed_all(conn)
    with conn.cursor() as cur:
        cur.execute("SELECT id, name FROM places WHERE slug=%s", (slug,))
        r = cur.fetchone()
    return r["id"], r["name"]


# ------------------------------------------------------------------------------------------------ AT33 / AT45 taxonomy
def test_taxonomy_seed_has_every_r33_topic_and_audience_set(clean_conn, tmp_path):
    seed_all(clean_conn)
    with clean_conn.cursor() as cur:
        cur.execute("SELECT key, scope, audiences, freshness_risk, source_families FROM topics")
        rows = {r["key"]: r for r in cur.fetchall()}
    assert taxonomy.REQUIRED_R33_KEYS <= set(rows)
    assert sum(1 for r in rows.values() if r["scope"] == "town") == 10
    for k in ("alumni_benefits", "alumni_records", "alumni_events", "alumni_education", "alumni_giving", "alumni_visiting",
              "parents_calendar", "parents_billing", "parents_logistics", "parents_prep",
              "jobs_student", "jobs_internships", "jobs_outcomes", "jobs_university", "jobs_grad", "town_jobs"):
        assert k in rows, k
    assert "alumni" in rows["alumni_benefits"]["audiences"] and "parent" in rows["parents_billing"]["audiences"] and "faculty_staff" in rows["jobs_university"]["audiences"]
    assert all(r["freshness_risk"] in ("low", "medium", "high") and r["source_families"] for k, r in rows.items() if k in taxonomy.REQUIRED_R33_KEYS)
    doc = taxonomy.write_doc(clean_conn, tmp_path / "topic-taxonomy.md").read_text()
    assert "## School topics" in doc and "## Town topics" in doc and "Audience topic sets" in doc and "`town_government`" in doc


# ------------------------------------------------------------------------------------------------ AT19 harvest (school)
HALL_RULE = harvest.HarvestRule(key="fixture_halls", source_url="https://housing.fixturestate.example.edu/housing/residence-halls/", entity_type="residence_hall", topic_key="housing",
                                link_prefix="/housing/residence-halls/", exclude_regex=r"apply", group_from_heading=True, publisher="Fixture State Housing (synthetic)")


def test_harvest_fixture_halls_then_rerun_adds_new_hall_and_deactivates_missing(clean_conn):
    inst, campus, topics = make_school(clean_conn)
    with clean_conn.cursor() as cur:
        cur.execute("INSERT INTO source_permissions (domain_pattern, publisher, connector, access_mode, permission_state) VALUES ('*.fixturestate.example.edu','Fixture State','official_html','fetch_permitted','allowed_with_limits') ON CONFLICT DO NOTHING")
    clean_conn.commit()
    harvest.register_rule(clean_conn, HALL_RULE, institution_id=inst, campus_id=campus)
    r1 = harvest.harvest_html(clean_conn, HALL_RULE, (FIX / "harvest" / "halls_v1.html").read_bytes(), institution_id=inst, campus_id=campus)
    assert r1["found"] == 3 and r1["created"] == 3 and r1["deactivated"] == 0
    with clean_conn.cursor() as cur:
        cur.execute("SELECT name, slug, source_url, first_seen_at, last_seen_at, attributes, status FROM entities WHERE institution_id=%s AND entity_type='residence_hall' ORDER BY slug", (inst,))
        ents = cur.fetchall()
    assert [e["slug"] for e in ents] == ["fixture-hall", "hilltop-house", "riverside-hall"]
    assert all(e["source_url"] == HALL_RULE.source_url and e["first_seen_at"] and e["last_seen_at"] for e in ents)
    assert {e["attributes"]["group"] for e in ents} == {"North Area", "West Area"}
    # re-run with a new hall listed: exactly one more entity; existing ones keep first_seen_at
    r2 = harvest.harvest_html(clean_conn, HALL_RULE, (FIX / "harvest" / "halls_v2_new_hall.html").read_bytes(), institution_id=inst, campus_id=campus)
    assert r2["found"] == 4 and r2["created"] == 1 and r2["updated"] == 3
    # a later run without one hall marks it inactive but never deletes it
    r3 = harvest.harvest_html(clean_conn, HALL_RULE, (FIX / "harvest" / "halls_v1.html").read_bytes(), institution_id=inst, campus_id=campus)
    assert r3["deactivated"] == 1
    with clean_conn.cursor() as cur:
        cur.execute("SELECT status FROM entities WHERE institution_id=%s AND slug='new-gorge-hall'", (inst,))
        assert cur.fetchone()["status"] == "inactive"
    assert harvest.due_harvest_sources(clean_conn) == []  # just harvested; next refresh in the future


def test_harvest_requires_exactly_one_scope():
    with pytest.raises(ValueError):
        harvest.harvest_html(None, HALL_RULE, b"", institution_id=None, place_id=None)


# ------------------------------------------------------------------------------------------------ AT34 town harvest
def test_town_harvest_three_official_sources_store_place_scoped_entities(clean_conn):
    place_id, town = _place(clean_conn)
    rules = [
        harvest.HarvestRule(key="tcat_routes", source_url="https://tcatbus.com/routes/", entity_type="bus_route", topic_key="town_transit_local", link_prefix="/routes/", publisher="TCAT (fixture)"),
        harvest.HarvestRule(key="ny_parks", source_url="https://parks.ny.gov/parks/", entity_type="park", topic_key="town_outdoors", link_prefix="/parks/", publisher="NY State Parks (fixture)"),
        harvest.HarvestRule(key="city_services", source_url="https://www.cityofithaca.org/services/", entity_type="town_service", topic_key="town_government", link_prefix="/services/", publisher="City of Ithaca (fixture)"),
    ]
    pages = {"tcat_routes": "tcat_routes.html", "ny_parks": "parks.html", "city_services": "city_services.html"}
    for r in rules:
        harvest.register_rule(clean_conn, r, institution_id=None, place_id=place_id)
        res = harvest.harvest_html(clean_conn, r, (FIX / "town" / pages[r.key]).read_bytes(), institution_id=None, place_id=place_id)
        assert res["created"] >= 2, res
    with clean_conn.cursor() as cur:
        cur.execute("SELECT entity_type, name, place_id, institution_id, source_url, first_seen_at FROM entities WHERE place_id=%s ORDER BY entity_type, slug", (place_id,))
        rows = cur.fetchall()
        cur.execute("SELECT count(DISTINCT source_id) AS n FROM entities WHERE place_id=%s", (place_id,))
        sources = cur.fetchone()["n"]
    assert len(rows) == 8 and sources == 3
    assert all(r["institution_id"] is None and r["place_id"] == place_id and r["source_url"] and r["first_seen_at"] for r in rows)
    assert {r["entity_type"] for r in rows} == {"bus_route", "park", "town_service"}
    assert any("Route 30" in r["name"] for r in rows) and any("Voter registration" in r["name"] for r in rows)


# ------------------------------------------------------------------------------------------------ AT20 expansion
def test_expansion_generates_hypotheses_only_never_demand(clean_conn):
    inst, campus, topics = make_school(clean_conn)
    with clean_conn.cursor() as cur:
        cur.execute("INSERT INTO source_permissions (domain_pattern, publisher, connector, access_mode, permission_state) VALUES ('*.fixturestate.example.edu','Fixture State','official_html','fetch_permitted','allowed_with_limits') ON CONFLICT DO NOTHING")
    clean_conn.commit()
    harvest.harvest_html(clean_conn, HALL_RULE, (FIX / "harvest" / "halls_v1.html").read_bytes(), institution_id=inst, campus_id=campus)
    res = expand.expand_scope(clean_conn, institution_id=inst, campus_id=campus, school_name="Fixture State")
    assert res["entities"] == 3 and res["generated"] > 0 and res["stored"] == res["generated"]
    with clean_conn.cursor() as cur:
        cur.execute("SELECT raw_text, origin, is_hypothesis, pattern_key, pattern_version, entity_id FROM questions WHERE institution_id=%s", (inst,))
        qs = cur.fetchall()
        cur.execute("SELECT count(*) AS n FROM intent_clusters WHERE institution_id=%s AND observed_count > 0", (inst,))
        observed_clusters = cur.fetchone()["n"]
    assert qs and all(q["is_hypothesis"] and q["origin"] == "hypothesis" and q["pattern_key"] and q["pattern_version"] == expand.PATTERN_VERSION and q["entity_id"] for q in qs)
    texts = {q["raw_text"] for q in qs}
    assert "Fixture Hall review" in texts and "Fixture Hall room size" in texts and "is Fixture Hall good for transfers" in texts and "how to get to Riverside Hall" in texts
    # vs pairs only inside the same group: Fixture Hall & Riverside Hall share "North Area"; Hilltop House has no partner
    vs = {t for t in texts if " vs " in t}
    assert vs == {"Fixture Hall vs Riverside Hall"}
    # no hypothesis is counted as demand
    assert observed_clusters == 0
    with clean_conn.cursor() as cur:
        cur.execute("SELECT id FROM intent_clusters WHERE institution_id=%s LIMIT 1", (inst,))
        cid = cur.fetchone()["id"]
    assert sweetspot.d_score(sweetspot.demand_points(clean_conn, cid)) == 0
    # idempotent
    res2 = expand.expand_scope(clean_conn, institution_id=inst, campus_id=campus, school_name="Fixture State")
    assert res2["stored"] == 0 and res2["duplicate_occurrences"] == res["generated"]


def test_query_patterns_doc_matches_code():
    doc = (ROOT / "docs" / "strategy" / "query-patterns.md").read_text()
    for p in expand.PATTERNS + expand.TOWN_PATTERNS:
        assert f"| {p.key} |" in doc, p.key
    assert f"version {expand.PATTERN_VERSION[1:]}" in doc


# ------------------------------------------------------------------------------------------------ AT35 access modes
def test_search_observation_sources_cannot_be_fetched_or_quoted_and_unknown_domains_denied(clean_conn):
    seed_all(clean_conn)
    assert permissions.access_mode_for(clean_conn, "https://www.reddit.com/r/Cornell/comments/x/") == "search_observation"
    d = permissions.check_url(clean_conn, "https://www.reddit.com/r/Cornell/comments/x/")
    assert not d.allowed and d.reason == "search_observation_only"
    f = SafeFetcher(clean_conn, transport=httpx.MockTransport(lambda r: httpx.Response(200, text="<html>never</html>")), resolver=resolver_factory({}), sleep=lambda s: None)
    with pytest.raises(FetchRefused) as ei:
        f.fetch("https://www.reddit.com/r/Cornell/")
    assert ei.value.reason == "permission_denied"
    ok, why = permissions.may_quote(clean_conn, "https://www.reddit.com/r/Cornell/comments/x/")
    assert not ok and "never quotes" in why
    with pytest.raises(permissions.QuoteNotPermitted):
        permissions.assert_may_quote(clean_conn, "https://old.reddit.com/r/ithaca/")
    assert not permissions.check_url(clean_conn, "https://unregistered.example.invalid/page").allowed
    assert permissions.access_mode_for(clean_conn, "https://unregistered.example.invalid/") == "disabled"
    # official sources: fetch and quote permitted; Stack Exchange quote needs attribution
    assert permissions.check_url(clean_conn, "https://scl.cornell.edu/residential-life/").allowed
    ok, why = permissions.may_quote(clean_conn, "https://api.stackexchange.com/2.3/search")
    assert ok and "CC BY-SA" in why


def test_robots_disallow_blocks_fetch_and_is_recorded(clean_conn):
    make_school(clean_conn)
    with clean_conn.cursor() as cur:
        cur.execute("INSERT INTO source_permissions (domain_pattern, publisher, connector, access_mode, permission_state) VALUES ('www.fixturestate.example.edu','Fixture State','official_html','fetch_permitted','allowed_with_limits') ON CONFLICT DO NOTHING")
    clean_conn.commit()

    def handler(req):
        if req.url.path == "/robots.txt":
            return httpx.Response(200, text="User-agent: *\nDisallow: /private/\n", headers={"content-type": "text/plain"})
        return httpx.Response(200, text="<html><body><h1>ok</h1><p>" + "x" * 100 + "</p></body></html>", headers={"content-type": "text/html"})
    f = SafeFetcher(clean_conn, transport=httpx.MockTransport(handler), resolver=resolver_factory({}), sleep=lambda s: None)
    assert f.fetch("https://www.fixturestate.example.edu/housing/").status == 200
    with pytest.raises(FetchRefused) as ei:
        f.fetch("https://www.fixturestate.example.edu/private/rates/")
    assert ei.value.reason == "robots_disallow"
    with clean_conn.cursor() as cur:
        cur.execute("SELECT robots_checked_at, robots_allows FROM source_permissions WHERE domain_pattern='www.fixturestate.example.edu'")
        r = cur.fetchone()
    assert r["robots_checked_at"] is not None and r["robots_allows"] is False  # last check recorded


def test_reddit_collector_is_off_until_authorized_and_parses_fixtures_without_identity_or_network(clean_conn):
    inst, campus, topics = make_school(clean_conn)
    seed_all(clean_conn)
    col = reddit.RedditCollector(client_id=None, client_secret=None)
    cap = col.capability(clean_conn)
    assert not cap.connected and "search-result observation only" in cap.reason
    # even with credentials, the permission row (search_observation) keeps it off
    col2 = reddit.RedditCollector(client_id="id", client_secret="secret")
    assert not col2.capability(clean_conn).connected
    with pytest.raises(PermissionError):
        col2.collect(clean_conn, "FixtureState")  # would need network; refused before any request
    # fixture listing: questions only, no author fields retained, deletion compliance
    listing = json.loads((FIX / "community" / "reddit_listing.json").read_text())
    calls = []

    class Boom(httpx.BaseTransport):
        def handle_request(self, request):
            calls.append(request.url)
            raise AssertionError("network must not be used")
    col2.transport = Boom()
    res = col2.collect(clean_conn, "FixtureState", listing=listing, institution_id=inst, topic_key="housing")
    assert res["parsed"] == 2 and res["stored"] == 2 and calls == []
    with clean_conn.cursor() as cur:
        cur.execute("SELECT raw_text, origin, source_ref, constraints FROM questions WHERE origin='reddit_api' ORDER BY raw_text")
        rows = cur.fetchall()
    assert [r["raw_text"] for r in rows] == ["How much does a double in Riverside Hall cost?", "Is Fixture Hall good for transfers?"]
    assert all("someuser" not in json.dumps(dict(r), default=str) and "author" not in json.dumps(dict(r), default=str) for r in rows)
    assert reddit.RedditCollector.forget(clean_conn, "abc123") == 1
    scrubbed = reddit.RedditCollector.scrub(listing["data"]["children"][0]["data"])
    assert "author" not in scrubbed and "author_fullname" not in scrubbed and scrubbed["title"]
    # permission flip is explicit and recorded
    permissions.record_terms_check(clean_conn, "*.reddit.com", access_mode="api_authorized", terms_reference="Reddit Data API terms (owner authorization recorded)", note="fixture test")
    assert col2.capability(clean_conn).connected


# ------------------------------------------------------------------------------------------------ AT21 AGI
def test_agi_forum_only_high_dedicated_official_low_navigational_rejected():
    assert agi.compute(_intel("forum_only")).agi >= 4
    assert agi.compute(_intel("dedicated_official")).agi <= 1
    nav = agi.compute(_intel("navigational"))
    assert nav.navigational and nav.detail["variants"][0]["navigational"]
    po = agi.compute(_intel("partial_official"))
    assert po.agi >= 3 and po.weak_or_missing and "partial_official" in po.detail["variants"][0]["weak_kinds"]


# ------------------------------------------------------------------------------------------------ AT22 sweet-spot queue + AT23 funnel + AT24 cache
def _cluster(conn, inst, campus, topics, text, *, observed=0, entity_id=None, audience_text=""):
    items = [QuestionInput(raw_text=text + audience_text, origin="related_question", institution_id=inst, campus_id=campus, topic_key="housing", entity_id=entity_id,
                           observed_at=datetime.now(timezone.utc), source_ref=f"src:{text}:{i}") for i in range(observed)]
    if not items:
        items = [QuestionInput(raw_text=text, origin="hypothesis", institution_id=inst, campus_id=campus, topic_key="housing", entity_id=entity_id, is_hypothesis=True, source_ref=f"hyp:{text}")]
    discovery.ingest(conn, items)
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM intent_clusters WHERE institution_id=%s AND label=%s", (inst, (text + audience_text)[:140]))
        return cur.fetchone()["id"]


def _official_source(conn, inst, campus):
    with conn.cursor() as cur:
        cur.execute("INSERT INTO source_permissions (domain_pattern, publisher, connector, access_mode, permission_state) VALUES ('*.fixturestate.example.edu','Fixture State','official_html','fetch_permitted','allowed_with_limits') ON CONFLICT DO NOTHING")
    conn.commit()
    from campus_worker.collectors.html import register_source
    register_source(conn, canonical_url="https://housing.fixturestate.example.edu/rates/", institution_id=inst, campus_id=campus, source_kind="official_html", publisher="Fixture State Housing", source_family="fixture-housing")


def test_sweet_spot_queue_from_ten_fixture_clusters(clean_conn):
    inst, campus, topics = make_school(clean_conn)
    _official_source(clean_conn, inst, campus)  # E = 3 for this scope
    now = datetime.now(timezone.utc)
    spec = [  # (text, observed occurrences, intel fixture) → expectation
        ("fixture hall review", 3, "forum_only", "sweet_spot"),
        ("riverside hall review", 2, "forum_only", "sweet_spot"),
        ("hilltop house cost", 2, "partial_official", "sweet_spot"),
        ("fixture hall room size", 1, "forum_only", "watch"),            # D=1 < 2
        ("fixture state housing portal", 3, "navigational", "navigational"),
        ("fixture hall", 4, "dedicated_official", "watch"),              # strong incumbent → head term watch
        ("meal plan cost fixture state", 0, "forum_only", "reject"),     # D=0 and hypothesis only → reject
        ("is housing guaranteed for transfers fixture state", 5, "partial_official", "sweet_spot"),
        ("gorge safety rules", 2, None, "needs_intel"),                  # no intel yet
        ("fixture hall vs riverside hall", 2, "forum_only", "sweet_spot"),
    ]
    results = {}
    for text, obs, fx, expect in spec:
        cid = _cluster(clean_conn, inst, campus, topics, text, observed=obs)
        if fx:
            search_intel.ingest_intel(clean_conn, cid, dict(_intel(fx), variants=[dict(v, query=text if i == 0 else v["query"]) for i, v in enumerate(_intel(fx)["variants"])]), cached={}, now=now)
        cs = sweetspot.score_cluster(clean_conn, cid)
        results[text] = (cs, expect)
    for text, (cs, expect) in results.items():
        assert cs.decision == expect, (text, cs.decision, cs.reason)
    q = sweetspot.queue(clean_conn)
    assert [x["label"] for x in q] == [t for t, (cs, e) in sorted(results.items(), key=lambda kv: -kv[1][0].niche_score) if e == "sweet_spot"]
    assert all(x["d"] >= 2 and x["agi"] >= 3 and x["g"] >= 3 and x["e"] >= 3 for x in q)
    scores = [float(x["niche_score"]) for x in q]
    assert scores == sorted(scores, reverse=True)
    assert any(w["label"] == "fixture hall" and "incumbent" in w["queue_reason"] for w in sweetspot.watch_list(clean_conn))
    # the map lists every cluster with a decision; priority recorded but not the advance rule
    scratch = Path(tempfile.mkdtemp(prefix="opp-map-"))  # never the real docs/strategy + build/ artifacts: the live sweep writes those
    out = sweep.write_map(clean_conn, md_path=scratch / "opp.md", csv_path=scratch / "opp.csv")
    assert out["rows"] >= 10 and out["status"]["sweet_spot"] == 5  # follow-up questions from intel create extra (needs_intel) clusters
    with clean_conn.cursor() as cur:
        cur.execute("SELECT agi_detail->'priority' AS p FROM intent_clusters WHERE label='fixture hall review'")
        assert cur.fetchone()["p"] is not None


def test_funnel_never_dispatches_expensive_agents_for_a_cluster_failing_agi(clean_conn, tmp_path):
    inst, campus, topics = make_school(clean_conn)
    _official_source(clean_conn, inst, campus)
    cid = _cluster(clean_conn, inst, campus, topics, "fixture hall", observed=4)
    search_intel.ingest_intel(clean_conn, cid, dict(_intel("dedicated_official"), variants=[dict(_intel("dedicated_official")["variants"][0], query="fixture hall")]), cached={})
    log = tmp_path / "dispatch.jsonl"
    specs = dsp.load_agents()
    stages = []
    for agent in ("researcher", "planner", "writer", "editor", "verifier"):
        g = funnel.guard(clean_conn, cid, agent, log_path=log)
        stages.append(g.ok)
        if g.ok:  # would dispatch — must not happen
            dsp.dispatch(specs[agent], dsp.build_packet(task_id=f"t:{str(cid)[:8]}", run_id="r", objective="o", input_ids=[]), runner=lambda a, p: (0, cli_stdout(a.role), ""), log_path=log)
    assert stages == [False] * 5
    seen = funnel.dispatched_agents(log, cluster_id=cid)
    assert set(seen) == {"refused_by_funnel"} and sorted(seen["refused_by_funnel"]) == ["editor", "planner", "researcher", "verifier", "writer"]
    assert "ok" not in seen
    # cheap stages are never refused
    assert funnel.guard(clean_conn, cid, "search-intel", log_path=log).ok


def test_search_intel_cache_zero_new_calls_inside_window(clean_conn, tmp_path):
    inst, campus, topics = make_school(clean_conn)
    _official_source(clean_conn, inst, campus)
    settings = get_settings()
    cid = _cluster(clean_conn, inst, campus, topics, "fixture hall review", observed=2)
    fx = _intel("forum_only")
    variants = search_intel.variants_for_cluster(clean_conn, cid)
    fx["variants"] = [dict(v, query=variants[i] if i < len(variants) else v["query"]) for i, v in enumerate(fx["variants"])][:len(variants)]
    dispatches = []

    def runner(a, p):
        dispatches.append(a.name)
        return 0, cli_stdout(a.role, text=json.dumps(envelope("search_intel", fx))), ""
    t0 = datetime.now(timezone.utc)
    r1 = search_intel.run_cluster(clean_conn, cid, settings=settings, runner=runner, log_path=tmp_path / "d.jsonl", now=t0)
    assert r1["dispatched"] and r1["status"] == "ok" and dispatches == ["search-intel"]
    calls1 = search_cache.search_calls(clean_conn, cluster_id=cid)
    assert calls1["new_calls"] == len(variants) and calls1["cache_hits"] == 0
    # demand evidence from follow-up questions and community occurrences was recorded as observed (not hypothesis)
    with clean_conn.cursor() as cur:
        cur.execute("SELECT count(*) AS n FROM questions WHERE institution_id=%s AND origin IN ('related_question','discussion') AND NOT is_hypothesis", (inst,))
        assert cur.fetchone()["n"] >= 4
    # repeat inside 14 days: no dispatch, zero new search calls (asserted from the ledger)
    r2 = search_intel.run_cluster(clean_conn, cid, settings=settings, runner=runner, log_path=tmp_path / "d.jsonl", now=t0 + timedelta(days=13))
    assert r2["dispatched"] is False and r2["status"] == "cached" and dispatches == ["search-intel"]
    calls2 = search_cache.search_calls(clean_conn, cluster_id=cid)
    assert calls2["new_calls"] == calls1["new_calls"] and calls2["cache_hits"] == len(variants)
    # after the window the agent is dispatched again
    r3 = search_intel.run_cluster(clean_conn, cid, settings=settings, runner=runner, log_path=tmp_path / "d.jsonl", now=t0 + timedelta(days=15))
    assert r3["dispatched"] and dispatches == ["search-intel", "search-intel"]


# ------------------------------------------------------------------------------------------------ AT46 open discovery (fixture part)
def test_twenty_questions_four_unmatched_create_exactly_one_topic_with_digest_entry(clean_conn):
    inst, campus, topics = make_school(clean_conn)
    items = [QuestionInput(raw_text=f"How much does housing cost at Fixture State ({i})?", origin="related_question", institution_id=inst, campus_id=campus, topic_key="housing", source_ref=f"s{i}") for i in range(16)]
    # 4 independent questions that fit no topic and cluster together (same answer)
    for i in range(4):
        items.append(QuestionInput(raw_text="Where can students store a kayak over winter near campus?", origin="discussion", institution_id=inst, campus_id=campus, topic_key=None, source_ref=f"kayak-thread-{i}"))
    res = discovery.ingest(clean_conn, items)
    assert res["stored"] == 20
    created = discovery.auto_create_topics(clean_conn, run_id="test-run")
    assert len(created) == 1 and created[0]["new"] and created[0]["topic_key"].startswith("auto_")
    with clean_conn.cursor() as cur:
        cur.execute("SELECT key, label, auto_created, created_from FROM topics WHERE auto_created")
        rows = cur.fetchall()
        cur.execute("SELECT count(*) AS n FROM intent_clusters WHERE topic_id IS NULL")
        orphan = cur.fetchone()["n"]
    assert len(rows) == 1 and "kayak" in rows[0]["key"] and rows[0]["created_from"] and orphan == 0
    ev = [e for e in events.for_day(clean_conn) if e["kind"] == "topic_created"]
    assert len(ev) == 1 and ev[0]["detail"]["key"] == rows[0]["key"] and ev[0]["detail"]["independent"] == 4
    # idempotent: a second pass creates nothing new
    assert discovery.auto_create_topics(clean_conn) == []
    # the taxonomy doc lists it under auto-created
    doc = taxonomy.render_markdown(taxonomy.load(clean_conn))
    assert rows[0]["key"] in doc and "(auto-created)" in doc


def test_class_roster_fixture_stores_courses_with_term_and_prerequisites(clean_conn):
    inst, campus, topics = make_school(clean_conn)
    payload = json.loads((FIX / "community" / "class_roster_fxtr.json").read_text())
    client = class_roster.ClassRosterClient(fetch_json=lambda url: payload)
    res = class_roster.harvest_subject(clean_conn, client, institution_id=inst, roster="FA26", subject="FXTR")
    assert res["created"] == 2
    with clean_conn.cursor() as cur:
        cur.execute("SELECT name, slug, attributes, source_url FROM entities WHERE institution_id=%s AND entity_type='course' ORDER BY slug", (inst,))
        rows = cur.fetchall()
    assert [r["slug"] for r in rows] == ["fxtr-1010", "fxtr-2200"]
    assert rows[1]["attributes"]["term"] == "FA26" and "FXTR 1010" in rows[1]["attributes"]["prerequisites"] and rows[0]["attributes"]["prerequisites"] is None
    assert class_roster.prerequisite_course_codes(rows[1]["attributes"]["prerequisites"]) == ["FXTR 1010", "MATH 1110"]
    assert rows[0]["source_url"].startswith("https://classes.cornell.edu/api/2.0/")
    # re-harvest is an update, not a duplicate
    assert class_roster.harvest_subject(clean_conn, client, institution_id=inst, roster="FA26", subject="FXTR")["created"] == 0


def test_stackexchange_and_first_party_sources(clean_conn):
    inst, campus, topics = make_school(clean_conn)
    payload = json.loads((FIX / "community" / "stackexchange_search.json").read_text())
    client = stackexchange.StackExchangeClient(fetch_json=lambda url: payload)
    res = stackexchange.collect(clean_conn, client, site="academia", query="change major", institution_id=inst, topic_key="programs")
    assert res["parsed"] == 2 and res["stored"] == 2 and res["attribution"] == "CC BY-SA 4.0 (Stack Exchange)"
    with clean_conn.cursor() as cur:
        cur.execute("SELECT raw_text, constraints, source_ref FROM questions WHERE origin='stackexchange' ORDER BY raw_text")
        rows = cur.fetchall()
    assert rows[0]["raw_text"].startswith("How do I change my major as a sophomore & keep credits") and any("attribution:CC BY-SA" in c for c in rows[0]["constraints"])
    assert all("someone" not in json.dumps(dict(r)) for r in rows)
    ok = first_party.load_file(FIX / "first_party" / "clients_ok.csv", institution_id=inst)
    bad = first_party.load_file(FIX / "first_party" / "clients_bad.csv", institution_id=inst)
    assert len(ok.accepted) == 2 and not ok.rejected
    assert len(bad.accepted) == 1 and len(bad.rejected) == 2 and "name phrase" in bad.rejected[0][1] and "email" in bad.rejected[1][1]
    out = first_party.load_all(clean_conn, directory=FIX / "first_party", institution_id=inst)
    assert out["files"] == 2 and out["accepted"] == 3 and len(out["rejected"]) == 2 and out["stored"] == 3


# ------------------------------------------------------------------------------------------------ AT45 audience rule (fixture part)
def test_parent_variant_with_same_facts_is_merged_as_section(clean_conn):
    from campus_worker import claims
    from tests.test_claims import _money
    inst, campus, topics = make_school(clean_conn)
    ent = make_entity(clean_conn, inst, campus, topics["housing"])
    claims.store_claim(clean_conn, _money(inst, campus, topics["housing"], ent, 1204200), snapshot_id=None)
    parent = _money(inst, campus, topics["housing"], ent, 1204200).model_copy(update={"audience_applicability": ["parent"]})
    claims.store_claim(clean_conn, parent, snapshot_id=None)
    cid = _cluster(clean_conn, inst, campus, topics, "what does my kid pay for fixture hall", observed=2, entity_id=ent)
    with clean_conn.cursor() as cur:
        cur.execute("UPDATE intent_clusters SET audience='parent' WHERE id=%s", (cid,))
    clean_conn.commit()
    d = sweetspot.apply_audience_rule(clean_conn, cid)
    assert d["decision"] == "merge_as_section" and d["capture_format"] == "section"
    # when a parent-specific rule actually differs, a separate page is justified
    differing = _money(inst, campus, topics["housing"], ent, 1300000).model_copy(update={"audience_applicability": ["parent"], "field": "rate.payment_plan_fee"})
    claims.store_claim(clean_conn, differing, snapshot_id=None)
    d2 = sweetspot.apply_audience_rule(clean_conn, cid)
    assert d2["decision"] == "separate_page"


# ------------------------------------------------------------------------------------------------ lanes + sweep status
def test_lane_mix_orders_by_deficit_and_falls_through_empty_lanes(clean_conn, monkeypatch):
    # the repo's docs/ops/skill-evaluations.md may record a scout run from today; the test wants the no-scout-record state regardless
    monkeypatch.setattr(lanes, "_skill_scout_due", lambda: {"kind": "skill_scout_due", "reason": "no scout record (test)", "next": "dispatch skill-scout"})
    mix = lanes.parse_mix("50,30,20")
    assert lanes.order_by_deficit(mix, {}) == ["production", "discovery", "maintenance"]
    assert lanes.order_by_deficit(mix, {"production": 1})[0] == "discovery"
    assert lanes.order_by_deficit(mix, {"production": 5, "discovery": 3, "maintenance": 0})[0] == "maintenance"
    with pytest.raises(ValueError):
        lanes.parse_mix("50,50")
    settings = get_settings()
    out = lanes.next_lane(clean_conn, settings, run_id="t1")
    # empty DB: production and discovery have nothing (no scout record → discovery offers the skill scout), so the pick is deterministic
    assert out["lane"] in ("discovery", "maintenance") and out["item"]
    item = lanes.first_unblocked_backlog_item()
    assert item is None or item["id"]


def test_sweep_status_and_next_step_progression(clean_conn):
    seed_all(clean_conn)
    st = sweep.status(clean_conn)
    assert st["clusters"] == 0 and st["complete"] is False
    inst, campus, topics = make_school(clean_conn)
    with clean_conn.cursor() as cur:
        cur.execute("INSERT INTO source_permissions (domain_pattern, publisher, connector, access_mode, permission_state) VALUES ('*.fixturestate.example.edu','Fixture State','official_html','fetch_permitted','allowed_with_limits') ON CONFLICT DO NOTHING")
    clean_conn.commit()
    harvest.register_rule(clean_conn, HALL_RULE, institution_id=inst, campus_id=campus)
    assert sweep.next_step(clean_conn)["step"] == "harvest"
    harvest.harvest_html(clean_conn, HALL_RULE, (FIX / "harvest" / "halls_v1.html").read_bytes(), institution_id=inst, campus_id=campus)
    assert sweep.next_step(clean_conn)["step"] == "expand"
    sweep.run_expand(clean_conn, include_fixtures=True)
    nxt = sweep.next_step(clean_conn, batch=25)
    assert nxt["step"] == "intel" and 1 <= len(nxt["detail"]["batch"]) <= 25
    # observe every cluster with the forum fixture, then score → complete
    now = datetime.now(timezone.utc)
    for row in sweep.intel_batch(clean_conn, batch=1000):
        search_intel.ingest_intel(clean_conn, row["cluster_id"], _intel("forum_only"), cached={}, now=now)
    assert sweep.next_step(clean_conn)["step"] == "score"
    sweep.run_score(clean_conn)
    nxt = sweep.next_step(clean_conn)
    assert nxt["step"] == "complete" and nxt["sweep_complete"] is True


def test_search_intel_batch_dispatch_ingests_every_cluster_once(clean_conn, tmp_path):
    inst, campus, topics = make_school(clean_conn)
    _official_source(clean_conn, inst, campus)
    settings = get_settings()
    ids = [_cluster(clean_conn, inst, campus, topics, t, observed=2) for t in ("fixture hall review", "riverside hall cost", "hilltop house parking")]
    fx = _intel("forum_only")
    calls = []

    def runner(a, p):
        calls.append(a.name)
        packet = json.loads(p.split("#packet\n", 1)[1].split("\n\n#contract\n", 1)[0])
        assert "#contract" in p and '"output_schema"' in p  # every dispatch carries the exact contract
        assert packet["batch_mode"] is True and len(packet["clusters"]) == 3
        batch = [dict(fx, cluster_id=c["cluster_id"], variants=[dict(v, query=c["variants"][i] if i < len(c["variants"]) else v["query"]) for i, v in enumerate(fx["variants"])][:len(c["variants"])]) for c in packet["clusters"]]
        return 0, cli_stdout(a.role, text=json.dumps(envelope("search_intel", {"batch": batch, "search_calls_made": 6, "cache_hits": 0}))), ""
    r = search_intel.run_batch(clean_conn, ids, settings=settings, runner=runner, log_path=tmp_path / "d.jsonl")
    assert r["status"] == "ok" and calls == ["search-intel"] and len(r["results"]) == 3 and all(v["status"] == "ok" for v in r["results"].values())
    with clean_conn.cursor() as cur:
        cur.execute("SELECT count(*) AS n FROM intent_clusters WHERE id = ANY(%s) AND last_intel_at IS NOT NULL", (ids,))
        assert cur.fetchone()["n"] == 3
    # second batch inside the cache window: no dispatch at all
    r2 = search_intel.run_batch(clean_conn, ids, settings=settings, runner=runner, log_path=tmp_path / "d.jsonl")
    assert r2["dispatched"] is False and calls == ["search-intel"] and all(v["status"] == "cached" for v in r2["results"].values())


def test_sweep_run_intel_dispatches_one_batch_ingests_and_scores(clean_conn, tmp_path):
    inst, campus, topics = make_school(clean_conn)
    _official_source(clean_conn, inst, campus)
    ids = [_cluster(clean_conn, inst, campus, topics, t, observed=2) for t in ("fixture hall review", "riverside hall cost")]
    fx = _intel("forum_only")
    calls = []

    def runner(a, p):
        calls.append(a.name)
        packet = json.loads(p.split("#packet\n", 1)[1].split("\n\n#contract\n", 1)[0])
        batch = [dict(fx, cluster_id=c["cluster_id"], variants=[dict(v, query=c["variants"][i] if i < len(c["variants"]) else v["query"]) for i, v in enumerate(fx["variants"])][:len(c["variants"])]) for c in packet["clusters"]]
        return 0, cli_stdout(a.role, text=json.dumps(envelope("search_intel", {"batch": batch, "search_calls_made": 4, "cache_hits": 0}))), ""
    out = sweep.run_intel(clean_conn, batch=25, runner=runner, log_path=tmp_path / "d.jsonl")
    assert calls == ["search-intel"] and out["intel"]["status"] == "ok" and "score" in out
    with clean_conn.cursor() as cur:
        cur.execute("SELECT count(*) AS n FROM intent_clusters WHERE id = ANY(%s) AND last_intel_at IS NOT NULL", (ids,))
        assert cur.fetchone()["n"] == 2


def test_topic_seed_expansion_covers_every_r33_topic_and_sweep_cap_defers(clean_conn):
    seed_all(clean_conn)
    inst, campus, topics = make_school(clean_conn)
    place_id, town = _place(clean_conn)
    r = expand.expand_topics(clean_conn, institution_id=inst, campus_id=campus, school_name="Fixture State")
    rt = expand.expand_topics(clean_conn, place_id=place_id, town_name=town)
    assert r["stored"] > 50 and rt["stored"] >= 20
    with clean_conn.cursor() as cur:
        cur.execute("SELECT DISTINCT t.key FROM questions q JOIN topics t ON t.id=q.topic_id WHERE q.pattern_key='topic_seed'")
        covered = {x["key"] for x in cur.fetchall()}
    assert taxonomy.REQUIRED_R33_KEYS <= covered, taxonomy.REQUIRED_R33_KEYS - covered
    with clean_conn.cursor() as cur:
        cur.execute("SELECT raw_text FROM questions WHERE pattern_key='topic_seed' AND place_id=%s LIMIT 3", (place_id,))
        assert all("Ithaca" in x["raw_text"] for x in cur.fetchall())
    # idempotent
    assert expand.expand_topics(clean_conn, institution_id=inst, campus_id=campus, school_name="Fixture State")["stored"] == 0
    # bounded sweep: beyond the cap, clusters are deferred as watch with a reason; a topic-seed cluster outranks a plain pattern
    total = sweep.status(clean_conn)["need_intel"]
    deferred = sweep.defer_beyond_cap(clean_conn, cap=10)
    assert deferred == total - 10
    st = sweep.status(clean_conn)
    assert st["need_intel"] == 10 and st["watch"] == deferred
    batch = sweep.intel_batch(clean_conn, batch=25)
    assert len(batch) == 10


def test_sweep_decides_single_occurrence_clusters_watch_so_the_map_can_complete(clean_conn):
    inst, campus, topics = make_school(clean_conn)
    _official_source(clean_conn, inst, campus)
    lone = _cluster(clean_conn, inst, campus, topics, "fixture hall laundry hours", observed=1)      # one occurrence, no hypothesis: not eligible
    strong = _cluster(clean_conn, inst, campus, topics, "fixture hall review", observed=2)           # eligible
    n = sweep.defer_beyond_cap(clean_conn, cap=300)
    with clean_conn.cursor() as cur:
        cur.execute("SELECT id, queue_state, queue_reason FROM intent_clusters WHERE id IN (%s, %s)", (lone, strong))
        rows = {r["id"]: r for r in cur.fetchall()}
    assert n >= 1 and rows[lone]["queue_state"] == "watch" and "second independent occurrence" in rows[lone]["queue_reason"]
    assert rows[strong]["queue_state"] in ("candidate", "needs_intel")
    st = sweep.status(clean_conn)
    assert st["waiting_second_occurrence"] == 0 and st["undecided"] == 1


def test_score_all_reconnects_once_when_the_connection_drops(clean_conn, monkeypatch):
    import psycopg
    from campus_worker import db
    inst, campus, topics = make_school(clean_conn)
    _cluster(clean_conn, inst, campus, topics, "fixture hall review", observed=2)
    _cluster(clean_conn, inst, campus, topics, "riverside hall cost", observed=2)
    real, calls = sweetspot.score_cluster, {"n": 0}

    def flaky(conn, cid, **kw):
        calls["n"] += 1
        if calls["n"] == 2:
            raise psycopg.OperationalError("server closed the connection unexpectedly")
        return real(conn, cid, **kw)
    monkeypatch.setattr(sweetspot, "score_cluster", flaky)
    monkeypatch.setattr(db, "ensure_conn", lambda c, *a, **k: c)
    with clean_conn.cursor() as cur:
        cur.execute("SELECT count(*) AS n FROM intent_clusters")
        n = cur.fetchone()["n"]
    assert len(sweetspot.score_all(clean_conn)) == n and calls["n"] == n + 1
