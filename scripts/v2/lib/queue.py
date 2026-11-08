#!/usr/bin/env python
"""queue/queue.csv for the v2 pipeline (docs/v2/spec.md step 1): read, append and update rows atomically (temp file + rename),
one id sequence per topic (writes are locked across threads and processes), status transitions, the --auto-approve helper, the merge of a proposed CSV written by a demand
session, and the queue-row -> article lookup (by the article's queue_id frontmatter).

    sys.path.insert(0, "scripts/v2"); from lib import queue as q
    rows = q.read(); q.by_status("approved"); q.set_status("q-housing-0001", "writing"); q.article_for("q-housing-0001")

CLI:  python scripts/v2/lib/queue.py [--file queue/queue.csv] list [--status S] [--topic T] [--json]
                                     show ID | set-status ID STATUS [--force] | approve [--ids a,b] | next-id TOPIC
                                     merge FILE.csv [--topic T] [--approve]
Columns (RFC-4180; url lists inside a cell are separated by " | "):
    id,question,primary_query,topic,demand_evidence,top_results,verdict,angle,status
"""
from __future__ import annotations

import argparse
import contextlib
import csv
import fcntl
import json
import os
import re
import sys
import tempfile
import threading
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[3]
QUEUE = REPO / "queue" / "queue.csv"
ARTICLES = REPO / "content" / "articles"
HEADER = ["id", "question", "primary_query", "topic", "demand_evidence", "top_results", "verdict", "angle", "status"]
TOPICS = ["housing", "getting-around", "academics", "money", "daily-life", "careers", "parents", "alumni"]
VERDICTS = ("gap", "weak", "owned")
STATUSES = ("proposed", "approved", "writing", "written", "reviewing", "fix", "published", "rejected", "owned")
TRANSITIONS = {
    "proposed": {"approved", "rejected"},
    "approved": {"writing", "rejected"},
    "writing": {"written", "approved", "fix"},     # back to approved (or fix) when the session left no complete article
    "written": {"reviewing", "published", "fix", "rejected"},   # published only with a passing review; publish.sh's lint may send it to one revision or reject a duplicate
    "reviewing": {"written", "fix", "rejected"},   # written = the review passed (verdict lives in content/reviews/<slug>.json)
    "fix": {"writing", "rejected"},
    "published": set(),
    "rejected": set(),
    "owned": set(),
}
SEP = " | "
ID_RE = re.compile(r"^q-([a-z-]+)-(\d{4})$")
_lock = threading.RLock()


