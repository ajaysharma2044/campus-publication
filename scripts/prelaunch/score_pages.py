"""Phase 9a of docs/v5/prelaunch-spec.md: the quality scorer. A page is eligible for indexing only if every check passes.

    worker/.venv/bin/python scripts/prelaunch/score_pages.py          -> reports/09-eligibility.csv (+ a summary on stdout)

Checks (all must pass): the banned-phrase linter; at least 3 cited official or primary sources (frontmatter sources on a .edu, .gov,
.ny.us, .org of a public body, a statute site, or an established news outlet; the lists are in OFFICIAL_HOSTS and NEWS_HOSTS);
a distinct primary query not used by another eligible page; at least one data element (a Markdown table, a figure block, a tool embed,
a dataset link or a computed figure introduced as ours); a named author (frontmatter author or the site default, never the generic
editors entry) and an Updated date within the last 12 months; a lead image that passed Phase 6 (reports/06-images-final.json) or no
lead image. Score = the number of passed checks (max 6) plus demand bonus points (a primary query, a tool, a dataset, a pillar).
"""
from __future__ import annotations

import csv
import json
import re
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import urlparse

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts" / "v2"))
from lib import queue as q  # noqa: E402

OFFICIAL_SUFFIXES = (".edu", ".gov", ".ny.us", ".mil")
OFFICIAL_HOSTS = {"nysenate.gov", "elections.ny.gov", "dmv.ny.gov", "ag.ny.gov", "cityofithacany.gov", "tompkinscountyny.gov", "town.ithaca.ny.us", "tcatbus.com",
                  "ithacacarshare.org", "ithacabikeshare.org", "hud.gov", "census.gov", "bls.gov", "law.cornell.edu", "ecode360.com", "codelibrary.amlegal.com",
                  "ourbus.com", "flixbus.com", "greyhound.com", "amtrak.com", "flyithaca.com", "syrairport.org", "commondataset.org", "ipeds.ed.gov", "nces.ed.gov"}
NEWS_HOSTS = {"cornellsun.com", "news.cornell.edu", "ithacavoice.com", "ithacajournal.com", "ithaca.com", "fingerlakes1.com", "wskg.org", "wamc.org", "nytimes.com",
              "chronicle.com", "insidehighered.com", "apnews.com", "reuters.com", "wsj.com", "washingtonpost.com", "bloomberg.com", "syracuse.com", "cornellians.cornell.edu"}
FORUM_HOSTS = {"reddit.com", "collegeconfidential.com", "quora.com", "facebook.com", "x.com", "twitter.com", "tiktok.com", "instagram.com"}
GENERIC_AUTHORS = {"", "eduexplained-editors", "footnote-daily-editors", "editors"}


QROWS = {r["id"]: r for r in q.read(q.QUEUE)}   # a tool, dataset or start page carries its primary query on its queue row (Phase 9 decision, 2026-11-11)


def host(u: str) -> str:
    h = urlparse(u).netloc.lower()
    return h[4:] if h.startswith("www.") else h


def is_official(u: str) -> bool:
    h = host(u)
    return h.endswith(OFFICIAL_SUFFIXES) or h in OFFICIAL_HOSTS or any(h.endswith("." + o) for o in OFFICIAL_HOSTS)


def is_news(u: str) -> bool:
    h = host(u)
    return h in NEWS_HOSTS or any(h.endswith("." + n) for n in NEWS_HOSTS)


