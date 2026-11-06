"""Source permissions registry and access modes (SPEC §08, §09; continuous-local-run R35, R36).

Every community or third-party source is registered with exactly one access mode, enforced here and in the
fetcher:

  search_observation  only titles, URLs, dates and snippets as they appear in search results. Used to detect
                      recurring questions and demand. Never fetched in full; never quoted; never feeds an
                      experience section. Allowed for any indexed site, including Reddit.
  fetch_permitted     full page fetch, only where robots.txt and the site's terms allow automated access,
                      recorded per domain with the date checked.
  api_authorized      an official API under terms that allow this use (credentials in .env when needed).
  disabled            nothing.

Legacy modes from SPEC §08 remain valid for official sources: public_http (official pages, robots-checked at
fetch), feed, export_import (downloaded datasets). Robots rules are checked at fetch time; this registry
records what the publication is *permitted* to do under terms, which robots alone does not settle.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from urllib.parse import urlparse

import psycopg

FETCH_MODES = {"fetch_permitted", "api_authorized", "public_http", "feed", "export_import"}
QUOTE_MODES = {"fetch_permitted", "api_authorized", "public_http", "feed", "export_import"}
OBSERVE_ONLY = {"search_observation"}
ALL_MODES = FETCH_MODES | OBSERVE_ONLY | {"disabled"}

DEFAULT_PERMISSIONS = [
    # domain_pattern, publisher, connector, access_mode, permission_state, retention, rpm, notes, attribution
    ("*.cornell.edu", "Cornell University", "official_html", "fetch_permitted", "allowed_with_limits", "excerpts_only", 6,
     "Official pages; public. robots.txt checked at fetch time and recorded.", None),
    ("classes.cornell.edu", "Cornell University Registrar (Class Roster API)", "api", "api_authorized", "allowed_with_limits", "full_text", 10,
     "Public JSON API https://classes.cornell.edu/api/2.0 — courses, prerequisites, term offerings (R46). No credential required.", None),
    ("nces.ed.gov", "NCES", "dataset", "export_import", "allowed", "full_text", 2, "IPEDS releases; import from downloaded files.", None),
    ("api.data.gov", "U.S. Department of Education (College Scorecard)", "api", "api_authorized", "allowed_with_limits", "full_text", 10,
     "College Scorecard API for first-destination earnings (R33 jobs); api key optional in .env.", None),
    # community / third-party: search observation until terms are checked and recorded (R35)
    ("*.reddit.com", "Reddit", "discussion", "search_observation", "allowed_with_limits", "none", 0,
     "Search-result observation only (titles, URLs, dates, snippets). Content collection stays off until the Reddit Data API is authorized (R36).", None),
    ("*.collegeconfidential.com", "College Confidential", "discussion", "search_observation", "allowed_with_limits", "none", 0, "search observation until terms checked", None),
    ("*.quora.com", "Quora", "discussion", "search_observation", "allowed_with_limits", "none", 0, "search observation until terms checked", None),
    ("*.youtube.com", "YouTube", "discussion", "search_observation", "allowed_with_limits", "none", 0, "titles only via search results", None),
    ("cornellsun.com", "The Cornell Daily Sun", "news", "search_observation", "allowed_with_limits", "none", 0, "secondary/historical context; search observation until terms checked", None),
    ("ithacavoice.org", "The Ithaca Voice", "news", "search_observation", "allowed_with_limits", "none", 0, "search observation until terms checked", None),
    ("*.wikipedia.org", "Wikipedia", "reference", "search_observation", "allowed_with_limits", "none", 0, "search observation until terms recorded (CC BY-SA)", "CC BY-SA 4.0"),
    ("api.stackexchange.com", "Stack Exchange (Academia and others)", "api", "api_authorized", "allowed_with_limits", "excerpts_only", 5,
     "Official API, CC BY-SA content with attribution (R46). Public quota without a key; key optional in .env.", "CC BY-SA 4.0"),
    # town sources (R34): official or authoritative; fetch_permitted pending the recorded robots check
    ("*.cityofithaca.org", "City of Ithaca", "official_html", "fetch_permitted", "allowed_with_limits", "excerpts_only", 4, "city government", None),
    ("*.tompkinscountyny.gov", "Tompkins County", "official_html", "fetch_permitted", "allowed_with_limits", "excerpts_only", 4, "county government", None),
    ("*.tcatbus.com", "TCAT (Tompkins Consolidated Area Transit)", "official_html", "fetch_permitted", "allowed_with_limits", "excerpts_only", 4, "local transit agency", None),
    ("*.flyithaca.com", "Ithaca Tompkins International Airport", "official_html", "fetch_permitted", "allowed_with_limits", "excerpts_only", 4, "airport", None),
    ("parks.ny.gov", "New York State Parks", "official_html", "fetch_permitted", "allowed_with_limits", "excerpts_only", 4, "state parks", None),
    ("*.visitithaca.com", "Visit Ithaca (visitor bureau)", "official_html", "fetch_permitted", "allowed_with_limits", "excerpts_only", 4, "visitor bureau", None),
    ("*.tcpl.org", "Tompkins County Public Library", "official_html", "fetch_permitted", "allowed_with_limits", "excerpts_only", 4, "public library", None),
    ("*.ourbus.com", "OurBus", "official_html", "fetch_permitted", "allowed_with_limits", "excerpts_only", 2, "intercity bus operator; factual details only", None),
    ("*.flixbus.com", "FlixBus / Greyhound", "official_html", "fetch_permitted", "allowed_with_limits", "excerpts_only", 2, "intercity bus operator; factual details only", None),
]


@dataclass(frozen=True)
class PermissionDecision:
    allowed: bool
    reason: str
    permission_id: str | None = None
    retention_policy: str = "none"
    rate_limit_per_minute: int = 0
    connector: str | None = None
    access_mode: str | None = None


def seed_defaults(conn: psycopg.Connection) -> None:
    with conn.cursor() as cur:
        for dp, pub, conn_name, mode, state, ret, rpm, notes, attrib in DEFAULT_PERMISSIONS:
            cur.execute(
                """INSERT INTO source_permissions (domain_pattern, publisher, connector, access_mode,
                   permission_state, retention_policy, rate_limit_per_minute, notes, reviewed_at, attribution_required)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,now(),%s)
                   ON CONFLICT (domain_pattern) DO UPDATE SET access_mode = CASE
                       -- never silently upgrade a disabled/legacy row to a looser mode; only migrate legacy public_http → fetch_permitted for the same publisher
                       WHEN source_permissions.access_mode = 'public_http' AND EXCLUDED.access_mode = 'fetch_permitted' THEN 'fetch_permitted'
                       WHEN source_permissions.access_mode = 'disabled' AND EXCLUDED.access_mode = 'search_observation' THEN 'search_observation'
                       ELSE source_permissions.access_mode END,
                     permission_state = CASE WHEN source_permissions.access_mode='disabled' AND EXCLUDED.access_mode='search_observation' THEN EXCLUDED.permission_state ELSE source_permissions.permission_state END,
                     attribution_required = COALESCE(source_permissions.attribution_required, EXCLUDED.attribution_required)""",
                (dp, pub, conn_name, mode, state, ret, rpm, notes, attrib),
            )
    conn.commit()


def _host_matches(pattern: str, host: str) -> bool:
    pattern = pattern.lower()
    host = host.lower()
    if pattern.startswith("*."):
        base = pattern[2:]
        return host == base or host.endswith("." + base)
    return host == pattern


def _best_row(conn: psycopg.Connection, url: str):
    parsed = urlparse(url)
    if parsed.scheme not in ("https", "http"):
        return None, "scheme_not_allowed"
    host = parsed.hostname or ""
    if not host:
        return None, "no_host"
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM source_permissions")
        rows = cur.fetchall()
    matches = [r for r in rows if _host_matches(r["domain_pattern"], host)]
    if not matches:
        return None, "no_permission_record"
    # most specific match wins: exact host over wildcard, longer pattern over shorter
    matches.sort(key=lambda r: (r["domain_pattern"].startswith("*."), -len(r["domain_pattern"])))
    return matches[0], "ok"


def access_mode_for(conn: psycopg.Connection, url: str) -> str:
    """The single registered access mode for a URL's host; 'disabled' when unregistered (unknown domains are denied)."""
    row, _ = _best_row(conn, url)
    if row is None:
        return "disabled"
    if row["permission_state"] in ("disabled", "pending_authorization"):
        return "disabled"
    return row["access_mode"]


