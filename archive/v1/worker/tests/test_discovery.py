from datetime import datetime, timezone
from campus_worker import discovery as d
from tests.helpers import make_entity, make_school

T = datetime(2026, 10, 1, tzinfo=timezone.utc)


def test_synonyms_merge_and_raw_kept(clean_conn):
    inst, campus, topics = make_school(clean_conn)
    items = [
        d.QuestionInput("Do the dorms have AC?", "discussion", inst, campus, "housing", observed_at=T, source_ref="post1"),
        d.QuestionInput("Is there air conditioning in the residence halls", "official_faq", inst, campus, "housing", observed_at=T),
        d.QuestionInput("Do the dorms have AC?", "discussion", inst, campus, "housing", observed_at=T, source_ref="post1"),  # crosspost
        d.QuestionInput("do dorms have a/c", "search_suggestion", inst, campus, "housing", observed_at=T),
    ]
    out = d.ingest(clean_conn, items)
    assert out["stored"] == 3 and out["duplicate_occurrences"] == 1 and out["clusters_created"] == 1
    with clean_conn.cursor() as cur:
        cur.execute("SELECT raw_text FROM questions ORDER BY created_at")
        raws = [r["raw_text"] for r in cur.fetchall()]
    assert "Do the dorms have AC?" in raws  # raw wording preserved


def test_audience_split_only_where_rules_differ(clean_conn):
    inst, campus, topics = make_school(clean_conn)
    out = d.ingest(clean_conn, [
        d.QuestionInput("Can transfer students live on campus", "discussion", inst, campus, "housing", observed_at=T, source_ref="a"),
        d.QuestionInput("Can first-year students live on campus", "discussion", inst, campus, "housing", observed_at=T, source_ref="b"),
        d.QuestionInput("Is there parking for transfer students", "discussion", inst, campus, "transportation", observed_at=T, source_ref="c"),
        d.QuestionInput("Is there parking for first-year students", "discussion", inst, campus, "transportation", observed_at=T, source_ref="d"),
    ])
    with clean_conn.cursor() as cur:
        cur.execute("SELECT t.key, count(*) AS n FROM intent_clusters c JOIN topics t ON t.id=c.topic_id GROUP BY t.key")
        counts = {r["key"]: r["n"] for r in cur.fetchall()}
    assert counts["housing"] == 2      # eligibility differs by audience → split
    assert counts["transportation"] == 1  # parking rules do not → merged, audience kept on questions


def test_hypotheses_labeled_and_not_counted_as_observed(clean_conn):
    inst, campus, topics = make_school(clean_conn)
    ent = make_entity(clean_conn, inst, campus, topics["housing"])
    with clean_conn.cursor() as cur:
        cur.execute("INSERT INTO school_configs (institution_id, campus_id) VALUES (%s,%s) RETURNING id", (inst, campus))
        cfg = cur.fetchone()["id"]
        cur.execute("INSERT INTO school_topic_applicability (school_config_id, topic_id, applicability) VALUES (%s,%s,'applicable')", (cfg, topics["housing"]))
    clean_conn.commit()
    out = d.generate_hypotheses(clean_conn, institution_id=inst, campus_id=campus, topic_key="housing", entity_names=[(ent, "Fixture Hall")],
                                audiences=["first_year", "transfer"], limit=10)
    assert out["generated"] == 10 and out["hypotheses"] == 10
    with clean_conn.cursor() as cur:
        cur.execute("SELECT sum(observed_count) AS o, sum(hypothesis_count) AS h FROM intent_clusters")
        r = cur.fetchone()
    assert r["o"] == 0 and r["h"] == 10


def test_not_applicable_topic_generates_nothing(clean_conn):
    inst, campus, topics = make_school(clean_conn, name="Riverbend CC", slug="riverbend", itype="community_college", unitid="900003")
    with clean_conn.cursor() as cur:
        cur.execute("INSERT INTO school_configs (institution_id, campus_id) VALUES (%s,%s) RETURNING id", (inst, campus))
        cfg = cur.fetchone()["id"]
        cur.execute("INSERT INTO school_topic_applicability (school_config_id, topic_id, applicability) VALUES (%s,%s,'not_applicable')", (cfg, topics["housing"]))
    clean_conn.commit()
    out = d.generate_hypotheses(clean_conn, institution_id=inst, campus_id=campus, topic_key="housing", entity_names=[], audiences=["commuter"])
    assert out["stored"] == 0 and out["skipped_reason"] == "topic_not_applicable"


def test_normalize_examples():
    assert set(d.normalize("Do the dorms have AC?").split()) == set(d.normalize("air conditioning residence halls").split())
    assert d.detect_audience("Can transfers get housing?") == "transfer"
    assert d.detect_audience("How much is a double?") is None
