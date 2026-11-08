REQUIRED = """institutions campuses institution_external_ids school_configs topics entities
source_registry fetch_snapshots claims claim_sources conflicts questions intent_clusters
demand_observations serp_observations coverage_edges opportunity_scores briefs pages page_versions
page_claims dependencies tool_configs source_permissions jobs runs usage_ledger experiments
analytics_aggregates revenue_reports exceptions correction_requests heartbeats""".split()


def test_all_required_tables_exist(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
        names = {r["table_name"] for r in cur.fetchall()}
    missing = set(REQUIRED) - names
    assert not missing, missing


def test_topics_seeded(conn):
    """Migration 0001 seeds 13 base topics; the R33 taxonomy (campus_worker.taxonomy.seed) adds more, so the count is a floor."""
    with conn.cursor() as cur:
        cur.execute("SELECT key FROM topics")
        keys = {r["key"] for r in cur.fetchall()}
    assert len(keys) >= 13 and {"housing", "transfer", "costs_aid", "dining", "transportation", "accessibility"} <= keys


def test_money_claims_must_be_integer_minor_units(conn):
    import pytest, psycopg
    with conn.cursor() as cur:
        cur.execute("INSERT INTO institutions (canonical_name, slug, institution_type, identity_status) VALUES ('Fixture U','fixture-u','university','synthetic_fixture') RETURNING id")
        inst = cur.fetchone()["id"]
        cur.execute("SELECT id FROM topics WHERE key='housing'")
        topic = cur.fetchone()["id"]
        with pytest.raises(psycopg.errors.CheckViolation):
            cur.execute(
                """INSERT INTO claims (institution_id, topic_id, field, value_type, value_number, unit, currency,
                   evidence_category, extraction_method, retrieved_at)
                   VALUES (%s,%s,'rate','money',1234.56,'minor_units','USD','verified_fact','deterministic',now())""",
                (inst, topic),
            )
    conn.rollback()


def test_timestamps_are_timestamptz(conn):
    with conn.cursor() as cur:
        cur.execute(
            """SELECT table_name, column_name FROM information_schema.columns
               WHERE table_schema='public' AND data_type='timestamp without time zone'"""
        )
        assert cur.fetchall() == []


def test_jobs_idempotency_key_unique(conn):
    import pytest, psycopg
    with conn.cursor() as cur:
        cur.execute("INSERT INTO jobs (job_type, idempotency_key) VALUES ('x','k1')")
        with pytest.raises(psycopg.errors.UniqueViolation):
            cur.execute("INSERT INTO jobs (job_type, idempotency_key) VALUES ('x','k1')")
    conn.rollback()
