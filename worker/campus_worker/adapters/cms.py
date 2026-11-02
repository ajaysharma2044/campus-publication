"""CMS adapter: WordPress REST API with idempotent upsert by stable external id + content hash
(SPEC §25, Stage E). Unconnected unless CAMPUS_WP_BASE_URL, CAMPUS_WP_USER and
CAMPUS_WP_APP_PASSWORD are set. An InMemoryCMS provides the same contract for tests; it is a
fixture, not a connected service.

The Campus Core plugin exposes `POST /wp-json/campus/v1/upsert` which takes
{external_id, content_hash, post_type, title, slug, path, content_html, meta} and returns
{id, created, changed}. If the hash matches the stored one, nothing is written (changed=false).
"""
from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass, field

from .base import Capability, NotConnected, ProviderError


@dataclass
class PublishRequest:
    external_id: str           # pages.id (stable)
    post_type: str             # campus_guide | campus_profile | campus_comparison | campus_tool | campus_school | campus_topic
    title: str
    slug: str
    path: str
    content_html: str
    status: str = "draft"      # draft | publish
    meta: dict = field(default_factory=dict)

    @property
    def content_hash(self) -> str:
        payload = json.dumps({"t": self.title, "s": self.slug, "p": self.path, "c": self.content_html,
                              "m": self.meta, "st": self.status}, sort_keys=True)
        return hashlib.sha256(payload.encode()).hexdigest()


@dataclass
class PublishResult:
    cms_id: str
    created: bool
    changed: bool
    content_hash: str
    url: str | None = None


class InMemoryCMS:
    """Fixture CMS honoring the upsert contract. Not a live service."""

    def __init__(self):
        self.posts: dict[str, dict] = {}
        self.writes = 0

    def capability(self) -> Capability:
        return Capability("cms_fixture", "fixture", "in-memory CMS for tests")

    def upsert(self, req: PublishRequest) -> PublishResult:
        h = req.content_hash
        existing = self.posts.get(req.external_id)
        if existing and existing["content_hash"] == h:
            return PublishResult(existing["id"], False, False, h, existing["path"])
        self.writes += 1
        if existing:
            existing.update(title=req.title, slug=req.slug, path=req.path, content_html=req.content_html,
                            content_hash=h, status=req.status, meta=req.meta, revision=existing["revision"] + 1)
            return PublishResult(existing["id"], False, True, h, req.path)
        pid = str(len(self.posts) + 1)
        self.posts[req.external_id] = {"id": pid, "title": req.title, "slug": req.slug, "path": req.path,
                                       "content_html": req.content_html, "content_hash": h, "status": req.status,
                                       "meta": req.meta, "revision": 1, "post_type": req.post_type}
        return PublishResult(pid, True, True, h, req.path)

    def add_redirect(self, from_path: str, to_path: str) -> None:
        self.posts.setdefault("__redirects__", {"id": "r", "content_hash": "", "path": "", "revision": 0, "map": {}})
        self.posts["__redirects__"]["map"][from_path] = to_path


class WordPressAdapter:
    provider_name = "wordpress"

    def __init__(self, base_url: str | None, user: str | None, app_password: str | None, *, timeout: float = 20.0):
        self.base_url = (base_url or "").rstrip("/") or None
        self.user = user
        self._pw = app_password
        self.timeout = timeout

    @classmethod
    def from_settings(cls, settings) -> "WordPressAdapter":
        return cls(settings.wp_base_url, settings.wp_user, os.environ.get("CAMPUS_WP_APP_PASSWORD"))

    def capability(self) -> Capability:
        if self.base_url and self.user and self._pw:
            return Capability(self.provider_name, "connected", f"REST credentials configured for {self.base_url} (untested until first upsert)", features=("upsert", "redirect"))
        return Capability(self.provider_name, "unconnected", "CAMPUS_WP_BASE_URL / CAMPUS_WP_USER / CAMPUS_WP_APP_PASSWORD not set")

    def _client(self):
        import httpx

        return httpx.Client(base_url=self.base_url, auth=(self.user, self._pw), timeout=self.timeout,
                            headers={"User-Agent": "campus-worker/0.1"})

    def upsert(self, req: PublishRequest) -> PublishResult:
        if not self.capability().connected:
            raise NotConnected(self.provider_name)
        body = {"external_id": req.external_id, "content_hash": req.content_hash, "post_type": req.post_type,
                "title": req.title, "slug": req.slug, "path": req.path, "content_html": req.content_html,
                "status": req.status, "meta": req.meta}
        with self._client() as c:
            r = c.post("/wp-json/campus/v1/upsert", json=body)
        if r.status_code in (401, 403):
            raise ProviderError(f"WordPress auth failed: {r.status_code}", retryable=False, kind="auth")
        if r.status_code == 429 or r.status_code >= 500:
            ra = r.headers.get("Retry-After")
            raise ProviderError(f"WordPress unavailable: {r.status_code}", retryable=True, kind="rate_limit" if r.status_code == 429 else "outage",
                                retry_after_seconds=int(ra) if ra and ra.isdigit() else None)
        if r.status_code >= 400:
            raise ProviderError(f"WordPress rejected upsert: {r.status_code} {r.text[:200]}", retryable=False, kind="invalid_input")
        data = r.json()
        return PublishResult(str(data["id"]), bool(data.get("created")), bool(data.get("changed")), req.content_hash, data.get("url"))

    def add_redirect(self, from_path: str, to_path: str) -> None:
        if not self.capability().connected:
            raise NotConnected(self.provider_name)
        with self._client() as c:
            r = c.post("/wp-json/campus/v1/redirect", json={"from": from_path, "to": to_path})
        if r.status_code >= 400:
            raise ProviderError(f"redirect failed: {r.status_code}", retryable=r.status_code >= 500, kind="error")
