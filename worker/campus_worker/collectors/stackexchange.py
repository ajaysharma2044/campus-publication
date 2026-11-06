"""Stack Exchange API collector (continuous-local-run R46). Official API, CC BY-SA content with attribution.

Only question titles, links and dates are retained; they become discovery questions (origin 'stackexchange') with the
attribution recorded on every row. Works unauthenticated at the public quota; STACKEXCHANGE_KEY in .env raises it.
"""
from __future__ import annotations

import os
from datetime import datetime, timezone
from uuid import UUID

import psycopg

from ..discovery import QuestionInput

BASE = "https://api.stackexchange.com/2.3"
ATTRIBUTION = "CC BY-SA 4.0 (Stack Exchange)"


class StackExchangeClient:
    def __init__(self, fetch_json=None, key: str | None = None):
        self._fetch = fetch_json or self._default_fetch
        self.key = key or os.environ.get("STACKEXCHANGE_KEY")

    @staticmethod
    def _default_fetch(url: str) -> dict:
        import httpx

        with httpx.Client(timeout=30.0, headers={"User-Agent": "CampusPublicationBot/0.1 (+editorial research)"}) as c:
            r = c.get(url)
            r.raise_for_status()
            return r.json()

    def search(self, site: str, q: str, *, pagesize: int = 50) -> dict:
        from urllib.parse import urlencode

        params = {"site": site, "q": q, "order": "desc", "sort": "relevance", "pagesize": pagesize, "filter": "default"}
        if self.key:
            params["key"] = self.key
        return self._fetch(f"{BASE}/search/advanced?{urlencode(params)}")


def parse_items(payload: dict, *, site: str, institution_id: UUID | None = None, topic_key: str | None = None) -> list[QuestionInput]:
    out = []
    for it in (payload or {}).get("items") or []:
        title = (it.get("title") or "").strip()
        link = it.get("link") or ""
        if not title or not link:
            continue
        created = it.get("creation_date")
        observed = datetime.fromtimestamp(int(created), tz=timezone.utc) if created else None
        # owner / display_name are never retained (identity)
        out.append(QuestionInput(raw_text=_unescape(title)[:300], origin="stackexchange", institution_id=institution_id, topic_key=topic_key,
                                 observed_at=observed, source_ref=f"stackexchange:{site}:{it.get('question_id')}:{link}",
                                 constraints=[f"attribution:{ATTRIBUTION}", f"site:{site}"]))
    return out


def _unescape(s: str) -> str:
    import html

    return html.unescape(s)


def collect(conn: psycopg.Connection, client: StackExchangeClient, *, site: str, query: str, institution_id: UUID | None = None, topic_key: str | None = None) -> dict:
    from .. import discovery

    items = parse_items(client.search(site, query), site=site, institution_id=institution_id, topic_key=topic_key)
    res = discovery.ingest(conn, items)
    res["parsed"] = len(items)
    res["attribution"] = ATTRIBUTION
    return res
