#!/usr/bin/env python
"""Lint for publish.sh (docs/v2/spec.md step 4). Code checks only, no judgement calls:
frontmatter complete (title, meta, primary_query, topic, school, type, updated, queue_id, sources[url,title,accessed]; images
entries complete when present, credit_url and license_url may be empty), title <= 60 and meta 120..155 chars, no em dash (U+2014) anywhere, the banned-phrase list,
internal links resolve to an existing article (for publish.sh: one that will be live), topic index or policy page, every cited
URL returns 2xx (HEAD then GET, 10 s, cached; 401/403/429 count as blocked, a warning, since the page exists but refuses automated clients), no near-duplicate of a published article (title + primary_query token Jaccard >= 0.8), and no run of more than 25
consecutive words copied from any cited page (word shingles against the fetched page text).

    worker/.venv/bin/python scripts/v2/lint.py content/articles/housing/x.md [...] [--root DIR] [--queue FILE] [--no-network] [--all]
    -> "OK <path>" or "FAIL <path>" plus one "  - problem" line each; exit 1 when any article fails.
    sys.path.insert(0, "scripts/v2"); import lint
    errors = lint.lint_article(path, root=REPO, web=lint.Web(REPO), published=lint.published_pairs(REPO))
Caches: build/runs/v2/lint/urls.json (2xx results) and build/runs/v2/lint/pages/<sha1>.txt (page text).
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import sys
import time
from pathlib import Path

import httpx
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import queue as q  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
TYPES = ("how-to", "decision", "scenario", "comparison", "place", "checklist", "roundup")
REQUIRED = ("title", "meta", "primary_query", "topic", "school", "type", "updated", "queue_id", "sources")
SOURCE_KEYS = ("url", "title", "accessed")
IMAGE_KEYS = ("file", "alt", "caption", "credit", "credit_url", "license", "license_url")
IMAGE_OPTIONAL = ("credit_url", "license_url")   # keys present, values may be empty: a public-domain Commons file has no license URL
BANNED = ("navigating", "it's important to note", "delve", "vibrant", "journey", "seamless", "robust", "leverage", "unlock", "dive into", "in today's")
BANNED_RE = re.compile(r"\b(?:" + "|".join(re.escape(b) for b in BANNED) + r")", re.I)
POLICY_PAGES = {"/", "/about/", "/privacy/", "/contact/", "/editorial-policy/", "/corrections/"}
MAX_COPY = 25
TIMEOUT = 10
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36 FootnoteDailyLint/1.0"
FM_RE = re.compile(r"﻿?---\s*\n(.*?)\n---\s*(?:\n|$)", re.S)
LINK_RE = re.compile(r"\[[^\]]*\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")
FIGURE_RE = re.compile(r"```figure\s*\n.*?\n```", re.S)
WORD_RE = re.compile(r"[a-z0-9]+(?:'[a-z0-9]+)?")


# ------------------------------------------------------------------------------------------ parsing
def parse(path: Path | str) -> tuple[dict, str, str, list[str]]:
    """(frontmatter, body, whole text, errors)."""
    raw = Path(path).read_text(encoding="utf-8")
    m = FM_RE.match(raw)
    if not m:
        return {}, raw, raw, ["no YAML frontmatter between --- lines"]
    try:
        fm = yaml.safe_load(m.group(1))
    except yaml.YAMLError as e:
        return {}, raw[m.end():], raw, [f"frontmatter is not valid YAML: {str(e).splitlines()[0]}"]
    if not isinstance(fm, dict):
        return {}, raw[m.end():], raw, ["frontmatter is not a mapping"]
    return fm, raw[m.end():], raw, []


def missing_keys(fm: dict) -> list[str]:
    """Completeness only (write.sh uses this to decide written vs back to approved); lengths and values are check_frontmatter's."""
    miss = [k for k in REQUIRED if fm.get(k) in (None, "", [])]
    sources = fm.get("sources")
    if isinstance(sources, list):
        for i, s in enumerate(sources):
            if not isinstance(s, dict) or any(not s.get(k) for k in SOURCE_KEYS):
                miss.append(f"sources[{i}] needs url, title and accessed")
    elif sources not in (None, ""):
        miss.append("sources must be a list")
    images = fm.get("images") or []
    if not isinstance(images, list):
        miss.append("images must be a list")
    else:
        for i, im in enumerate(images):
            if not isinstance(im, dict) or any(k not in im for k in IMAGE_KEYS) or any(not im.get(k) for k in IMAGE_KEYS if k not in IMAGE_OPTIONAL):
                miss.append(f"images[{i}] needs " + ", ".join(IMAGE_KEYS) + " (credit_url and license_url may be empty)")
    return miss


