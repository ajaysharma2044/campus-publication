from datetime import date
from campus_worker import analytics as a


def _ev(name="page_view", **props):
    base = {"page_id": "p1", "template": "guide", "device_class": "phone", "session_token": "s1"}
    base.update(props)
    return {"name": name, "props": base, "ts": "2026-11-02T10:15:00Z"}


def test_dictionary_and_pii_rejection():
    assert a.validate_event(_ev()) == []
    assert any("personal" in e for e in a.validate_event(_ev(email="x@y.com")))
    assert any("personal data" in e for e in a.validate_event(_ev(audience="call me at 555-123-4567")))
    assert a.validate_event(_ev("made_up_event"))
    assert a.validate_event(_ev(device_class="iPhone 15 Pro Max"))
    assert a.validate_event({"name": "page_view", "props": {"q": "mews hall"}, "ts": "x"})


def test_dedupe_bots_and_aggregate(clean_conn):
    evs = [_ev(), _ev(), _ev(session_token="s2"), _ev("source_click"), _ev(user_agent="Googlebot/2.1"), _ev("page_view", email="a@b.c")]
    out = a.aggregate(clean_conn, evs, day=date(2026, 11, 2))
    assert out == {"accepted": 3, "deduped": 1, "rejected": 2}
    with clean_conn.cursor() as cur:
        cur.execute("SELECT event_name, count FROM analytics_aggregates ORDER BY event_name")
        rows = [(r["event_name"], r["count"]) for r in cur.fetchall()]
    assert rows == [("page_view", 2), ("source_click", 1)]
    assert a.purge_expired(clean_conn) == 0


def test_analytics_tag_only_in_production_with_consent():
    assert a.analytics_tag(True, "staging", True) == ""
    assert a.analytics_tag(True, "production", False) == ""
    assert a.analytics_tag(False, "production", True) == ""
    assert "<script" in a.analytics_tag(True, "production", True)
