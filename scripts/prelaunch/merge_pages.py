"""Phase 5 of docs/v5/prelaunch-spec.md, the mechanics after the content merge: the merged-away page is removed, its URLs 301 to the keeper,
every internal link is re-pointed, and its queue row is retired. The content itself was moved into the keeper by the merge agents first.

    worker/.venv/bin/python scripts/prelaunch/merge_pages.py            # dry run, from reports/05-merges.json
    worker/.venv/bin/python scripts/prelaunch/merge_pages.py --apply

A pair whose keeper is a /tools/ page is Phase 4's (scripts/prelaunch/consolidate_tools.py handles it) and is skipped here.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts" / "v2"))
from lib import queue as q  # noqa: E402

APPLY = "--apply" in sys.argv


def path_for(url_or_path: str) -> Path | None:
    s = url_or_path.strip()
    if s.startswith("content/"):
        return REPO / s
    parts = [p for p in s.split("/") if p]
    if parts and parts[0] == "cornell" and len(parts) == 3:
        return REPO / "content" / "articles" / parts[1] / f"{parts[2]}.md"
    if len(parts) == 2:   # /<section>/<slug>/ (renderer path) or a bare section/slug
        return REPO / "content" / "articles" / parts[0] / f"{parts[1]}.md"
    if len(parts) == 1:   # a bare slug: find it
        hits = list((REPO / "content" / "articles").glob(f"*/{parts[0]}.md"))
        return hits[0] if len(hits) == 1 else None
    return None


def add_redirects(page: Path, urls: list[str]) -> None:
    text = page.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    assert m, page
    fm = m.group(1)
    if re.search(r"^redirect_from:", fm, re.M):
        fm = re.sub(r"^redirect_from:.*(\n  - .*)*", lambda mm: mm.group(0).rstrip("\n") + "".join(f"\n  - {u}" for u in urls if u not in mm.group(0)), fm, count=1, flags=re.M)
    else:
        fm = fm + "\nredirect_from:" + "".join(f"\n  - {u}" for u in urls)
    page.write_text(f"---\n{fm}\n---\n" + text[m.end():], encoding="utf-8")


def main() -> int:
    pairs = json.loads((REPO / "reports" / "05-merges.json").read_text(encoding="utf-8"))
    plan = []
    for pr in pairs:
        if "/tools/" in pr["keep"]:
            print(f"  skip (Phase 4): {pr['keep']} <- {pr['merge_in']}")
            continue
        keep = path_for(pr["keep"])
        assert keep and keep.exists(), f"keeper not found: {pr['keep']}"
        for gone_ref in pr["merge_in"]:
            gone = path_for(gone_ref)
            assert gone and gone.exists(), f"merged page not found: {gone_ref}"
            plan.append((keep, gone))
    rewrites = {}
    for keep, gone in plan:
        ks, ksec = keep.stem, keep.parent.name
        gs, gsec = gone.stem, gone.parent.name
        print(f"  {gsec}/{gs} -> {ksec}/{ks}")
        rewrites[f"/{gsec}/{gs}/"] = f"/{ksec}/{ks}/"
        rewrites[f"/cornell/{gsec}/{gs}/"] = f"/{ksec}/{ks}/"
        # the merged page may have moved in Phase 3: its own redirect_from entries carry over to the keeper
        fm = q.frontmatter(gone)
        for old in (fm.get("redirect_from") or []):
            rewrites[str(old)] = f"/{ksec}/{ks}/"
    pat = re.compile("|".join(re.escape(k) for k in sorted(rewrites, key=len, reverse=True))) if rewrites else None
    files = [p for d in ("articles", "tools", "datasets", "start", "pages") for p in (REPO / "content" / d).rglob("*.md")]
    gone_set = {g for _, g in plan}
    touched = 0
    for f in files:
        if f in gone_set or not pat:
            continue
        s = f.read_text(encoding="utf-8")
        t = pat.sub(lambda m: rewrites[m.group(0)], s)
        if t != s:
            touched += 1
            if APPLY:
                f.write_text(t, encoding="utf-8")
    print(f"{len(plan)} merge(s); {touched} file(s) with links to re-point")
    if not APPLY:
        print("dry run; nothing changed")
        return 0
    rows = {r["id"]: r for r in q.read(q.QUEUE)}
    for keep, gone in plan:
        gfm = q.frontmatter(gone)
        urls = [f"/cornell/{gone.parent.name}/{gone.stem}/", f"/{gone.parent.name}/{gone.stem}/"] + [str(x) for x in (gfm.get("redirect_from") or [])]
        qid = str(gfm.get("queue_id") or "")
        subprocess.run(["git", "rm", "-q", str(gone)], cwd=REPO, check=True)
        for side, ext in (("checks", ".json"), ("reviews", ".json"), ("reviews", ".prev.json"), ("reviews", ".prev.v2.json"), ("edits", ".md")):
            p = REPO / "content" / side / f"{gone.stem}{ext}"
            if p.exists():
                subprocess.run(["git", "rm", "-q", str(p)], cwd=REPO, check=True)
        add_redirects(keep, urls)
        for r in rows.values():
            if (qid and r["id"] == qid) or (f"slug={gone.stem};" in r["angle"] and r["topic"] == gone.parent.name):
                if r["status"] == "published":
                    q.set_status(r["id"], "rejected", q.QUEUE, force=True)
                    q.update(r["id"], q.QUEUE, top_results=f"merged 2026-11-11 into /{keep.parent.name}/{keep.stem}/ (docs/v5 Phase 5); 301 in place")
    print("applied")
    return 0


if __name__ == "__main__":
    sys.exit(main())
