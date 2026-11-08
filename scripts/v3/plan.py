#!/usr/bin/env python
"""v3 content and data plan (docs/v3/spec.md, section 4): one opus session plans the whole topic from the brief and the reader map,
then this script turns the plan table into queue rows for Ajay's approval.

    scripts/v3/plan.sh <topic> [--model opus] [--max-turns 80] [--timeout 5400] [--limit-spokes 30] [--approve] [--dry-run]
                               [--intel-dir DIR] [--queue FILE] [--content-dir DIR] [--articles-dir DIR]

The session reads intel/<topic>/brief.md, intel/<topic>/readers.md, the demand rows and the titles of every existing article and
writes intel/<topic>/plan.md (prompts/plan.md): one Markdown table with the columns kind | slug | title | question | primary_query |
type | readers | brief_sections | notes; kinds pillar (exactly one), spoke (10 to 30), reader_guide, tool, dataset, start_here and
rewrite (an article of this topic rewritten in place under its own slug). Then every table row becomes a row in queue/queue.csv:
id q-<topic dir>-NNNN, question = the plan title, primary_query, topic = the topic dir, demand_evidence = the brief path plus any
demand row ids named in the plan, verdict plan, angle "kind=<kind>; slug=<slug>; readers=<a,b>; type=<type>", status proposed.
One queue row per slug and topic, ever: a slug that already has a plan row (proposed, approved, written, published or rejected) is
skipped with the row named (a rejected page is retried by hand: queue.py set-status <id> approved --force), and so is a tool, dataset
or start page already built on disk. A proposed or approved row whose plan line changed by hand (title, readers, type, kind) is
synced from the plan. --limit-spokes N queues the first N spokes only; the rest stay in the plan for a later run. The summary
printed at the end is what Ajay reads. --approve then flips the topic's proposed plan rows to approved: with an existing plan.md it
runs no session (the approval step after the read), and it approves only rows that are in the plan table (plus the rewrite rows
requeue_v2.py made for this topic's live v2 pages); a row Ajay removed from the plan is left proposed and named. --dry-run parses
and prints without touching the queue.

The plan's question, brief_sections and notes columns stay in plan.md, where the write step reads them by slug. Tools, datasets
and start-here pages get queue rows too (the spec queues everything in the plan); their angle kind tells the v3 steps what to
build, and the v2 write.sh must not be run on them. A rewrite can only name an article under this topic's own dir: slugs are
unique across the site (images are stored under content/images/<slug>/), so a planned article whose slug exists under another
topic's dir is dropped with a warning. Log: build/runs/v2/plan-<ts>.log.
"""
from __future__ import annotations

import argparse
import re
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts" / "v3"))
sys.path.insert(0, str(REPO / "scripts" / "v2"))
import brief as B  # noqa: E402
from lib import queue as q, sessions  # noqa: E402

try:   # the article types lint.py accepts (scripts/v2/lint.py TYPES); the same tuple here when lint cannot be imported
    from lint import TYPES as ARTICLE_TYPES  # noqa: E402
except Exception:  # noqa: BLE001
    ARTICLE_TYPES = ("how-to", "decision", "scenario", "comparison", "place", "checklist", "roundup")

