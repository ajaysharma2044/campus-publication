from campus_worker import permissions


def test_reddit_disabled_and_unknown_denied(clean_conn):
    permissions.seed_defaults(clean_conn)
    assert permissions.check_url(clean_conn, "https://www.reddit.com/r/Cornell/").allowed is False
    assert permissions.check_url(clean_conn, "https://www.reddit.com/r/Cornell/").reason == "permission_disabled"
    assert permissions.check_url(clean_conn, "https://example.com/anything").reason == "no_permission_record"
    d = permissions.check_url(clean_conn, "https://scl.cornell.edu/residential-life/housing")
    assert d.allowed and d.retention_policy == "excerpts_only" and d.rate_limit_per_minute == 6
    assert permissions.check_url(clean_conn, "ftp://scl.cornell.edu/x").allowed is False
    assert permissions.check_url(clean_conn, "https://cornell.edu.evil.example/").allowed is False
