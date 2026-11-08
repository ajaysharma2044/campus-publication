"""Keyword-metrics and SERP adapters (SPEC §11).

Both are unconnected: no authorized provider exists yet. They support importing owner-supplied
exports (CSV/JSON) so demand and SERP observations can be recorded with provenance. Nothing is
fabricated; unknown or suppressed volumes stay NULL and overlapping variants are grouped, never
summed.
"""
from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from uuid import UUID

import psycopg

from .base import Capability, NotConnected


@dataclass
class DemandRow:
    query_text: str
    geography: str
    language: str
    window_start: date
    window_end: date
    volume_low: int | None
    volume_high: int | None
    is_suppressed: bool
    variant_group: str | None
    monthly_breakdown: dict | None
    provider: str
    retrieved_at: datetime


class KeywordProviderAdapter:
    provider_name = "keyword_metrics"

    def __init__(self, api_key: str | None = None):
        self._key = api_key

    def capability(self) -> Capability:
        if self._key:
            return Capability(self.provider_name, "connected", "authorized provider key present", priced=True)
        return Capability(self.provider_name, "unconnected", "no authorized keyword-metrics provider; import exports only", priced=True, features=("import_export",))

    def fetch(self, *_a, **_k):
        raise NotConnected(self.provider_name)

    @staticmethod
    def parse_export(path: Path, *, provider: str, geography: str, language: str, retrieved_at: datetime) -> list[DemandRow]:
        """Parse a generic export with columns: query, window_start, window_end, volume_low, volume_high,
        suppressed, variant_group, monthly_json. Blank volume → NULL (unknown), never 0."""
        rows: list[DemandRow] = []
        with path.open(newline="", encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                def _int(v):
                    v = (v or "").strip()
                    return int(v) if v.isdigit() else None
                suppressed = (r.get("suppressed") or "").strip().lower() in ("1", "true", "yes")
                rows.append(DemandRow(
                    query_text=r["query"].strip(),
                    geography=geography, language=language,
                    window_start=date.fromisoformat(r["window_start"]),
                    window_end=date.fromisoformat(r["window_end"]),
                    volume_low=None if suppressed else _int(r.get("volume_low")),
                    volume_high=None if suppressed else _int(r.get("volume_high")),
                    is_suppressed=suppressed,
                    variant_group=(r.get("variant_group") or "").strip() or None,
                    monthly_breakdown=json.loads(r["monthly_json"]) if (r.get("monthly_json") or "").strip() else None,
                    provider=provider, retrieved_at=retrieved_at,
                ))
        return rows


def store_demand(conn: psycopg.Connection, cluster_id: UUID, rows: list[DemandRow]) -> int:
    n = 0
    with conn.cursor() as cur:
        for r in rows:
            cur.execute(
                """INSERT INTO demand_observations (cluster_id, provider, query_text, geography, language, window_start,
                   window_end, monthly_breakdown, volume_low, volume_high, is_suppressed, variant_group, retrieved_at)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s::jsonb,%s,%s,%s,%s,%s)""",
                (cluster_id, r.provider, r.query_text, r.geography, r.language, r.window_start, r.window_end,
                 json.dumps(r.monthly_breakdown) if r.monthly_breakdown is not None else None,
                 r.volume_low, r.volume_high, r.is_suppressed, r.variant_group, r.retrieved_at),
            )
            n += 1
    conn.commit()
    return n


def demand_summary(conn: psycopg.Connection, cluster_id: UUID) -> dict:
    """Aggregate demand without double counting: one representative per variant group (max high),
    ungrouped rows counted individually. Suppressed/unknown rows are reported, not summed."""
    with conn.cursor() as cur:
        cur.execute("SELECT query_text, volume_low, volume_high, is_suppressed, variant_group FROM demand_observations WHERE cluster_id=%s", (cluster_id,))
        rows = cur.fetchall()
    groups: dict[str, dict] = {}
    unknown = 0
    for r in rows:
        if r["is_suppressed"] or r["volume_high"] is None:
            unknown += 1
            continue
        key = r["variant_group"] or f"__solo__{r['query_text']}"
        g = groups.get(key)
        if g is None or r["volume_high"] > g["volume_high"]:
            groups[key] = dict(r)
    low = sum((g["volume_low"] or 0) for g in groups.values())
    high = sum(g["volume_high"] for g in groups.values())
    return {"groups": len(groups), "volume_low": low if groups else None, "volume_high": high if groups else None,
            "unknown_or_suppressed": unknown, "observations": len(rows)}


class SerpProviderAdapter:
    provider_name = "serp"

    def __init__(self, api_key: str | None = None):
        self._key = api_key

    def capability(self) -> Capability:
        if self._key:
            return Capability(self.provider_name, "connected", "authorized SERP provider key present", priced=True)
        return Capability(self.provider_name, "unconnected", "no authorized SERP provider; import manual observations only", priced=True, features=("import_export",))

    def fetch(self, *_a, **_k):
        raise NotConnected(self.provider_name)


def store_serp_observation(conn: psycopg.Connection, cluster_id: UUID, *, query_text: str, locale: str, device: str,
                           results: list[dict], direct_answer_quality: str | None, missing_contribution: str | None,
                           provider: str, observed_at: datetime | None = None) -> UUID:
    if len(results) > 10:
        results = results[:10]
    with conn.cursor() as cur:
        cur.execute(
            """INSERT INTO serp_observations (cluster_id, query_text, observed_at, locale, device, results,
               direct_answer_quality, missing_contribution, provider) VALUES (%s,%s,%s,%s,%s,%s::jsonb,%s,%s,%s) RETURNING id""",
            (cluster_id, query_text, observed_at or datetime.now(timezone.utc), locale, device, json.dumps(results),
             direct_answer_quality, missing_contribution, provider),
        )
        sid = cur.fetchone()["id"]
    conn.commit()
    return sid
