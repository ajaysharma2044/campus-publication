import pytest
from campus_worker import experiments as x


def _spec(key="headline-1", area="headline"):
    return x.ExperimentSpec(key, area, "A headline naming the billing basis raises CTR without lowering task completion.", {"control": 50, "variant": 50},
                            "ctr", [{"metric": "comparison_complete", "max_regression_pct": 5}], "14 days and 2000 impressions per arm", "stop at 28 days or if guardrail breached", "revert title in CMS")


def test_registry_rules(clean_conn):
    eid = x.create(clean_conn, _spec())
    x.start(clean_conn, "headline-1")
    with pytest.raises(ValueError, match="already running"):
        x.create(clean_conn, _spec(key="headline-2"))
    bad = _spec(key="h3", area="ads"); bad.guardrails = []
    with pytest.raises(ValueError, match="guardrail"):
        x.create(clean_conn, bad)
    with pytest.raises(ValueError, match="measured result"):
        x.conclude(clean_conn, "headline-1", outcome="win")
    x.conclude(clean_conn, "headline-1", outcome="inconclusive: 1,400 impressions per arm after 28 days; CTR +0.3pp, CI crosses zero")
    assigns = {x.assign("headline-1", {"control": 50, "variant": 50}, f"tok{i}") for i in range(50)}
    assert assigns == {"control", "variant"}
    assert x.assign("headline-1", {"control": 50, "variant": 50}, "tok1") == x.assign("headline-1", {"control": 50, "variant": 50}, "tok1")
