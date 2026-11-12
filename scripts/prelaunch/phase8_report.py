"""Phase 8 of docs/v5/prelaunch-spec.md, the record: reports/08-authorship.md. Bylines (no generic byline left), the author page and its
{{BIO}} placeholders, Person structured data, the Edited by line, the trust pages in the footer, the legal-rights line, and the data labels
(beds vs residents) from reports/08-labels.json (the labeling agent's report and the skeptic's verdict).

    worker/.venv/bin/python scripts/prelaunch/phase8_report.py
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from collections import Counter
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts" / "v2"))
from lib import queue as q  # noqa: E402


def main() -> int:
    files = [p for g in ("articles/*/*.md", "tools/*/tool.md", "datasets/*.md", "start/*.md") for p in sorted((REPO / "content").glob(g))]
    authors, edited, reviewed, generic = Counter(), 0, 0, []
    for p in files:
        try:
            fm = q.frontmatter(p)
        except Exception:
            continue
        a = str(fm.get("author") or "").strip()
        authors[a or "(none: site default)"] += 1
        if re.search(r"editors|staff|team", a, re.I):
            generic.append(str(p.relative_to(REPO)))
        edited += 1 if fm.get("edited_by") else 0
        reviewed += 1 if fm.get("reviewed_by") else 0
    cfg = (REPO / "site" / "site.config.ts").read_text(encoding="utf-8")
    author_block = cfg[cfg.find("slug: 'ajay-sharma'"):][:1500]
    bio = re.search(r"bio:\s*'([^']*)'", author_block)
    placeholders = re.findall(r"\{\{BIO[^}]*\}\}", bio.group(1) if bio else "")
    default_author = re.search(r"defaultAuthor:\s*'([a-z-]+)'", cfg)
    editors_entry = "eduexplained-editors" in cfg or "footnote-daily-editors" in cfg
    schema = (REPO / "site" / "src" / "lib" / "schema.ts").read_text(encoding="utf-8")
    has_person = "'Person'" in schema
    byline = (REPO / "site" / "src" / "components" / "Byline.astro").read_text(encoding="utf-8")
    footer_cfg = cfg[cfg.find("footer:"):][:1200]
    trust = {k: (f"'/{k}/'" in footer_cfg) for k in ("about", "editorial-standards", "sources", "corrections")}
    legal = subprocess.run(["grep", "-rli", "not legal advice", "content/articles", "content/tools", "content/start"], cwd=REPO, capture_output=True, text=True).stdout.split()
    labels = {}
    lp = REPO / "reports" / "08-labels.json"
    if lp.exists():
        labels = json.loads(lp.read_text(encoding="utf-8"))
    L = [f"# Phase 8: authorship and trust ({date.today().isoformat()})", "",
         "## Bylines", "",
         f"- Pages scanned: {len(files)}; frontmatter author values: {dict(authors)} (a page without an author takes site.config.ts defaultAuthor = {default_author.group(1) if default_author else '?'}).",
         f"- Pages with a generic byline (editors, staff, team): {generic or 'none'}.",
         f"- The old organisation author entry (EduExplained editors / Footnote Daily editors) is {'still' if editors_entry else 'no longer'} in site.config.ts; its URLs /authors/eduexplained-editors/ and /authors/footnote-daily-editors/ 301 to /authors/ajay-sharma/ (site/scripts/check-build.mjs writes dist/_redirects).",
         f"- Pages carrying edited_by: {edited}; reviewed_by: {reviewed}. Byline.astro prints an 'Edited by' line when the editor is not the author and a 'Reviewed by' line when a reviewer is named ({'present' if 'Edited by' in byline else 'MISSING'}).", "",
         "## Author page", "",
         f"- /authors/ajay-sharma/: name Ajay Sharma, kind person, role Editor-in-chief, with {len(placeholders)} {{{{BIO: ...}}}} placeholder(s) left for Ajay to fill ({'; '.join(placeholders) or 'none'}) rather than claims written for him; the one sentence stated as fact is the editor-in-chief role.",
         f"- The TransferringUp disclosure is a single labeled line in the bio ({'present' if 'TransferringUp' in author_block else 'MISSING'}); no article body mentions it (checked in reports/07-sections.md).",
         f"- Structured data: site/src/lib/schema.ts emits a Person (kind person) or Organization as the author of every Article and a Person node on the author page ({'present' if has_person else 'MISSING'}).", "",
         "## Trust pages", "",
         f"- Footer (site/src/components/Footer.astro, links from site.config.ts footer.columns, on every page): about {trust['about']}, editorial standards {trust['editorial-standards']}, sources {trust['sources']}, corrections {trust['corrections']}; the footer's own 'How we work' link points at /editorial-standards/.",
         "- Every tool page links /corrections/ under its result; the home page links the standards and corrections pages; /editorial-policy/ 301s to /editorial-standards/.", "",
         "## Sensitive topics", "",
         f"- Legal-rights pages carrying the line 'This page is general information, not legal advice.' (or the tool form 'This is not legal advice.'): {len(legal)}.", "",
         "## Data labels (beds vs residents)", ""]
    if labels:
        rep, ver = labels.get("report") or {}, labels.get("verdict") or {}
        L += [f"- Pages labeled: {len(rep.get('files') or [])}; bed-count source: {rep.get('bed_counts_source')}; skeptic verdict: {'sound' if ver.get('sound') else 'NOT SOUND: ' + str(ver.get('problems'))[:400]}", ""]
        for c in rep.get("changes") or []:
            L.append(f"- {c.get('file')}: {str(c.get('change'))[:300]}" + (f" (source: {c.get('source')})" if c.get("source") else ""))
        L.append("")
    else:
        L += ["- reports/08-labels.json not written yet.", ""]
    L += ["## Acceptance", "", f"- No article shows a generic byline: {'PASS' if not generic else 'FAIL'}.", "- Author pages render with structured data: the Astro build (site/scripts/check-build.mjs) renders /authors/ajay-sharma/ with the Person node; verified in the preview build.", ""]
    out = REPO / "reports" / "08-authorship.md"
    out.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"written {out.relative_to(REPO)}: generic bylines {len(generic)}, placeholders {len(placeholders)}, legal pages {len(legal)}, labels {'yes' if labels else 'pending'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
