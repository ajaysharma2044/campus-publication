"""Phase 6 of docs/v5/prelaunch-spec.md, step 2: act on the image review. Every lead image judged replace gets a current, relevant,
licensed photo found with the reviewer's query (scripts/v3/images.py --replace --query, which runs scripts/v2/find_images.py: Wikimedia
Commons and Openverse, CC0, public domain, CC BY or CC BY-SA only, credited in content/images/credits.yml); when nothing relevant turns
up, or the verdict is remove, the lead image is removed. Writes reports/06-images.md.

    worker/.venv/bin/python scripts/prelaunch/replace_images.py            # dry run: the plan
    worker/.venv/bin/python scripts/prelaunch/replace_images.py --apply    # searches run serially (Commons rate-limits parallel search)

Inputs: reports/06-images-review.json (the first review, 207 lead images) and reports/06-images-rechecks.json (the skeptic's verdicts).
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import time
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts" / "v2"))
from lib import queue as q  # noqa: E402

APPLY = "--apply" in sys.argv


def page_for(slug: str) -> Path | None:
    hits = list((REPO / "content" / "articles").glob(f"*/{slug}.md"))
    if hits:
        return hits[0]
    for p in (REPO / "content" / "tools" / slug / "tool.md", REPO / "content" / "datasets" / f"{slug}.md"):
        if p.exists():
            return p
    return None


def clean_query(qs: str) -> list[str]:
    """A reviewer's query text into one to three search strings: quoted file titles become titles, 'search terms' become terms."""
    out = []
    for m in re.finditer(r"File:([^;()\n]+?)\.(?:jpe?g|png|webp|tiff?)", qs, re.I):
        out.append(m.group(1).replace("_", " ").strip())
    for m in re.finditer(r"\"([^\"]{6,80})\"", qs):
        out.append(m.group(1).strip())
    if not out:
        first = re.split(r"[;(]", qs)[0]
        first = re.sub(r"^(Wikimedia Commons|Openverse)\s*:\s*", "", first, flags=re.I).strip()
        if first:
            out.append(first[:90])
    seen, res = set(), []
    for x in out:
        if x.lower() not in seen:
            seen.add(x.lower()); res.append(x)
    return res[:3]


def remove_lead(page: Path, slug: str) -> None:
    text = page.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    fm = m.group(1)
    fm2 = re.sub(r"^images:.*?(?=^\S|\Z)", "images: []\n", fm + "\n", count=1, flags=re.S | re.M).rstrip("\n")
    page.write_text(f"---\n{fm2}\n---\n" + text[m.end():], encoding="utf-8")
    subprocess.run([sys.executable, "-c", f"import sys; sys.path.insert(0, 'scripts/v3'); import images; from pathlib import Path; images.drop_photos(Path('content/images'), {slug!r})"], cwd=REPO, check=True)


def main() -> int:
    review = {x["slug"]: x for x in json.loads((REPO / "reports" / "06-images-review.json").read_text(encoding="utf-8"))}
    rechecks = {}
    rc = REPO / "reports" / "06-images-rechecks.json"
    if rc.exists():
        rechecks = {x["slug"]: x for x in json.loads(rc.read_text(encoding="utf-8"))}
    plan = []
    for slug, x in review.items():
        final = x["final"]
        query = x.get("query") or ""
        r = rechecks.get(slug)
        if r:
            final, query = r["final"], (r.get("query") or query)
        if final == "keep":
            continue
        plan.append((slug, final, query, x.get("reason", "")))
    print(f"{len(plan)} lead image(s) to act on: replace {sum(1 for p in plan if p[1] == 'replace')}, remove {sum(1 for p in plan if p[1] == 'remove')}")
    rows = []
    for slug, final, query, reason in plan:
        page = page_for(slug)
        if not page:
            rows.append((slug, final, "page not found (moved or merged)", "")); continue
        qs = clean_query(query) if final == "replace" else []
        fm_before = q.frontmatter(page)
        before = (fm_before.get("images") or [{}])[0] if fm_before.get("images") else {}
        if not APPLY:
            rows.append((slug, final, "; ".join(qs) or "(remove)", str(before.get("caption", ""))[:80])); continue
        if final == "replace" and qs:
            cmd = [str(REPO / "worker/.venv/bin/python"), "scripts/v3/images.py", str(page), "--replace", "--no-fallback"] + [a for s in qs for a in ("--query", s)]
            out = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, timeout=1200)
            fm_after = q.frontmatter(page)
            after = (fm_after.get("images") or [{}])[0] if fm_after.get("images") else {}
            if after.get("file"):
                rows.append((slug, "replaced", "; ".join(qs), f"{after.get('caption', '')[:70]} ({after.get('license', '')})"))
            else:
                rows.append((slug, "removed (no relevant licensed photo for the query)", "; ".join(qs), ""))
            time.sleep(0.7)
        else:
            remove_lead(page, slug)
            rows.append((slug, "removed", reason[:90], ""))
    if APPLY:   # the scorer (scripts/prelaunch/score_pages.py) reads this: a replaced lead image passed Phase 6, a removed one leaves no image to judge
        final = {slug: ("removed" if outcome.startswith("removed") else "keep") for slug, outcome, _, _ in rows if "not found" not in outcome}
        (REPO / "reports" / "06-images-final.json").write_text(json.dumps(final, indent=1, sort_keys=True), encoding="utf-8")
    out = REPO / "reports" / "06-images.md"
    L = [f"# Phase 6: lead images ({date.today().isoformat()})", "",
         "Every lead image was judged by a reviewer (reports/06-images-review.json: shows the subject, generic, caption true, older than 20 years) and every replace or remove verdict rechecked by a skeptic (reports/06-images-rechecks.json). "
         "Replacements come from Wikimedia Commons or Openverse through scripts/v2/find_images.py (CC0, public domain, CC BY or CC BY-SA only; author, source, license name and license link recorded in content/images/credits.yml and shown under the photo). "
         "A page whose search found nothing relevant lost its lead image rather than keep a wrong one. Captions describe what the new photo shows (the file's title from Commons).", "",
         f"{len(rows)} lead image(s) acted on{' (dry run)' if not APPLY else ''}.", "", "| Page | Outcome | Search or reason | New photo |", "|---|---|---|---|"]
    for slug, outcome, qtext, new in rows:
        L.append(f"| {slug} | {outcome} | {qtext.replace('|', '/')} | {new.replace('|', '/')} |")
    out.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"written {out.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
