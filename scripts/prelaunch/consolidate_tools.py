"""Phase 4 of docs/v5/prelaunch-spec.md: one canonical URL per tool, /tools/<slug>/.

    worker/.venv/bin/python scripts/prelaunch/consolidate_tools.py            # dry run
    worker/.venv/bin/python scripts/prelaunch/consolidate_tools.py --apply    # git rm the duplicate article, 301 it, re-point links, retire its queue row

For each tool that also exists as an article with the same slug (reports/00-baseline.json "tools" with duplicate_pages): the article is
removed (any content worth keeping was moved onto the tool page or a related article first, by hand, from the Phase 4 analysis),
the tool.md frontmatter gains redirect_from with the article's two URLs, every Markdown link to the article becomes /tools/<slug>/,
and the article's queue row is set to rejected with a note (superseded by the tool page).
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


def duplicates() -> list[tuple[str, str, str]]:
    """(tool slug, article section, article url) for each tool at two URLs."""
    d = json.loads((REPO / "reports" / "00-baseline.json").read_text(encoding="utf-8"))
    out = []
    for t in d["tools"]:
        for u in t["duplicate_pages"]:
            parts = [p for p in u.split("/") if p]
            if len(parts) == 3 and parts[0] == "cornell" and parts[2] == t["tool"]:
                out.append((t["tool"], parts[1], u))
    return sorted(out)


def add_redirects(tool_md: Path, urls: list[str]) -> None:
    text = tool_md.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    assert m, tool_md
    fm = m.group(1)
    if re.search(r"^redirect_from:", fm, re.M):
        fm = re.sub(r"^redirect_from:.*(\n  - .*)*", lambda mm: mm.group(0).rstrip("\n") + "".join(f"\n  - {u}" for u in urls if u not in mm.group(0)), fm, count=1, flags=re.M)
    else:
        fm = fm + "\nredirect_from:" + "".join(f"\n  - {u}" for u in urls)
    tool_md.write_text(f"---\n{fm}\n---\n" + text[m.end():], encoding="utf-8")


def main() -> int:
    dups = duplicates()
    print(f"{len(dups)} duplicate article page(s)")
    rewrites = {}
    for slug, section, url in dups:
        art = REPO / "content" / "articles" / section / f"{slug}.md"
        tool = REPO / "content" / "tools" / slug / "tool.md"
        assert tool.exists(), tool
        state = "present" if art.exists() else "already removed"
        print(f"  {url} -> /tools/{slug}/ ({state})")
        rewrites[f"/{section}/{slug}/"] = f"/tools/{slug}/"
        rewrites[f"/cornell/{section}/{slug}/"] = f"/tools/{slug}/"
    pat = re.compile("|".join(re.escape(k) for k in sorted(rewrites, key=len, reverse=True)))
    files = [p for d in ("articles", "tools", "datasets", "start", "pages") for p in (REPO / "content" / d).rglob("*.md")]
    touched = 0
    for f in files:
        if f.parent.name in {s for _, s, _ in dups} and f.stem in {s for s, _, _ in dups}:
            continue   # the duplicate itself
        s = f.read_text(encoding="utf-8")
        t = pat.sub(lambda m: rewrites[m.group(0)], s)
        if t != s:
            touched += 1
            if APPLY:
                f.write_text(t, encoding="utf-8")
    print(f"{touched} file(s) with links to re-point")
    if not APPLY:
        print("dry run; nothing changed")
        return 0
    rows = {r["id"]: r for r in q.read(q.QUEUE)}
    for slug, section, url in dups:
        art = REPO / "content" / "articles" / section / f"{slug}.md"
        qid = str(q.frontmatter(art).get("queue_id") or "") if art.exists() else ""
        if art.exists():
            subprocess.run(["git", "rm", "-q", str(art)], cwd=REPO, check=True)
        add_redirects(REPO / "content" / "tools" / slug / "tool.md", [f"/cornell/{section}/{slug}/", f"/{section}/{slug}/"])
        for r in rows.values():
            if (qid and r["id"] == qid) or (r["topic"] == section and f"slug={slug};" in r["angle"] and "kind=tool" not in r["angle"]):
                if r["status"] == "published":
                    q.set_status(r["id"], "rejected", q.QUEUE, force=True)
                    q.update(r["id"], q.QUEUE, top_results=f"superseded 2026-11-11: the page lives at /tools/{slug}/ (docs/v5 Phase 4); 301 in place")
    print("applied")
    return 0


if __name__ == "__main__":
    sys.exit(main())
