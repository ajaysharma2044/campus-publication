#!/usr/bin/env python
"""v3 write step (docs/v3/spec.md §5 and the speed mode): one opus session per planned page writes the draft from the topic brief,
runs the seven editing passes of docs/v2/style.md Part 6 on it, plays three readers from the reader map, fixes once and saves.

    scripts/v3/write.sh <topic> [--workers 8] [--model opus] [--limit N] [--ids a,b] [--kind spoke|pillar|reader_guide|tool|dataset|rewrite]
                        [--fix] [--max-turns 80] [--timeout 3600] [--two-drafts pillar,reader_guide] [--cold-edit-every 10] [--no-images]
                        [--intel-dir DIR] [--queue FILE] [--articles-dir DIR] [--content-dir DIR] [--state-file FILE]
    scripts/v3/write.sh <topic> --count-pending       # approved plan rows this step would take, plus rows in status fix (run.sh stops at 0)
    scripts/v3/write.sh <topic> --restore-rewrites    # a rejected rewrite gets its old page and its old queue row back

Takes the topic's approved plan rows (queue/queue.csv rows whose angle reads "kind=<kind>; slug=<slug>; readers=<a,b>; type=<type>",
contract 2), status -> writing while the sessions run. Per kind:
  spoke, rewrite      one session writes content/articles/<dir>/<slug>.md (contract 3); a rewrite overwrites the live v2 page in place
                      (the original is backed up under build/runs/v2/rewrites/ and restored if the rewrite fails or is rejected).
  pillar, reader_guide two sessions write two drafts (decision-first and timeline-first) under build/runs/v2/drafts/<slug>/, then a
                      fresh session (prompts/pick-best.md) reads both cold as the target reader, picks one, merges what the loser did
                      better and saves the final page. --two-drafts pillar limits this to pillars (speed mode item 7).
  tool                one session writes content/tools/<slug>/tool.md and tool.html (contract 4, prompts/tool.md).
  dataset             one session writes content/datasets/<slug>.md and <slug>.csv (contract 4, prompts/tool.md).
Before an article session the image finder runs (scripts/v2/find_images.py --query "<title>"; when it finds nothing it tries the scene the
plan row names, then the neighborhood or topic); after the session find_images.py --article stores the photos the writer picked.
Afterwards the row is written when the page exists with complete frontmatter (scripts/v2/lint.py missing_keys plus the v3 keys kind,
readers, brief, pillar), else it goes back to approved with the reason in the log. Every 10th finished article (count in
build/runs/v2/v3-counter.json) gets a fresh cold editor session (prompts/cold-edit.md) that writes content/edits/<slug>.md and fixes the
page in place. --fix takes the topic's rows in status fix instead: one revision session with the exact fix lists from
content/reviews/<slug>.json (lint_fixes, fixes) and content/checks/<slug>.json; the row returns to written.
Logs: build/runs/v2/write-<ts>.log (and pick-best-, cold-edit-, write-fix-). Stop cleanly: scripts/v2/stop.sh. A usage limit pauses and
resumes on its own (scripts/v2/lib/sessions.py). CLAUDE_BIN points the sessions at a stub for tests.
"""
from __future__ import annotations

import argparse
import fcntl
import json
import os
import re
import shutil
import subprocess
import sys
import threading
from datetime import date, datetime
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts" / "v2"))
import lint  # noqa: E402
from lib import queue as q, sessions  # noqa: E402

# v3 sessions edit in place (the writer's seven passes, the checker's fixes, the brief's change log), so Edit is allowed; the
# allowedTools patterns scope it. Bash and the agent tools stay off, as in v2.
sessions.DISALLOWED_TOOLS = "Bash,MultiEdit,NotebookEdit,Agent,Task"

PROMPTS = REPO / "scripts" / "v3" / "prompts"
FIND_IMAGES = REPO / "scripts" / "v2" / "find_images.py"
BEST_DIR = REPO / "docs" / "v3" / "best"
HANDLED = ("spoke", "pillar", "reader_guide", "tool", "dataset", "rewrite")
ARTICLE_KINDS = ("spoke", "pillar", "reader_guide", "rewrite")
# publish floors (docs/v3/spec.md "Publish requirements"): words, sources, reader blocks; a rewrite follows the spoke floors
FLOORS = {"spoke": (1200, 8, 2), "pillar": (3000, 20, 4), "reader_guide": (1500, 8, 4), "rewrite": (1200, 8, 2)}
V3_KEYS = ("kind", "readers", "brief")   # plus pillar (except on the pillar itself); tools may be an empty list
TOOL_KEYS = ("title", "meta", "topic", "updated", "numbers_as_of", "sources", "brief")
DATASET_KEYS = ("title", "meta", "topic", "updated", "as_of", "sample_size", "method", "sources")
ORGANIZATIONS = {
    "decision": "DECISION-FIRST: open with the decisions this reader faces, biggest first (where, when, how much, with whom), and give the answer "
                "for each situation before any background. Timelines and process steps come inside the decision they serve.",
    "timeline": "TIMELINE-FIRST: organize by when things happen for this reader (now, the month before, the week of, after), each stage with its "
                "numbers, decisions and mistakes, so the reader can find today's stage and act. Comparisons and costs live inside the stage "
                "where the reader needs them.",
}
PLACES = ("Collegetown", "Fall Creek", "Downtown Ithaca", "Ithaca Commons", "Northside", "South Hill", "East Hill", "West Hill", "Cayuga Heights",
          "Lansing", "Cornell campus", "Ho Plaza", "Arts Quad", "West Campus", "North Campus", "TCAT bus", "Ithaca Tompkins International Airport",
          "Cayuga Lake", "Ithaca Falls", "Cascadilla Gorge", "Stewart Avenue", "College Avenue", "Dryden Road", "Eddy Street", "Linden Avenue")
WRITER_TOOLS = "Read,Grep,Glob,WebFetch,WebSearch,Write(content/**),Write(build/runs/v2/drafts/**),Edit(content/**),Edit(intel/**)"
PICK_TOOLS = "Read,Grep,Glob,Write(content/**),Edit(content/**)"
COLD_TOOLS = "Read,Grep,Glob,Write(content/edits/**),Edit(content/**)"
TODAY = date.today().isoformat()


# ------------------------------------------------------------------------------------------ topics, plan, queue rows
def topics() -> list[dict]:
    return yaml.safe_load((REPO / "scripts/v3/topics.yml").read_text(encoding="utf-8"))


