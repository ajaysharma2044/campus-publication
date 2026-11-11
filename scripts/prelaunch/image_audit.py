"""Phase 6 of docs/v5/prelaunch-spec.md, step 1: every lead image with its date, so pages whose photo is more than 20 years old are
flagged by code; whether a photo shows the page's subject and whether its caption is true is judged page by page afterwards.

    worker/.venv/bin/python scripts/prelaunch/image_audit.py [--out reports/06-images-candidates.json]

Reads images[0] of every page under content/articles, content/tools and content/datasets, looks the file up on Wikimedia Commons
(extmetadata DateTimeOriginal, else the upload date) through the public API, and writes the candidates file the relevance review
reads. Read-only. Photos not from Commons (Openverse, owner, permission) get their date from content/images/credits.yml when present.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path
from urllib.parse import unquote, urlparse

import httpx
import yaml

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts" / "v2"))
from lib import queue as q  # noqa: E402

API = "https://commons.wikimedia.org/w/api.php"
UA = "EduExplained image audit (https://eduexplained.netlify.app; editor contact via the site) httpx"
OLD_YEARS = 20


def commons_title(url: str) -> str | None:
    """File:... title from a Commons file page URL (credit_url / page_url)."""
    if not url or "wikimedia.org" not in url:
        return None
    path = unquote(urlparse(url).path)
    m = re.search(r"/(File:.+)$", path)
    return m.group(1).replace("_", " ") if m else None


def fetch_dates(titles: list[str]) -> dict[str, dict]:
    out: dict[str, dict] = {}
    with httpx.Client(headers={"User-Agent": UA}, timeout=30) as c:
        for i in range(0, len(titles), 40):
            chunk = titles[i: i + 40]
            r = c.get(API, params={"action": "query", "titles": "|".join(chunk), "prop": "imageinfo", "iiprop": "extmetadata|timestamp|user",
                                   "iiextmetadatafilter": "DateTimeOriginal|DateTime|ObjectName|ImageDescription", "format": "json", "redirects": 1})
            r.raise_for_status()
            for page in r.json().get("query", {}).get("pages", {}).values():
                ii = (page.get("imageinfo") or [{}])[0]
                ext = ii.get("extmetadata") or {}
                taken = (ext.get("DateTimeOriginal") or {}).get("value", "")
                uploaded = ii.get("timestamp", "")
                desc = re.sub(r"<[^>]+>", " ", (ext.get("ImageDescription") or {}).get("value", "")).strip()
                out[page.get("title", "")] = {"taken": taken, "uploaded": uploaded, "description": " ".join(desc.split())[:300], "missing": "missing" in page}
            time.sleep(0.3)
    return out


def year_of(s: str) -> int | None:
    m = re.search(r"(1[89]\d\d|20\d\d)", s or "")
    return int(m.group(1)) if m else None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(REPO / "reports" / "06-images-candidates.json"))
    a = ap.parse_args()
    ledger = {}
    led = REPO / "content" / "images" / "credits.yml"
    if led.exists():
        for e in yaml.safe_load(led.read_text(encoding="utf-8")) or []:
            if isinstance(e, dict):
                ledger[(e.get("article_slug"), e.get("file"))] = e
    pages = []
    for kind, pattern in (("article", "articles/*/*.md"), ("tool", "tools/*/tool.md"), ("dataset", "datasets/*.md")):
        for p in sorted((REPO / "content").glob(pattern)):
            fm = q.frontmatter(p)
            imgs = fm.get("images") if isinstance(fm.get("images"), list) else []
            lead = imgs[0] if imgs and isinstance(imgs[0], dict) else None
            slug = p.parent.name if kind == "tool" else p.stem
            section = p.parent.name if kind == "article" else kind + "s"
            url = f"/cornell/{section}/{slug}/" if kind == "article" else f"/{kind}s/{slug}/"
            entry = {"page": str(p.relative_to(REPO)), "url": url, "title": str(fm.get("title") or ""), "subject": str(fm.get("subject") or ""),
                     "lead": bool(lead)}
            if lead:
                led_entry = ledger.get((slug, lead.get("file")), {})
                entry.update({"file": f"content/images/{slug}/{lead.get('file')}", "alt": lead.get("alt", ""), "caption": lead.get("caption", ""),
                              "credit": lead.get("credit", ""), "credit_url": lead.get("credit_url", "") or led_entry.get("page_url", ""),
                              "license": lead.get("license", ""), "source": led_entry.get("source", ""), "commons_title": commons_title(lead.get("credit_url", "") or led_entry.get("page_url", ""))})
            pages.append(entry)
    titles = sorted({e["commons_title"] for e in pages if e.get("commons_title")})
    print(f"{len(pages)} pages, {sum(1 for e in pages if e['lead'])} with a lead image, {len(titles)} distinct Commons files to look up")
    dates = fetch_dates(titles) if titles else {}
    this_year = time.gmtime().tm_year
    old = 0
    for e in pages:
        d = dates.get(e.get("commons_title") or "", {})
        e["taken"] = d.get("taken", ""); e["uploaded"] = d.get("uploaded", ""); e["commons_description"] = d.get("description", "")
        y = year_of(e["taken"]) or year_of(e["uploaded"])
        e["year"] = y
        e["older_than_20y"] = bool(y and this_year - y > OLD_YEARS)
        e["date_unknown"] = bool(e["lead"] and not y)
        old += e["older_than_20y"]
    out = Path(a.out); out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(pages, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"{old} lead image(s) older than {OLD_YEARS} years; {sum(1 for e in pages if e.get('date_unknown'))} with no date; written {out.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
