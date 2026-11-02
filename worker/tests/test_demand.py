from datetime import datetime, timezone
from pathlib import Path
from campus_worker.adapters.search import KeywordProviderAdapter, demand_summary, store_demand, store_serp_observation
from tests.helpers import make_school

T = datetime(2026, 10, 1, tzinfo=timezone.utc)


def test_export_import_preserves_unknown_and_does_not_sum_variants(clean_conn, tmp_path):
    inst, campus, topics = make_school(clean_conn)
    with clean_conn.cursor() as cur:
        cur.execute("INSERT INTO intent_clusters (institution_id, label, answer_key) VALUES (%s,'x','k1') RETURNING id", (inst,))
        cid = cur.fetchone()["id"]
    clean_conn.commit()
    p = tmp_path / "export.csv"
    p.write_text("query,window_start,window_end,volume_low,volume_high,suppressed,variant_group,monthly_json\n"
                 "cornell dorm cost,2025-10-01,2026-09-30,100,1000,,g1,\n"
                 "cornell dorms cost,2025-10-01,2026-09-30,100,1000,,g1,\n"
                 "cornell housing rates,2025-10-01,2026-09-30,10,100,,,\n"
                 "mews hall ac,2025-10-01,2026-09-30,,,true,,\n")
    rows = KeywordProviderAdapter.parse_export(p, provider="fixture_export", geography="US", language="en", retrieved_at=T)
    assert rows[3].volume_high is None and rows[3].is_suppressed
    assert store_demand(clean_conn, cid, rows) == 4
    s = demand_summary(clean_conn, cid)
    assert s["groups"] == 2 and s["volume_high"] == 1100 and s["unknown_or_suppressed"] == 1  # g1 counted once
    assert KeywordProviderAdapter().capability().state == "unconnected"


def test_serp_observation_capped_at_ten(clean_conn):
    inst, campus, topics = make_school(clean_conn)
    with clean_conn.cursor() as cur:
        cur.execute("INSERT INTO intent_clusters (institution_id, label, answer_key) VALUES (%s,'x','k2') RETURNING id", (inst,))
        cid = cur.fetchone()["id"]
    clean_conn.commit()
    sid = store_serp_observation(clean_conn, cid, query_text="q", locale="en-US", device="mobile", results=[{"position": i} for i in range(15)],
                                 direct_answer_quality="partial", missing_contribution="current per-person rates", provider="manual")
    with clean_conn.cursor() as cur:
        cur.execute("SELECT jsonb_array_length(results) AS n FROM serp_observations WHERE id=%s", (sid,))
        assert cur.fetchone()["n"] == 10