def resolve_topic(arg: str) -> dict:
    """The topic by slug (off-campus-housing), or by its content dir (housing) when that is unambiguous."""
    ts = topics()
    for t in ts:
        if t["slug"] == arg:
            return t
    hits = [t for t in ts if t["dir"] == arg]
    if len(hits) == 1:
        return hits[0]
    raise SystemExit(f"unknown topic {arg!r}; slugs: {', '.join(t['slug'] for t in ts)}")


def parse_angle(angle: str) -> dict:
    """'kind=spoke; slug=x; readers=a,b; type=decision' -> {'kind': 'spoke', ...} (keys lowercased, values stripped)."""
    out = {}
    for part in re.split(r"\s*;\s*", angle or ""):
        if "=" in part:
            k, v = part.split("=", 1)
            out[k.strip().lower()] = v.strip()
    return out


def read_plan(path: Path) -> dict[str, dict]:
    """intel/<topic>/plan.md's table (kind | slug | title | question | primary_query | type | readers | brief_sections | notes) by slug."""
    if not path.exists():
        return {}
    rows, header = {}, None
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip().startswith("|"):
            header = header if header else None
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if header is None:
            if "slug" in [c.lower() for c in cells] and "kind" in [c.lower() for c in cells]:
                header = [c.lower().replace(" ", "_") for c in cells]
            continue
        if set("".join(cells)) <= set("-: "):
            continue
        row = {header[i]: cells[i] if i < len(cells) else "" for i in range(len(header))}
        if row.get("slug"):
            rows[row["slug"]] = row
    return rows


