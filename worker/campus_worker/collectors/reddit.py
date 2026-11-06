"""Reddit collector — api_authorized mode only (SPEC §09; continuous-local-run R36; AT35).

Stays OFF until the owner holds Reddit Data API authorization and REDDIT_CLIENT_ID / REDDIT_CLIENT_SECRET are in
.env AND the `*.reddit.com` permission row says api_authorized. Until then `capability()` is unconnected and
`collect()` refuses network access; parsing is fully exercised on fixture listings.

Rules enforced here:
- question extraction only: titles (and self-text questions) become QuestionInput rows; never comments-as-content
- no identity profiling: authors, user ids, flair and avatars are never read or stored
- minimal retention: post id, permalink, created time, title; `forget()` deletes everything for a post id
- attributed synthesis happens elsewhere and only with sample, period and limits (SPEC §09); nothing here quotes
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID

import psycopg

from ..adapters.base import Capability
from ..discovery import QuestionInput
from ..permissions import access_mode_for

QUESTION_START = re.compile(r"^(is|are|do|does|did|can|could|should|would|will|how|what|which|where|when|why|who|anyone|any)\b", re.I)
FORBIDDEN_FIELDS = ("author", "author_fullname", "author_flair_text", "author_flair_css_class", "author_premium", "author_patreon_flair")


def looks_like_question(title: str) -> bool:
    t = (title or "").strip()
    return bool(t) and ("?" in t or bool(QUESTION_START.match(t)))


@dataclass
class RedditCollector:
    client_id: str | None = None
    client_secret: str | None = None
    user_agent: str = "campus-publication/0.1 (editorial research; questions only)"
    transport=None  # httpx transport for tests; the real one is created only when connected

    @classmethod
    def from_env(cls) -> "RedditCollector":
        return cls(os.environ.get("REDDIT_CLIENT_ID"), os.environ.get("REDDIT_CLIENT_SECRET"))

    def capability(self, conn: psycopg.Connection | None = None) -> Capability:
        mode = access_mode_for(conn, "https://www.reddit.com/") if conn is not None else "unknown"
        if self.client_id and self.client_secret and mode == "api_authorized":
            return Capability("reddit", "connected", "Reddit Data API credentials present and permission row is api_authorized", features=("questions",))
        if mode in ("search_observation", "unknown"):
            return Capability("reddit", "unconnected", f"permission mode is {mode}: search-result observation only; no content collection (R36)")
        return Capability("reddit", "unconnected", "no Reddit Data API credentials in .env (owner step, R36)")

    # -- parsing (no network) --------------------------------------------------------------------
    @staticmethod
    def parse_listing(listing: dict, *, subreddit: str, institution_id: UUID | None = None, place_id: UUID | None = None,
                      topic_key: str | None = None, questions_only: bool = True) -> list[QuestionInput]:
        children = ((listing or {}).get("data") or {}).get("children") or []
        out: list[QuestionInput] = []
        for ch in children:
            d = ch.get("data") or {}
            title = (d.get("title") or "").strip()
            if not title:
                continue
            if questions_only and not looks_like_question(title):
                continue
            created = d.get("created_utc")
            observed = datetime.fromtimestamp(float(created), tz=timezone.utc) if created else None
            permalink = d.get("permalink") or f"/r/{subreddit}/comments/{d.get('id', '')}/"
            # minimal retention: id + permalink + time + title. Never author fields.
            out.append(QuestionInput(raw_text=title[:300], origin="reddit_api", institution_id=institution_id, topic_key=topic_key,
                                     observed_at=observed, source_ref=f"reddit:{d.get('id', '')}:{permalink}", constraints=[f"subreddit:{subreddit}"]))
        return out

    @staticmethod
    def scrub(d: dict) -> dict:
        """Defensive: drop any identity fields before a listing is retained anywhere (tests assert this)."""
        return {k: v for k, v in d.items() if k not in FORBIDDEN_FIELDS and not k.startswith("author")}

    # -- collection -------------------------------------------------------------------------------
    def collect(self, conn: psycopg.Connection, subreddit: str, *, listing: dict | None = None, institution_id: UUID | None = None,
                place_id: UUID | None = None, topic_key: str | None = None, limit: int = 100) -> dict:
        from .. import discovery

        if listing is None:
            cap = self.capability(conn)
            if not cap.connected:
                raise PermissionError(f"reddit collector is not connected: {cap.reason}")
            listing = self._fetch_listing(subreddit, limit=limit)
        items = self.parse_listing(listing, subreddit=subreddit, institution_id=institution_id, place_id=place_id, topic_key=topic_key)
        res = discovery.ingest(conn, items)
        res["parsed"] = len(items)
        return res

    def _fetch_listing(self, subreddit: str, *, limit: int) -> dict:
        import httpx

        auth = httpx.BasicAuth(self.client_id or "", self.client_secret or "")
        with httpx.Client(transport=self.transport, timeout=20.0, headers={"User-Agent": self.user_agent}) as client:
            tok = client.post("https://www.reddit.com/api/v1/access_token", auth=auth, data={"grant_type": "client_credentials"})
            tok.raise_for_status()
            token = tok.json()["access_token"]
            r = client.get(f"https://oauth.reddit.com/r/{subreddit}/new", params={"limit": min(limit, 100)}, headers={"Authorization": f"bearer {token}"})
            r.raise_for_status()
            return r.json()

    @staticmethod
    def forget(conn: psycopg.Connection, post_id: str) -> int:
        """Deletion compliance: remove every retained row for a post id."""
        with conn.cursor() as cur:
            cur.execute("DELETE FROM questions WHERE origin='reddit_api' AND source_ref LIKE %s", (f"reddit:{post_id}:%",))
            n = cur.rowcount
        conn.commit()
        return n