@contextlib.contextmanager
def locked(path: Path | str = QUEUE):
    """One read-modify-write at a time, across threads and across processes (write.sh and review.sh run side by side):
    the thread lock plus flock on <queue>.lock next to the csv."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with _lock, path.with_suffix(".lock").open("a") as fh:
        fcntl.flock(fh, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(fh, fcntl.LOCK_UN)


# ------------------------------------------------------------------------------------------ rows
def read(path: Path | str = QUEUE) -> list[dict]:
    path = Path(path)
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))
    return [{k: (r.get(k) or "").strip() for k in HEADER} for r in rows]


def write(rows: list[dict], path: Path | str = QUEUE) -> None:
    """Whole-file replace through a temp file in the same folder + rename, so a reader never sees a half-written queue."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".queue-", suffix=".csv", dir=path.parent)
    with os.fdopen(fd, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=HEADER, extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        w.writerows({k: (r.get(k) or "") for k in HEADER} for r in rows)
    os.replace(tmp, path)


def next_id(topic: str, rows: list[dict]) -> str:
    n = 0
    for r in rows:
        m = ID_RE.match(r.get("id", ""))
        if m and m.group(1) == topic:
            n = max(n, int(m.group(2)))
    return f"q-{topic}-{n + 1:04d}"


def normalize(row: dict, topic: str | None = None) -> dict:
    r = {k: str(row.get(k) or "").strip() for k in HEADER}
    r["topic"] = r["topic"] if r["topic"] in TOPICS else (topic or r["topic"])
    r["verdict"] = r["verdict"].lower()
    r["status"] = r["status"].lower()
    r["primary_query"] = r["primary_query"] or r["question"]
    for k in ("demand_evidence", "top_results"):
        urls = [u.rstrip(".,;)") for u in re.findall(r"https?://[^\s|]+", r[k])]
        r[k] = SEP.join(urls) if urls else r[k]
    return r


def append(new_rows: list[dict], path: Path | str = QUEUE) -> list[dict]:
    """Append rows; a missing, malformed or already used id is replaced by the topic's next id. Returns the rows as written."""
    with locked(path):
        rows = read(path)
        used = {r["id"] for r in rows}
        out = []
        for row in new_rows:
            r = normalize(row)
            if r["topic"] not in TOPICS:
                raise ValueError(f"unknown topic {r['topic']!r} (one of {', '.join(TOPICS)})")
            if r["status"] not in STATUSES:
                r["status"] = "owned" if r["verdict"] == "owned" else "proposed"
            if not ID_RE.match(r["id"]) or r["id"] in used:
                r["id"] = next_id(r["topic"], rows)
            used.add(r["id"])
            rows.append(r)
            out.append(r)
        write(rows, path)
    return out


def get(queue_id: str, path: Path | str = QUEUE) -> dict:
    for r in read(path):
        if r["id"] == queue_id:
            return r
    raise KeyError(f"no queue row {queue_id}")


def by_status(*statuses: str, path: Path | str = QUEUE) -> list[dict]:
    return [r for r in read(path) if r["status"] in statuses]


def update(queue_id: str, path: Path | str = QUEUE, **fields) -> dict:
    with locked(path):
        rows = read(path)
        for r in rows:
            if r["id"] == queue_id:
                r.update({k: str(v) for k, v in fields.items() if k in HEADER})
                write(rows, path)
                return r
    raise KeyError(f"no queue row {queue_id}")


def set_status(queue_id: str, status: str, path: Path | str = QUEUE, force: bool = False) -> dict:
    """Move a row along the pipeline; anything outside TRANSITIONS needs force=True (hand repairs)."""
    if status not in STATUSES:
        raise ValueError(f"unknown status {status!r} (one of {', '.join(STATUSES)})")
    with locked(path):
        rows = read(path)
        for r in rows:
            if r["id"] == queue_id:
                if r["status"] != status and status not in TRANSITIONS.get(r["status"], set()) and not force:
                    raise ValueError(f"{queue_id}: {r['status']} -> {status} is not a pipeline transition (use force for a hand repair)")
                r["status"] = status
                write(rows, path)
                return r
    raise KeyError(f"no queue row {queue_id}")


def approve(ids: list[str] | None = None, path: Path | str = QUEUE) -> list[str]:
    """The --auto-approve helper: proposed -> approved for the given ids, or for every proposed row. Returns the ids flipped."""
    with locked(path):
        rows = read(path)
        done = []
        for r in rows:
            if r["status"] == "proposed" and (ids is None or r["id"] in ids):
                r["status"] = "approved"
                done.append(r["id"])
        if done:
            write(rows, path)
    return done


# ------------------------------------------------------------------------------------------ merge of a demand session's file
def _key(text: str) -> str:
    return re.sub(r"[^a-z0-9 ]+", "", text.lower()).strip()


def merge_proposed(file: Path | str, path: Path | str = QUEUE, topic: str | None = None) -> tuple[list[dict], list[tuple[str, str]]]:
    """Merge queue/proposed/<topic>-<ts>.csv into the queue: gap|weak -> proposed, owned -> owned, ids assigned here,
    rows whose question or primary query already exists word for word are skipped (meaning-level dedupe is the session's job).
    Returns (added rows, [(question, reason) skipped])."""
    file = Path(file)
    topic = topic or (file.stem.rsplit("-", 1)[0] if file.stem.rsplit("-", 1)[0] in TOPICS else None)
    with file.open(newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        raw = [{(k or "").strip().lower(): v for k, v in r.items()} for r in reader]
    added, skipped = [], []
    with locked(path):
        rows = read(path)
        seen = {_key(r["question"]) for r in rows} | {_key(r["primary_query"]) for r in rows}
        for item in raw:
            r = normalize(item, topic)
            if not r["question"]:
                skipped.append(("", "empty question"))
                continue
            if r["verdict"] not in VERDICTS:
                skipped.append((r["question"], f"verdict {r['verdict']!r} is not gap|weak|owned"))
                continue
            if r["topic"] not in TOPICS:
                skipped.append((r["question"], f"unknown topic {r['topic']!r}"))
                continue
            if _key(r["question"]) in seen or _key(r["primary_query"]) in seen:
                skipped.append((r["question"], "already in the queue"))
                continue
            r["status"] = "owned" if r["verdict"] == "owned" else "proposed"
            r["id"] = next_id(r["topic"], rows)
            rows.append(r)
            added.append(r)
            seen |= {_key(r["question"]), _key(r["primary_query"])}
        if added:
            write(rows, path)
    return added, skipped


# ------------------------------------------------------------------------------------------ articles
def frontmatter(md_path: Path | str) -> dict:
    """The YAML block between the first two --- lines, or {} when the file has none or it does not parse."""
    try:
        text = Path(md_path).read_text(encoding="utf-8")
    except OSError:
        return {}
    m = re.match(r"﻿?---\s*\n(.*?)\n---\s*(?:\n|$)", text, re.S)
    if not m:
        return {}
    try:
        fm = yaml.safe_load(m.group(1))
    except yaml.YAMLError:
        return {}
    return fm if isinstance(fm, dict) else {}


def articles(root: Path | str = REPO) -> list[Path]:
    return sorted((Path(root) / "content" / "articles").glob("*/*.md"))


def article_for(queue_id: str, root: Path | str = REPO) -> Path | None:
    for p in articles(root):
        if str(frontmatter(p).get("queue_id", "")) == queue_id:
            return p
    return None


def slugify(text: str, limit: int = 60) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    if len(s) > limit:
        s = s[:limit].rsplit("-", 1)[0]
    return s or "article"


# ------------------------------------------------------------------------------------------ CLI
def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(prog="queue.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--file", default=str(QUEUE), help="queue csv (default queue/queue.csv)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("list")
    p.add_argument("--status")
    p.add_argument("--topic")
    p.add_argument("--json", action="store_true")
    sub.add_parser("show").add_argument("id")
    p = sub.add_parser("set-status")
    p.add_argument("id")
    p.add_argument("status", choices=STATUSES)
    p.add_argument("--force", action="store_true")
    sub.add_parser("approve").add_argument("--ids", help="comma-separated ids (default: every proposed row)")
    sub.add_parser("next-id").add_argument("topic", choices=TOPICS)
    sub.add_parser("dedupe", help="merge rows that ask the same thing within a topic (the later row becomes rejected)")
    p = sub.add_parser("merge")
    p.add_argument("csv")
    p.add_argument("--topic", choices=TOPICS)
    p.add_argument("--approve", action="store_true")
    a = ap.parse_args(argv)
    path = Path(a.file)
    if a.cmd == "dedupe":
        pairs = dedupe(a.queue if hasattr(a, "queue") and a.queue else QUEUE)
        for dup, kept_id in pairs:
            print(f"{dup} -> duplicate of {kept_id}")
        print(f"{len(pairs)} duplicate row(s) merged")
        return 0
    if a.cmd == "list":
        rows = [r for r in read(path) if (not a.status or r["status"] == a.status) and (not a.topic or r["topic"] == a.topic)]
        if a.json:
            print(json.dumps(rows, indent=1))
        else:
            for r in rows:
                print(f"{r['id']:<24} {r['status']:<10} {r['verdict']:<6} {r['question'][:90]}")
            print(f"{len(rows)} rows")
    elif a.cmd == "show":
        print(json.dumps(get(a.id, path), indent=1))
    elif a.cmd == "set-status":
        r = set_status(a.id, a.status, path, force=a.force)
        print(f"{r['id']} -> {r['status']}")
    elif a.cmd == "approve":
        done = approve(a.ids.split(",") if a.ids else None, path)
        print(f"approved {len(done)}: {', '.join(done)}")
    elif a.cmd == "next-id":
        print(next_id(a.topic, read(path)))
    elif a.cmd == "merge":
        added, skipped = merge_proposed(a.csv, path, a.topic)
        for r in added:
            print(f"+ {r['id']} {r['verdict']:<5} {r['status']:<8} {r['question'][:80]}")
        for q_, why in skipped:
            print(f"- skipped ({why}): {q_[:80]}")
        if a.approve:
            done = approve([r["id"] for r in added], path)
            print(f"approved {len(done)}")
        print(f"added {len(added)}, skipped {len(skipped)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))


def _tokens(*texts: str) -> set[str]:
    import re as _re
    stop = {"a", "an", "the", "of", "at", "in", "on", "for", "to", "and", "or", "is", "are", "do", "does", "how", "what", "when", "where", "which", "who", "my", "i", "can", "cornell", "ithaca", "students", "student"}
    return {w for t in texts for w in _re.findall(r"[a-z0-9]+", (t or "").lower()) if w not in stop and len(w) > 2}


def dedupe(path: Path | str = QUEUE, threshold: float = 0.8) -> list[tuple[str, str]]:
    """Merge rows that ask the same thing (token Jaccard of question + primary query >= threshold within a topic): the earlier row
    keeps its status and gains the other's demand evidence; the later row becomes rejected unless it is already published."""
    merged = []
    with locked(path):
        rows = read(path)
        kept: list[dict] = []
        for r in rows:
            if r["status"] in ("published",):
                kept.append(r); continue
            t = _tokens(r["question"], r["primary_query"])
            dup = None
            for k in kept:
                if k["topic"] != r["topic"] or k["status"] == "rejected":
                    continue
                kt = _tokens(k["question"], k["primary_query"])
                if t and kt and len(t & kt) / len(t | kt) >= threshold:
                    dup = k; break
            if dup is not None and r["status"] not in ("published",):
                dup["demand_evidence"] = SEP.join(x for x in dict.fromkeys((dup["demand_evidence"] + SEP + r["demand_evidence"]).split(SEP)) if x)
                r["status"] = "rejected"
                r["angle"] = (r["angle"] + "; " if r["angle"] else "") + f"duplicate of {dup['id']}"
                merged.append((r["id"], dup["id"]))
            kept.append(r)
        write(rows, path)
    return merged