def main() -> int:
    lint = json.loads(subprocess.run([sys.executable, str(REPO / "scripts" / "lint-content.py"), "--json"], capture_output=True, text=True, cwd=REPO).stdout)
    lint_bad = {h["file"] for h in lint["hits"]}
    images_final = {}
    fin = REPO / "reports" / "06-images-final.json"
    if fin.exists():
        for e in json.loads(fin.read_text(encoding="utf-8")):
            images_final[e["slug"]] = e.get("final", "keep")
    default_author = ""
    cfg = (REPO / "site" / "site.config.ts").read_text(encoding="utf-8")
    m = re.search(r"defaultAuthor:\s*'([^']+)'", cfg)
    if m:
        default_author = m.group(1)
    rows = []
    kinds = [("article", "articles/*/*.md"), ("tool", "tools/*/tool.md"), ("dataset", "datasets/*.md"), ("start", "start/*.md")]
    cutoff = date.today() - timedelta(days=365)
    for kind, pattern in kinds:
        for p in sorted((REPO / "content").glob(pattern)):
            fm = q.frontmatter(p)
            rel = str(p.relative_to(REPO))
            slug = p.parent.name if kind == "tool" else p.stem
            section = p.parent.name if kind == "article" else str(fm.get("topic") or kind)
            url = f"/cornell/{section}/{slug}/" if kind == "article" else f"/{kind}s/{slug}/" if kind != "start" else f"/start/{slug}/"
            body = re.sub(r"^---\n.*?\n---\n", "", p.read_text(encoding="utf-8"), count=1, flags=re.S)
            srcs = [s.get("url", "") for s in (fm.get("sources") or []) if isinstance(s, dict)]
            official = [u for u in srcs if is_official(u) or is_news(u)]
            forum = [u for u in srcs if host(u) in FORUM_HOSTS or any(host(u).endswith("." + f) for f in FORUM_HOSTS)]
            has_table = bool(re.search(r"^\|[-:| ]+\|\s*$", body, re.M))
            has_figure = "```figure" in body or "```tool" in body or "/datasets/" in body or "/tools/" in body or kind in ("tool", "dataset")
            has_our_figure = bool(re.search(r"\bour (count|estimate|calculation|median|average|total|math)\b", body, re.I))
            author = str(fm.get("author") or default_author)
            updated = str(fm.get("updated") or "")[:10]
            try:
                recent = date.fromisoformat(updated) >= cutoff
            except ValueError:
                recent = False
            img_ok = images_final.get(slug, "keep") == "keep" or not fm.get("images")
            checks = {
                "linter": rel not in lint_bad,
                "sources3": len(official) >= 3 and not forum,
                "data_element": has_table or has_figure or has_our_figure,
                "author_and_date": author not in GENERIC_AUTHORS and recent,
                "images": img_ok,
            }
            rows.append({"url": url, "file": rel, "kind": kind, "section": section, "primary_query": str(fm.get("primary_query") or (QROWS.get(str(fm.get("queue_id") or "")) or {}).get("primary_query") or "").strip().lower(), "index": bool(fm.get("index")),
                         "words": len(body.split()), "sources_official": len(official), "forum_sources": len(forum), "author": author, "updated": updated, **checks})
    # the distinct-query check: among pages that pass everything else, a primary query used twice fails both
    seen: dict[str, list[dict]] = {}
    for r in rows:
        if r["primary_query"]:
            seen.setdefault(r["primary_query"], []).append(r)
    for r in rows:
        others = [o for o in seen.get(r["primary_query"], []) if o is not r and all(o[c] for c in ("linter", "sources3", "data_element", "author_and_date", "images"))]
        r["distinct_query"] = bool(r["primary_query"]) and not others
    for r in rows:
        checks = [r[c] for c in ("linter", "sources3", "distinct_query", "data_element", "author_and_date", "images")]
        r["eligible"] = all(checks)
        r["score"] = sum(checks) + (1 if r["kind"] in ("tool", "dataset") else 0) + (1 if r["words"] >= 2500 else 0) + (1 if r["sources_official"] >= 8 else 0)
        r["failing"] = ";".join(c for c in ("linter", "sources3", "distinct_query", "data_element", "author_and_date", "images") if not r[c])
    out = REPO / "reports" / "09-eligibility.csv"
    cols = ["url", "kind", "section", "eligible", "score", "failing", "index", "words", "sources_official", "forum_sources", "author", "updated", "primary_query", "file"]
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in sorted(rows, key=lambda r: (-r["score"], r["url"])):
            w.writerow({c: r[c] for c in cols})
    elig = sum(1 for r in rows if r["eligible"])
    fails = {}
    for r in rows:
        for c in r["failing"].split(";"):
            if c:
                fails[c] = fails.get(c, 0) + 1
    print(f"{len(rows)} pages scored; {elig} eligible; failing checks: {fails}; written {out.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
