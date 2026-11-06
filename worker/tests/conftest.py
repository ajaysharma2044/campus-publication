import os

os.environ.setdefault("CAMPUS_LEAN_MODE", "0")  # the spec's acceptance tests run with the spec's thresholds; tests/test_lean.py covers LEAN MODE
import pytest

from campus_worker import db as dbmod

TEST_URL = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql://campus:campus_local_dev@localhost:5432/campus_research_test",
)


@pytest.fixture(scope="session")
def migrated_url():
    conn = dbmod.connect(TEST_URL)
    try:
        dbmod.reset_database(conn)
        dbmod.migrate(conn)
    finally:
        conn.close()
    return TEST_URL


@pytest.fixture
def conn(migrated_url):
    c = dbmod.connect(migrated_url)
    try:
        yield c
    finally:
        if not c.closed:  # a test may close it on purpose (test_ensure_conn)
            c.rollback()
            c.close()


@pytest.fixture
def clean_conn(migrated_url):
    """Connection with operational tables truncated (keeps topics seed)."""
    c = dbmod.connect(migrated_url)
    with c.cursor() as cur:
        cur.execute("UPDATE ramp_state SET live_since=NULL, hold=FALSE, hold_reason=NULL, hold_rate_per_day=NULL WHERE id=1")
        cur.execute(
            """TRUNCATE jobs, runs, usage_ledger, exceptions, heartbeats, pages, page_versions,
               page_claims, dependencies, briefs, opportunity_scores, serp_observations,
               demand_observations, questions, intent_clusters, coverage_edges, conflicts,
               claim_sources, claims, fetch_snapshots, source_registry, source_permissions,
               entities, school_topic_applicability, school_configs, campuses,
               institution_external_ids, institution_aliases, institutions, tool_configs,
               experiments, analytics_aggregates, revenue_reports, correction_requests, live_releases, serp_cache, strategies, query_targets, lane_state, digest_events, harvest_sources, places CASCADE"""
        )
        cur.execute("DELETE FROM topics WHERE auto_created")
    c.commit()
    try:
        yield c
    finally:
        c.rollback()
        c.close()
