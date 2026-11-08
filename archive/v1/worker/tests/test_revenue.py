from pathlib import Path
from campus_worker import revenue as r


def test_denominators_are_separate():
    m = r.Metrics(pageviews=50_000, sessions=30_000, ad_impressions=120_000, viewable_impressions=84_000, earnings_minor=75_000)
    assert m.page_rpm_minor() == 1500.0            # $15.00 per 1,000 pageviews
    assert m.impression_rpm_minor() == 625.0       # $6.25 per 1,000 impressions — different denominator
    assert m.viewability() == 0.7
    assert m.session_revenue_minor() == 2.5
    assert r.Metrics(0, None, None, None, 100).page_rpm_minor() is None
    assert r.page_revenue_scenario_minor(50_000, 1500) == 75_000  # SPEC §23 example: $750, a scenario not a forecast


def test_import_and_contribution(clean_conn, tmp_path):
    p = tmp_path / "adsense.csv"
    p.write_text("date,granularity,page_path,pageviews,ad_impressions,viewable_impressions,clicks,earnings\n2026-11-01,site,,1200,2500,1800,7,4.31\n2026-11-01,page,/unknown/,10,20,10,0,0.10\n")
    assert r.import_adsense_report(clean_conn, p, currency="USD") == 1  # unknown page path skipped, not invented
    c = r.contribution(clean_conn, "2026-11", hosting_minor=None, licensing_minor=None)
    assert c.gross_publisher_earnings_minor == 431 and "hosting" in c.missing_cost_items and c.contribution_minor == 431
    with clean_conn.cursor() as cur:
        cur.execute("SELECT is_estimated FROM revenue_reports")
        assert cur.fetchone()["is_estimated"] is True
