"""Safe HTTP fetcher (SPEC §08, §27).

Guarantees:
- Only https/http to hosts with an allowed source_permissions record.
- Every hop (including redirects) is resolved and checked against private/loopback/link-local/
  metadata ranges before connecting; redirects are followed manually (max 5) and re-validated.
- Credentials in URLs are stripped. Response size is capped while streaming.
- Content type must be in the expected set for the collector.
- Per-domain rate limit (token bucket) and a circuit breaker fed by source_registry failures.
- Conditional requests with ETag / Last-Modified from the previous snapshot.
- Retry-After is honoured and surfaced; the fetcher never retries on its own (the queue does).

Fetched bytes are untrusted data. Nothing here interprets them.
"""
from __future__ import annotations

import ipaddress
import socket
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from urllib.parse import urljoin, urlsplit, urlunsplit

import httpx
import psycopg

from .permissions import check_url, record_robots, robots_allows

MAX_BYTES_DEFAULT = 5 * 1024 * 1024
MAX_REDIRECTS = 5
CIRCUIT_FAILURES = 5
CIRCUIT_COOLDOWN = timedelta(hours=6)
USER_AGENT = "CampusPublicationBot/0.1 (+editorial research; contact via publication site)"

BLOCKED_NETWORKS = [ipaddress.ip_network(n) for n in (
    "0.0.0.0/8", "10.0.0.0/8", "100.64.0.0/10", "127.0.0.0/8", "169.254.0.0/16", "172.16.0.0/12",
    "192.0.0.0/24", "192.168.0.0/16", "198.18.0.0/15", "224.0.0.0/4", "240.0.0.0/4",
    "::1/128", "fc00::/7", "fe80::/10", "::ffff:0:0/96",
)]
BLOCKED_HOSTS = {"localhost", "metadata.google.internal", "metadata", "instance-data"}


class FetchRefused(Exception):
    def __init__(self, reason: str, detail: str = ""):
        super().__init__(f"{reason}: {detail}" if detail else reason)
        self.reason = reason
        self.detail = detail


@dataclass
class FetchResult:
    requested_url: str
    final_url: str
    status: int
    content_type: str | None
    body: bytes
    etag: str | None
    last_modified: str | None
    fetched_at: datetime
    unchanged: bool = False          # 304
    retry_after_seconds: int | None = None
    hops: list[str] = field(default_factory=list)


class RateLimiter:
    """Simple per-host token bucket. One process; the DB-level rate is enforced by job spacing."""

    def __init__(self):
        self._next_allowed: dict[str, float] = {}

    def wait(self, host: str, per_minute: int, *, sleep=time.sleep, now=time.monotonic) -> float:
        if per_minute <= 0:
            raise FetchRefused("rate_limit_zero", host)
        interval = 60.0 / per_minute
        t = now()
        nxt = self._next_allowed.get(host, 0.0)
        waited = 0.0
        if t < nxt:
            waited = nxt - t
            sleep(waited)
            t = nxt
        self._next_allowed[host] = t + interval
        return waited


def _strip_credentials(url: str) -> str:
    parts = urlsplit(url)
    if "@" in parts.netloc:
        host = parts.netloc.rsplit("@", 1)[1]
        parts = parts._replace(netloc=host)
    return urlunsplit(parts._replace(fragment=""))


def resolve_and_check(host: str, *, resolver=socket.getaddrinfo) -> list[str]:
    """Resolve host and refuse if any address is private/loopback/link-local/metadata.
    Returns the addresses so callers can pin them (defence against DNS rebinding)."""
    if not host or host.lower() in BLOCKED_HOSTS or host.endswith(".internal") or host.endswith(".local"):
        raise FetchRefused("blocked_host", host)
    try:
        ipaddress.ip_address(host)
        literal = True
    except ValueError:
        literal = False
    if literal:
        addrs = [host]
    else:
        try:
            infos = resolver(host, 443, proto=socket.IPPROTO_TCP)
        except socket.gaierror as e:
            raise FetchRefused("dns_failure", f"{host}: {e}")
        addrs = sorted({i[4][0] for i in infos})
    if not addrs:
        raise FetchRefused("dns_failure", host)
    for a in addrs:
        ip = ipaddress.ip_address(a)
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_multicast or ip.is_reserved or ip.is_unspecified \
                or any(ip in n for n in BLOCKED_NETWORKS):
            raise FetchRefused("private_address", f"{host} -> {a}")
    return addrs


