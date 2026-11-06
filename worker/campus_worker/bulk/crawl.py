"""D1: crawl the official sites through their sitemaps with the existing safe fetcher.

Every page request goes through SafeFetcher (robots.txt, source_permissions: fetch_permitted hosts only with their per-host rate,
redirect/size guards), so the crawl can never fetch past robots rules or terms. Concurrency is across hosts (one worker per host,
up to `concurrency`), which keeps each host's rate limit exact. Page text is stored by content hash in fetch_snapshots with the URL
and fetch date (collectors.html.collect_html_source); a crawl_runs row records the counts.
"""
from __future__ import annotations

import gzip
import re
import time
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit
from uuid import UUID

import psycopg
import yaml

from ..collectors.html import collect_html_source, register_source
from ..config import REPO_ROOT
from ..fetcher import FetchRefused, SafeFetcher
from ..permissions import check_url

SKIP_EXT = (".pdf", ".jpg", ".jpeg", ".png", ".gif", ".svg", ".zip", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".mp4", ".mp3", ".ics", ".css", ".js", ".webp",
            ".ico", ".json", ".txt", ".rss", ".atom", ".gz")
MAX_SITEMAP_DEPTH = 3
MAX_SITEMAP_ENTRIES = 50_000


def load_config(slug: str) -> dict:
    p = REPO_ROOT / "data" / "schools" / f"{slug}.yaml"
    if not p.exists():
        raise FileNotFoundError(f"no bulk config for {slug}: {p}")
    return yaml.safe_load(p.read_text())


def normalize_url(url: str) -> str:
    """https, lower-case host, no query or fragment (sitemaps sometimes list http:// locs; the fetcher follows the redirect)."""
    parts = urlsplit(url.strip())
    path = re.sub(r"/{2,}", "/", parts.path or "/")
    return urlunsplit(("https", (parts.netloc or "").lower(), path, "", ""))


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1].lower()


def parse_sitemap(body: bytes) -> tuple[list[str], list[tuple[str, str | None]]]:
    """(child sitemap urls, page (loc, lastmod)) from a sitemap or sitemap index document."""
    if body[:2] == b"\x1f\x8b":
        body = gzip.decompress(body)
    try:
        root = ET.fromstring(body)
    except ET.ParseError:
        return [], []
    kind = _local(root.tag)
    children, pages = [], []
    for el in root:
        loc = lastmod = None
        for sub in el:
            if _local(sub.tag) == "loc":
                loc = (sub.text or "").strip()
            elif _local(sub.tag) == "lastmod":
                lastmod = (sub.text or "").strip()
        if not loc:
            continue
        if kind == "sitemapindex" or _local(el.tag) == "sitemap":
            children.append(loc)
        else:
            pages.append((loc, lastmod))
    return children, pages


def discover_sitemaps(fetcher: SafeFetcher, host: str) -> list[str]:
    """Sitemap URLs from robots.txt (Sitemap: lines), else the usual locations."""
    text = fetcher._robots_text("https", host) or ""
    found = [m.strip() for m in re.findall(r"(?im)^\s*sitemap:\s*(\S+)", text)]
    return found or [f"https://{host}/sitemap.xml", f"https://{host}/sitemap_index.xml"]


def crawl_delay(fetcher: SafeFetcher, host: str) -> float | None:
    text = fetcher._robots_text("https", host) or ""
    m = re.search(r"(?im)^\s*crawl-delay:\s*(\d+(?:\.\d+)?)", text)
    return float(m.group(1)) if m else None


def sitemap_pages(fetcher: SafeFetcher, host: str, *, log=print) -> list[tuple[str, str | None]]:
    seen, out, queue = set(), [], [(u, 0) for u in discover_sitemaps(fetcher, host)]
    while queue and len(out) < MAX_SITEMAP_ENTRIES:
        url, depth = queue.pop(0)
        if url in seen or depth > MAX_SITEMAP_DEPTH:
            continue
        seen.add(url)
        try:
            res = fetcher.fetch(url, expected_types=("application/xml", "text/xml", "application/gzip", "application/x-gzip", "application/octet-stream", "text/html", "text/plain"), use_conditional=False)
        except FetchRefused as e:
            log(f"  sitemap {url}: refused ({e.reason})")
            continue
        if res.status != 200 or not res.body:
            continue
        children, pages = parse_sitemap(res.body)
        queue.extend((c, depth + 1) for c in children)
        out.extend(pages)
    return out


