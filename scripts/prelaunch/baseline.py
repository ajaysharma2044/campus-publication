"""Phase 0 of docs/v5/prelaunch-spec.md: crawl the built site (site/dist) and write reports/00-baseline.md (+ .json).

    worker/.venv/bin/python scripts/prelaunch/baseline.py [--dist site/dist] [--out reports/00-baseline.md]

For every URL: section, word count of the article text (the sources list, related cards, sidebar, newsletter, feedback and tool
widgets excluded), cited source count (the page's sources list), distinct external hosts linked from the body, Updated date, author,
robots meta, tool embeds and internal links. Then: banned-phrase matches (the spec's Phase 1 patterns), tools that exist at more than
one URL, pages whose section does not match the Phase 3 mapping, pages per section, orphan pages (no internal in-link) and the
indexing state. Read-only: it changes nothing under content/ or site/.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import date, datetime
from pathlib import Path
from urllib.parse import urlparse

from bs4 import BeautifulSoup

REPO = Path(__file__).resolve().parents[2]
SITE_HOSTS = {"eduexplained.netlify.app", "footnote-daily.netlify.app", "www.eduexplained.com", "eduexplained.com"}

# Phase 1a of the spec, case-insensitive, plus the variants the first crawl showed (keep in sync with scripts/lint-content.py)
BANNED = [
    r"sources? (for|behind|in) this (guide|page|article)",
    r"the sources? .{0,40}(do not|does not|don't|contain no|include no)",
    r"no source (gives|lists|says|reports|provides)",
    r"(page|site|document) (lists|gives|shows|provides) no ",
    r"we (could not|couldn't) find",
    r"not (included|available) in (our|the) sources",
    r"as of (our|this) research",
]

# Phase 3b mapping: (target section, pattern on "slug title" lowercased). First match wins; every match is reported.
SECTION_RULES = [
    ("health-safety", r"fire[- ]safety|fire alarm|fire drill|smoke detector"),
    ("health-safety", r"health insurance|find(ing)? a doctor|cornell health|ship plan|student health"),
    ("health-safety", r"winter blues|seasonal affective|mental health|counseling|caps "),
    ("health-safety", r"collegetown safe|is .* safe|crime|dorm security|blue light"),
    ("daily-life", r"snow day|class(es)? cancel|campus clos"),
    ("daily-life", r"\bvot(e|ing)\b|polling|register to vote|election"),
    ("daily-life", r"\bid card\b|cornell id\b|cornell card|student id"),
    ("daily-life", r"\bmail\b|package|parcel"),
    ("daily-life", r"laundry|laundromat"),
    ("housing", r"air[- ]conditioning|\bac\b|a/c|air conditioned"),
    ("housing", r"heat out|no heat|frozen pipe|drafty|utilit|nyseg|setting up (power|gas|electric)"),
    ("housing", r"sidewalk snow|snow removal|shovel"),
    ("daily-life", r"internet|wifi|wi-fi|broadband|spectrum|ethernet"),
    ("daily-life", r"driver'?s? licen[sc]e|\bdmv\b|new york licen[sc]e|license plate"),
    ("daily-life", r"what to wear|winter clothing|winter activit|winter survival|winter guide|surviv(e|ing) (an )?ithaca winter|winter gear|winter boots"),
    ("daily-life", r"first[- ]month|first month|logistics checklist|first week|arrival checklist"),
]
# Reviewed by hand on the first crawl: pages a rule matches whose section is right as it stands (kept out of the mismatch count).
REVIEWED_KEEP = {
    "/cornell/housing/cornell-fall-housing-selection-juniors-seniors/": "on-campus housing selection; the ID-card rule matched the title",
    "/cornell/housing/cornell-general-room-selection-timeslots-strategy/": "on-campus room selection; the ID-card rule matched the title",
    "/cornell/housing/ithaca-apartments-in-unit-laundry/": "an apartment-search page; the laundry rule matched",
    "/cornell/money/ithaca-utilities-cost-winter-heating-bill-apartment-students/": "a cost page, money is right; the utilities rule matched",
}
TRANSPORT = r"park|garage|permit|bus|tcat|airport|flight|fly|bike|bicycle|cycling|scooter|uber|lyft|taxi|rideshare|carshare|car-?share|driving|drive|car\b|break travel|thanksgiving|winter break|c2c|ourbus|flixbus|greyhound|train|amtrak|commute|getting to|get to|ride|shuttle|move-in|move-out|moving|storage|shipping|road|snow tires|winter driving|storms? travel|traffic|walk|hills|route"


def text_of(node) -> str:
    return re.sub(r"\s+", " ", node.get_text(" ", strip=True)) if node else ""


def classify(url: str) -> tuple[str, str]:
    """(section, kind) for a URL: article sections are the topic dirs under /cornell/."""
    parts = [p for p in url.split("/") if p]
    if not parts:
        return "site", "home"
    if parts[0] == "cornell":
        if len(parts) == 1:
            return "site", "school-hub"
        if len(parts) == 2:
            return parts[1], "hub"
        return parts[1], "article"
    if parts[0] in ("tools", "datasets", "start"):
        return parts[0], "index" if len(parts) == 1 else {"tools": "tool", "datasets": "dataset", "start": "start"}[parts[0]]
    if parts[0] == "styleguide":
        return "styleguide", "sample"
    if parts[0] == "authors":
        return "site", "authors" if len(parts) == 1 else "author"
    return "site", "page"


def parse_updated(s: str) -> str:
    m = re.search(r"Updated\s+([A-Z][a-z]+ \d{1,2}, \d{4})", s)
    if not m:
        return ""
    try:
        return datetime.strptime(m.group(1), "%B %d, %Y").date().isoformat()
    except ValueError:
        return m.group(1)


def crawl(dist: Path) -> list[dict]:
    pages = []
    for html in sorted(dist.rglob("index.html")):
        rel = html.relative_to(dist).as_posix()
        url = "/" if rel == "index.html" else "/" + rel[: -len("index.html")]
        soup = BeautifulSoup(html.read_text(encoding="utf-8", errors="replace"), "lxml")
        section, kind = classify(url)
        main = soup.select_one("article.main") or soup.select_one("main") or soup
        title = text_of(soup.select_one("h1")) or text_of(soup.title)
        robots = (soup.find("meta", attrs={"name": "robots"}) or {}).get("content", "") if soup.find("meta", attrs={"name": "robots"}) else ""
        canonical = (soup.find("link", attrs={"rel": "canonical"}) or {}).get("href", "") if soup.find("link", attrs={"rel": "canonical"}) else ""
        byline = soup.select_one(".byline")
        updated = parse_updated(text_of(byline)) if byline else ""
        author_a = byline.select_one("a[rel=author]") if byline else None
        author = text_of(author_a) if author_a else ""
        sources_list = main.select_one("ol.sources__list")
        n_sources = len(sources_list.find_all("li", recursive=False)) if sources_list else 0
        # the article text: drop the chrome and the widgets, keep the prose, tables and figures
        body = BeautifulSoup(str(main), "lxml")
        for sel in ("section.sources", "section.related", "section.feedback", "section.newsletter", "section.most", "nav.toc",
                    "aside.sidebar", "section.tool-embed", "nav.crumbs", ".byline", "script", "style", "section.section[aria-labelledby=used-title]"):
            for n in body.select(sel):
                n.decompose()
        words = len(text_of(body).split())
        ext_hosts, internal = set(), set()
        for a in main.find_all("a", href=True):
            href = a["href"].strip()
            if href.startswith("/") and not href.startswith("//"):
                internal.add(href.split("#")[0].split("?")[0])
            elif href.startswith("http"):
                host = urlparse(href).netloc.lower().removeprefix("www.")
                if host and host not in SITE_HOSTS:
                    ext_hosts.add(host)
        tools = []
        for emb in main.select("section.tool-embed"):
            a = emb.select_one("a[href^='/tools/']")
            slug = a["href"].strip("/").split("/")[-1] if a else (emb.get("aria-labelledby") or "")
            tools.append(slug or text_of(emb)[:40])
        if kind == "tool":
            tools.append(url.strip("/").split("/")[-1])
        page_text = text_of(body)
        hits = []
        for pat in BANNED:
            for m in re.finditer(pat, page_text, re.I):
                s = max(0, m.start() - 70)
                hits.append({"pattern": pat, "snippet": page_text[s: m.end() + 70].strip()})
        all_internal = set()
        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            if href.startswith("/") and not href.startswith("//"):
                all_internal.add(href.split("#")[0].split("?")[0])
        pages.append({"url": url, "section": section, "kind": kind, "title": title, "words": words, "sources": n_sources,
                      "external_hosts": len(ext_hosts), "updated": updated, "author": author, "robots": robots, "canonical": canonical,
                      "tools": tools, "banned": hits, "links_body": sorted(internal), "links_all": sorted(all_internal)})
    return pages


def section_mismatches(pages: list[dict]) -> list[dict]:
    out = []
    for p in pages:
        if p["kind"] != "article":
            continue
        key = f"{p['url'].rstrip('/').split('/')[-1].replace('-', ' ')} {p['title']}".lower()
        matches = [(sec, pat) for sec, pat in SECTION_RULES if re.search(pat, key)]
        if not matches:
            continue
        target = matches[0][0]
        transport = bool(re.search(TRANSPORT, key))
        if target != p["section"] and p["url"] in REVIEWED_KEEP:
            p["reviewed_keep"] = REVIEWED_KEEP[p["url"]]
            continue
        if target != p["section"]:
            out.append({"url": p["url"], "title": p["title"], "section": p["section"], "suggested": target,
                        "rules": sorted({m[0] + ": " + m[1][:40] for m in matches}), "transport_terms": transport})
    return out


def tool_duplicates(pages: list[dict]) -> list[dict]:
    by_tool = defaultdict(list)
    for p in pages:
        for t in p["tools"]:
            by_tool[t].append(p)
    out = []
    for slug, ps in sorted(by_tool.items()):
        urls = [p for p in ps if p["kind"] == "tool"] + [p for p in ps if p["kind"] != "tool"]
        primary = [p for p in ps if p["kind"] != "tool" and (p["url"].rstrip("/").endswith("/" + slug) or p["words"] < 350)]
        out.append({"tool": slug, "urls": [{"url": p["url"], "kind": p["kind"], "words": p["words"]} for p in urls],
                    "duplicate_pages": [p["url"] for p in primary]})
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dist", default=str(REPO / "site" / "dist"))
    ap.add_argument("--out", default=str(REPO / "reports" / "00-baseline.md"))
    a = ap.parse_args()
    dist = Path(a.dist)
    if not (dist / "index.html").exists():
        print(f"no build at {dist}; run the Astro build first (cd site && npm run build)")
        return 2
    pages = crawl(dist)
    site_pages = [p for p in pages if p["section"] != "styleguide"]
    inlinks = Counter()
    for p in pages:
        for href in p["links_all"]:
            if href != p["url"]:
                inlinks[href] += 1
    hub_links = Counter()
    for p in pages:
        if p["kind"] in ("hub", "index", "school-hub", "home"):
            for href in p["links_all"]:
                hub_links[href] += 1
    orphans = [p for p in site_pages if p["kind"] in ("article", "tool", "dataset", "start") and inlinks[p["url"]] == 0]
    not_on_hub = [p for p in site_pages if p["kind"] in ("article", "tool", "dataset", "start") and hub_links[p["url"]] == 0]
    per_section = Counter(p["section"] for p in site_pages if p["kind"] in ("article",))
    per_kind = Counter(p["kind"] for p in site_pages)
    banned = [(p, h) for p in site_pages for h in p["banned"]]
    banned_pages = sorted({p["url"] for p, _ in banned})
    mism = section_mismatches(site_pages)
    tools = tool_duplicates(site_pages)
    dup_tools = [t for t in tools if len(t["urls"]) > 1 and t["duplicate_pages"]]
    robots_txt = (dist / "robots.txt").read_text(encoding="utf-8").strip() if (dist / "robots.txt").exists() else "(none)"
    sitemap = (dist / "sitemap.xml").read_text(encoding="utf-8") if (dist / "sitemap.xml").exists() else ""
    sitemap_n = sitemap.count("<loc>")
    robots_meta = Counter(p["robots"] or "(none)" for p in site_pages)
    noindex_all = all("noindex" in (p["robots"] or "") for p in site_pages if p["kind"] in ("article", "tool", "dataset", "start", "hub"))
    emdash = Counter()
    for root in (REPO / "content", dist):
        for f in root.rglob("*"):
            if f.suffix in (".md", ".html") and f.is_file() and "—" in f.read_text(encoding="utf-8", errors="replace"):
                emdash[root.name] += 1
    today = date.today().isoformat()

    L = []
    L.append(f"# Baseline audit (Phase 0), {today}")
    L.append("")
    L.append(f"Crawl of the local Astro build at {dist.relative_to(REPO) if dist.is_relative_to(REPO) else dist} by scripts/prelaunch/baseline.py. Nothing was changed. "
             f"Pages: {len(site_pages)} (plus {len(pages) - len(site_pages)} styleguide samples, excluded below).")
    L.append("")
    L.append("## Summary")
    L.append("")
    L.append("| Measure | Value |")
    L.append("|---|---|")
    L.append(f"| Pages crawled (site) | {len(site_pages)} |")
    L.append("| By kind | " + ", ".join(f"{k} {n}" for k, n in sorted(per_kind.items())) + " |")
    L.append(f"| Articles by section | " + ", ".join(f"{k} {n}" for k, n in sorted(per_section.items())) + " |")
    L.append(f"| Pages matching a banned phrase | {len(banned_pages)} ({len(banned)} matches) |")
    L.append(f"| Tools at more than one URL | {len(dup_tools)} |")
    L.append(f"| Pages whose section does not match the Phase 3 mapping | {len(mism)} |")
    L.append(f"| Orphan pages (no internal in-link) | {len(orphans)} |")
    L.append(f"| Pages not linked from any hub or index page | {len(not_on_hub)} |")
    L.append(f"| robots.txt | {robots_txt.replace(chr(10), ' / ')} |")
    L.append(f"| sitemap.xml URLs | {sitemap_n} |")
    L.append(f"| robots meta | " + ", ".join(f"{k}: {n}" for k, n in robots_meta.most_common()) + (" (every content page noindex)" if noindex_all else " (some content pages lack noindex)") + " |")
    L.append(f"| Files with an em dash | content {emdash['content']}, build {emdash['dist']} |")
    L.append("")
    L.append("## Pages per section")
    L.append("")
    L.append("| Section | Articles | Hub exists |")
    L.append("|---|---|---|")
    hubs = {p["section"] for p in site_pages if p["kind"] == "hub"}
    for sec in sorted(set(per_section) | hubs):
        L.append(f"| {sec} | {per_section.get(sec, 0)} | {'yes' if sec in hubs else 'no'} |")
    L.append("")
    L.append("## Banned-phrase matches (Phase 1 patterns)")
    L.append("")
    if banned:
        L.append("| Page | Pattern | Text |")
        L.append("|---|---|---|")
        for p, h in banned:
            L.append(f"| {p['url']} | `{h['pattern']}` | {h['snippet'].replace('|', '/')} |")
    else:
        L.append("None.")
    L.append("")
    L.append("## Tools at more than one URL")
    L.append("")
    L.append("| Tool | URLs (kind, words) | Duplicate page(s) |")
    L.append("|---|---|---|")
    for t in tools:
        if len(t["urls"]) > 1:
            L.append(f"| {t['tool']} | " + "; ".join(f"{u['url']} ({u['kind']}, {u['words']}w)" for u in t["urls"]) + " | " + (", ".join(t["duplicate_pages"]) or "none (embeds only)") + " |")
    L.append("")
    L.append("## Pages whose section does not match the Phase 3 mapping")
    L.append("")
    L.append("| Page | Current | Suggested | Matched rule(s) | Transport terms too |")
    L.append("|---|---|---|---|---|")
    for m in mism:
        L.append(f"| {m['url']} | {m['section']} | {m['suggested']} | {'; '.join(m['rules'])} | {'yes' if m['transport_terms'] else 'no'} |")
    L.append("")
    kept = [(p["url"], p["reviewed_keep"]) for p in site_pages if p.get("reviewed_keep")]
    if kept:
        L.append("Reviewed by hand and kept where they are: " + "; ".join(f"{u} ({why})" for u, why in kept) + ".")
        L.append("")
    L.append("## Orphans and hub coverage")
    L.append("")
    L.append("Orphan pages (no page links to them): " + (", ".join(p["url"] for p in orphans) or "none") + ".")
    L.append("")
    L.append("Pages no hub or index page links to (reachable only from other articles): " + (", ".join(p["url"] for p in not_on_hub) or "none") + ".")
    L.append("")
    L.append("## Every URL")
    L.append("")
    L.append("| URL | Section | Kind | Words | Sources | External hosts | Updated | Author | Robots |")
    L.append("|---|---|---|---|---|---|---|---|---|")
    for p in sorted(site_pages, key=lambda p: (p["section"], p["url"])):
        L.append(f"| {p['url']} | {p['section']} | {p['kind']} | {p['words']} | {p['sources']} | {p['external_hosts']} | {p['updated']} | {p['author']} | {p['robots']} |")
    L.append("")
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L) + "\n", encoding="utf-8")
    out.with_suffix(".json").write_text(json.dumps({"date": today, "pages": site_pages, "mismatches": mism, "tools": tools, "orphans": [p["url"] for p in orphans],
                                                    "not_on_hub": [p["url"] for p in not_on_hub]}, indent=1), encoding="utf-8")
    print(f"{len(site_pages)} pages; banned phrases on {len(banned_pages)} pages ({len(banned)} matches); {len(dup_tools)} tools at two URLs; "
          f"{len(mism)} section mismatches; {len(orphans)} orphans; {len(not_on_hub)} not on a hub; sitemap {sitemap_n} URLs; noindex everywhere: {noindex_all}")
    print(f"written {out.relative_to(REPO)} and {out.with_suffix('.json').relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