def check_url(conn: psycopg.Connection, url: str) -> PermissionDecision:
    """May the fetcher open this URL in full? Only FETCH_MODES. search_observation is denied with its own reason."""
    row, why = _best_row(conn, url)
    if row is None:
        return PermissionDecision(False, why)
    if row["permission_state"] in ("disabled", "pending_authorization") or row["access_mode"] == "disabled":
        return PermissionDecision(False, f"permission_{row['permission_state']}", str(row["id"]), row["retention_policy"], 0, row["connector"], row["access_mode"])
    if row["access_mode"] in OBSERVE_ONLY:
        return PermissionDecision(False, "search_observation_only", str(row["id"]), "none", 0, row["connector"], row["access_mode"])
    if row["access_mode"] == "fetch_permitted" and row.get("robots_allows") is False:
        return PermissionDecision(False, "robots_disallow_recorded", str(row["id"]), row["retention_policy"], 0, row["connector"], row["access_mode"])
    return PermissionDecision(True, "allowed", str(row["id"]), row["retention_policy"], row["rate_limit_per_minute"], row["connector"], row["access_mode"])


def may_quote(conn: psycopg.Connection, url: str) -> tuple[bool, str]:
    """May text from this source be quoted or used in a 'what residents report' section? Never for search_observation."""
    mode = access_mode_for(conn, url)
    if mode in QUOTE_MODES:
        row, _ = _best_row(conn, url)
        attrib = (row or {}).get("attribution_required")
        return True, f"mode {mode}" + (f"; attribution required: {attrib}" if attrib else "")
    return False, f"mode {mode}: community content may create questions and demand evidence only, never quotes or experience material (R35)"


