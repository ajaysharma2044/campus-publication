"""Search-result cache and search-call ledger (continuous-local-run R26; AT24).

A query observed inside CAMPUS_SERP_CACHE_DAYS is never re-searched: the coordinator hands cached observations to the
search-intel agent in its packet and skips dispatch entirely when every variant is cached. Every real search call is
recorded in the usage ledger (provider 'search', unpriced) so "zero new search calls" is asserted from the ledger.
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timedelta, timezone
from uuid import UUID

import psycopg

from .discovery import normalize

PROVIDER = "search"


def query_norm(q: str) -> str:
    n = normalize(q)
    return re.sub(r"\s+", " ", n).strip() or q.strip().lower()


def get(conn: psycopg.Connection, query: str, *, days: int, now: datetime | None = None) -> dict | None:
    now = now or datetime.now(timezone.utc)
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM serp_cache WHERE query_norm=%s AND observed_at >= %s", (query_norm(query), now - timedelta(days=days)))
        r = cur.fetchone()
    return dict(r) if r else None


def get_many(conn: psycopg.Connection, queries: list[str], *, days: int, now: datetime | None = None) -> dict[str, dict]:
    out = {}
    for q in queries:
        r = get(conn, q, days=days, now=now)
        if r:
            out[q] = r
    return out


def store(conn: psycopg.Connection, query: str, *, results: list[dict], follow_up_questions: list[str] | None = None,
          community_occurrences: list[dict] | None = None, navigational: bool = False, observed_at: datetime | None = None, provider: str = "websearch",
          demand_evidence: list[dict] | None = None) -> UUID:
    observed_at = observed_at or datetime.now(timezone.utc)
    with conn.cursor() as cur:
        cur.execute(
            """INSERT INTO serp_cache (query_norm, query_text, observed_at, provider, results, follow_up_questions, community_occurrences, navigational, demand_evidence)
               VALUES (%s,%s,%s,%s,%s::jsonb,%s::jsonb,%s::jsonb,%s,%s::jsonb)
               ON CONFLICT (query_norm) DO UPDATE SET query_text=EXCLUDED.query_text, observed_at=EXCLUDED.observed_at, provider=EXCLUDED.provider,
                 results=EXCLUDED.results, follow_up_questions=EXCLUDED.follow_up_questions, community_occurrences=EXCLUDED.community_occurrences, navigational=EXCLUDED.navigational,
                 demand_evidence=EXCLUDED.demand_evidence
               RETURNING id""",
            (query_norm(query), query, observed_at, provider, json.dumps(results[:10]), json.dumps(follow_up_questions or []), json.dumps(community_occurrences or []), navigational,
             json.dumps(demand_evidence or [])),
        )
        rid = cur.fetchone()["id"]
    conn.commit()
    return rid


def record_search_call(conn: psycopg.Connection, query: str, *, cached: bool, cluster_id: UUID | None = None, agent: str = "search-intel",
                       now: datetime | None = None) -> None:
    """One ledger row per search call (cached=False) or cache reuse (cached=True). Unpriced, visible."""
    now = now or datetime.now(timezone.utc)
    with conn.cursor() as cur:
        cur.execute(
            """INSERT INTO usage_ledger (occurred_at, day, month, provider, kind, amount_minor, currency, priced, detail)
               VALUES (%s,%s,%s,%s,'actual',0,'USD',FALSE,%s::jsonb)""",
            (now, now.date(), now.strftime("%Y-%m"), PROVIDER, json.dumps({"query": query, "cached": cached, "cluster_id": str(cluster_id) if cluster_id else None, "agent": agent})),
        )
    conn.commit()


def search_calls(conn: psycopg.Connection, *, since: datetime | None = None, cluster_id: UUID | None = None) -> dict:
    with conn.cursor() as cur:
        cur.execute(
            """SELECT count(*) FILTER (WHERE (detail->>'cached')::boolean IS FALSE) AS new_calls,
                      count(*) FILTER (WHERE (detail->>'cached')::boolean IS TRUE) AS cache_hits
               FROM usage_ledger WHERE provider=%s AND (%s::timestamptz IS NULL OR occurred_at >= %s) AND (%s::text IS NULL OR detail->>'cluster_id' = %s)""",
            (PROVIDER, since, since, str(cluster_id) if cluster_id else None, str(cluster_id) if cluster_id else None),
        )
        return dict(cur.fetchone())


def purge_expired(conn: psycopg.Connection, *, days: int, now: datetime | None = None) -> int:
    now = now or datetime.now(timezone.utc)
    with conn.cursor() as cur:
        cur.execute("DELETE FROM serp_cache WHERE observed_at < %s", (now - timedelta(days=days * 4),))
        n = cur.rowcount
    conn.commit()
    return n
