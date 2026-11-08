#!/usr/bin/env python
"""Lint for publish.sh (docs/v2/spec.md step 4, and the "Publish requirements" of docs/v3/spec.md). Code checks only, no judgement calls.

Every article (the v2 checks): frontmatter complete (title, meta, primary_query, topic, school, type, updated, queue_id,
sources[url,title,accessed]; images entries complete when present, credit_url and license_url may be empty), title <= 60 and meta
120..155 chars, no em dash (U+2014) anywhere, the style guide's banned-word list, internal links resolve to an existing article (for
publish.sh: one that will be live), topic index, tool, dataset, start-here or policy page, every cited URL returns 2xx (HEAD then GET,
10 s, cached; 401/403/429 count as blocked, a warning, since the page exists but refuses automated clients), no near-duplicate of a
published article (title + primary_query token Jaccard >= 0.8), and no run of more than 25 consecutive words copied from any cited page
(word shingles against the fetched page text).

Articles with a frontmatter `kind` (v3: pillar | spoke | reader_guide | rewrite) also meet the publish requirements of docs/v3/spec.md.
The published v2 pages carry no kind and keep the v2 checks alone until they are rewritten.
    frontmatter: kind; readers (a non-empty list); pillar (/<dir>/<slug>/ of the topic pillar, empty for the pillar itself, and it
      resolves); brief (an intel/.../*.md path that exists); tools (the slugs the body embeds, each with content/tools/<slug>/tool.md
      and tool.html)
    lead photo: images[0] present and its file stored under content/images/<slug>/
    visuals: beyond the lead photo, one photo, ```figure fence, ```tool fence or <iframe> embed per 600 words (words // 600)
    layers: exactly one ```glance fence with 4 to 6 bullets, before the first ## heading; then the answer paragraph, 3 sentences or
      fewer; then ```reader "If you're ..." fences (2 at least; pillars and reader guides 4), the first of them before the first ##
      heading
    detail: words >= 1,200 (spoke, rewrite), 3,000 (pillar), 1,500 (reader_guide); >= 1 Markdown table; sources >= 8 (pillar 20);
      a "## Common mistakes" heading; a "## FAQ" section with >= 4 questions (bold lead-ins or ### headings); a link to the pillar
      path and to >= 2 other articles in the same topic dir; every ![alt](n.webp) reference has an images entry
    writing: no research-narration phrase (docs/v2/style.md Part 7); average sentence under 18 words over the prose (tables, fences,
      headings and link URLs excluded; reader blocks included)
Every message names its requirement, so publish.sh routes it as a text-level failure (one revision) unless it is a dead source URL
(wait) or a near-duplicate (reject). A rewrite (kind: rewrite) is never a duplicate of the published row whose file it overwrites.

    worker/.venv/bin/python scripts/v2/lint.py content/articles/housing/x.md [...] [--root DIR] [--queue FILE] [--no-network] [--all] [--explain]
    -> "OK <path>" or "FAIL <path>" plus one "  - problem" line each; exit 1 when any article fails.
       --explain adds one "  measured: ..." line per article with the numbers behind the checks.
    sys.path.insert(0, "scripts/v2"); import lint
    errors = lint.lint_article(path, root=REPO, web=lint.Web(REPO), published=lint.published_pairs(REPO))
    measures, errors = lint.v3_checks(fm, body, path, root)          # the v3 numbers and messages alone
The banned words and the narration phrases are read from docs/v2/style.md (the "No filler:" line and the research-narration lines), with
the built-in lists as the fallback; topic dirs come from scripts/v2/lib/queue.py plus scripts/v3/topics.yml. scripts/v2/render_site.py
imports split_fences(), TOPIC_DIRS and KINDS from here so both read an article the same way.
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
DEFAULT_BANNED = ("navigating", "it's important to note", "delve", "vibrant", "journey", "seamless", "robust", "leverage", "unlock", "dive into", "in today's")
DEFAULT_NARRATION = ("we found", "we checked", "our research", "the pages we opened", "the pages we checked", "sources say", "according to our review",
                     "we were unable to confirm", "it is worth noting", "as of our review", "we looked at", "our research shows")
POLICY_PAGES = {"/", "/about/", "/privacy/", "/contact/", "/editorial-policy/", "/corrections/", "/thanks/", "/tools/", "/datasets/", "/start/"}
SECTION_DIRS = ("tools", "datasets", "start")   # /tools/<slug>/, /datasets/<slug>/, /start/<reader>/ (docs/v3 contracts 4 and 3)
MAX_COPY = 25
TIMEOUT = 10
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36 FootnoteDailyLint/1.0"
FM_RE = re.compile(r"﻿?---\s*\n(.*?)\n---\s*(?:\n|$)", re.S)
LINK_RE = re.compile(r"\[[^\]]*\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")
IMG_REF_RE = re.compile(r"!\[[^\]]*\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")
WORD_RE = re.compile(r"[a-z0-9]+(?:'[a-z0-9]+)?")

# ------------------------------------------------------------------------------------------ v3 publish requirements (docs/v3/spec.md)
KINDS = ("pillar", "spoke", "reader_guide", "rewrite")
WORD_FLOOR = {"pillar": 3000, "spoke": 1200, "reader_guide": 1500, "rewrite": 1200}   # a rewrite follows its kind; the default is a spoke
SOURCE_FLOOR = {"pillar": 20}
SOURCE_DEFAULT = 8
READER_FLOOR = {"pillar": 4, "reader_guide": 4}
READER_DEFAULT = 2
VISUAL_WORDS = 600
GLANCE_BULLETS = (4, 6)
ANSWER_MAX = 3
FAQ_MIN = 4
SIBLINGS_MIN = 2
SENTENCE_MAX = 18.0
H2_RE = re.compile(r"^##[ \t]+\S", re.M)
MISTAKES_RE = re.compile(r"^##[ \t]+common mistakes\b", re.I | re.M)
FAQ_RE = re.compile(r"^##[ \t]+(?:faqs?|frequently asked questions)\b", re.I | re.M)
TABLE_SEP_RE = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*(?:\|\s*:?-{3,}:?\s*)+\|?\s*$")
QUESTION_RE = re.compile(r"^(?:[-*+][ \t]+)?(?:\*\*[^*\n]+\*\*|###[ \t]+\S)", re.M)
SENTENCE_SPLIT = re.compile(r"(?<=[.!?])[\"')\]]*\s+(?=[\"'(\[]?[A-Z0-9$])")
ABBREV_RE = re.compile(r"(?:\b(?:dr|mr|mrs|ms|st|ave|blvd|rd|inc|co|no|vs|etc|approx|dept|jan|feb|mar|apr|jun|jul|aug|sep|sept|oct|nov|dec)"
                       r"|\b[a-z]|\b(?:u\.s|e\.g|i\.e|a\.m|p\.m|ph\.d))\.$", re.I)


def style_lists(root: Path = REPO) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """The banned filler words and the research-narration phrases from docs/v2/style.md (the "No filler:" line, and the quoted phrases
    on every research-narration line of Parts 6 and 7), so a style-guide edit changes the lint without a code change. The built-in
    lists are the fallback when the file is missing or written another way."""
    banned, narration = DEFAULT_BANNED, DEFAULT_NARRATION
    try:
        text = (root / "docs" / "v2" / "style.md").read_text(encoding="utf-8")
    except OSError:
        return banned, narration
    m = re.search(r"No filler[^:\n]*:\s*([^\n]+)", text)
    if m:
        words = tuple(dict.fromkeys(w.strip().strip(".").strip().lower().replace("’", "'") for w in m.group(1).split(",") if w.strip().strip(".")))
        if len(words) >= 3:
            banned = words
    phrases = []
    for line in re.findall(r"^.*[Rr]esearch[- ]narration.*$", text, re.M):
        # the quoted phrases of the sentence that names the ban, not of the advice after it ('put gaps in one short "Not confirmed" line')
        sentence = re.split(r"(?<=[.)])\.?\s+(?=[A-Z])", line[line.lower().index("narration"):], maxsplit=1)[0]
        phrases += [p.strip().lower().replace("’", "'") for p in re.findall(r"\"([^\"]+)\"", sentence) if p.strip()]
    if len(phrases) >= 3:
        narration = tuple(dict.fromkeys(phrases))
    return banned, narration


BANNED, NARRATION = style_lists()
BANNED_RE = re.compile(r"\b(?:" + "|".join(re.escape(b) for b in BANNED) + r")", re.I)
NARRATION_RE = re.compile(r"\b(?:" + "|".join(re.escape(p) for p in NARRATION) + r")\b", re.I)


def topic_dirs(root: Path = REPO) -> list[str]:
    """The article dirs: the v2 topics of scripts/v2/lib/queue.py plus every `dir` in scripts/v3/topics.yml (dining, transfer, health are new)."""
    dirs = list(q.TOPICS)
    yml = root / "scripts" / "v3" / "topics.yml"
    if yml.is_file():
        try:
            for t in yaml.safe_load(yml.read_text(encoding="utf-8")) or []:
                d = str((t or {}).get("dir") or "").strip() if isinstance(t, dict) else ""
                if d and d not in dirs:
                    dirs.append(d)
        except yaml.YAMLError:
            pass
    return dirs


TOPIC_DIRS = topic_dirs()


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


def split_fences(body: str) -> list[tuple]:
    """The body as ("text", chunk) and ("fence", lang, info, content) segments, in order. A fence opens with ``` at column 0 followed by
    its language and an optional info string (the quoted title of a ```reader fence, the slug of a ```tool fence) and closes at the next
    line holding ``` alone; a one-line fence (```tool rent-commute-calculator```) has empty content. Fences do not nest: a ``` line inside
    a reader block closes it. An unterminated fence runs to the end of the body."""
    out: list[tuple] = []
    buf: list[str] = []
    lines = body.split("\n")

    def flush() -> None:
        if buf:
            out.append(("text", "\n".join(buf)))
            buf.clear()

    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("```"):
            rest = line[3:].strip()
            if len(rest) > 3 and rest.endswith("```"):      # one line: ```tool <slug>```
                lang, _, info = rest[:-3].strip().partition(" ")
                flush()
                out.append(("fence", lang.strip().lower(), info.strip(), ""))
                i += 1
                continue
            lang, _, info = rest.partition(" ")
            j = i + 1
            while j < len(lines) and not re.fullmatch(r"```[ \t]*", lines[j]):
                j += 1
            flush()
            out.append(("fence", lang.strip().lower(), info.strip(), "\n".join(lines[i + 1:j])))
            i = j + 1
            continue
        buf.append(line)
        i += 1
    flush()
    return out