# ------------------------------------------------------------------------------------------ checks
def check_frontmatter(fm: dict) -> list[str]:
    errs = [f"frontmatter: missing {m}" for m in missing_keys(fm)]
    title, meta = str(fm.get("title") or ""), str(fm.get("meta") or "")
    if title and len(title) > 60:
        errs.append(f"title is {len(title)} characters (60 max)")
    if meta and not 120 <= len(meta) <= 155:
        errs.append(f"meta is {len(meta)} characters (120 to 155)")
    if fm.get("type") and fm["type"] not in TYPES:
        errs.append(f"type {fm['type']!r} is not one of {', '.join(TYPES)}")
    if fm.get("topic") and fm["topic"] not in q.TOPICS:
        errs.append(f"topic {fm['topic']!r} is not one of {', '.join(q.TOPICS)}")
    if fm.get("school") and fm["school"] != "cornell-university":
        errs.append(f"school is {fm['school']!r} (cornell-university)")
    if fm.get("updated") and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(fm["updated"])):
        errs.append(f"updated {fm['updated']!r} is not YYYY-MM-DD")
    if fm.get("queue_id") and not q.ID_RE.match(str(fm["queue_id"])):
        errs.append(f"queue_id {fm['queue_id']!r} is not q-<topic>-<4 digits>")
    return errs


def strip_urls(text: str) -> str:
    text = LINK_RE.sub(lambda m: m.group(0)[: m.group(0).index("](") + 1] + "()", text)
    return re.sub(r"https?://\S+", "", text)


def check_text(raw: str) -> list[str]:
    errs = []
    n = raw.count("—")
    if n:
        errs.append(f"{n} em dash(es) (U+2014)")
    hits = sorted({m.group(0).lower() for m in BANNED_RE.finditer(strip_urls(raw).replace("’", "'"))})
    if hits:
        errs.append("banned phrase(s): " + ", ".join(hits))
    return errs


def link_targets(body: str) -> list[str]:
    return [t.strip() for t in LINK_RE.findall(body)]


def check_links(body: str, root: Path, live: set[str] | None = None) -> list[str]:
    """An article link resolves when its file exists, or, given `live` (publish.sh: the pages that will be on the site), when its
    /<topic>/<slug>/ path is in that set."""
    errs = []
    for target in link_targets(body):
        if not target.startswith("/"):
            continue
        path = target.split("#")[0].split("?")[0]
        if path in POLICY_PAGES or path.startswith("/images/"):
            continue
        parts = path.strip("/").split("/")
        if len(parts) == 1 and parts[0] in q.TOPICS:
            continue
        if len(parts) == 2 and parts[0] in q.TOPICS:
            ok = f"/{parts[0]}/{parts[1]}/" in live if live is not None else (root / "content" / "articles" / parts[0] / f"{parts[1]}.md").exists()
            if ok:
                continue
        errs.append(f"internal link does not resolve: {target}")
    return errs


def external_urls(fm: dict, body: str) -> list[str]:
    urls = [str(s.get("url")) for s in (fm.get("sources") or []) if isinstance(s, dict) and s.get("url")]
    urls += [t for t in link_targets(body) if t.startswith("http")]
    out: list[str] = []
    for u in urls:
        u = u.rstrip(".,;")
        if u not in out:
            out.append(u)
    return out