def link_crawl_pages(fetcher: SafeFetcher, host: str, *, max_pages: int, depth: int = 2, log=print) -> list[tuple[str, str | None]]:
    """Hosts without a sitemap: a shallow breadth-first walk of internal links from the home page (every request robots-checked)."""
    from ..collectors.html import extract_material

    start = f"https://{host}/"
    seen, queue, out = {start}, [(start, 0)], []
    while queue and len(out) < max_pages:
        url, d = queue.pop(0)
        try:
            res = fetcher.fetch(url, expected_types=("text/html", "application/xhtml+xml"), use_conditional=False)
        except FetchRefused:
            continue
        if res.status != 200 or not res.body:
            continue
        out.append((url, None))
        if d >= depth:
            continue
        ex = extract_material(res.body)
        for link in ex.links or []:
            href = link.get("href") if isinstance(link, dict) else str(link)
            if not href:
                continue
            u = normalize_url(href if "://" in href else f"https://{host}{href if href.startswith('/') else '/' + href}")
            parts = urlsplit(u)
            if parts.netloc not in (host, "www." + host, host[4:] if host.startswith("www.") else host) or any(parts.path.lower().endswith(e) for e in SKIP_EXT):
                continue
            if u not in seen:
                seen.add(u)
                queue.append((u, d + 1))
    return out


def filter_urls(pages: list[tuple[str, str | None]], *, host: str, prefixes: list[str] | None, max_pages: int) -> list[str]:
    hosts = {host, host[4:] if host.startswith("www.") else "www." + host}
    out, seen = [], set()
    for loc, _lastmod in pages:
        u = normalize_url(loc)
        parts = urlsplit(u)
        if parts.netloc not in hosts:
            continue
        if any(parts.path.lower().endswith(ext) for ext in SKIP_EXT):
            continue
        if prefixes and not any(parts.path.startswith(p) for p in prefixes):
            continue
        if u in seen:
            continue
        seen.add(u)
        out.append(u)
        if len(out) >= max_pages:
            break
    return out


def crawl_host(dsn: str, *, host: str, sections: list[dict], dry_run: bool, log=print) -> dict:
    """One worker per host: every section that names this host, in order, fetched at the host's permitted rate (one fetcher, one rate
    limiter per host, so parallel sections can never multiply the rate); each page is recorded as a source + snapshot."""
    from ..db import connect

    stats = {"host": host, "sections": [s["section"]["key"] for s in sections], "sitemap_urls": 0, "selected": 0, "fetched": 0, "unchanged": 0, "failed": 0, "not_permitted": 0, "seconds": 0.0}
    t0 = time.monotonic()
    conn = connect(dsn)
    try:
        fetcher = SafeFetcher(conn)
        d = check_url(conn, f"https://{host}/")
        if not d.allowed or d.access_mode != "fetch_permitted":
            stats["not_permitted"] = 1
            stats["reason"] = f"{d.reason}: {d.access_mode}"
            return stats
        pages = sitemap_pages(fetcher, host, log=log)
        stats["sitemap_urls"] = len(pages)
        if not pages and not dry_run:
            pages = link_crawl_pages(fetcher, host, max_pages=max(j["max_pages"] for j in sections), log=log)
            stats["link_crawl_urls"] = len(pages)
        delay = crawl_delay(fetcher, host)
        seen: set[str] = set()
        for job in sections:
            section = job["section"]
            urls = [u for u in filter_urls(pages, host=host, prefixes=section.get("prefixes"), max_pages=job["max_pages"] + len(seen)) if u not in seen][:job["max_pages"]]
            seen.update(urls)
            stats["selected"] += len(urls)
            if dry_run:
                stats.setdefault("sample", {})[section["key"]] = {"selected": len(urls), "first": urls[:3]}
                continue
            for i, url in enumerate(urls):
                try:
                    sid = register_source(conn, canonical_url=url, institution_id=job["institution_id"], campus_id=None, source_kind="official_html",
                                          publisher=section.get("publisher") or host, source_family=f"crawl:{section['key']}", place_id=job["place_id"])
                    with conn.cursor() as cur:
                        cur.execute("UPDATE source_registry SET crawl_section=%s WHERE id=%s", (section["key"], sid))
                    conn.commit()
                    res = collect_html_source(conn, fetcher, sid)
                    conn.commit()
                    out = res.get("outcome")
                    if out == "ok":
                        stats["fetched"] += 1
                    elif out == "unchanged":
                        stats["unchanged"] += 1
                    else:
                        stats["failed"] += 1
                    if delay and delay > 60 / max(1, d.rate_limit_per_minute):
                        time.sleep(delay)
                except Exception as e:  # noqa: BLE001 — one bad page never stops the host
                    conn.rollback()
                    stats["failed"] += 1
                    stats.setdefault("errors", []).append(f"{url}: {type(e).__name__}: {str(e)[:120]}")
                if (i + 1) % 25 == 0:
                    log(f"  {host} [{section['key']}]: {i + 1}/{len(urls)} ({stats['fetched']} fetched, {stats['unchanged']} unchanged, {stats['failed']} failed)")
    finally:
        stats["seconds"] = round(time.monotonic() - t0, 1)
        conn.close()
    return stats