def missing_keys(fm: dict) -> list[str]:
    """Completeness only (write.sh uses this to decide written vs back to approved); lengths and values are check_frontmatter's.
    With a `kind` (v3) the readers list, the brief path and, except for the pillar, the pillar path are part of completeness too."""
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
    if "kind" in fm:
        if not fm.get("readers"):
            miss.append("readers")
        if not fm.get("brief"):
            miss.append("brief")
        if str(fm.get("kind") or "").strip() != "pillar" and not fm.get("pillar"):
            miss.append("pillar")
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
    if fm.get("topic") and fm["topic"] not in TOPIC_DIRS:
        errs.append(f"topic {fm['topic']!r} is not one of {', '.join(TOPIC_DIRS)}")
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


def site_path(target: str) -> str:
    """/housing/slug -> /housing/slug/ without a fragment or query."""
    p = target.split("#")[0].split("?")[0]
    return p if p.endswith("/") else p + "/"


def resolves(path: str, root: Path, live: set[str] | None = None) -> bool:
    """A two-part site path lands on a page: an article (its file exists, or, given `live`, publish.sh's set of pages that will be on
    the site), a tool (content/tools/<slug>/tool.md), a dataset (content/datasets/<slug>.md) or a start page (content/start/<slug>.md)."""
    parts = path.strip("/").split("/")
    if len(parts) != 2:
        return False
    section, slug = parts
    if section in TOPIC_DIRS:
        return f"/{section}/{slug}/" in live if live is not None else (root / "content" / "articles" / section / f"{slug}.md").exists()
    if live is not None and f"/{section}/{slug}/" in live:
        return True
    if section == "tools":
        return (root / "content" / "tools" / slug / "tool.md").exists()
    if section == "datasets":
        return (root / "content" / "datasets" / f"{slug}.md").exists()
    if section == "start":
        return (root / "content" / "start" / f"{slug}.md").exists()
    return False