KINDS = ("pillar", "spoke", "reader_guide", "tool", "dataset", "start_here", "rewrite")
ARTICLE_KINDS = ("pillar", "spoke", "reader_guide", "rewrite")
TOOL_TYPES = ("calculator", "quiz", "checklist", "timeline")
BUILT_DIRS = {"tool": "tools", "dataset": "datasets", "start_here": "start"}
COLUMNS = ("kind", "slug", "title", "question", "primary_query", "type", "readers", "brief_sections", "notes")
COLUMN_ALIASES = {"primary query": "primary_query", "brief sections": "brief_sections", "reader": "readers", "section": "brief_sections", "sections": "brief_sections", "note": "notes"}
MIN_SPOKES, MAX_SPOKES = 10, 30
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
DEMAND_ID_RE = re.compile(r"\bq-[a-z-]+-\d{4}\b")
ANGLE_SLUG_RE = re.compile(r"\bslug=([a-z0-9-]+)")
READER_RE = re.compile(r"^## Reader: (.+?)\s*$", re.M)
# "Key: transfer-junior", also "**Key:** transfer-junior", "**Key**: x", "Key: `x`" or "- Key: x" (a session's formatting varies)
KEY_RE = re.compile(r"^(?:[-*]\s+)?(?:\*\*)?Key:?(?:\*\*)?:?\s*`?([a-z0-9][a-z0-9-]*)`?\s*$", re.M)
READER_FIELDS = ("Situation", "Questions in their words", "Decisions with numbers", "Timeline", "Mistakes and cost", "Brief facts that matter")


# ------------------------------------------------------------------------------------------ reader map (readers.sh imports these)
def reader_map(text: str) -> list[dict]:
    """The reader map's sections: name, key (the Key: line, else the slugified name) and which of the six fields each has."""
    heads = list(READER_RE.finditer(text))
    out = []
    for i, m in enumerate(heads):
        body = text[m.end(): heads[i + 1].start() if i + 1 < len(heads) else len(text)]
        km = KEY_RE.search(body)
        fields = [f for f in READER_FIELDS if re.search(rf"^###\s+{re.escape(f)}\b", body, re.M | re.I)]
        out.append({"name": m.group(1).strip(), "key": km.group(1) if km else q.slugify(m.group(1), 40), "has_key": bool(km), "fields": fields,
                    "missing": [f for f in READER_FIELDS if f not in fields]})
    return out


def parse_angle(angle: str) -> dict:
    """'kind=spoke; slug=x; readers=a,b; type=decision' -> {'kind': 'spoke', ...} (the same reading as scripts/v3/write.py)."""
    out = {}
    for part in re.split(r"\s*;\s*", angle or ""):
        if "=" in part:
            k, v = part.split("=", 1)
            out[k.strip().lower()] = v.strip()
    return out


# ------------------------------------------------------------------------------------------ the plan table
def _norm_col(c: str) -> str:
    c = re.sub(r"\s+", " ", c.strip().lower().replace("*", "").replace("`", ""))
    return COLUMN_ALIASES.get(c, c.replace(" ", "_"))


def _cells(line: str) -> list[str]:
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|") and not s.endswith("\\|"):
        s = s[:-1]
    return [c.replace("\\|", "|").strip() for c in re.split(r"(?<!\\)\|", s)]


def parse_plan(text: str) -> tuple[list[dict], list[str]]:
    """Rows of the first Markdown table whose header has kind, slug and title; problems for rows that do not fit it."""
    rows, problems, cols, in_table = [], [], [], False
    for i, line in enumerate(text.splitlines(), 1):
        s = line.strip()
        if not s.startswith("|"):
            if in_table:
                break
            continue
        cells = _cells(s)
        if not in_table:
            names = [_norm_col(c) for c in cells]
            if {"kind", "slug", "title"} <= set(names):
                cols, in_table = names, True
            continue
        if all(re.fullmatch(r":?-{2,}:?", c) or not c for c in cells):
            continue
        if len(cells) != len(cols):
            problems.append(f"line {i}: {len(cells)} cells but the header has {len(cols)}; row skipped: {s[:90]}")
            continue
        row = {k: "" for k in COLUMNS}
        row.update(dict(zip(cols, cells)))
        rows.append(row)
    if not in_table:
        problems.append("no Markdown table with the columns kind, slug and title")
    return rows, problems


