import pytest
from uuid import uuid4
from campus_worker.scoring import Score, decide, persist, opportunity_queue
from tests.helpers import make_school

OBS = {k: "observed" for k in ("demand", "answer_gap", "winnability", "evidence_advantage", "commercial")}


def test_priority_formula_and_null_propagation():
    s = Score(4, 4, 3, 4, 2, OBS)
    assert s.priority() == pytest.approx(72.0)
    assert Score(4, None, 3, 4, 2, OBS).priority() is None
    assert decide(Score(4, None, 3, 4, 2, OBS)).decision == "hold"


def test_threshold_requires_E_and_G():
    assert decide(Score(5, 5, 5, 2, 5, OBS)).decision == "hold"      # E<3 despite high priority
    assert decide(Score(5, 2, 5, 5, 5, OBS)).decision == "watch"     # G<3
    assert decide(Score(4, 4, 3, 4, 2, OBS)).decision == "advance"
    assert decide(Score(1, 3, 1, 3, 0, OBS)).decision == "reject"
    assert decide(Score(3, 3, 3, 3, 1, OBS)).decision == "watch"     # 58 → within 15 of 65


def test_existing_coverage_improves_rather_than_duplicates():
    page = uuid4()
    d = decide(Score(4, 4, 3, 4, 2, OBS), existing_coverage=[page], has_distinct_task=False)
    assert d.decision == "improve_section" and d.existing_coverage_checked == [page]


def test_editorial_exception_recorded_not_hidden(clean_conn):
    inst, campus, topics = make_school(clean_conn)
    with clean_conn.cursor() as cur:
        cur.execute("INSERT INTO intent_clusters (institution_id, label, answer_key) VALUES (%s,'x','k3') RETURNING id", (inst,))
        cid = cur.fetchone()["id"]
    clean_conn.commit()
    low = Score(1, 4, 3, 4, 0, OBS)
    d = decide(low, exception=("advance", "financial-aid deadline change affects every applicant this month"))
    oid = persist(clean_conn, cid, low, d, scorer_model="deterministic")
    with clean_conn.cursor() as cur:
        cur.execute("SELECT priority, decision, editorial_exception, exception_rationale FROM opportunity_scores WHERE id=%s", (cid and oid,))
        r = cur.fetchone()
    assert r["editorial_exception"] and float(r["priority"]) == 53.0 and r["decision"] == "advance"
    assert opportunity_queue(clean_conn)[0]["cluster_id"] == cid


def test_score_without_observation_rejected(clean_conn):
    inst, campus, topics = make_school(clean_conn)
    with clean_conn.cursor() as cur:
        cur.execute("INSERT INTO intent_clusters (institution_id, label, answer_key) VALUES (%s,'x','k4') RETURNING id", (inst,))
        cid = cur.fetchone()["id"]
    clean_conn.commit()
    with pytest.raises(ValueError, match="without an observation"):
        persist(clean_conn, cid, Score(4, 4, 3, 4, 2, {}), decide(Score(4, 4, 3, 4, 2, OBS)))