def check_links(body: str, root: Path, live: set[str] | None = None) -> list[str]:
    """An internal link resolves when it lands on a topic index, a policy page, an image, or a page resolves() knows."""
    errs = []
    for target in link_targets(body):
        if not target.startswith("/"):
            continue
        path = target.split("#")[0].split("?")[0]
        if path in POLICY_PAGES or path.startswith("/images/"):
            continue
        parts = path.strip("/").split("/")
        if len(parts) == 1 and parts[0] in TOPIC_DIRS:
            continue
        if len(parts) == 2 and resolves(site_path(path), root, live):
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


# ------------------------------------------------------------------------------------------ v3 measures
def clean_prose(text: str) -> str:
    """Markdown to plain sentences: link text kept and URLs dropped, images, HTML tags, emphasis, inline code, list markers and
    blockquote markers removed."""
    text = IMG_REF_RE.sub(" ", text)
    text = LINK_RE.sub(lambda m: m.group(0)[1:m.group(0).index("](")], text)
    text = re.sub(r"https?://\S+", "", text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"[*_`]+", "", text)
    text = re.sub(r"^[ \t]*(?:[-*+]|\d+[.)])[ \t]+", "", text, flags=re.M)
    text = re.sub(r"^[ \t]*>[ \t]?", "", text, flags=re.M)
    return text