def run_crawl(conn: psycopg.Connection, *, dsn: str, slug: str, concurrency: int = 20, max_pages_per_host: int | None = None, hosts: list[str] | None = None,
              sections: list[str] | None = None, dry_run: bool = False, run_id: str = "bulk", log=print) -> dict:
    cfg = load_config(slug)
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM institutions WHERE slug=%s", (cfg["school"],))
        inst = cur.fetchone()
        if not inst:
            raise LookupError(f"institution {cfg['school']} not in the registry")
        inst_id = inst["id"]
        cur.execute("SELECT id, slug FROM places")
        places = {r["slug"]: r["id"] for r in cur.fetchall()}
        cur.execute("INSERT INTO crawl_runs (institution_id, place_id, run_id) VALUES (%s, %s, %s) RETURNING id", (inst_id, places.get(cfg.get("place")), run_id))
        crawl_id = cur.fetchone()["id"]
    conn.commit()
    by_host: dict[str, list[dict]] = {}
    canon = lambda h: h[4:] if h.startswith("www.") else h  # x and www.x are one site: crawl it once
    for sec in cfg["sections"]:
        if sections and sec["key"] not in sections:
            continue
        for host in sec["hosts"]:
            if hosts and host not in hosts:
                continue
            if any(canon(h) == canon(host) and h != host for h in by_host):
                continue
            place = places.get(sec["place"]) if sec.get("place") else None
            by_host.setdefault(host, []).append(dict(section=sec, institution_id=None if place else inst_id, place_id=place,
                                                     max_pages=max_pages_per_host or sec.get("max_pages") or cfg.get("max_pages_per_host", 400)))
    t0 = time.monotonic()
    results = []
    with ThreadPoolExecutor(max_workers=max(1, min(concurrency, len(by_host) or 1))) as ex:
        futs = {ex.submit(crawl_host, dsn, host=h, sections=js, dry_run=dry_run, log=log): h for h, js in by_host.items()}
        for f in as_completed(futs):
            h = futs[f]
            try:
                st = f.result()
            except Exception as e:  # noqa: BLE001
                st = {"host": h, "sections": [j["section"]["key"] for j in by_host[h]], "error": f"{type(e).__name__}: {e}", "fetched": 0, "unchanged": 0, "failed": 0, "selected": 0}
            results.append(st)
            log(f"{st['host']} {st.get('sections')}: selected {st.get('selected', 0)}, fetched {st.get('fetched', 0)}, unchanged {st.get('unchanged', 0)}, failed {st.get('failed', 0)}" + (f", {st['reason']}" if st.get("reason") else "") + (f", error {st['error']}" if st.get("error") else ""))
    summary = {"crawl_id": str(crawl_id), "dry_run": dry_run, "hosts": results, "observe_only": cfg.get("observe_only", []),
               "pages_fetched": sum(r.get("fetched", 0) for r in results), "pages_unchanged": sum(r.get("unchanged", 0) for r in results),
               "pages_failed": sum(r.get("failed", 0) for r in results), "pages_selected": sum(r.get("selected", 0) for r in results),
               "minutes": round((time.monotonic() - t0) / 60, 1)}
    with conn.cursor() as cur:
        cur.execute("UPDATE crawl_runs SET finished_at=now(), stats=%s::jsonb WHERE id=%s", (__import__("json").dumps(summary, default=str), crawl_id))
    conn.commit()
    return summary


def crawled_page_count(conn: psycopg.Connection, *, institution_id: UUID | None = None) -> int:
    with conn.cursor() as cur:
        cur.execute("""SELECT count(DISTINCT s.source_id) AS n FROM fetch_snapshots s JOIN source_registry r ON r.id=s.source_id
                       WHERE s.outcome='ok' AND s.retained_text IS NOT NULL AND r.source_kind LIKE 'official%%' AND (%s::uuid IS NULL OR r.institution_id=%s OR r.place_id IS NOT NULL)""",
                    (institution_id, institution_id))
        return int(cur.fetchone()["n"])
