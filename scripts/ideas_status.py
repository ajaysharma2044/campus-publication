#!/usr/bin/env python3
"""Keep IDEAS-STATUS.md current for the idea-runner run (docs/v4/RUN-NOW.md).

IDEAS-STATUS.md is rebuilt from three inputs every time this runs:
  IDEAS.md                  the owner's idea list (id | mode | topic | title | tags)
  review/ideas-plan.json    the coordinator's decision per idea (action, slug, rewrite target, merges, notes)
  review/_status/<id>.json  one sidecar per idea, written as pages move (status, page, words, page_check, unmatched, note)

Usage:
  python3 scripts/ideas_status.py                                   rebuild IDEAS-STATUS.md
  python3 scripts/ideas_status.py --set 12 status=done page=review/getting-around/x.md page_check=PASS unmatched=0 note="..."
                                                                    update idea 12's sidecar, then rebuild
  python3 scripts/ideas_status.py --note "text"                     append a dated progress paragraph, then rebuild

Statuses: queued, writing, done, rewrite-done, merged, hub-row, waiting-data, needs-review, failed.
Files are written atomically (temp file plus rename), so concurrent runs from parallel agents never leave them half written.
A milestone paragraph (pages done, pages left, problems) is added to the progress notes every 10 pages.
"""
import datetime
import json
import os
import re
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IDEAS = os.path.join(REPO, "IDEAS.md")
PLAN = os.path.join(REPO, "review", "ideas-plan.json")
STATUS_DIR = os.path.join(REPO, "review", "_status")
PROGRESS = os.path.join(REPO, "review", "_progress.md")
OUT = os.path.join(REPO, "IDEAS-STATUS.md")
STATUSES = ["queued", "writing", "done", "rewrite-done", "merged", "hub-row", "waiting-data", "needs-review", "failed"]
ROW = re.compile(r"^(\d+) \| ([FA]) \| ([a-z-]+) \| (.+?)(?: \| ([A-Z ]+))?\s*$")


def now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M")


def atomic_write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), prefix=".tmp-")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(text)
    os.replace(tmp, path)


def load_json(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def read_ideas():
    ideas, wave = [], ""
    for line in open(IDEAS, encoding="utf-8"):
        line = line.rstrip("\n")
        m = re.match(r"^## (Wave \d+: .*)$", line)
        if m:
            wave = m.group(1)
            continue
        m = ROW.match(line)
        if m:
            ideas.append({"id": int(m.group(1)), "mode": m.group(2), "topic": m.group(3), "title": m.group(4).strip(),
                          "tags": (m.group(5) or "").split(), "wave": wave})
    return ideas


def sidecar_path(i):
    return os.path.join(STATUS_DIR, f"{int(i):03d}.json")


def set_sidecar(i, kv):
    d = load_json(sidecar_path(i), {})
    d.update(kv)
    d["id"] = int(i)
    d["updated"] = now()
    atomic_write(sidecar_path(i), json.dumps(d, indent=1, ensure_ascii=False))


def words_in(page):
    try:
        t = open(os.path.join(REPO, page), encoding="utf-8").read()
    except OSError:
        return ""
    body = t.split("---", 2)[2] if t.startswith("---") and t.count("---") >= 2 else t
    return len(body.split())


def cell(s):
    return str(s if s is not None else "").replace("|", "\\|").replace("\n", " ").strip()


def build():
    ideas = read_ideas()
    plan = load_json(PLAN, {})
    rows, counts = [], {s: 0 for s in STATUSES}
    for it in ideas:
        p = plan.get(str(it["id"]), {})
        sc = load_json(sidecar_path(it["id"]), {})
        default = {"merged": "merged", "hub-row": "hub-row", "waiting-data": "waiting-data"}.get(p.get("action"), "queued")
        status = sc.get("status") or default
        if status not in STATUSES:
            status = "needs-review"
        counts[status] += 1
        page = sc.get("page") or p.get("page") or ""
        note = sc.get("note") or p.get("note") or ""
        if p.get("action") == "merged" and p.get("merged_into") and "merged into" not in note.lower():
            note = f"merged into {p['merged_into']}. {note}".strip()
        if p.get("rewrite_target") and "rewrite of" not in note.lower():
            note = f"rewrite of {p['rewrite_target']}. {note}".strip()
        words = sc.get("words") or (words_in(page) if page else "")
        rows.append((it, status, page, words, sc.get("page_check", ""), sc.get("unmatched", ""), note))
    done = counts["done"] + counts["rewrite-done"]
    left = counts["queued"] + counts["writing"] + counts["waiting-data"]
    problems = [str(it["id"]) for it, s, *_ in rows if s in ("needs-review", "failed")]
    milestone(done, left, problems)
    progress = open(PROGRESS, encoding="utf-8").read().strip() if os.path.exists(PROGRESS) else ""
    head = (f"Updated {now()}. Pages done: {done} of {len(ideas)} ideas ({counts['done']} done, {counts['rewrite-done']} rewrite-done). "
            f"Left to write: {left} ({counts['queued']} queued, {counts['writing']} writing, {counts['waiting-data']} waiting-data). "
            f"Not pages: {counts['merged']} merged, {counts['hub-row']} hub-row. "
            f"Problems: {counts['needs-review']} needs-review, {counts['failed']} failed" + (f" (ideas {', '.join(problems)})." if problems else "."))
    out = ["# IDEAS-STATUS", "", head, ""]
    if progress:
        out += ["## Progress notes", "", progress, ""]
    out += ["## Ideas", "", "| id | title | status | page | words | page_check | unmatched | note |", "|---|---|---|---|---|---|---|---|"]
    wave = None
    for it, status, page, words, pc, um, note in rows:
        if it["wave"] != wave:
            wave = it["wave"]
            out.append(f"| | **{wave}** | | | | | | |")
        out.append(f"| {it['id']} | {cell(it['title'])} | {status} | {cell(page)} | {cell(words)} | {cell(pc)} | {cell(um)} | {cell(note)} |")
    atomic_write(OUT, "\n".join(out) + "\n")
    return done, left, problems


def milestone(done, left, problems):
    """Every 10 finished pages, add one paragraph to the progress notes (pages done, pages left, problems)."""
    if done == 0 or done % 10:
        return
    existing = open(PROGRESS, encoding="utf-8").read() if os.path.exists(PROGRESS) else ""
    if re.search(rf"^\*\*{done} pages done\*\*", existing, re.M):
        return
    text = f"**{done} pages done** ({now()}): {left} left to write; problems: " + (f"ideas {', '.join(problems)} need review." if problems else "none.")
    atomic_write(PROGRESS, (existing.rstrip() + "\n\n" if existing.strip() else "") + text + "\n")


def main(args):
    if args[:1] == ["--set"]:
        kv = {}
        for a in args[2:]:
            k, _, v = a.partition("=")
            kv[k] = v
        set_sidecar(args[1], kv)
    elif args[:1] == ["--note"]:
        existing = open(PROGRESS, encoding="utf-8").read() if os.path.exists(PROGRESS) else ""
        atomic_write(PROGRESS, (existing.rstrip() + "\n\n" if existing.strip() else "") + f"{now()}: {args[1]}\n")
    done, left, problems = build()
    print(f"IDEAS-STATUS.md rebuilt: {done} done, {left} left, problems: {', '.join(problems) or 'none'}")


if __name__ == "__main__":
    main(sys.argv[1:])