def sentences(text: str) -> list[str]:
    """Sentences of a Markdown chunk: each line (a paragraph, a list item) is split after . ! or ? when a capital, digit, dollar sign
    or opening quote follows; a split after an abbreviation or an initial (Dr., St., Jan., J.) is undone."""
    out = []
    for line in clean_prose(text).split("\n"):
        line = line.strip()
        if not line:
            continue
        merged: list[str] = []
        for part in SENTENCE_SPLIT.split(line):
            if merged and ABBREV_RE.search(merged[-1].rstrip("\"')]")):
                merged[-1] += " " + part
            else:
                merged.append(part)
        out += [p for p in merged if WORD_RE.search(p.lower())]
    return out


def prose_text(segs: list[tuple]) -> str:
    """The prose the sentence-length rule measures: the text segments and the reader blocks, minus headings and table rows
    (the glance bullets, figures, tools and other fences are left out)."""
    chunks = [s[1] for s in segs if s[0] == "text"] + [s[3] for s in segs if s[0] == "fence" and s[1] == "reader"]
    lines = [l for l in "\n".join(chunks).split("\n") if not l.lstrip().startswith("#") and not re.match(r"^\s*\|", l) and not TABLE_SEP_RE.match(l)]
    return "\n".join(lines)


def word_count(segs: list[tuple]) -> int:
    """Words of the article's own text: text segments plus the glance and reader fences; figures, tools and code fences do not count."""
    chunks = [s[1] for s in segs if s[0] == "text"] + [s[3] for s in segs if s[0] == "fence" and s[1] in ("glance", "reader")]
    return len(WORD_RE.findall(clean_prose("\n".join(chunks)).lower()))


