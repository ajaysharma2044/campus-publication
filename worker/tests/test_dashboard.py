from campus_worker.config import get_settings
from campus_worker.dashboard.app import gather, render_html


def test_dashboard_renders_without_live_claims(clean_conn):
    d = gather(clean_conn, get_settings())
    html = render_html(d)
    assert "Operating status" in html and "never run" in html
    assert d["integrations"]["anthropic"]["state"] == "unconnected" and d["integrations"]["adsense"]["state"] == "disabled"
    assert "unconnected" in html and "noindex" in html
    assert "verified claim" not in html  # dashboard never asserts verification it cannot show
