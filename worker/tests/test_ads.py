from campus_worker.adapters.ads import AdSenseAdapter, APPROVED_PLACEMENTS


def test_no_ad_code_when_disabled_or_staging():
    for env, enabled, pub in (("staging", True, "pub-1234567890123456"), ("production", False, "pub-1234567890123456"), ("production", True, None), ("production", True, "pub-bad")):
        a = AdSenseAdapter(publisher_id=pub, enabled=enabled, environment=env)
        assert not a.enabled and a.loader_tag(True) == "" and a.slots_for("guide", content_sections=8) == []
        assert a.capability().state == "disabled"


def test_one_loader_consent_and_approved_placements_only():
    a = AdSenseAdapter(publisher_id="pub-1234567890123456", enabled=True, environment="production")
    assert a.loader_tag(False) == "" and a.loader_tag(True).count("<script") == 1
    assert [s.placement for s in a.slots_for("guide", content_sections=2)] == ["after_essentials"]
    assert [s.placement for s in a.slots_for("guide", content_sections=6)] == ["after_essentials", "between_sections"]
    assert [s.placement for s in a.slots_for("entity_profile", is_desktop=False)] == ["after_facts"]
    assert a.slots_for("tool") == [] and a.slots_for("home") == []  # never around calculator controls
    html = a.slot_html(a.slots_for("guide")[0], "123")
    assert 'aria-label="Advertisement"' in html and "Advertisement" in html
    assert a.ads_txt().startswith("google.com, pub-1234567890123456, DIRECT")
    assert set(APPROVED_PLACEMENTS) >= {"guide", "entity_profile", "comparison", "tool"}


def test_rendered_pages_emit_no_ads_without_adapter():
    from campus_worker.render import engine, preview
    html = engine.render("entity_profile.html", **preview.profile_ctx())
    assert "adsbygoogle" not in html and "ad-slot" not in html