def avg_sentence(text: str) -> tuple[float, int]:
    s = sentences(text)
    words = sum(len(WORD_RE.findall(x.lower())) for x in s)
    return (words / len(s) if s else 0.0), len(s)


def count_tables(text: str) -> int:
    lines = text.split("\n")
    return sum(1 for i in range(1, len(lines)) if TABLE_SEP_RE.match(lines[i]) and "|" in lines[i - 1])


def faq_questions(text: str) -> int | None:
    """Questions in the ## FAQ section (bold lead-ins or ### headings), or None when there is no FAQ heading."""
    m = FAQ_RE.search(text)
    if not m:
        return None
    rest = text[m.end():]
    nxt = re.search(r"^##[ \t]", rest, re.M)
    return len(QUESTION_RE.findall(rest[: nxt.start()] if nxt else rest))


def answer_paragraph(segs: list[tuple]) -> str:
    """The first paragraph after the glance fence (the first paragraph of the body when there is none), or '' when a heading, a fence
    or the end comes first. An image line is not a paragraph."""
    start = next((i + 1 for i, s in enumerate(segs) if s[0] == "fence" and s[1] == "glance"), 0)
    for seg in segs[start:]:
        if seg[0] == "fence":
            return ""
        para: list[str] = []
        for line in seg[1].split("\n"):
            if not line.strip():
                if para:
                    break
                continue
            if line.lstrip().startswith("#") or TABLE_SEP_RE.match(line) or line.lstrip().startswith("|"):
                return "" if not para else " ".join(para)
            if IMG_REF_RE.fullmatch(line.strip()):
                continue
            para.append(line.strip())
        if para:
            return " ".join(para)
    return ""


def image_file(root: Path, slug: str, name: str) -> bool:
    """content/images/<slug>/<name>, or any file with the same stem (the finder stores 1.webp for an entry that says 1.jpg)."""
    if not name:
        return False
    d = root / "content" / "images" / slug
    return (d / name).is_file() or any(p.is_file() for p in d.glob(f"{Path(name).stem}.*"))


