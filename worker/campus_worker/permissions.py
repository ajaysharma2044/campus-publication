"""Source permissions registry (SPEC §08, §09).

A fetch is allowed only if a matching permission row says so. Robots rules are checked
separately at fetch time; this registry records what the publication is *permitted* to do under
terms and authorization, which robots alone does not settle. Reddit is seeded as disabled.
"""
from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlparse

import psycopg

DEFAULT_PERMISSIONS = [
    # domain_pattern, publisher, connector, access_mode, permission_state, retention, rpm, notes
    ("*.cornell.edu", "Cornell University", "official_html", "public_http", "allowed_with_limits", "excerpts_only", 6,
     "Official pages; public. Live fetch blocked in build container; fixtures only until egress allowed."),
    ("*.reddit.com", "Reddit", "discussion", "disabled", "disabled", "none", 0,
     "Disabled until a Reddit Data API commercial authorization exists (SPEC §09)."),
    ("nces.ed.gov", "NCES", "dataset", "export_import", "allowed", "full_text", 2,
     "IPEDS releases; import from downloaded files."),
]


@dataclass(frozen=True)
class PermissionDecision:
    allowed: bool
    reason: str
    permission_id: str | None = None
    retention_policy: str = "none"
    rate_limit_per_minute: int = 0
    connector: str | None = None


def seed_defaults(conn: psycopg.Connection) -> None:
    with conn.cursor() as cur:
        for dp, pub, conn_name, mode, state, ret, rpm, notes in DEFAULT_PERMISSIONS:
            cur.execute(
                """INSERT INTO source_permissions (domain_pattern, publisher, connector, access_mode,
                   permission_state, retention_policy, rate_limit_per_minute, notes, reviewed_at)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,now()) ON CONFLICT (domain_pattern) DO NOTHING""",
                (dp, pub, conn_name, mode, state, ret, rpm, notes),
            )
    conn.commit()


def _host_matches(pattern: str, host: str) -> bool:
    pattern = pattern.lower()
    host = host.lower()
    if pattern.startswith("*."):
        base = pattern[2:]
        return host == base or host.endswith("." + base)
    return host == pattern


def check_url(conn: psycopg.Connection, url: str) -> PermissionDecision:
    parsed = urlparse(url)
    if parsed.scheme not in ("https", "http"):
        return PermissionDecision(False, "scheme_not_allowed")
    host = parsed.hostname or ""
    if not host:
        return PermissionDecision(False, "no_host")
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM source_permissions")
        rows = cur.fetchall()
    # most specific match wins: exact host over wildcard
    matches = [r for r in rows if _host_matches(r["domain_pattern"], host)]
    if not matches:
        return PermissionDecision(False, "no_permission_record")
    matches.sort(key=lambda r: (r["domain_pattern"].startswith("*."), -len(r["domain_pattern"])))
    best = matches[0]
    if best["permission_state"] in ("disabled", "pending_authorization") or best["access_mode"] == "disabled":
        return PermissionDecision(False, f"permission_{best['permission_state']}", str(best["id"]),
                                  best["retention_policy"], 0, best["connector"])
    return PermissionDecision(True, "allowed", str(best["id"]), best["retention_policy"],
                              best["rate_limit_per_minute"], best["connector"])
