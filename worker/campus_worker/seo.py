"""Technical SEO controls (SPEC §20): URL policy, sitemap, robots, canonical rules, structured
data validation, internal-link integrity. Deterministic; no model involvement."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from urllib.parse import urlsplit
from uuid import UUID
from xml.sax.saxutils import escape

import psycopg

INDEXABLE_FORMATS = {"guide", "entity_profile", "comparison", "tool", "topic_hub", "school_hub", "policy", "home", "explainer"}
NOINDEX_QUERY_KEYS = {"sort", "filter", "compare", "q", "s", "page", "period", "occupants", "audience"}
PATH_RULES = [
    (re.compile(r"^/$"), "home"),
    (re.compile(r"^/schools/$"), "schools_index"),
    (re.compile(r"^/schools/[a-z0-9-]+/$"), "school_hub"),
    (re.compile(r"^/schools/[a-z0-9-]+/[a-z0-9-]+/$"), "topic_hub"),
    (re.compile(r"^/schools/[a-z0-9-]+/[a-z0-9-]+/[a-z0-9-]+/$"), "entity_profile_or_guide"),
    (re.compile(r"^/schools/[a-z0-9-]+/[a-z0-9-]+/compare/[a-z0-9-]+-vs-[a-z0-9-]+/$"), "comparison"),
    (re.compile(r"^/tools/[a-z0-9-]+/$"), "tool"),
    (re.compile(r"^/about/[a-z0-9-]+/$"), "policy"),
]


@dataclass
class UrlDecision:
    path: str
    indexable: bool
    canonical: str
    reason: str


def classify_url(url_or_path: str) -> UrlDecision:
    """Explicit URL strategy: only clean, trailing-slash paths matching the content model are
    indexable; any query string (filters, sorts, calculator state, search) canonicalises to the
    clean path and is noindex."""
    parts = urlsplit(url_or_path)
    path = parts.path or "/"
    if not path.endswith("/"):
        return UrlDecision(path, False, path + "/", "missing trailing slash → canonical adds it")
    if parts.query:
        keys = {kv.split("=")[0] for kv in parts.query.split("&") if kv}
        if keys & NOINDEX_QUERY_KEYS or keys:
            return UrlDecision(path, False, path, f"query parameters {sorted(keys)} → noindex, canonical to clean path")
    if re.search(r"[A-Z_ ]", path):
        return UrlDecision(path, False, path.lower().replace("_", "-").replace(" ", "-"), "uppercase/underscore/space → not canonical")
    for rx, kind in PATH_RULES:
        if rx.match(path):
            return UrlDecision(path, True, path, f"matches {kind}")
    return UrlDecision(path, False, path, "outside URL model → noindex")


def sitemap_xml(conn: psycopg.Connection, base_url: str) -> str:
    """Only published, indexable, non-redirected pages whose latest version passed gates."""
    with conn.cursor() as cur:
        cur.execute(
            """SELECT p.path, COALESCE(p.last_material_update_at, p.first_published_at) AS lastmod FROM pages p
               JOIN page_versions v ON v.id=p.current_version_id
               WHERE p.status='published' AND p.redirect_to_path IS NULL AND v.gate_status='passed' AND p.page_format = ANY(%s)
               ORDER BY p.path""", (sorted(INDEXABLE_FORMATS),))
        rows = cur.fetchall()
    out = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for r in rows:
        d = classify_url(r["path"])
        if not d.indexable:
            continue
        lm = f"<lastmod>{r['lastmod'].date().isoformat()}</lastmod>" if r["lastmod"] else ""
        out.append(f"<url><loc>{escape(base_url.rstrip('/') + r['path'])}</loc>{lm}</url>")
    out.append("</urlset>")
    return "\n".join(out)


def robots_txt(base_url: str, environment: str) -> str:
    if environment != "production":
        return "User-agent: *\nDisallow: /\n"  # staging never crawled; noindex headers also set by the plugin
    return f"User-agent: *\nAllow: /\nDisallow: /search/\nDisallow: /?s=\nDisallow: /wp-admin/\nSitemap: {base_url.rstrip('/')}/wp-sitemap.xml\n"


@dataclass
class SchemaCheck:
    ok: bool
    errors: list[str] = field(default_factory=list)


def validate_structured_data(ld: dict, *, visible_headline: str, visible_description: str | None, published: datetime, modified: datetime | None,
                             has_visible_reviews: bool = False) -> SchemaCheck:
    """Structured data must match visible content and real eligibility (SPEC §20)."""
    errs = []
    if ld.get("@type") not in ("Article", "NewsArticle", "WebPage", "Organization", "BreadcrumbList"):
        errs.append(f"unexpected @type {ld.get('@type')}")
    if ld.get("@type") in ("Article", "NewsArticle"):
        if ld.get("headline") != visible_headline:
            errs.append("headline does not match visible H1")
        if visible_description and ld.get("description") != visible_description:
            errs.append("description does not match visible deck")
        if ld.get("datePublished", "")[:10] != published.date().isoformat():
            errs.append("datePublished does not match the real publication date")
        if modified and ld.get("dateModified", "")[:10] != modified.date().isoformat():
            errs.append("dateModified does not match the real material-update date")
        author = ld.get("author") or {}
        if author.get("@type") == "Person":
            errs.append("author is a Person; no human reporter exists — use Organization/desk credit")
    for forbidden in ("aggregateRating", "review", "Review", "FAQPage", "HowTo"):
        if forbidden in json.dumps(ld) and not has_visible_reviews:
            errs.append(f"{forbidden} markup without corresponding visible, eligible content")
    return SchemaCheck(not errs, errs)


def check_internal_links(conn: psycopg.Connection, html_by_path: dict[str, str]) -> dict:
    """Broken-link and orphan detection over a set of rendered pages plus the pages table."""
    with conn.cursor() as cur:
        cur.execute("SELECT path, status, redirect_to_path FROM pages")
        known = {r["path"]: r for r in cur.fetchall()}
    known_paths = set(known) | set(html_by_path)
    inbound: dict[str, int] = {p: 0 for p in html_by_path}
    broken = []
    for src, html in html_by_path.items():
        for href in re.findall(r'href="([^"#?]+)', html):
            if href.startswith(("http://", "https://", "mailto:", "/static/", "/wp-", "/about/", "/search/", "/schools/", "/tools/", "/topics/")) and not href.startswith("/schools/") and not href.startswith("/tools/"):
                continue
            if href.startswith("/"):
                target = href if href.endswith("/") else href + "/"
                if target in known_paths:
                    inbound[target] = inbound.get(target, 0) + 1
                    r = known.get(target)
                    if r and r["status"] == "redirected":
                        broken.append({"from": src, "href": href, "problem": f"links to a redirected path; update to {r['redirect_to_path']}"})
                else:
                    broken.append({"from": src, "href": href, "problem": "target not in page registry"})
    orphans = [p for p, n in inbound.items() if n == 0 and p not in ("/", "/schools/")]
    return {"broken": broken, "orphans": orphans, "checked": len(html_by_path)}


def title_and_description(headline: str, deck: str | None, site_name: str, *, max_title: int = 65, max_desc: int = 155) -> tuple[str, str]:
    """Truthful <title> and description from the real headline/deck; no keyword stuffing, no year
    unless already in the headline."""
    title = headline if len(headline) <= max_title else headline[: max_title - 1].rsplit(" ", 1)[0] + "…"
    full = f"{title} — {site_name}" if len(title) + len(site_name) + 3 <= 70 else title
    desc = (deck or headline).strip()
    if len(desc) > max_desc:
        desc = desc[: max_desc - 1].rsplit(" ", 1)[0] + "…"
    return full, desc