class SafeFetcher:
    def __init__(self, conn: psycopg.Connection, *, transport: httpx.BaseTransport | None = None,
                 resolver=socket.getaddrinfo, rate_limiter: RateLimiter | None = None,
                 max_bytes: int = MAX_BYTES_DEFAULT, timeout: float = 20.0, sleep=time.sleep, check_robots: bool = True):
        self.conn = conn
        self.transport = transport
        self.resolver = resolver
        self.rate = rate_limiter or RateLimiter()
        self.max_bytes = max_bytes
        self.timeout = timeout
        self._sleep = sleep
        self.check_robots = check_robots
        self._robots: dict[str, str | None] = {}   # host → robots.txt text (None = unreachable → treated as allow, recorded as unknown)

    # -- robots.txt (continuous-local-run R35: never fetch past robots rules) -----------------
    def _robots_text(self, scheme: str, host: str) -> str | None:
        if host in self._robots:
            return self._robots[host]
        text: str | None = None
        try:
            with httpx.Client(transport=self.transport, timeout=self.timeout, follow_redirects=True) as client:
                r = client.get(f"{scheme}://{host}/robots.txt", headers={"User-Agent": USER_AGENT})
                if r.status_code == 200 and (r.headers.get("content-type", "").startswith("text/") or r.text.lstrip().lower().startswith(("user-agent", "#", "sitemap"))):
                    text = r.text[:200_000]
                elif r.status_code in (401, 403):
                    text = "User-agent: *\nDisallow: /\n"   # conservative: a robots file we are refused counts as disallow
                else:
                    text = ""                                   # 404 etc. → no rules
        except Exception:  # noqa: BLE001 — unreachable robots is not a disallow, but it is recorded as unknown
            text = None
        self._robots[host] = text
        return text

    def robots_ok(self, url: str) -> bool:
        parts = urlsplit(url)
        text = self._robots_text(parts.scheme, parts.hostname or "")
        if text is None:
            return True
        ua = USER_AGENT.split("/")[0]
        ok = robots_allows(text, parts.path or "/", ua)
        # The permission row covers a whole domain pattern, so it records whether robots allows the SITE (its root), not this one path:
        # a single disallowed path (a /search/ or /user/ URL from a sitemap) must not switch every later fetch of the domain off (bulk crawl, 2026-11-06).
        try:
            record_robots(self.conn, url, ok if (parts.path or "/") == "/" else robots_allows(text, "/", ua))
        except Exception:  # noqa: BLE001
            pass
        return ok

    # -- circuit breaker -------------------------------------------------
    def _circuit_open(self, url: str) -> bool:
        with self.conn.cursor() as cur:
            cur.execute("SELECT consecutive_failures, last_fetched_at, health FROM source_registry WHERE canonical_url=%s", (url,))
            r = cur.fetchone()
        if not r:
            return False
        if r["health"] == "gone":
            return True
        if r["consecutive_failures"] >= CIRCUIT_FAILURES and r["last_fetched_at"] and \
                r["last_fetched_at"] > datetime.now(timezone.utc) - CIRCUIT_COOLDOWN:
            return True
        return False

    def _previous_validators(self, url: str) -> tuple[str | None, str | None]:
        with self.conn.cursor() as cur:
            cur.execute(
                """SELECT s.etag, s.last_modified FROM fetch_snapshots s JOIN source_registry r ON r.id=s.source_id
                   WHERE r.canonical_url=%s AND s.outcome IN ('ok','unchanged') ORDER BY s.fetched_at DESC LIMIT 1""", (url,))
            r = cur.fetchone()
        return (r["etag"], r["last_modified"]) if r else (None, None)

    # -- main ------------------------------------------------------------
    def fetch(self, url: str, *, expected_types: tuple[str, ...] = ("text/html",), use_conditional: bool = True) -> FetchResult:
        url = _strip_credentials(url)
        decision = check_url(self.conn, url)
        if not decision.allowed:
            raise FetchRefused("permission_denied", decision.reason)
        if self._circuit_open(url):
            raise FetchRefused("circuit_open", url)
        if self.check_robots and not self.robots_ok(url):
            raise FetchRefused("robots_disallow", url)
        etag, last_mod = self._previous_validators(url) if use_conditional else (None, None)
        headers = {"User-Agent": USER_AGENT, "Accept": ", ".join(expected_types) + ", */*;q=0.1"}
        if etag:
            headers["If-None-Match"] = etag
        if last_mod:
            headers["If-Modified-Since"] = last_mod

        hops: list[str] = []
        current = url
        with httpx.Client(transport=self.transport, timeout=self.timeout, follow_redirects=False) as client:
            for _ in range(MAX_REDIRECTS + 1):
                parts = urlsplit(current)
                if parts.scheme not in ("http", "https"):
                    raise FetchRefused("scheme_not_allowed", parts.scheme)
                host = parts.hostname or ""
                resolve_and_check(host, resolver=self.resolver)
                hop_decision = check_url(self.conn, current)
                if not hop_decision.allowed:
                    raise FetchRefused("redirect_permission_denied", current)
                self.rate.wait(host, hop_decision.rate_limit_per_minute, sleep=self._sleep)
                hops.append(current)
                with client.stream("GET", current, headers=headers) as resp:
                    if resp.status_code in (301, 302, 303, 307, 308):
                        loc = resp.headers.get("location")
                        if not loc:
                            raise FetchRefused("redirect_without_location", current)
                        current = _strip_credentials(urljoin(current, loc))
                        continue
                    retry_after = resp.headers.get("retry-after")
                    ra = int(retry_after) if retry_after and retry_after.isdigit() else None
                    if resp.status_code == 304:
                        return FetchResult(url, current, 304, None, b"", etag, last_mod, datetime.now(timezone.utc), unchanged=True, hops=hops)
                    ctype = (resp.headers.get("content-type") or "").split(";")[0].strip().lower() or None
                    if resp.status_code >= 400:
                        return FetchResult(url, current, resp.status_code, ctype, b"", None, None, datetime.now(timezone.utc), retry_after_seconds=ra, hops=hops)
                    if ctype not in expected_types:
                        raise FetchRefused("unexpected_content_type", f"{ctype} not in {expected_types}")
                    declared = resp.headers.get("content-length")
                    if declared and declared.isdigit() and int(declared) > self.max_bytes:
                        raise FetchRefused("oversized", f"declared {declared} > {self.max_bytes}")
                    buf = bytearray()
                    for chunk in resp.iter_bytes():
                        buf.extend(chunk)
                        if len(buf) > self.max_bytes:
                            raise FetchRefused("oversized", f"stream exceeded {self.max_bytes}")
                    return FetchResult(url, current, resp.status_code, ctype, bytes(buf), resp.headers.get("etag"),
                                       resp.headers.get("last-modified"), datetime.now(timezone.utc), hops=hops)
        raise FetchRefused("too_many_redirects", url)
