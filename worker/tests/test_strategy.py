"""Search strategy persistence (specs/continuous-local-run.md R14, R45; AT13 fixture part)."""
import pytest

from campus_worker import strategy
from tests.agent_fixtures import OUTPUTS
from tests.helpers import make_school


def test_store_strategy_writes_every_r14_section_and_targets(clean_conn, tmp_path):
    inst, campus, topics = make_school(clean_conn)
    doc = OUTPUTS["search_strategist"]
    res = strategy.store(clean_conn, doc, institution_id=inst, place_id=None, topic_key="housing", md_root=tmp_path)
    md = (tmp_path / "fixture-state" / "housing.md").read_text()
    for section in strategy.SECTIONS:
        assert f"## {section}" in md, section
    assert "Fixture Hall: Rooms, Cost and What to Know" in md and res["targets"] == 2 and res["version"] == 1
    assert strategy.win_plan_for(clean_conn, "/schools/fixture-state/housing/fixture-hall/")["target_title"].startswith("Fixture Hall")
    assert strategy.primary_query_conflict(clean_conn, "/schools/fixture-state/housing/other/", "fixture hall review") == "/schools/fixture-state/housing/fixture-hall/"
    assert strategy.primary_query_conflict(clean_conn, "/schools/fixture-state/housing/fixture-hall/", "fixture hall review") is None
    # a new version replaces the old targets for the same scope/topic
    res2 = strategy.store(clean_conn, doc, institution_id=inst, place_id=None, topic_key="housing", md_root=tmp_path)
    assert res2["version"] == 2 and strategy.existing_targets(clean_conn) and len(strategy.existing_targets(clean_conn)) == 2


def test_two_pages_targeting_the_same_query_is_rejected(clean_conn, tmp_path):
    inst, campus, topics = make_school(clean_conn)
    doc = dict(OUTPUTS["search_strategist"])
    doc["cluster_map"] = doc["cluster_map"] + [{"query_group": "dup", "queries": ["fixture hall review"], "page_path": "/schools/fixture-state/housing/fixture-hall-2/", "format": "guide"}]
    doc["win_plans"] = doc["win_plans"] + [dict(doc["win_plans"][0], page_path="/schools/fixture-state/housing/fixture-hall-2/")]
    errs = strategy.check_cluster_map(doc)
    assert errs and "targeted by two pages" in errs[0]
    with pytest.raises(strategy.CannibalizationError):
        strategy.store(clean_conn, doc, institution_id=inst, place_id=None, topic_key="housing", md_root=tmp_path)
    # a different topic's strategy may not claim a query an earlier strategy already owns
    strategy.store(clean_conn, OUTPUTS["search_strategist"], institution_id=inst, place_id=None, topic_key="housing", md_root=tmp_path)
    other = dict(OUTPUTS["search_strategist"], scope={"school_slug": "fixture-state", "topic_key": "dining"})
    other["cluster_map"] = [{"query_group": "g", "queries": ["fixture hall review"], "page_path": "/schools/fixture-state/dining/fixture-hall-dining/", "format": "guide"}]
    other["win_plans"] = [dict(OUTPUTS["search_strategist"]["win_plans"][0], page_path="/schools/fixture-state/dining/fixture-hall-dining/")]
    with pytest.raises(strategy.CannibalizationError):
        strategy.store(clean_conn, other, institution_id=inst, place_id=None, topic_key="dining", md_root=tmp_path)