def v3_checks(fm: dict, body: str, path: Path | str, root: Path | str = REPO, live: set[str] | None = None) -> tuple[dict, list[str]]:
    """The docs/v3/spec.md publish requirements for one article with a `kind`: (measures, error messages). Each message names its
    requirement (frontmatter, lead photo, visuals, glance box, layers, answer, reader blocks, words, tables, sources, sections, FAQ,
    links, research narration, sentence length) so publish.sh can route it."""
    path, root = Path(path), Path(root)
    kind = str(fm.get("kind") or "").strip()
    slug, topic = path.stem, str(fm.get("topic") or path.parent.name)
    segs = split_fences(body)
    fences = [s for s in segs if s[0] == "fence"]
    glance = [s for s in fences if s[1] == "glance"]
    readers = [s for s in fences if s[1] == "reader"]
    tools = [s for s in fences if s[1] == "tool"]
    figures = [s for s in fences if s[1] == "figure"]
    text = "\n".join(s[1] for s in segs if s[0] == "text")
    text_and_readers = text + "\n" + "\n".join(s[3] for s in readers)
    m: dict = {"kind": kind or "(missing)"}
    errs: list[str] = []

    # frontmatter (v3 keys)
    if kind not in KINDS:
        errs.append(f"frontmatter: kind {kind!r} is not one of {', '.join(KINDS)}")
    rd = fm.get("readers")
    if not isinstance(rd, list) or not rd or not all(isinstance(r, str) and r.strip() for r in rd):
        errs.append("frontmatter: readers must be a non-empty list of reader types")
    pillar = str(fm.get("pillar") or "").strip()
    if kind == "pillar":
        if pillar:
            errs.append("frontmatter: pillar must be empty for the pillar itself")
    elif not re.fullmatch(rf"/{re.escape(topic)}/[a-z0-9][a-z0-9-]*/", pillar):
        errs.append(f"frontmatter: pillar {pillar!r} is not the topic pillar's site path (/{topic}/<slug>/)")
    elif not resolves(pillar, root, live):
        errs.append(f"frontmatter: pillar {pillar} does not resolve to an article")
    brief = str(fm.get("brief") or "").strip()
    if not (brief.startswith("intel/") and brief.endswith(".md")):
        errs.append(f"frontmatter: brief {brief!r} is not an intel/<topic>/brief.md path")
    elif not (root / brief).is_file():
        errs.append(f"frontmatter: brief {brief} not found")
    tools_fm = fm.get("tools") if fm.get("tools") is not None else []
    if not isinstance(tools_fm, list) or not all(isinstance(t, str) and t.strip() for t in tools_fm):
        errs.append("frontmatter: tools must be a list of tool slugs")
        tools_fm = []
    tools_fm = [t.strip() for t in tools_fm]
    for t in tools_fm:
        if not ((root / "content" / "tools" / t / "tool.md").is_file() and (root / "content" / "tools" / t / "tool.html").is_file()):
            errs.append(f"tools: content/tools/{t}/ needs tool.md and tool.html")
    embedded = [s[2] for s in tools]
    if any(not s for s in embedded):
        errs.append("tools: a ```tool fence without a slug (write ```tool <slug>``` on one line)")
    embedded = [s for s in embedded if s]
    if set(embedded) != set(tools_fm):
        errs.append(f"tools: frontmatter lists [{', '.join(tools_fm)}] but the body embeds [{', '.join(embedded)}]")
    m["tools"] = embedded

    # lead photo and body image references
    images = [im for im in (fm.get("images") if isinstance(fm.get("images"), list) else []) if isinstance(im, dict)]
    m["images"] = len(images)
    if not images:
        errs.append("lead photo: images is empty (a lead photo under the title is required; the image step supplies it)")
    else:
        first = str(images[0].get("file") or "")
        if not image_file(root, slug, first):
            errs.append(f"lead photo: content/images/{slug}/{first or '?'} not found (the image step stores it)")
    names = {str(im.get("file") or "") for im in images} | {Path(str(im.get("file") or "")).stem for im in images}
    for ref in IMG_REF_RE.findall(text_and_readers):
        if ref.startswith("http"):
            continue
        name = ref.rsplit("/", 1)[-1]
        if name not in names and Path(name).stem not in names:
            errs.append(f"image reference {name} has no images entry")

    # words, visuals
    words = word_count(segs)
    m["words"] = words
    floor = WORD_FLOOR.get(kind, WORD_FLOOR["spoke"])
    m["words_required"] = floor
    if words < floor:
        errs.append(f"words: {words} ({floor} required for a {kind or 'spoke'})")
    iframes = len(re.findall(r"<iframe\b", text, re.I))
    have, need = max(0, len(images) - 1) + len(figures) + len(tools) + iframes, words // VISUAL_WORDS
    m["visuals"], m["visuals_required"] = have, need
    if have < need:
        errs.append(f"visuals: {have} beyond the lead photo for {words} words ({need} required: one photo, figure, map or tool per {VISUAL_WORDS} words)")

    # layers: glance box, answer, reader blocks, then the sections
    first_h2 = next((i for i, s in enumerate(segs) if s[0] == "text" and H2_RE.search(s[1])), len(segs))
    m["glance_bullets"] = 0
    if len(glance) != 1:
        errs.append(f"glance box: {len(glance)} ```glance fences (exactly one, with {GLANCE_BULLETS[0]} to {GLANCE_BULLETS[1]} bullets)")
    else:
        bullets = [l for l in glance[0][3].split("\n") if re.match(r"^\s*[-*+]\s+\S", l)]
        m["glance_bullets"] = len(bullets)
        if not GLANCE_BULLETS[0] <= len(bullets) <= GLANCE_BULLETS[1]:
            errs.append(f"glance box: {len(bullets)} bullets ({GLANCE_BULLETS[0]} to {GLANCE_BULLETS[1]})")
        if segs.index(glance[0]) > first_h2:
            errs.append("layers: the glance box must come before the first ## heading")
    answer = answer_paragraph(segs)
    n_ans = len(sentences(answer)) if answer else 0
    m["answer_sentences"] = n_ans
    if not answer:
        errs.append("answer: no paragraph between the glance box and the first heading or fence (the answer, 3 sentences or fewer, goes there)")
    elif n_ans > ANSWER_MAX:
        errs.append(f"answer: {n_ans} sentences in the first paragraph ({ANSWER_MAX} or fewer)")
    rneed = READER_FLOOR.get(kind, READER_DEFAULT)
    m["reader_blocks"], m["reader_blocks_required"] = len(readers), rneed
    if len(readers) < rneed:
        errs.append(f"reader blocks: {len(readers)} ```reader fences ({rneed} required for a {kind or 'spoke'})")
    for s in readers:
        title = s[2].strip().strip("\"'").strip()
        if not title:
            errs.append("reader block: a fence without a title (```reader \"If you're <reader>\"```)")
        elif not title.lower().startswith("if you"):
            errs.append(f"reader block title {title!r} should read \"If you're ...\"")
    if readers and segs.index(readers[0]) > first_h2:
        errs.append("layers: the first reader block must come before the first ## heading (the answer, then the reader blocks, then the detailed sections)")

    # detail: tables, sources, the two sections, links
    m["tables"] = count_tables(text_and_readers)
    if m["tables"] < 1:
        errs.append("tables: no Markdown table (at least one required)")
    urls = {str(s.get("url") or "").strip() for s in (fm.get("sources") or []) if isinstance(s, dict) and s.get("url")}
    sneed = SOURCE_FLOOR.get(kind, SOURCE_DEFAULT)
    m["sources"], m["sources_required"] = len(urls), sneed
    if len(urls) < sneed:
        errs.append(f"sources: {len(urls)} cited ({sneed} required for a {kind or 'spoke'})")
    if not MISTAKES_RE.search(text):
        errs.append('sections: no "## Common mistakes" heading')
    faq_n = faq_questions(text)
    m["faq_questions"] = faq_n if faq_n is not None else 0
    if faq_n is None:
        errs.append('sections: no "## FAQ" heading')
    elif faq_n < FAQ_MIN:
        errs.append(f"FAQ: {faq_n} questions ({FAQ_MIN} required, as bold lead-ins or ### headings)")
    internal = {site_path(t) for t in link_targets(body) if t.startswith("/")}
    self_path = f"/{topic}/{slug}/"
    if kind != "pillar":
        m["pillar_link"] = bool(pillar) and pillar in internal
        if pillar and pillar not in internal:
            errs.append(f"links: no link to the pillar {pillar}")
    sibs = {t for t in internal if re.fullmatch(rf"/{re.escape(topic)}/[^/]+/", t) and t not in (self_path, pillar)}
    m["sibling_links"] = len(sibs)
    if len(sibs) < SIBLINGS_MIN:
        errs.append(f"links: {len(sibs)} link(s) to other articles in /{topic}/ ({SIBLINGS_MIN} required besides the pillar)")

    # writing
    prose = prose_text(segs)
    hits = sorted({x.lower() for x in NARRATION_RE.findall(strip_urls(prose).replace("’", "'"))})
    m["narration"] = hits
    if hits:
        errs.append("research narration: " + ", ".join(hits))
    avg, n_sent = avg_sentence(prose)
    m["avg_sentence"], m["sentences"] = round(avg, 1), n_sent
    if avg >= SENTENCE_MAX:
        errs.append(f"sentence length: average {avg:.1f} words over {n_sent} sentences (under {SENTENCE_MAX:.0f} required)")
    return m, errs