def slugify_reader(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def tokens(text: str) -> set[str]:
    stop = {"the", "a", "an", "and", "or", "for", "to", "in", "of", "at", "on", "how", "what", "when", "where", "is", "it", "vs", "your", "you"}
    return {w for w in re.findall(r"[a-z0-9]+", (text or "").lower()) if w not in stop}


def best_pages(title: str, n: int = 3) -> str:
    """The n pages in docs/v3/best/ whose titles share the most words with this one (the folder may be empty)."""
    pages = []
    for p in sorted(BEST_DIR.glob("*.md")):
        fm = q.frontmatter(p)
        t = str(fm.get("title") or "")
        if not t:
            m = re.search(r"^#\s+(.+)$", p.read_text(encoding="utf-8"), re.M)
            t = m.group(1).strip() if m else p.stem.replace("-", " ")
        mine, theirs = tokens(title), tokens(t)
        score = len(mine & theirs) / len(mine | theirs) if mine | theirs else 0.0
        pages.append((score, str(p.relative_to(REPO)), t))
    pages.sort(key=lambda x: (-x[0], x[1]))
    top = pages[:n]
    return "\n".join(f"  - {path} ({t})" for _, path, t in top) if top else "  (none yet: docs/v3/best/ is empty; docs/v2/exemplar.md is the bar)"


def article_queue_id(path: Path) -> str:
    return str(q.frontmatter(path).get("queue_id") or "")


def find_article(qid: str, articles_dir: Path) -> Path | None:
    for p in sorted(articles_dir.glob("*/*.md")):
        if article_queue_id(p) == qid:
            return p
    return None


def rel(p: Path | str) -> str:
    p = Path(p)
    try:
        return str(p.resolve().relative_to(REPO))
    except ValueError:
        return str(p)


def page_stats(path: Path) -> str:
    """One diagnostic line (not a gate): words, reader blocks, tables, sources, FAQ questions, glance box, images."""
    fm, body, _, errs = lint.parse(path)
    if errs:
        return errs[0]
    text = re.sub(r"```.*?```", " ", body, flags=re.S)
    words = len(re.findall(r"\w+", text))
    readers = len(re.findall(r"^```reader\b", body, re.M))
    tables = len(re.findall(r"^\|[-:| ]+\|\s*$", body, re.M))
    faq_m = re.search(r"^##\s+FAQ.*?$(.*?)(?=^##\s|\Z)", body, re.M | re.S)
    faq = len(re.findall(r"^\*\*.+?\*\*", faq_m.group(1), re.M)) if faq_m else 0
    glance = "yes" if re.search(r"^```glance", body, re.M) else "NO"
    sents = [s for s in re.split(r"(?<=[.!?])\s+", re.sub(r"\s+", " ", text)) if s.strip()]
    avg = sum(len(re.findall(r"\w+", s)) for s in sents) / len(sents) if sents else 0
    return (f"{words} words, {readers} reader blocks, {tables} tables, {len(fm.get('sources') or [])} sources, {faq} FAQ questions, glance {glance}, "
            f"{len(fm.get('images') or [])} images, {avg:.1f} words/sentence, {'mistakes' if re.search(r'^##\s+Common mistakes', body, re.M) else 'NO mistakes section'}")


# ------------------------------------------------------------------------------------------ the counter (every 10th article)
def counter_bump(state: Path) -> int:
    """Count a finished article; returns the new count. Locked across threads and processes."""
    state.parent.mkdir(parents=True, exist_ok=True)
    with state.with_suffix(".lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        try:
            d = json.loads(state.read_text(encoding="utf-8")) if state.exists() else {}
        except ValueError:
            d = {}
        d["finished"] = int(d.get("finished") or 0) + 1
        d["updated"] = datetime.now().isoformat(timespec="seconds")
        state.write_text(json.dumps(d, indent=1), encoding="utf-8")
        return d["finished"]


def counter_note_cold_edit(state: Path, slug: str) -> None:
    with state.with_suffix(".lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        d = json.loads(state.read_text(encoding="utf-8")) if state.exists() else {}
        d.setdefault("cold_edits", []).append({"slug": slug, "at": datetime.now().isoformat(timespec="seconds")})
        state.write_text(json.dumps(d, indent=1), encoding="utf-8")


# ------------------------------------------------------------------------------------------ rewrites: backup, retire, restore
def rewrite_sidecar(backups: Path, topic_dir: str, slug: str) -> Path:
    return backups / f"{topic_dir}--{slug}.json"


def backup_rewrite(art: Path, new_id: str, paths, topic_dir: str, queue_path: Path, log) -> dict | None:
    """Before a rewrite session: copy the live page aside, remember its queue row, and move the old review and check files out of the
    way so publish.sh cannot publish the new text on a stale verdict. Returns the sidecar dict (None when there is no page to back up)."""
    if not art.exists():
        return None
    side = rewrite_sidecar(paths.backups, topic_dir, art.stem)
    if side.exists():
        d = json.loads(side.read_text(encoding="utf-8"))
        if not d.get("restored") and d.get("new_id") == new_id and Path(d["backup"]).exists():
            return d    # a retry of the same rewrite keeps the original backup
    paths.backups.mkdir(parents=True, exist_ok=True)
    backup = paths.backups / f"{topic_dir}--{art.stem}.orig.md"
    shutil.copy2(art, backup)
    old_id = article_queue_id(art)
    old_status = ""
    for r in q.read(queue_path):
        if r["id"] == old_id:
            old_status = r["status"]
    moved = {}
    for kind, folder, suffixes in (("reviews", paths.reviews, (".json", ".prev.json")), ("checks", paths.checks, (".json", ".prev.json"))):
        for suf in suffixes:
            f = folder / f"{art.stem}{suf}"
            if f.exists():
                dest = folder / f"{art.stem}{suf.replace('.json', '.v2.json')}"
                f.replace(dest)
                moved[str(f)] = str(dest)
    d = {"slug": art.stem, "dir": topic_dir, "article": str(art), "backup": str(backup), "old_id": old_id, "old_status": old_status, "new_id": new_id,
         "moved": moved, "restored": False, "retired": False, "at": datetime.now().isoformat(timespec="seconds")}
    side.write_text(json.dumps(d, indent=1), encoding="utf-8")
    log(f"[{new_id}] rewrite: backed up {rel(art)} (row {old_id or 'none'}, {old_status or 'no row'}) to {rel(backup)}")
    return d


def retire_old_row(side: dict, queue_path: Path, log) -> None:
    """The rewritten page now carries the new row's queue_id, so the old row maps to no file and would trip the publish lint's
    near-duplicate check; it is retired (status rejected, a note in its angle) and brought back only if the rewrite is rejected."""
    old = side.get("old_id")
    if not old or old == side["new_id"] or side.get("retired"):
        return
    try:
        row = q.get(old, queue_path)
    except KeyError:
        return
    if row["status"] in ("rejected", "owned"):
        return
    q.set_status(old, "rejected", queue_path, force=True)
    q.update(old, queue_path, angle=(row["angle"] + "; " if row["angle"] else "") + f"superseded by {side['new_id']} (rewritten in place, v3)")
    side["retired"] = True
    side_path = rewrite_sidecar(Path(side["backup"]).parent, side["dir"], side["slug"])
    side_path.write_text(json.dumps(side, indent=1), encoding="utf-8")
    log(f"[{side['new_id']}] rewrite: old row {old} retired ({row['status']} -> rejected, superseded)")


def restore_rewrite(side: dict, queue_path: Path, log) -> None:
    """The rewrite failed or was rejected: the original page, its review and check files and its queue row come back."""
    if side.get("restored"):
        return
    backup, art = Path(side["backup"]), Path(side["article"])
    if backup.exists():
        shutil.copy2(backup, art)
    for new_path in (Path(side["article"]).parent.parent.parent / "reviews" / f"{side['slug']}.json",):
        pass
    for orig, moved in (side.get("moved") or {}).items():
        if Path(moved).exists():
            Path(orig).unlink(missing_ok=True)
            Path(moved).replace(Path(orig))
    old = side.get("old_id")
    if old and old != side["new_id"] and side.get("old_status"):
        try:
            q.set_status(old, side["old_status"], queue_path, force=True)
        except KeyError:
            pass
    side["restored"] = True
    side_path = rewrite_sidecar(backup.parent, side["dir"], side["slug"])
    side_path.write_text(json.dumps(side, indent=1), encoding="utf-8")
    log(f"[{side['new_id']}] rewrite undone: {rel(art)} restored from backup; row {old or 'none'} back to {side.get('old_status') or 'n/a'}")


def restore_rejected_rewrites(topic_dir: str, paths, queue_path: Path, log) -> int:
    """--restore-rewrites (run.sh after publish.sh): every rewrite whose new row ended up rejected gets the old page back."""
    n = 0
    status = {r["id"]: r["status"] for r in q.read(queue_path)}
    for side_path in sorted(paths.backups.glob(f"{topic_dir}--*.json")):
        side = json.loads(side_path.read_text(encoding="utf-8"))
        if side.get("restored") or status.get(side.get("new_id")) != "rejected":
            continue
        restore_rewrite(side, queue_path, log)
        n += 1
    return n


# ------------------------------------------------------------------------------------------ paths
class Paths:
    def __init__(self, a, topic: dict):
        self.intel = Path(a.intel_dir).resolve() if a.intel_dir else REPO / "intel"
        self.topic_intel = self.intel / topic["slug"]
        self.brief, self.readers, self.plan = self.topic_intel / "brief.md", self.topic_intel / "readers.md", self.topic_intel / "plan.md"
        self.content = Path(a.content_dir).resolve() if a.content_dir else REPO / "content"
        self.articles = Path(a.articles_dir).resolve() if a.articles_dir else self.content / "articles"
        self.tools, self.datasets = self.content / "tools", self.content / "datasets"
        self.checks, self.reviews, self.edits = self.content / "checks", self.content / "reviews", self.content / "edits"
        self.images = self.content / "images"
        self.candidates = self.images / "candidates"
        self.queue = Path(a.queue).resolve() if a.queue else q.QUEUE
        self.state = Path(a.state_file).resolve() if a.state_file else sessions.RUNS / "v3-counter.json"
        self.drafts = sessions.RUNS / "drafts"
        self.backups = sessions.RUNS / "rewrites"


# ------------------------------------------------------------------------------------------ the step
def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(prog="write.sh", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("topic", help="topic slug from scripts/v3/topics.yml (or its content dir)")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--model", default="opus")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--ids", default="")
    ap.add_argument("--kind", choices=HANDLED)
    ap.add_argument("--fix", action="store_true", help="revise the topic's rows in status fix instead of writing approved rows")
    ap.add_argument("--max-turns", type=int, default=80)
    ap.add_argument("--timeout", type=int, default=3600)
    ap.add_argument("--two-drafts", default="pillar,reader_guide", help="kinds that get two drafts and a pick-best session (speed mode: pillar)")
    ap.add_argument("--cold-edit-every", type=int, default=10, help="a fresh cold editor reads every Nth finished article (0 = never)")
    ap.add_argument("--cold-edit", action="store_true", help="cold-edit every article finished in this run (tests, or a suspect batch)")
    ap.add_argument("--no-images", action="store_true", help="skip the image finder (tests)")
    ap.add_argument("--intel-dir")
    ap.add_argument("--queue")
    ap.add_argument("--articles-dir")
    ap.add_argument("--content-dir")
    ap.add_argument("--state-file")
    ap.add_argument("--count-pending", action="store_true")
    ap.add_argument("--restore-rewrites", action="store_true")
    a = ap.parse_args(argv)

    topic = resolve_topic(a.topic)
    tdir = topic["dir"]
    P = Paths(a, topic)
    two_draft_kinds = {k.strip() for k in a.two_drafts.split(",") if k.strip()}

    def plan_rows_for(status: str) -> list[dict]:
        out = []
        for r in q.by_status(status, path=P.queue):
            if r["topic"] != tdir:
                continue
            ang = parse_angle(r["angle"])
            if status == "approved" and ang.get("kind") not in HANDLED:
                continue   # a v2 row (no plan angle) or a start_here row: not this step's
            out.append(r)
        return out

    if a.count_pending:
        print(len(plan_rows_for("approved")) + len(plan_rows_for("fix")))
        return 0
    if a.restore_rewrites:
        log, _ = sessions.open_log("write-restore")
        n = restore_rejected_rewrites(tdir, P, P.queue, log)
        log(f"restored {n} rejected rewrite(s) for {tdir}")
        return 0

    step = "write-fix" if a.fix else "write"
    want = "fix" if a.fix else "approved"
    log, log_path = sessions.open_log(step)
    sessions.clear_stop(log)
    rows = plan_rows_for(want)
    if a.ids:
        ids = [i.strip() for i in a.ids.split(",") if i.strip()]
        have = {r["id"] for r in rows}
        for i in ids:
            if i not in have:
                log(f"{i}: not an approved plan row of {tdir} in status {want}; skipped")
        rows = [r for r in rows if r["id"] in ids]
    if a.kind:
        rows = [r for r in rows if parse_angle(r["angle"]).get("kind") == a.kind]
    # pillars first, then reader guides, so sibling links to the pillar resolve by the time spokes publish
    order = {"pillar": 0, "reader_guide": 1, "spoke": 2, "rewrite": 3, "tool": 4, "dataset": 5}
    rows.sort(key=lambda r: (order.get(parse_angle(r["angle"]).get("kind", ""), 9), r["id"]))
    if a.limit:
        rows = rows[: a.limit]
    if not rows:
        log(f"nothing to do: no plan rows of {tdir} in status {want}")
        return 0
    for p in (P.brief, P.readers):
        if not p.exists():
            log(f"warning: {rel(p)} is missing; the sessions cannot work from the brief (run brief.sh and readers.sh first)")
    plan = read_plan(P.plan)
    if not plan:
        log(f"note: {rel(P.plan)} missing or has no table; sessions work from the queue rows alone")

    queue_status = {r["id"]: r["status"] for r in q.read(P.queue)}
    existing_lines, existing_slugs = [], set()
    for p in sorted((P.articles / tdir).glob("*.md")):
        fm = q.frontmatter(p)
        if queue_status.get(str(fm.get("queue_id") or ""), "") == "rejected":
            continue
        existing_slugs.add(p.stem)
        existing_lines.append(f"  /{tdir}/{p.stem}/ | {fm.get('title') or p.stem}" + (f" ({fm.get('kind')})" if fm.get("kind") else ""))
    planned_lines = [f"  /{tdir}/{s}/ | {r.get('title') or s} ({r.get('kind')})" for s, r in plan.items()
                     if r.get("kind") in ("pillar", "spoke", "reader_guide") and s not in existing_slugs]
    pillar_slug = next((s for s, r in plan.items() if r.get("kind") == "pillar"), "")
    if not pillar_slug:
        for p in sorted((P.articles / tdir).glob("*.md")):
            if q.frontmatter(p).get("kind") == "pillar":
                pillar_slug = p.stem
    for r in rows:   # a pillar row in this run names the pillar even when the plan table is missing
        ang = parse_angle(r["angle"])
        if ang.get("kind") == "pillar" and ang.get("slug"):
            pillar_slug = pillar_slug or ang["slug"]
    pillar_path = f"/{tdir}/{pillar_slug}/" if pillar_slug else ""
    built_tools = sorted(p.parent.name for p in P.tools.glob("*/tool.md"))
    planned_tools = [s for s, r in plan.items() if r.get("kind") == "tool" and s not in built_tools]
    tools_available = (", ".join(built_tools) if built_tools else "(no tool is built yet)") + (f"; planned, not built yet (prefer built ones): {', '.join(planned_tools)}" if planned_tools else "")
    reader_names = re.findall(r"^##\s+Reader:\s*(.+?)\s*$", P.readers.read_text(encoding="utf-8"), re.M) if P.readers.exists() else []

    templates = {name: (PROMPTS / f"{name}.md").read_text(encoding="utf-8") for name in ("write", "write-pillar", "pick-best", "cold-edit", "tool")}
    lock = threading.Lock()
    images_done: set[str] = set()
    cold_edit_queue: list[dict] = []
    stats = {"written": 0, "failed": 0}

    def revision_text(slug: str) -> str:
        if not a.fix:
            return "None: this is the first draft."
        lines = ["This is the one revision round. Read the current page, apply exactly these fixes, keep everything else as it is, then save the file."]
        rev = P.reviews / f"{slug}.json"
        if rev.exists():
            try:
                d = json.loads(rev.read_text(encoding="utf-8"))
            except ValueError:
                d = {}
            if d.get("lint_fixes"):
                lines += ["Publish checks (code) failed on these points; fix each exactly and change nothing else:"] + [f"- {f}" for f in d["lint_fixes"]]
            if d.get("fixes"):
                lines += ["Fixes from the fact check:"] + [f"- {f}" for f in d["fixes"]]
        chk = P.checks / f"{slug}.json"
        if chk.exists():
            try:
                d = json.loads(chk.read_text(encoding="utf-8"))
            except ValueError:
                d = {}
            if d.get("fixes"):
                lines += ["Fixes the checker could not apply itself:"] + [f"- {f}" for f in d["fixes"]]
            wrong = [c for c in d.get("checked") or [] if c.get("status") not in ("ok", "fixed", "unverifiable")]
            if wrong:
                lines += ["Facts the checker marked wrong:"] + [f"- {c.get('claim')} ({c.get('source_url')}): {c.get('note')}" for c in wrong]
        if len(lines) == 1:
            lines.append("No fix list was found; re-check every hard fact against the brief and its source, and re-run the Part 6 passes.")
        return "\n".join(lines)

    def context(r: dict) -> dict:
        ang = parse_angle(r["angle"])
        kind = ang.get("kind", "spoke")
        slug = ang.get("slug") or q.slugify(r["primary_query"] or r["question"])
        prow = plan.get(slug, {})
        readers_raw = ang.get("readers") or prow.get("readers") or ""
        readers = [x.strip() for x in re.split(r"[,/]", readers_raw) if x.strip()]
        ptype = ang.get("type") or prow.get("type") or "how-to"
        if ptype not in lint.TYPES:
            ptype = "how-to"
        ctx = {"row": r, "id": r["id"], "kind": kind, "slug": slug, "title": prow.get("title") or r["question"], "question": prow.get("question") or r["question"],
               "primary_query": r["primary_query"] or prow.get("primary_query") or r["question"], "type": ptype, "readers": readers,
               "brief_sections": prow.get("brief_sections") or "1, 2, 3 and whichever of 4 to 10 the page needs", "notes": prow.get("notes") or "(none)",
               "want": want}
        if kind == "tool":
            ctx["page"] = P.tools / slug / "tool.md"
            ctx["files"] = [ctx["page"], P.tools / slug / "tool.html"]
        elif kind == "dataset":
            ctx["page"] = P.datasets / f"{slug}.md"
            ctx["files"] = [ctx["page"], P.datasets / f"{slug}.csv"]
        else:
            ctx["page"] = P.articles / tdir / f"{slug}.md"
            ctx["files"] = [ctx["page"]]
        ctx["cand"] = P.candidates / f"{r['id']}.json"
        return ctx

    def common_fill(ctx: dict) -> dict:
        kind = ctx["kind"]
        floors = FLOORS.get(kind, FLOORS["spoke"])
        existing = [l for l in existing_lines if f"/{tdir}/{ctx['slug']}/ " not in l] or ["  (none yet)"]
        planned = [l for l in planned_lines if f"/{tdir}/{ctx['slug']}/ " not in l] or ["  (none)"]
        fm_kind = "rewrite" if kind == "rewrite" else kind
        return dict(today=TODAY, id=ctx["id"], kind=kind, fm_kind=fm_kind, slug=ctx["slug"], title=ctx["title"], question=ctx["question"],
                    primary_query=ctx["primary_query"], type=ctx["type"], topic_dir=tdir, topic_title=topic["title"],
                    readers=", ".join(ctx["readers"]) or "(not planned: pick 2 to 4 from the reader map whose answer differs most)",
                    readers_yaml=", ".join(slugify_reader(x) for x in ctx["readers"]) or "reader-one, reader-two",
                    reader_names=", ".join(reader_names) or "(readers.md is missing)", brief_sections=ctx["brief_sections"], notes=ctx["notes"],
                    brief_path=rel(P.brief), readers_path=rel(P.readers), plan_path=rel(P.plan), pillar_path=pillar_path or "",
                    best_pages=best_pages(ctx["title"]), existing_articles="\n".join(existing), planned_articles="\n".join(planned),
                    tools_available=tools_available, word_floor=f"{floors[0]:,}", source_floor=str(floors[1]), reader_floor=str(floors[2]),
                    revision=revision_text(ctx["slug"]), candidates_path=rel(ctx["cand"]) if not a.no_images else "(the image finder was skipped for this run)")

    # ---------------------------------------------------------------------------------- images
    def scene_hints(ctx: dict) -> list[str]:
        hints = []
        m = re.search(r"(?:image|scene|photo)s?\s*:\s*([^;|]+)", ctx["notes"], re.I)
        if m:
            hints.append(m.group(1).strip())
        text = f"{ctx['title']} {ctx['question']} {ctx['notes']}"
        hints += [p for p in PLACES if p.lower() in text.lower()]
        hints.append(topic["title"])
        hints.append("Cornell University campus Ithaca")
        out = []
        for h in hints:
            if h and h not in out:
                out.append(h)
        return out

    def find_images(ctx: dict) -> None:
        """The finder runs once per row: the title first; when that finds nothing, the scene the plan names, then the place or topic."""
        if a.no_images or ctx["kind"] in ("tool", "dataset") or not FIND_IMAGES.exists():
            return
        with lock:
            if ctx["id"] in images_done:
                return
            images_done.add(ctx["id"])
        cand = ctx["cand"]
        cand.parent.mkdir(parents=True, exist_ok=True)

        def run(queries: list[str]) -> int:
            args = []
            for t in queries:
                args += ["--query", t]
            try:
                p = subprocess.run([sys.executable, str(FIND_IMAGES), *args, "--out", str(cand), "--images-dir", str(P.images)], cwd=REPO,
                                   capture_output=True, text=True, timeout=300)
                tail = (p.stdout + p.stderr).strip().splitlines()
                log(f"[{ctx['id']}] find_images {queries[0]!r}: exit {p.returncode}: {tail[-1][:140] if tail else ''}")
                return len(json.loads(cand.read_text(encoding="utf-8"))) if cand.exists() else 0
            except Exception as e:  # noqa: BLE001 - no photo candidates is not a reason to skip the page
                log(f"[{ctx['id']}] find_images failed: {type(e).__name__}: {str(e)[:120]}")
                return 0

        if cand.exists():
            try:
                if json.loads(cand.read_text(encoding="utf-8")):
                    return
            except ValueError:
                pass
        if run([ctx["title"]]):
            return
        for hint in scene_hints(ctx):
            if run([hint]):
                log(f"[{ctx['id']}] photos found with the fallback query {hint!r}")
                return
        log(f"[{ctx['id']}] no licensed photo found for the title or any related scene; the page leans on figures and tables")

    def place_images(ctx: dict) -> None:
        """After the session: find_images.py --article downloads the photos the writer picked (matched by credit_url), rewrites the
        frontmatter entries from the API's license data, and logs them in credits.yml; an entry whose file was not stored is dropped."""
        art = ctx["page"]
        fm, body, _, errs = lint.parse(art)
        images = fm.get("images") or []
        if errs or not isinstance(images, list) or not images or a.no_images or not FIND_IMAGES.exists():
            if not errs and not images and ctx["kind"] in ARTICLE_KINDS:
                log(f"[{ctx['id']}] no images in the frontmatter (the publish lint wants a lead photo)")
            return
        try:
            p = subprocess.run([sys.executable, str(FIND_IMAGES), "--article", str(art), "--out", str(ctx["cand"]), "--images-dir", str(P.images)],
                               cwd=REPO, capture_output=True, text=True, timeout=900)
            if p.returncode:
                log(f"[{ctx['id']}] find_images --article exit {p.returncode}: {(p.stderr.strip().splitlines() or [''])[-1][:160]}")
        except Exception as e:  # noqa: BLE001
            log(f"[{ctx['id']}] find_images --article failed: {type(e).__name__}: {str(e)[:160]}")
        fm, body, _, errs = lint.parse(art)
        if errs:
            return
        folder = P.images / art.stem
        keep = [im for im in (fm.get("images") or []) if isinstance(im, dict) and im.get("file") and (folder / str(im["file"])).is_file()]
        dropped = len(fm.get("images") or []) - len(keep)
        if dropped:
            fm["images"] = keep
            art.write_text("---\n" + yaml.safe_dump(fm, sort_keys=False, allow_unicode=True, width=10000) + "---\n" + body, encoding="utf-8")
            log(f"[{ctx['id']}] {dropped} image entr{'y' if dropped == 1 else 'ies'} not stored (credit_url not a candidate, or download failed); dropped")
        log(f"[{ctx['id']}] images: {len(keep)} under {rel(folder)}/")

    # ---------------------------------------------------------------------------------- completeness
    def page_problems(ctx: dict, path: Path | None = None) -> list[str]:
        path = path or ctx["page"]
        kind = ctx["kind"]
        if not path.exists():
            return [f"missing {rel(path)}"]
        fm = q.frontmatter(path)
        if not fm:
            return ["no parseable frontmatter"]
        if str(fm.get("queue_id", "")) != ctx["id"]:
            return [f"queue_id is {fm.get('queue_id')!r}, expected {ctx['id']}"]
        if kind == "tool":
            miss = [k for k in TOOL_KEYS if fm.get(k) in (None, "", [])]
            html = ctx["files"][1]
            if not html.exists():
                miss.append(f"missing {rel(html)}")
            else:
                t = html.read_text(encoding="utf-8")
                if "<script" not in t:
                    miss.append("tool.html has no inline <script>")
                if "data-as-of" not in t:
                    miss.append("tool.html constants carry no data-as-of")
                if re.search(r"\b(fetch\(|XMLHttpRequest|localStorage|sessionStorage|document\.cookie|<script[^>]+src=)", t):
                    miss.append("tool.html uses the network or storage (not allowed)")
            return [f"tool incomplete: {'; '.join(miss)}"] if miss else []
        if kind == "dataset":
            miss = [k for k in DATASET_KEYS if fm.get(k) in (None, "", [])]
            csv_path = ctx["files"][1]
            if not csv_path.exists():
                miss.append(f"missing {rel(csv_path)}")
            else:
                lines = [l for l in csv_path.read_text(encoding="utf-8").splitlines() if l.strip()]
                if len(lines) < 3:
                    miss.append("csv has fewer than a header and two rows")
            if not re.search(r"^\|[-:| ]+\|\s*$", path.read_text(encoding="utf-8"), re.M):
                miss.append("dataset page has no Markdown table")
            return [f"dataset incomplete: {'; '.join(miss)}"] if miss else []
        miss = lint.missing_keys(fm)
        miss += [f"v3 key {k}" for k in V3_KEYS if fm.get(k) in (None, "", [])]
        if fm.get("kind") not in ("pillar", "spoke", "reader_guide", "rewrite"):
            miss.append(f"kind {fm.get('kind')!r} is not pillar|spoke|reader_guide|rewrite")
        if fm.get("kind") != "pillar" and pillar_path and not fm.get("pillar"):
            miss.append(f"pillar (the topic pillar is {pillar_path})")
        if "tools" not in fm:
            miss.append("tools (a list, [] when none is embedded)")
        return [f"frontmatter incomplete: {'; '.join(miss)}"] if miss else []

    # ---------------------------------------------------------------------------------- finishing a page
    def finalize(ctx: dict, ok: bool, problems: list[str]) -> None:
        side_path = rewrite_sidecar(P.backups, tdir, ctx["slug"])
        side = json.loads(side_path.read_text(encoding="utf-8")) if ctx["kind"] == "rewrite" and side_path.exists() else None
        if not ok:
            q.set_status(ctx["id"], ctx["want"], P.queue)
            if side and not side.get("restored"):
                restore_rewrite(side, P.queue, log)
            with lock:
                stats["failed"] += 1
            log(f"[{ctx['id']}] back to {ctx['want']}: {'; '.join(problems)[:300]}")
            return
        q.set_status(ctx["id"], "written", P.queue)
        if side:
            retire_old_row(side, P.queue, log)
        with lock:
            stats["written"] += 1
        if ctx["kind"] in ARTICLE_KINDS:
            log(f"[{ctx['id']}] written: {rel(ctx['page'])} ({page_stats(ctx['page'])})")
            n = counter_bump(P.state) if not a.fix else 0
            if a.cold_edit or (a.cold_edit_every and n and n % a.cold_edit_every == 0):
                with lock:
                    cold_edit_queue.append(ctx)
                log(f"[{ctx['id']}] article #{n} finished: a fresh cold editor reads it after this batch")
        else:
            log(f"[{ctx['id']}] written: " + ", ".join(rel(f) for f in ctx["files"]))

    def final_check(ctx: dict):
        def go():
            problems = page_problems(ctx)
            if problems:
                return problems
            if ctx["kind"] in ARTICLE_KINDS:
                try:
                    place_images(ctx)
                except Exception as e:  # noqa: BLE001 - photos are optional; the page stands without them
                    log(f"[{ctx['id']}] images not placed: {type(e).__name__}: {str(e)[:160]}")
            return []
        return go

    def prepare(ctx: dict):
        def go():
            q.set_status(ctx["id"], "writing", P.queue)
            ctx["page"].parent.mkdir(parents=True, exist_ok=True)
            if ctx["kind"] == "rewrite" and not a.fix:
                backup_rewrite(ctx["page"], ctx["id"], P, tdir, P.queue, log)
            find_images(ctx)
        return go

    # ---------------------------------------------------------------------------------- jobs
    jobs, two = [], {}
    for r in rows:
        ctx = context(r)
        fill = common_fill(ctx)
        if ctx["kind"] in ("tool", "dataset"):
            if ctx["kind"] == "tool":
                deliverable = sessions.fill(TOOL_DELIVERABLE, tool_md=rel(ctx["files"][0]), tool_html=rel(ctx["files"][1]), **{k: fill[k] for k in ("slug", "topic_dir", "today", "id", "brief_path", "pillar_path", "readers_yaml")})
            else:
                deliverable = sessions.fill(DATASET_DELIVERABLE, dataset_md=rel(ctx["files"][0]), dataset_csv=rel(ctx["files"][1]), **{k: fill[k] for k in ("slug", "topic_dir", "today", "id", "brief_path", "pillar_path", "readers_yaml")})
            prompt = sessions.fill(templates["tool"], deliverable=deliverable, **fill)
            sessions.save_prompt(step, r["id"], prompt)
            jobs.append({"id": r["id"], "prompt": prompt, "expect": [str(f) for f in ctx["files"]], "prepare": prepare(ctx), "check": final_check(ctx), "ctx": ctx})
        elif ctx["kind"] in two_draft_kinds and not a.fix:
            if ctx["kind"] == "rewrite" and ctx["page"].exists():
                pass
            drafts = {}
            for org, desc in ORGANIZATIONS.items():
                draft = P.drafts / ctx["slug"] / f"{org}.md"
                draft.parent.mkdir(parents=True, exist_ok=True)
                if draft.exists():
                    draft.unlink()
                prompt = sessions.fill(templates["write-pillar"], draft_path=rel(draft), organization=desc, organization_name=org,
                                       primary_reader=ctx["readers"][0] if ctx["readers"] else "the reader the title names", **fill)
                sessions.save_prompt(step, f"{r['id']}-{org}", prompt)
                dctx = dict(ctx, draft=draft, org=org)
                jobs.append({"id": f"{r['id']}:{org}", "prompt": prompt, "expect": [str(draft)], "prepare": prepare(ctx),
                             "check": (lambda c=dctx: (lambda: page_problems(c, c["draft"])))(), "ctx": dctx, "draft": True})
                drafts[org] = draft
            two[r["id"]] = {"ctx": ctx, "drafts": drafts, "ok": set(), "fill": fill}
        else:
            rewrite_note = ""
            if ctx["kind"] == "rewrite":
                rewrite_note = REWRITE_NOTE.replace("{{article_path}}", rel(ctx["page"])) if ctx["page"].exists() else \
                    f"- Planned as a rewrite of /{tdir}/{ctx['slug']}/, but no page exists there yet: write it as a new spoke at that path (kind: rewrite in the frontmatter)."
            prompt = sessions.fill(templates["write"], rewrite_note=rewrite_note, **fill)
            sessions.save_prompt(step, r["id"], prompt)
            jobs.append({"id": r["id"], "prompt": prompt, "expect": [str(ctx["page"])], "prepare": prepare(ctx), "check": final_check(ctx), "ctx": ctx})

    def on_done(job, ok, r, problems):
        if job.get("draft"):
            rid = job["ctx"]["id"]
            if ok:
                two[rid]["ok"].add(job["ctx"]["org"])
            else:
                log(f"[{rid}] {job['ctx']['org']} draft failed: {'; '.join(problems)[:200]}")
            return
        finalize(job["ctx"], ok, problems)

    n_pages = len(rows)
    log(f"{topic['title']} ({tdir}): {n_pages} page(s) in status {want}, {len(jobs)} session(s) with {a.model}, {a.workers} workers, "
        f"{a.max_turns} turns, {a.timeout} s; two drafts for {', '.join(sorted(two_draft_kinds)) or 'none'}; log {rel(log_path)}")
    for r in rows:
        ang = parse_angle(r["angle"])
        log(f"  {r['id']} {ang.get('kind', '?'):<12} {ang.get('slug', '')}")
    st = sessions.run_jobs(jobs, workers=a.workers, label=step, model=a.model, max_turns=a.max_turns, allowed_tools=WRITER_TOOLS, timeout_s=a.timeout, log=log, on_done=on_done)

    # ---------------------------------------------------------------------------------- pick the best of two drafts
    picks = []
    for rid, t in two.items():
        ctx, oks = t["ctx"], sorted(t["ok"])
        if sessions.stopped() and len(oks) < 2:
            q.set_status(rid, want, P.queue)
            log(f"[{rid}] stopped before both drafts were done; back to {want}")
            continue
        if len(oks) == 2:
            prompt = sessions.fill(templates["pick-best"], draft_a=rel(t["drafts"]["decision"]), draft_b=rel(t["drafts"]["timeline"]),
                                   article_path=rel(ctx["page"]), primary_reader=ctx["readers"][0] if ctx["readers"] else "the reader the title names", **t["fill"])
            sessions.save_prompt("pick-best", rid, prompt)
            picks.append({"id": rid, "prompt": prompt, "expect": [str(ctx["page"])], "check": final_check(ctx), "ctx": ctx})
        elif len(oks) == 1:
            shutil.copy2(t["drafts"][oks[0]], ctx["page"])
            log(f"[{rid}] only the {oks[0]} draft was written; it becomes the page without a pick-best round")
            problems = final_check(ctx)()
            finalize(ctx, not problems, problems)
        else:
            finalize(ctx, False, ["neither draft was written"])
    if picks:
        log(f"{len(picks)} pick-best session(s): a fresh reader picks and merges the two drafts")
        st2 = sessions.run_jobs(picks, workers=a.workers, label="pick-best", model=a.model, max_turns=max(40, a.max_turns // 2), allowed_tools=PICK_TOOLS,
                                timeout_s=a.timeout, log=log, on_done=lambda job, ok, r, problems: finalize(job["ctx"], ok, problems))
        st["sessions"] += st2["sessions"]
        st["pauses"] += st2["pauses"]

    # ---------------------------------------------------------------------------------- every 10th article: a cold editor
    if cold_edit_queue and not sessions.stopped():
        colds = []
        for ctx in cold_edit_queue:
            edits_path = P.edits / f"{ctx['slug']}.md"
            edits_path.parent.mkdir(parents=True, exist_ok=True)
            floors = FLOORS.get(ctx["kind"], FLOORS["spoke"])
            prompt = sessions.fill(templates["cold-edit"], today=TODAY, article_path=rel(ctx["page"]), edits_path=rel(edits_path), slug=ctx["slug"],
                                   title=ctx["title"], readers=", ".join(ctx["readers"]) or "the readers the page names", word_floor=f"{floors[0]:,}",
                                   reader_floor=str(floors[2]), kind=ctx["kind"])
            sessions.save_prompt("cold-edit", ctx["id"], prompt)
            colds.append({"id": ctx["id"], "prompt": prompt, "expect": [str(edits_path)], "ctx": ctx, "edits": edits_path,
                          "check": (lambda c=ctx: (lambda: page_problems(c)))()})

        def cold_done(job, ok, r, problems):
            if ok:
                counter_note_cold_edit(P.state, job["ctx"]["slug"])
                log(f"[{job['id']}] cold edit done: {rel(job['edits'])} ({page_stats(job['ctx']['page'])})")
            else:
                log(f"[{job['id']}] cold edit did not finish ({'; '.join(problems)[:200]}); the page stands as written")
        st3 = sessions.run_jobs(colds, workers=a.workers, label="cold-edit", model=a.model, max_turns=max(40, a.max_turns // 2), allowed_tools=COLD_TOOLS,
                                timeout_s=a.timeout, log=log, on_done=cold_done)
        st["sessions"] += st3["sessions"]
        st["pauses"] += st3["pauses"]

    log(f"{step} done for {tdir}: {stats['written']} written, {stats['failed']} back to {want}; {st['sessions']} sessions; {st['pauses']} pause(s)"
        + ("; STOPPED" if st.get("stopped") else "") + "; next: scripts/v3/check.sh " + topic["slug"])
    return 0


REWRITE_NOTE = """- THIS IS A REWRITE of a live page. Read {{article_path}} first. Keep its slug and every fact the brief confirms (with its source);
  replace whatever the brief contradicts or dates; rebuild it to the page shape below from the brief. Frontmatter kind: rewrite. The old
  page planned no readers: pick 2 to 4 from the reader map whose answer differs most. Overwrite the file in place."""

TOOL_DELIVERABLE = """## Deliverable: a calculator or checklist tool (two files)
Write these two files with the Write tool: {{tool_md}} and {{tool_html}}

1. {{tool_md}}: YAML frontmatter with exactly these keys, then a Markdown body.
```yaml
title: "..."                 # 60 characters or fewer, says what the tool computes ("Rent + commute calculator: Ithaca neighborhoods")
meta: "..."                  # 120 to 155 characters: what you put in, what you get out
topic: {{topic_dir}}
updated: {{today}}
numbers_as_of: YYYY-MM-DD    # the date the brief's numbers apply to (the latest "Applies to" or sample date among the numbers used)
queue_id: {{id}}
kind: tool
readers: [{{readers_yaml}}]
brief: {{brief_path}}
sources:
  - {url: "https://...", title: "...", accessed: "YYYY-MM-DD"}   # every source URL behind a number in the tool
```
Body: what the tool computes (one paragraph, plain words); who it is for; the inputs and what each means; every number and formula in prose and
in one table (| Number | Value | Applies to | Source |) so a reader can redo the math by hand; the assumptions and what the tool does not cover;
"## How to read the result"; a short "## Related guides" section linking the pillar ({{pillar_path}}) and the guides that will embed the tool.

2. {{tool_html}}: a self-contained HTML fragment (no <html>, <head> or <body>; the renderer inserts it into a page and into every article that
embeds it with a ```tool {{slug}}``` fence). Requirements:
- one root element <div class="tool" id="tool-{{slug}}" data-tool="{{slug}}" data-as-of="YYYY-MM-DD">, labelled inputs (<label for=...>, ids prefixed
  "{{slug}}-"), sensible defaults and ranges, and a result area with aria-live="polite";
- one inline <script> in plain JavaScript: no frameworks, no fetch or XMLHttpRequest, no localStorage, sessionStorage or cookies, no external
  scripts, fonts or images; it must not break other tools on the same page (wrap it in an IIFE, look elements up inside the root);
- every constant (a rent, fare, distance, minutes, rate) lives in one `const NUMBERS = {...}` where each entry carries {value, asOf: "YYYY-MM-DD",
  source: "https://..."}, and any constant printed in the markup carries data-as-of="YYYY-MM-DD" on its element;
- recompute on every input change; show the result in words a student understands ("$1,610 a month all-in, 47 minutes door to door"), with the
  as-of date under it and a one-line note on what is estimated; the inputs still render if the script fails;
- under about 300 lines; styles inline and minimal (the site stylesheet handles type and color).
Every number comes from the brief, with its source URL. Never invent a number; when the brief has a range, use the range (low, typical, high) and say so.
Reply with one line: DONE tool {{slug}}: <n> numbers as of <date>, <m> inputs."""

DATASET_DELIVERABLE = """## Deliverable: an original dataset (two files)
Write these two files with the Write tool: {{dataset_md}} and {{dataset_csv}}

1. {{dataset_md}}: YAML frontmatter with exactly these keys, then a Markdown body.
```yaml
title: "..."                 # 60 characters or fewer, names the table and its date ("Ithaca rent by neighborhood, fall 2026")
meta: "..."                  # 120 to 155 characters: what the table shows, from how many observations, as of when
topic: {{topic_dir}}
updated: {{today}}
as_of: YYYY-MM-DD            # the date the observations apply to
sample_size: 0               # the number of observations behind the table
method: "one sentence: how the rows were collected and computed"
queue_id: {{id}}
kind: dataset
readers: [{{readers_yaml}}]
brief: {{brief_path}}
sources:
  - {url: "https://...", title: "...", accessed: "YYYY-MM-DD"}
```
Body: what the table shows and who should use it; "## Method" (the brief's own steps, from section 10 or 3, step by step, so anyone can redo it);
the table itself in Markdown with the same columns and rows as the CSV; "## Caveats" (sample size, dates, what it does not cover); "## How to cite";
"## Change log" ({{today}}: first release); "## Related guides" linking the pillar ({{pillar_path}}) and the guides the data serves.

2. {{dataset_csv}}: RFC-4180, UTF-8, a header row then one row per observation or group, no blank lines, no commentary. Column names
lowercase_snake_case; dates ISO (YYYY-MM-DD); money as plain numbers with a unit column (usd_per_month); a sample_size column where rows are
aggregates; a source_url column where rows differ in source; a notes column for caveats. Rows come from the brief's tables, never from memory.
Reply with one line: DONE dataset {{slug}}: <rows> rows as of <date>."""


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