def plan_check(path: Path) -> list[str]:
    """What makes a written plan unusable (the session's one retry fixes it): no table or no rows, or not exactly one pillar."""
    if not path.exists():
        return [f"missing {B.rel(path)}"]
    rows, problems = parse_plan(path.read_text(encoding="utf-8"))
    if not rows:
        return problems[:1] or ["the plan table has no rows"]
    pillars = sum(1 for r in rows if r["kind"].strip().lower() == "pillar")
    return [] if pillars == 1 else [f"the plan has {pillars} pillar rows; exactly one is required"]


def existing_files(topic_dir: str, content: Path, articles: Path) -> dict:
    """Slugs already on disk: articles in this topic dir, articles elsewhere (slug -> dir), tools, datasets, start pages."""
    return {"article": {p.stem for p in (articles / topic_dir).glob("*.md")},
            "elsewhere": {p.stem: p.parent.name for p in articles.glob("*/*.md") if p.parent.name != topic_dir},
            "tool": {p.parent.name for p in (content / "tools").glob("*/tool.md")},
            "dataset": {p.stem for p in (content / "datasets").glob("*.md")},
            "start_here": {p.stem: start_topics(p) for p in (content / "start").glob("*.md")}}


def start_topics(page: Path) -> list[str]:
    """The topics a start page already has a path for (its `topics:` list). A start page is one per reader, shared by the topics
    (docs/v3/spec.md §4: start-here paths are additions to /start/<reader>/ pages), so another topic adds its path instead of skipping."""
    try:
        t = q.frontmatter(page).get("topics")
    except Exception:
        return []
    return [str(x).strip() for x in t] if isinstance(t, list) else []


def validate(rows: list[dict], *, reader_keys: set[str], on_disk: dict, limit_spokes: int, topic_dir: str = "") -> tuple[list[dict], list[str], list[str]]:
    """Clean rows (kind fixed up, slugs valid and unique, readers as a list, spokes beyond the limit marked deferred), warnings, and
    errors that stop queueing."""
    out, warnings, errors, spokes = [], [], [], 0

    def norm_slug(r: dict) -> str:
        s = r["slug"].strip().strip("`/").lower()
        return s if SLUG_RE.match(s) and len(s) <= 60 else q.slugify(s or r["title"])

    last = {norm_slug(r): i for i, r in enumerate(rows)}   # a duplicated slug keeps its last row: scripts/v3/write.py reads plan.md the same way
    for i, r in enumerate(rows):
        r = dict(r)
        label = r.get("slug") or r.get("title") or "?"
        kind = r["kind"].strip().lower().replace("-", "_").replace(" ", "_")
        kind = {"reader": "reader_guide", "readerguide": "reader_guide", "starthere": "start_here", "start": "start_here", "data": "dataset"}.get(kind, kind)
        if kind not in KINDS:
            warnings.append(f"{label}: kind {r['kind']!r} is not one of {', '.join(KINDS)}; row dropped")
            continue
        slug = norm_slug(r)
        if slug != r["slug"].strip().strip("`/"):
            warnings.append(f"{label}: slug {r['slug']!r} is not lowercase-hyphen (60 max); using {slug!r}")
        if last[slug] != i:
            warnings.append(f"{slug}: duplicate slug; this earlier row is dropped (the writer reads the last row for a slug; make slugs unique in the plan)")
            continue
        if not r["title"]:
            warnings.append(f"{slug}: no title; row dropped")
            continue
        if len(r["title"]) > 60:
            warnings.append(f"{slug}: title is {len(r['title'])} characters (60 max; the writer shortens it)")
        typ = r["type"].strip().lower()
        if kind in ARTICLE_KINDS and typ not in ARTICLE_TYPES:
            warnings.append(f"{slug}: type {r['type']!r} is not one of {', '.join(ARTICLE_TYPES)} (lint rejects it at publish)")
        if kind == "tool" and typ not in TOOL_TYPES:
            warnings.append(f"{slug}: tool type {r['type']!r} is not one of {', '.join(TOOL_TYPES)}")
        readers = [x.strip() for x in re.split(r"[,;]\s*", r["readers"]) if x.strip()]
        unknown = [x for x in readers if x not in reader_keys]
        if unknown and reader_keys:
            warnings.append(f"{slug}: reader key(s) not in the reader map: {', '.join(unknown)}")
        other = on_disk.get("elsewhere", {}).get(slug)
        if kind == "rewrite" and slug not in on_disk["article"]:
            if other:
                warnings.append(f"{slug}: marked rewrite but the article lives under /{other}/, not /{topic_dir}/; its own topic rewrites it "
                                f"(scripts/v3/requeue_v2.py); row dropped")
                continue
            warnings.append(f"{slug}: marked rewrite but no content/articles/{topic_dir}/ file has this slug; queued as a spoke")
            kind = "spoke"
        elif kind in ARTICLE_KINDS and other and slug not in on_disk["article"]:
            warnings.append(f"{slug}: the slug is taken by /{other}/{slug}/ (slugs are unique across the site; images are stored by slug); pick another slug; row dropped")
            continue
        elif kind in ("spoke", "reader_guide") and slug in on_disk["article"]:
            warnings.append(f"{slug}: an article with this slug exists; queued as a rewrite (overwritten in place)")
            kind = "rewrite"
        elif kind == "pillar" and slug in on_disk["article"]:
            warnings.append(f"{slug}: the pillar overwrites the existing article with this slug")
        deferred = False
        if kind == "spoke":
            spokes += 1
            if spokes > limit_spokes:
                warnings.append(f"{slug}: spoke {spokes} is beyond --limit-spokes {limit_spokes}; stays in the plan, not queued now")
                deferred = True
        r.update(kind=kind, slug=slug, type=typ, readers=readers, deferred=deferred, demand_ids=sorted(set(DEMAND_ID_RE.findall(f"{r['notes']} {r['question']}"))))
        out.append(r)
    pillars = [r for r in out if r["kind"] == "pillar"]
    if len(pillars) != 1:
        errors.append(f"the plan has {len(pillars)} pillar rows; exactly one is required (fix intel/<topic>/plan.md by hand, then run plan.sh <topic> --approve)")
    if not MIN_SPOKES <= spokes <= MAX_SPOKES:
        warnings.append(f"{spokes} spokes in the plan; the spec expects {MIN_SPOKES} to {MAX_SPOKES}")
    return out, warnings, errors


