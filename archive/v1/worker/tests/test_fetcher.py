import socket
import httpx
import pytest
from campus_worker.fetcher import FetchRefused, RateLimiter, SafeFetcher, resolve_and_check
from tests.helpers import make_school

PUBLIC = [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 443))]
PRIVATE = [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("10.0.0.5", 443))]


def resolver_factory(mapping):
    def _res(host, port, proto=0):
        return mapping.get(host, PUBLIC)
    return _res


def test_private_and_metadata_addresses_refused():
    with pytest.raises(FetchRefused, match="private_address"):
        resolve_and_check("evil.example.edu", resolver=resolver_factory({"evil.example.edu": PRIVATE}))
    for h in ("169.254.169.254", "127.0.0.1", "localhost", "metadata.google.internal", "::1"):
        with pytest.raises(FetchRefused):
            resolve_and_check(h, resolver=resolver_factory({}))


def test_permission_denied_before_any_network(clean_conn):
    make_school(clean_conn)
    calls = []
    def handler(req):
        calls.append(req.url); return httpx.Response(200, text="x")
    f = SafeFetcher(clean_conn, transport=httpx.MockTransport(handler), resolver=resolver_factory({}), sleep=lambda s: None)
    with pytest.raises(FetchRefused, match="permission_denied"):
        f.fetch("https://unknown.example.com/page")
    with pytest.raises(FetchRefused, match="permission_denied"):
        f.fetch("https://www.reddit.com/r/x")
    assert calls == []


def test_redirect_to_private_or_unpermitted_host_rejected(clean_conn):
    make_school(clean_conn)
    def handler(req):
        if req.url.host == "www.example.edu":
            return httpx.Response(302, headers={"location": "https://internal.example.edu/secret"})
        return httpx.Response(200, headers={"content-type": "text/html"}, text="<p>secret</p>")
    f = SafeFetcher(clean_conn, transport=httpx.MockTransport(handler), resolver=resolver_factory({"internal.example.edu": PRIVATE}), sleep=lambda s: None)
    with pytest.raises(FetchRefused, match="private_address"):
        f.fetch("https://www.example.edu/start")
    def handler2(req):
        if req.url.host == "www.example.edu":
            return httpx.Response(301, headers={"location": "https://other.example.org/"})
        return httpx.Response(200, text="x")
    f2 = SafeFetcher(clean_conn, transport=httpx.MockTransport(handler2), resolver=resolver_factory({}), sleep=lambda s: None)
    with pytest.raises(FetchRefused, match="redirect_permission_denied"):
        f2.fetch("https://www.example.edu/start")


def test_oversized_and_wrong_type_refused_and_credentials_stripped(clean_conn):
    make_school(clean_conn)
    seen = []
    def handler(req):
        seen.append(str(req.url))
        if req.url.path == "/big":
            return httpx.Response(200, headers={"content-type": "text/html"}, content=b"x" * 2000)
        if req.url.path == "/zip":
            return httpx.Response(200, headers={"content-type": "application/zip"}, content=b"PK")
        return httpx.Response(200, headers={"content-type": "text/html", "etag": '"e1"'}, text="<main>ok</main>")
    f = SafeFetcher(clean_conn, transport=httpx.MockTransport(handler), resolver=resolver_factory({}), max_bytes=1000, sleep=lambda s: None)
    with pytest.raises(FetchRefused, match="oversized"):
        f.fetch("https://www.example.edu/big")
    with pytest.raises(FetchRefused, match="unexpected_content_type"):
        f.fetch("https://www.example.edu/zip")
    r = f.fetch("https://user:pw@www.example.edu/ok")
    assert r.status == 200 and "user:pw" not in seen[-1] and r.etag == '"e1"'


def test_rate_limiter_spaces_requests():
    rl = RateLimiter()
    t = [100.0]
    slept = []
    def now(): return t[0]
    def sleep(s): slept.append(s); t[0] += s
    rl.wait("h", 6, sleep=sleep, now=now)
    rl.wait("h", 6, sleep=sleep, now=now)
    assert slept and abs(slept[0] - 10.0) < 1e-6
    with pytest.raises(FetchRefused):
        rl.wait("h", 0, sleep=sleep, now=now)


def test_retry_after_surfaced_and_404_returned(clean_conn):
    make_school(clean_conn)
    def handler(req):
        if req.url.path == "/slow":
            return httpx.Response(429, headers={"retry-after": "120"})
        return httpx.Response(404)
    f = SafeFetcher(clean_conn, transport=httpx.MockTransport(handler), resolver=resolver_factory({}), sleep=lambda s: None)
    r = f.fetch("https://www.example.edu/slow")
    assert r.status == 429 and r.retry_after_seconds == 120
    assert f.fetch("https://www.example.edu/gone").status == 404
