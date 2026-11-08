from campus_worker import permissions


def test_reddit_content_collection_off_and_unknown_denied(clean_conn):
    """Reddit is search_observation (continuous-local-run R35/R36): full fetch is denied with its own reason; content collection stays off."""
    permissions.seed_defaults(clean_conn)
    assert permissions.check_url(clean_conn, "https://www.reddit.com/r/Cornell/").allowed is False
    assert permissions.check_url(clean_conn, "https://www.reddit.com/r/Cornell/").reason == "search_observation_only"
    assert permissions.access_mode_for(clean_conn, "https://www.reddit.com/r/Cornell/") == "search_observation"
    assert permissions.check_url(clean_conn, "https://example.com/anything").reason == "no_permission_record"
    d = permissions.check_url(clean_conn, "https://scl.cornell.edu/residential-life/housing")
    assert d.allowed and d.retention_policy == "excerpts_only" and d.rate_limit_per_minute == 6
    assert permissions.check_url(clean_conn, "ftp://scl.cornell.edu/x").allowed is False
    assert permissions.check_url(clean_conn, "https://cornell.edu.evil.example/").allowed is False
