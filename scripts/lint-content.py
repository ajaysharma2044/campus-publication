#!/usr/bin/env python3
"""Banned-phrase linter (docs/v5/prelaunch-spec.md, Phase 1a): a page may never tell the reader that the sources, the guide, the page
or our research lack something. Fails when any page body matches a pattern; the site build runs it before Astro (site/package.json
prebuild) and scripts/v2/lint.py applies the same patterns to every draft, so a draft that matches cannot be published.

    python3 scripts/lint-content.py [paths...] [--warn] [--json] [--emdash]

With no paths it scans content/articles, content/tools, content/datasets, content/start and content/pages. --warn reports and exits 0
(local verification builds before Phase 2 clears the pages: LINT_CONTENT_WARN=1 npm run build). --emdash also fails on an em dash
anywhere under content/ and site/dist (the spec's rule 1). Plain Python 3, no third-party modules, so the build can run it anywhere.
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CONTENT_DIRS = ("content/articles", "content/tools", "content/datasets", "content/start", "content/pages")

# The spec's patterns (Phase 1a), then the variants the Phase 0 crawl and the house pages showed. Case-insensitive, on the body text.
PATTERNS: list[tuple[str, str]] = [
    ("spec", r"sources? (for|behind|in) this (guide|page|article)"),
    ("spec", r"the sources? .{0,40}(do not|does not|don't|contain no|include no)"),
    ("spec", r"no source (gives|lists|says|reports|provides)"),
    ("spec", r"(page|site|document) (lists|gives|shows|provides) no "),
    ("spec", r"we (could not|couldn't) find"),
    ("spec", r"not (included|available) in (our|the) sources"),
    ("spec", r"as of (our|this) research"),
    ("variant", r"honest limit"),
    ("variant", r"\bnot confirmed\b"),
    ("variant", r"(we|this guide|this page|the guide|our research) (cannot|can't|could not|couldn't|did not|didn't|do not|don't|was unable to|were unable to) (confirm|verify|find|locate|establish)"),
    ("variant", r"(unable|not able) to (confirm|verify|find|locate)"),
    ("variant", r"(our|the) (sources|research|brief|guide) (lack|lacks|omit|omits|miss|misses|do not cover|does not cover|did not cover)"),
    ("variant", r"(is|was|are|were) not in (our|the) (sources|brief|research|pages we)"),
    ("variant", r"not (covered|addressed|answered) (by|in) (our|the|these|any) (sources?|research|brief)"),
    ("variant", r"no (official|public|published|reliable) (figure|number|list|page|source|data) (exists|is available|was found|could be found|turned up)"),
    ("variant", r"(nothing|no page|no figure|no number) (we|the sources?) (found|opened|checked|read)"),
    ("variant", r"(gap|hole) in (our|the) (sources|research|coverage)"),
    ("variant", r"we (do not|don't) (know|have) (a|an|the) (figure|number|date|price|answer)"),
    # forms the Phase 5 cluster agents found on pages the first list missed (reports/05-deferred.json), 2026-11-11
    ("variant", r"(pages?|site|website|notice|rate page|fee page|policy page|calendar|handbook) (do not|does not|don't|doesn't|did not|didn't|never) (say|give|state|list|mention|name|cover|address|answer|explain|spell out|show)"),
    ("variant", r"(gives?|lists?|offers?|publish(es)?|posts?|provides?|names?|states?) no (founding|price|prices|figure|figures|date|dates|amount|amounts|number|numbers|rate|rates|deadline|deadlines|cost|costs|hours|list|address|phone|fee|fees|total|totals|breakdown|cap|caps|limit|limits)"),
    ("variant", r"no public (source|figure|data|number|list|record)"),
    ("variant", r"(aren't|are not|isn't|is not|wasn't|was not) (covered|addressed|included|answered) here"),
    ("variant", r"records behind this (page|guide|article)"),
    ("variant", r"(page|notice|policy|policy page|document|pdf|table|chart) (is |was )?undated"),
    ("variant", r"(amounts?|figures?|prices?|dates?|numbers?|rates?|hours|totals?) (is|are|was|were) not on (it|the page|that page|the site|the notice)"),
    ("variant", r"(fact file|brief|our notes|the notes|our records) (has|have|had|holds|hold) no"),
    ("variant", r"not in (our|the) (brief|fact file|notes|sources|corpus|records)"),
    ("variant", r"no .{0,40}(story|article|page|figure|source|record|number|listing) (was|were|could be|has been|have been) (found|located|turned up)"),
    ("variant", r"none (was |were )?confirmed"),
    ("variant", r"we have (not|n't) (checked|verified|confirmed|read|opened|seen)"),
    ("variant", r"(could not|couldn't|cannot|can't) be (confirmed|verified|located)"),
    ("variant", r"(has|have) not been (read|checked|verified|confirmed) in"),
    # forms the Phase 5 skeptics found after the second pass (reports/05-deferred-results.json), 2026-11-11: table cells and labels that
    # describe what a listing or page leaves out, planner notes and references to the pipeline's own documents, and source-quality asides
    ("variant", r"\|\s*(not|none|nothing) (listed|published|stated|named|printed|posted|shown|given|available|provided|disclosed|confirmed|found)\b[^|]{0,40}\|"),
    ("variant", r"\|\s*(not|none|nothing) (listed|published|stated|named|printed|posted|shown|given|available|provided|disclosed|confirmed|found)\b[^|]{0,40}$"),
    ("variant", r"\bnot (stated|printed|posted|disclosed)\b"),
    ("variant", r"\b(price|prices|rate|rates|rent|rents|fee|fees|date|dates|year|hours|amount|amounts|figure|figures) (is |are |was |were )?not (posted|shown|listed|published|printed|given|stated)\b"),
    ("variant", r"\bno (rates?|prices?|rents?|fees?|dates?|figures?|amounts?|hours) (shown|listed|posted|published|printed|given|stated)\b"),
    ("variant", r"\b(topic brief|the brief, section|brief sections?|from the brief|in the brief|per the brief|brief inputs|brief figures?|fact file|facts\.csv|the fact sheet|our notes|planner notes?)\b"),
    ("variant", r"\b(search snippet|snippet-only|seen only as|seen as a snippet|could not be opened|cannot be opened|failed to load|returned (a )?404|returns (a )?404|page not found)\b"),
    ("variant", r"\b(page|site|website|listing|listings|notice|calendar|handbook|pdf|document|table|scorecard|brochure|flyer|map|form|portal)s? (says [^.|]{0,80} and )?(does not|doesn't|do not|don't|did not|didn't|never) (list|name|state|give|say|show|mention|publish|post|print|spell out|cover|address|answer|explain)\b"),
    ("variant", r"\b(treat (them|it|this|these) as (a )?leads?|confirm with [A-Z][a-z]+ before relying|as (a )?leads?, not (facts?|figures?))\b"),
    ("variant", r"\b(no guide covers (them|it|this) yet|no page covers (them|it|this) yet|not covered yet)\b"),
]
COMPILED = [(kind, re.compile(p, re.I)) for kind, p in PATTERNS]
FM_RE = re.compile(r"^---\n.*?\n---\n", re.S)
URL_RE = re.compile(r"\(https?://[^)]+\)|<https?://[^>]+>|https?://\S+")


def body_text(path: Path) -> str:
    """The page body without frontmatter, URLs and Markdown link brackets; fenced blocks stay (glance, reader and figure text renders)."""
    raw = path.read_text(encoding="utf-8", errors="replace")
    body = FM_RE.sub("", raw, count=1)
    fm = FM_RE.match(raw)
    if fm:   # text the page renders from its frontmatter: captions and alt text under photos, the meta description, the dek and the title
        body += "\n" + "\n".join(m.group(2) for m in re.finditer(r"^\s*(?:caption|alt|meta|dek|title|description): *(['\"]?)(.+?)\1\s*$", fm.group(0), re.M))
    body = URL_RE.sub(" ", body)
    body = re.sub(r"!\[[^\]]*\]", " ", body)
    return body


def scan(paths: list[Path]) -> list[dict]:
    hits = []
    for p in paths:
        text = body_text(p)
        lines = text.split("\n")
        for i, line in enumerate(lines, 1):
            for kind, rx in COMPILED:
                for m in rx.finditer(line):
                    s = max(0, m.start() - 60)
                    hits.append({"file": str(p.relative_to(REPO)) if p.is_relative_to(REPO) else str(p), "line": i, "kind": kind,
                                 "pattern": rx.pattern, "match": m.group(0), "snippet": line[s: m.end() + 60].strip()})
    return hits


def emdash_hits(roots: list[Path]) -> list[str]:
    out = []
    for root in roots:
        if not root.exists():
            continue
        for f in root.rglob("*"):
            if f.is_file() and f.suffix in (".md", ".html", ".csv", ".json", ".yml", ".yaml", ".txt") and "—" in f.read_text(encoding="utf-8", errors="replace"):
                out.append(str(f.relative_to(REPO)) if f.is_relative_to(REPO) else str(f))
    return out


def default_paths() -> list[Path]:
    out: list[Path] = []
    for d in CONTENT_DIRS:
        out += sorted((REPO / d).rglob("*.md")) if (REPO / d).exists() else []
    return out


def main(argv: list[str]) -> int:
    warn = "--warn" in argv or os.environ.get("LINT_CONTENT_WARN") == "1"
    as_json = "--json" in argv
    emdash = "--emdash" in argv
    given = [Path(a) for a in argv if not a.startswith("--")]
    paths = [p for g in given for p in (sorted(g.rglob("*.md")) if g.is_dir() else [g])] if given else default_paths()
    hits = scan(paths)
    dashes = emdash_hits([REPO / "content", REPO / "site" / "dist"]) if emdash else []
    if as_json:
        print(json.dumps({"hits": hits, "em_dash_files": dashes}, indent=1))
    else:
        for h in hits:
            print(f"{h['file']}:{h['line']}: {h['match']!r}: {h['snippet']}")
        for f in dashes:
            print(f"{f}: em dash")
        files = len({h["file"] for h in hits})
        print(f"lint-content: {len(hits)} banned-phrase match(es) on {files} page(s) of {len(paths)} scanned" + (f"; {len(dashes)} file(s) with an em dash" if emdash else ""))
    bad = bool(hits or dashes)
    if bad and warn:
        print("lint-content: WARN mode, not failing the build (LINT_CONTENT_WARN=1 or --warn)")
        return 0
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