def queue_row(p: dict, topic_dir: str, brief_path: str) -> dict:
    """The queue row (contract 2) for one planned page."""
    return {"id": "", "question": p["title"], "primary_query": p["primary_query"] or p["question"] or p["title"], "topic": topic_dir,
            "demand_evidence": q.SEP.join([brief_path] + p["demand_ids"]), "top_results": "", "verdict": "plan",
            "angle": f"kind={p['kind']}; slug={p['slug']}; readers={','.join(p['readers'])}; type={p['type']}", "status": "proposed"}


def queue_rows(planned: list[dict], *, topic_dir: str, brief_path: str, existing: list[dict], on_disk: dict) -> tuple[list[dict], list[tuple[str, str]], list[tuple[str, dict]]]:
    """(new rows, (slug, reason) skipped, (id, changed fields) to sync) for the planned pages: one plan row per slug and topic, ever."""
    prior: dict[str, list[dict]] = {}
    for r in existing:
        m = ANGLE_SLUG_RE.search(r["angle"]) if r["topic"] == topic_dir and r["verdict"] == "plan" else None
        if m:
            prior.setdefault(m.group(1), []).append(r)
    new, skipped, updates = [], [], []
    for p in planned:
        if p.get("deferred"):
            skipped.append((p["slug"], "beyond --limit-spokes; stays in the plan, not queued now"))
            continue
        have = prior.get(p["slug"], [])
        if have:
            r = have[-1]
            if r["status"] in ("proposed", "approved"):   # Ajay's hand edits to the plan reach a row nobody has written yet
                want = {k: v for k, v in queue_row(p, topic_dir, brief_path).items() if k in ("question", "primary_query", "angle", "demand_evidence")}
                diff = {k: v for k, v in want.items() if r.get(k) != v}
                if diff:
                    updates.append((r["id"], diff))
            why = (f"rejected as {r['id']}; to retry: worker/.venv/bin/python scripts/v2/lib/queue.py set-status {r['id']} approved --force" if r["status"] == "rejected"
                   else f"already {'published' if r['status'] == 'published' else 'queued'} as {r['id']} ({r['status']})")
            skipped.append((p["slug"], why))
            continue
        if p["kind"] in BUILT_DIRS and p["slug"] in on_disk[p["kind"]]:
            if p["kind"] != "start_here":
                skipped.append((p["slug"], f"already built under content/{BUILT_DIRS[p['kind']]}/"))
                continue
            if topic_dir in on_disk["start_here"][p["slug"]]:
                skipped.append((p["slug"], f"content/start/{p['slug']}.md already has a {topic_dir} path"))
                continue
            p = {**p, "notes": (p.get("notes") or "").strip() + f" Extends the existing content/start/{p['slug']}.md (written for another topic) with this topic's path."}
        new.append(queue_row(p, topic_dir, brief_path))
    return new, skipped, updates