class QuoteNotPermitted(Exception):
    pass


def assert_may_quote(conn: psycopg.Connection, url: str) -> str:
    ok, why = may_quote(conn, url)
    if not ok:
        raise QuoteNotPermitted(why)
    return why


def record_terms_check(conn: psycopg.Connection, domain_pattern: str, *, access_mode: str, robots_allows: bool | None = None,
                       terms_reference: str | None = None, note: str | None = None, attribution_required: str | None = None,
                       now: datetime | None = None) -> None:
    """Record a terms / robots check for a domain and set its single access mode (R35). Owner or coordinator action, logged."""
    if access_mode not in ALL_MODES:
        raise ValueError(f"unknown access mode {access_mode}")
    now = now or datetime.now(timezone.utc)
    with conn.cursor() as cur:
        cur.execute(
            """UPDATE source_permissions SET access_mode=%s, terms_checked_at=%s, robots_checked_at=CASE WHEN %s::boolean IS NULL THEN robots_checked_at ELSE %s END,
               robots_allows=COALESCE(%s, robots_allows), terms_reference=COALESCE(%s, terms_reference), notes=COALESCE(%s, notes),
               attribution_required=COALESCE(%s, attribution_required), reviewed_at=%s,
               permission_state = CASE WHEN %s='disabled' THEN 'disabled' WHEN permission_state='disabled' THEN 'allowed_with_limits' ELSE permission_state END
               WHERE domain_pattern=%s""",
            (access_mode, now, robots_allows, now, robots_allows, terms_reference, note, attribution_required, now, access_mode, domain_pattern),
        )
        if cur.rowcount == 0:
            raise LookupError(f"no permission row for {domain_pattern}")
    conn.commit()


def record_robots(conn: psycopg.Connection, url: str, allows: bool, *, now: datetime | None = None) -> None:
    row, _ = _best_row(conn, url)
    if row is None:
        return
    with conn.cursor() as cur:
        cur.execute("UPDATE source_permissions SET robots_checked_at=%s, robots_allows=%s WHERE id=%s", (now or datetime.now(timezone.utc), allows, row["id"]))
    conn.commit()


def robots_allows(robots_txt: str, path: str, user_agent: str) -> bool:
    """Deterministic robots.txt evaluation with the standard library parser. Empty/unparseable → allowed."""
    from urllib.robotparser import RobotFileParser

    rp = RobotFileParser()
    rp.parse((robots_txt or "").splitlines())
    try:
        return rp.can_fetch(user_agent, path or "/")
    except Exception:  # noqa: BLE001
        return True


def list_modes(conn: psycopg.Connection) -> list[dict]:
    with conn.cursor() as cur:
        cur.execute("SELECT domain_pattern, publisher, access_mode, permission_state, robots_allows, robots_checked_at, terms_checked_at, attribution_required FROM source_permissions ORDER BY domain_pattern")
        return [dict(r) for r in cur.fetchall()]