def explain_line(m: dict) -> str:
    if "words_required" not in m:
        return "measured: " + " ".join(f"{k}={v}" for k, v in m.items())
    pl = "" if m.get("pillar_link") is None else f" pillar_link={'yes' if m['pillar_link'] else 'no'}"
    return (f"measured: kind={m['kind']} words={m['words']}/{m['words_required']} visuals={m['visuals']}/{m['visuals_required']} "
            f"glance_bullets={m['glance_bullets']} answer_sentences={m['answer_sentences']} reader_blocks={m['reader_blocks']}/{m['reader_blocks_required']} "
            f"tables={m['tables']} sources={m['sources']}/{m['sources_required']} faq_questions={m['faq_questions']}{pl} sibling_links={m['sibling_links']} "
            f"avg_sentence={m['avg_sentence']} ({m['sentences']} sentences) narration={len(m['narration'])} images={m['images']} tools={','.join(m['tools']) or '-'}")


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
    """The words the copy check compares: the text plus the glance and reader fences (figures, tools and code fences are not prose)."""
    segs = split_fences(body)
    text = "\n".join([s[1] for s in segs if s[0] == "text"] + [s[3] for s in segs if s[0] == "fence" and s[1] in ("glance", "reader")])
    return WORD_RE.findall(strip_urls(text).lower().replace("’", "'"))


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
                 live: set[str] | None = None, explain: dict | None = None) -> list[str]:
    """Every check for one article. `explain`, when given a dict, receives the measured values (explain_line prints them)."""
    path, root = Path(path), Path(root)
    fm, body, raw, errs = parse(path)
    errs += check_frontmatter(fm)
    errs += check_text(raw)
    errs += check_links(body, root, live)
    if fm.get("topic") and path.parent.name != fm["topic"]:
        errs.append(f"file is under {path.parent.name}/ but topic is {fm['topic']}")
    pub = list(published or [])
    if str(fm.get("kind") or "").strip() == "rewrite":   # a rewrite overwrites a published v2 file in place; that file's own row is not a duplicate
        mine = path.resolve()
        pub = [p for p in pub if (q.article_for(p[0], root) or Path("/nonexistent")).resolve() != mine]
    errs += check_duplicate(fm, pub)
    if "kind" in fm:
        measures, v3_errs = v3_checks(fm, body, path, root, live)
        errs += v3_errs
    else:
        measures = {"kind": "none (v2 checks only)", "title_chars": len(str(fm.get("title") or "")), "meta_chars": len(str(fm.get("meta") or "")),
                    "words": word_count(split_fences(body)), "sources": len({str(s.get("url")) for s in (fm.get("sources") or []) if isinstance(s, dict) and s.get("url")})}
    if explain is not None:
        explain.update(measures)
    if web is not None and web.enabled:
        live_urls = []
        for u in external_urls(fm, body):
            st = web.status(u)
            if isinstance(st, int) and 200 <= st < 300:
                live_urls.append(u)
            elif st in BLOCKED:   # the page exists but refuses automated clients (bot protection); the reviewer opened it, so it is a warning, not a dead link
                print(f"  warning: source url blocked our checker ({st}), not counted as dead: {u}", file=sys.stderr)
            else:
                errs.append(f"source url returned {st}: {u}")
        errs += check_copy(body, live_urls, web)
    return errs


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(prog="lint.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="*", help="article files (default with --all: every content/articles/*/*.md under --root)")
    ap.add_argument("--root", default=str(REPO), help="repo root (content/, queue/, build/ live here)")
    ap.add_argument("--queue", help="queue csv (default <root>/queue/queue.csv)")
    ap.add_argument("--no-network", action="store_true", help="skip the URL and copied-text checks")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--explain", action="store_true", help="print the measured values (words, visuals, sentences, ...) for each article")
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
        measures: dict = {}
        errs = lint_article(p, root=root, web=web, published=published, explain=measures)
        if errs:
            failed += 1
            print(f"FAIL {p}")
            for e in errs:
                print(f"  - {e}")
        else:
            print(f"OK {p}")
        if a.explain:
            print("  " + explain_line(measures))
    print(f"{len(paths) - failed} ok, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