def existing_articles_text(topic_dir: str, queue_path: Path, articles: Path) -> str:
    status = {r["id"]: r["status"] for r in q.read(queue_path)}
    lines = []
    for p in sorted(articles.glob("*/*.md")):
        fm = q.frontmatter(p)
        lines.append((0 if p.parent.name == topic_dir else 1, f"  /{p.parent.name}/{p.stem}/ | {fm.get('title') or p.stem} | {status.get(str(fm.get('queue_id') or ''), 'no queue row')}"))
    return "\n".join(l for _, l in sorted(lines)) or "  (none yet)"


def summary(planned: list[dict], warnings: list[str], errors: list[str], plan_path: Path, title: str, log=print) -> None:
    by = {k: [r for r in planned if r["kind"] == k] for k in KINDS}
    log(f"PLAN for {title}: {B.rel(plan_path)}, {len(planned)} rows: " + ", ".join(f"{len(v)} {k}" for k, v in by.items() if v))
    for k in KINDS:
        for r in by[k]:
            log(f"  {k:<12} {r['slug']:<52} {r['title'][:60]:<60} readers: {','.join(r['readers']) or '-'}" + ("  (not queued now: beyond --limit-spokes)" if r.get("deferred") else ""))
    for w in warnings:
        log(f"  warning: {w}")
    for e in errors:
        log(f"  ERROR: {e}")


