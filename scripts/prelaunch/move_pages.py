"""Phase 3 of docs/v5/prelaunch-spec.md: move pages to their right section, with 301s and every internal link re-pointed.

    worker/.venv/bin/python scripts/prelaunch/move_pages.py            # dry run: prints every move and link rewrite
    worker/.venv/bin/python scripts/prelaunch/move_pages.py --apply    # git mv the files, edit frontmatter and links, update the queue

The moves come from reports/00-baseline.json ("mismatches": the Phase 0 crawl against the spec's Phase 3b table, hand-reviewed).
For each page: git mv content/articles/<old>/<slug>.md -> content/articles/<new>/<slug>.md; frontmatter topic: <new>; redirect_from gains
/cornell/<old>/<slug>/ and /<old>/<slug>/ (the Jinja-era path); every Markdown link to /<old>/<slug>/ or /cornell/<old>/<slug>/ anywhere
under content/ becomes /<new>/<slug>/; the queue row's topic becomes <new>. The site build turns redirect_from into _redirects lines
and its link map (site/src/lib/model.ts), and check-build fails on any link that still points at an old path.
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
BASELINE = REPO / "reports" / "00-baseline.json"


def moves() -> list[tuple[str, str, str]]:
    """(slug, old section, new section) from the Phase 0 mismatch list."""
    d = json.loads(BASELINE.read_text(encoding="utf-8"))
    out = []
    for m in d["mismatches"]:
        parts = [p for p in m["url"].split("/") if p]
        if len(parts) == 3 and parts[0] == "cornell":
            out.append((parts[2], parts[1], m["suggested"]))
    return sorted(out)


def set_frontmatter(text: str, topic: str, redirect_from: list[str]) -> str:
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    assert m, "no frontmatter"
    fm = m.group(1)
    fm, n = re.subn(r"^topic:.*$", f"topic: {topic}", fm, count=1, flags=re.M)
    assert n == 1, "no topic line"
    if re.search(r"^redirect_from:", fm, re.M):
        fm = re.sub(r"^redirect_from:.*(\n  - .*)*", lambda mm: mm.group(0).rstrip("\n") + "".join(f"\n  - {r}" for r in redirect_from if r not in mm.group(0)), fm, count=1, flags=re.M)
    else:
        fm = fm + "\nredirect_from:" + "".join(f"\n  - {r}" for r in redirect_from)
    return f"---\n{fm}\n---\n" + text[m.end():]


def main() -> int:
    pairs = [a for a in sys.argv[1:] if a.startswith("--pair=")]
    if pairs:   # --pair=<old section>/<slug>:<new section>, repeatable; else the Phase 0 mismatch list
        mv = []
        for a in pairs:
            src, new = a[len("--pair="):].split(":")
            old, slug = src.split("/")
            mv.append((slug, old, new))
    else:
        mv = moves()
    print(f"{len(mv)} page(s) to move")
    link_rewrites = {}
    for slug, old, new in mv:
        src = REPO / "content" / "articles" / old / f"{slug}.md"
        dst = REPO / "content" / "articles" / new / f"{slug}.md"
        assert src.exists(), src
        assert not dst.exists(), dst
        print(f"  {old}/{slug} -> {new}/{slug}")
        link_rewrites[f"/{old}/{slug}/"] = f"/{new}/{slug}/"
        link_rewrites[f"/cornell/{old}/{slug}/"] = f"/{new}/{slug}/"
    # links across every Markdown file the site or the pipeline reads
    files = [p for d in ("articles", "tools", "datasets", "start", "pages") for p in (REPO / "content" / d).rglob("*.md")]
    touched = 0
    pat = re.compile("|".join(re.escape(k) for k in sorted(link_rewrites, key=len, reverse=True)))
    for f in files:
        s = f.read_text(encoding="utf-8")
        t = pat.sub(lambda m: link_rewrites[m.group(0)], s)
        if t != s:
            touched += 1
            if APPLY:
                f.write_text(t, encoding="utf-8")
    print(f"{touched} file(s) with links to rewrite")
    if not APPLY:
        print("dry run; nothing changed")
        return 0
    rows = {r["id"]: r for r in q.read(q.QUEUE)}
    for slug, old, new in mv:
        src = REPO / "content" / "articles" / old / f"{slug}.md"
        dst = REPO / "content" / "articles" / new / f"{slug}.md"
        dst.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["git", "mv", str(src), str(dst)], cwd=REPO, check=True)
        text = dst.read_text(encoding="utf-8")
        text = pat.sub(lambda m: link_rewrites[m.group(0)], text)
        text = set_frontmatter(text, new, [f"/cornell/{old}/{slug}/", f"/{old}/{slug}/"])
        dst.write_text(text, encoding="utf-8")
        qid = str(q.frontmatter(dst).get("queue_id") or "")
        if qid in rows:
            q.update(qid, q.QUEUE, topic=new)
        else:   # a page without a queue_id of its own: its idea-run row is keyed by slug in the angle
            for r in rows.values():
                if r["topic"] == old and f"slug={slug};" in r["angle"]:
                    q.update(r["id"], q.QUEUE, topic=new)
    print("applied")
    return 0


if __name__ == "__main__":
    sys.exit(main())