def tokens(title: str, primary_query: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", f"{title} {primary_query}".lower()))


def published_pairs(root: Path | str, queue_path: Path | str | None = None) -> list[tuple[str, str, str]]:
    """(queue_id, title, primary_query) of every published article, the comparison set for the near-duplicate check."""
    root = Path(root)
    out = []
    for r in q.by_status("published", path=queue_path or root / "queue" / "queue.csv"):
        art = q.article_for(r["id"], root)
        fm = q.frontmatter(art) if art else {}
        out.append((r["id"], str(fm.get("title") or r["question"]), str(fm.get("primary_query") or r["primary_query"])))
    return out


def check_duplicate(fm: dict, published: list[tuple[str, str, str]]) -> list[str]:
    mine = tokens(str(fm.get("title") or ""), str(fm.get("primary_query") or ""))
    errs = []
    for qid, title, pq in published:
        if qid == str(fm.get("queue_id")) or not mine:
            continue
        other = tokens(title, pq)
        j = len(mine & other) / len(mine | other) if mine | other else 0.0
        if j >= 0.8:
            errs.append(f"near-duplicate of published {qid} ({title!r}): token similarity {j:.2f}")
    return errs


# ------------------------------------------------------------------------------------------ the web (cached)
def html_to_text(doc: str) -> str:
    doc = re.sub(r"(?is)<(script|style|noscript)\b.*?</\1>", " ", doc)
    doc = re.sub(r"(?s)<[^>]+>", " ", doc)
    return re.sub(r"\s+", " ", html.unescape(doc)).strip()


class Web:
    def __init__(self, root: Path | str, enabled: bool = True):
        self.enabled = enabled
        self.dir = Path(root) / "build" / "runs" / "v2" / "lint"
        (self.dir / "pages").mkdir(parents=True, exist_ok=True)
        self.cache_file = self.dir / "urls.json"
        self.cache: dict = json.loads(self.cache_file.read_text()) if self.cache_file.exists() else {}
        self.client = httpx.Client(follow_redirects=True, timeout=TIMEOUT, headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml,*/*;q=0.8"})

    def _page_file(self, url: str) -> Path:
        return self.dir / "pages" / (hashlib.sha1(url.encode()).hexdigest() + ".txt")

    def _store(self, url: str, r: httpx.Response) -> str:
        ctype = r.headers.get("content-type", "")
        text = html_to_text(r.text) if "html" in ctype else (r.text if ctype.startswith("text/") else "")
        self._page_file(url).write_text(text, encoding="utf-8")
        self.cache[url] = {"status": r.status_code, "at": time.strftime("%Y-%m-%dT%H:%M:%S")}
        self.cache_file.write_text(json.dumps(self.cache, indent=0, sort_keys=True))
        return text

    def status(self, url: str) -> int | str:
        """HEAD, then GET when HEAD is not 2xx; only 2xx results are cached, so a failure is checked again next run."""
        c = self.cache.get(url)
        if c and 200 <= int(c["status"]) < 300:
            return int(c["status"])
        try:
            r = self.client.head(url)
            if not 200 <= r.status_code < 300:
                r = self.client.get(url)
                if 200 <= r.status_code < 300:
                    self._store(url, r)
            elif not self._page_file(url).exists():
                g = self.client.get(url)
                if 200 <= g.status_code < 300:
                    self._store(url, g)
            return r.status_code
        except httpx.HTTPError as e:
            return f"error: {type(e).__name__}: {str(e)[:80]}"

    def text(self, url: str) -> str:
        p = self._page_file(url)
        if p.exists():
            return p.read_text(encoding="utf-8")
        try:
            r = self.client.get(url)
        except httpx.HTTPError:
            return ""
        return self._store(url, r) if 200 <= r.status_code < 300 else ""


def body_words(body: str) -> list[str]:
    text = FIGURE_RE.sub(" ", body)
    text = strip_urls(text)
    return WORD_RE.findall(text.lower().replace("’", "'"))


def check_copy(body: str, urls: list[str], web: Web) -> list[str]:
    n = MAX_COPY + 1
    ws = body_words(body)
    mine = {tuple(ws[i:i + n]) for i in range(len(ws) - n + 1)}
    errs = []
    for url in urls:
        theirs = WORD_RE.findall(web.text(url).lower().replace("’", "'"))
        for i in range(len(theirs) - n + 1):
            t = tuple(theirs[i:i + n])
            if t in mine:
                errs.append(f"copies more than {MAX_COPY} consecutive words from {url}: \"{' '.join(t[:8])} ...\"")
                break
    return errs


# ------------------------------------------------------------------------------------------ all together
BLOCKED = (401, 403, 429)   # refused or rate-limited, not gone: 404/410/5xx and connection errors stay failures


def lint_article(path: Path | str, *, root: Path | str = REPO, web: Web | None = None, published: list | None = None,
                 live: set[str] | None = None) -> list[str]:
    path, root = Path(path), Path(root)
    fm, body, raw, errs = parse(path)
    errs += check_frontmatter(fm)
    errs += check_text(raw)
    errs += check_links(body, root, live)
    if fm.get("topic") and path.parent.name != fm["topic"]:
        errs.append(f"file is under {path.parent.name}/ but topic is {fm['topic']}")
    errs += check_duplicate(fm, published or [])
    if web is not None and web.enabled:
        live = []
        for u in external_urls(fm, body):
            st = web.status(u)
            if isinstance(st, int) and 200 <= st < 300:
                live.append(u)
            elif st in BLOCKED:   # the page exists but refuses automated clients (bot protection); the reviewer opened it, so it is a warning, not a dead link
                print(f"  warning: source url blocked our checker ({st}), not counted as dead: {u}", file=sys.stderr)
            else:
                errs.append(f"source url returned {st}: {u}")
        errs += check_copy(body, live, web)
    return errs


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(prog="lint.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="*", help="article files (default with --all: every content/articles/*/*.md under --root)")
    ap.add_argument("--root", default=str(REPO), help="repo root (content/, queue/, build/ live here)")
    ap.add_argument("--queue", help="queue csv (default <root>/queue/queue.csv)")
    ap.add_argument("--no-network", action="store_true", help="skip the URL and copied-text checks")
    ap.add_argument("--all", action="store_true")
    a = ap.parse_args(argv)
    root = Path(a.root).resolve()
    paths = [Path(p) for p in a.paths] + (q.articles(root) if a.all else [])
    if not paths:
        ap.error("give article paths or --all")
    web = Web(root, enabled=not a.no_network)
    if a.no_network:
        print("network checks skipped (--no-network): source urls and copied text are not checked")
    published = published_pairs(root, a.queue)
    failed = 0
    for p in paths:
        errs = lint_article(p, root=root, web=web, published=published)
        if errs:
            failed += 1
            print(f"FAIL {p}")
            for e in errs:
                print(f"  - {e}")
        else:
            print(f"OK {p}")
    print(f"{len(paths) - failed} ok, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