# ------------------------------------------------------------------------------------------ the step
def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(prog="plan.sh", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("topic")
    ap.add_argument("--model", default="opus")
    ap.add_argument("--max-turns", type=int, default=80)
    ap.add_argument("--timeout", type=int, default=5400)
    ap.add_argument("--limit-spokes", type=int, default=MAX_SPOKES, help="queue at most N spokes (the plan may list more)")
    ap.add_argument("--approve", action="store_true", help="flip this topic's proposed plan rows to approved (no session when plan.md exists)")
    ap.add_argument("--dry-run", action="store_true", help="parse an existing plan and print the rows; the queue is not touched")
    ap.add_argument("--sync", action="store_true", help="queue the rows of the existing plan.md (new rows as proposed, edits synced); no session")
    ap.add_argument("--intel-dir", default=None)
    ap.add_argument("--queue", default=None, help="queue csv (default queue/queue.csv)")
    ap.add_argument("--content-dir", default=None, help="content folder (default content/; tests)")
    ap.add_argument("--articles-dir", default=None, help="articles folder (default <content>/articles; tests)")
    a = ap.parse_args(argv)
    t = B.topic_or_exit(a.topic)
    for topic in B.topics().values():   # queue.py's topic list predates topics.yml (dining, transfer, health)
        if topic["dir"] not in q.TOPICS:
            q.TOPICS.append(topic["dir"])
    tdir = B.intel_root(a.intel_dir) / a.topic
    brief, readers, plan, demand = tdir / "brief.md", tdir / "readers.md", tdir / "plan.md", tdir / "raw" / "demand-questions.md"
    queue_path = Path(a.queue).resolve() if a.queue else q.QUEUE
    content = Path(a.content_dir).resolve() if a.content_dir else REPO / "content"
    articles = Path(a.articles_dir).resolve() if a.articles_dir else content / "articles"
    log, log_path = sessions.open_log("plan")
    sessions.clear_stop(log)
    today = date.today().isoformat()
    reader_keys = {r["key"]: r["name"] for r in reader_map(readers.read_text(encoding="utf-8"))} if readers.exists() else {}
    run_session = not a.dry_run and not (a.sync and plan.exists()) and not (a.approve and plan.exists())
    if run_session:
        for p, step in ((brief, "brief.sh"), (readers, "readers.sh")):
            if not p.exists():
                log(f"{B.rel(p)} is missing; run scripts/v3/{step} {a.topic} first")
                return 2
        template = (B.PROMPTS / "plan.md").read_text(encoding="utf-8")
        prior_rows = [r for r in q.read(queue_path) if r["topic"] == t["dir"] and r["verdict"] == "plan" and r["status"] != "rejected"]
        queued = sorted({m.group(1) for r in prior_rows for m in [ANGLE_SLUG_RE.search(r["angle"])] if m})
        if plan.exists():
            n_rows = len(parse_plan(plan.read_text(encoding="utf-8"))[0])
            status = (f"{B.rel(plan)} exists with {n_rows} rows. Read it first and revise it: keep every row whose slug is already queued "
                      f"({', '.join(queued) or 'none yet'}) with its slug unchanged, add what is missing, merge overlaps, and rewrite the file in full.")
        else:
            status = "No plan exists yet." + (f" Slugs already queued for this topic from an earlier plan: {', '.join(queued)}." if queued else "")
        prompt = sessions.fill(template, today=today, topic_title=t["title"], topic_scope=t["scope"], topic_slug=a.topic, topic_dir=t["dir"],
                               brief_path=B.rel(brief), readers_path=B.rel(readers), reader_keys=", ".join(f"{k} ({v})" for k, v in reader_keys.items()) or "(none found in the reader map)",
                               demand_path=B.rel(demand) if demand.exists() else "(none exported)", existing_articles=existing_articles_text(t["dir"], queue_path, articles),
                               out_path=B.rel(plan), status=status, min_spokes=min(MIN_SPOKES, a.limit_spokes), max_spokes=min(MAX_SPOKES, a.limit_spokes))
        sessions.save_prompt("plan", a.topic, prompt)
        log(f"plan for {t['title']} ({a.topic}): one {a.model} session, {a.max_turns} turns; {len(reader_keys)} reader keys; brief {B.words(brief.read_text(encoding='utf-8')):,} words")
        tools = ",".join(["Read", "Grep", "Glob", B.tool_rule("Write", tdir)])
        job = {"id": f"{a.topic}:plan", "prompt": prompt, "expect": [str(plan)], "check": lambda: plan_check(plan)}
        sessions.run_jobs([job], workers=1, label="plan", model=a.model, max_turns=a.max_turns, allowed_tools=tools, timeout_s=a.timeout, log=log)
    if not plan.exists():
        log(f"no plan at {B.rel(plan)}; nothing queued")
        return 1
    rows, problems = parse_plan(plan.read_text(encoding="utf-8"))
    on_disk = existing_files(t["dir"], content, articles)
    planned, warnings, errors = validate(rows, reader_keys=set(reader_keys), on_disk=on_disk, limit_spokes=a.limit_spokes, topic_dir=t["dir"])
    summary(planned, problems + warnings, errors, plan, t["title"], log)
    # the approval copy for Ajay (docs/v3 catch-up, step 6): reports/plan-<topic>.md = counts, how to approve, the plan table
    from collections import Counter
    kinds = Counter(r["kind"] for r in planned)
    report = REPO / "reports" / f"plan-{a.topic}.md"
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text("\n".join([
        f"# Plan for approval: {t['title']} ({a.topic})",
        "",
        f"Source: intel/{a.topic}/plan.md, built from intel/{a.topic}/brief.md and readers.md on {date.today().isoformat()}.",
        "Counts: " + ", ".join(f"{k} {v}" for k, v in sorted(kinds.items())) + f"; {len(planned)} rows queued as status proposed.",
        "",
        f"Approve: `scripts/v3/plan.sh {a.topic} --approve` (flips this topic's proposed plan rows to approved), then start writing with `scripts/v3/run.sh {a.topic}`.",
        "To change the plan first, edit intel/" + a.topic + "/plan.md (add, remove or reword rows), run `scripts/v3/plan.sh " + a.topic + " --sync` to queue the changes without a new session, then approve.",
        "",
        plan.read_text(encoding="utf-8").strip(),
        "",
    ]), encoding="utf-8")
    log(f"approval copy written: {report.relative_to(REPO)}")
    if errors:
        log("plan not queued: fix the errors above in the plan file, then run plan.sh <topic> --approve (no new session)")
        return 1
    new, skipped, updates = queue_rows(planned, topic_dir=t["dir"], brief_path=B.rel(brief), existing=q.read(queue_path), on_disk=on_disk)
    if a.dry_run:
        for r in new:
            log(f"  would queue: {r['question'][:60]:<60} {r['angle']}")
        for rid, diff in updates:
            log(f"  would sync {rid}: {', '.join(diff)}")
        log(f"dry run: {len(new)} row(s) would be added to {B.rel(queue_path)}, {len(updates)} synced; {len(skipped)} skipped")
        return 0
    added = q.append(new, queue_path) if new else []
    for r in added:
        log(f"  + {r['id']} {r['angle']}")
    for rid, diff in updates:
        q.update(rid, queue_path, **diff)
        log(f"  ~ {rid}: synced from the plan ({', '.join(f'{k}={v!r}' for k, v in diff.items())[:200]})")
    for slug, why in skipped:
        log(f"  - {slug}: {why}")
    ids = [r["id"] for r in added]
    log(f"QUEUE {B.rel(queue_path)}: +{len(added)} proposed" + (f" ({ids[0]} to {ids[-1]})" if ids else "") + f", {len(updates)} synced; {len(skipped)} skipped")
    if a.approve:
        in_plan = {p["slug"] for p in planned if not p.get("deferred")}
        pending, left = [], []
        for r in q.read(queue_path):
            if r["topic"] != t["dir"] or r["verdict"] != "plan" or r["status"] != "proposed":
                continue
            ang = parse_angle(r["angle"])
            slug = ang.get("slug", "")
            if slug in in_plan or (ang.get("kind") == "rewrite" and slug in on_disk["article"]):   # the plan's rows, and requeue_v2.py's rewrites
                pending.append(r["id"])
            else:
                left.append((r["id"], slug))
        done = q.approve(pending, queue_path) if pending else []
        if run_session:
            log("note: --approve on a first run approves the plan without a read")
        log(f"APPROVED {len(done)} plan row(s) for {t['dir']}: {', '.join(done) or 'none pending'}; next: scripts/v3/write.sh {a.topic}")
        for rid, slug in left:
            log(f"  left proposed: {rid} ({slug or 'no slug'}) is not in {B.rel(plan)}; add the row back, or reject it: "
                f"worker/.venv/bin/python scripts/v2/lib/queue.py set-status {rid} rejected")
    else:
        log(f"Approve: read {B.rel(plan)}, then run: scripts/v3/plan.sh {a.topic} --approve")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
