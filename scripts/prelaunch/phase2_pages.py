"""Phase 2 input: every page scripts/lint-content.py flags, with what the rework agent needs (matches, kind, brief and fact file).

    worker/.venv/bin/python scripts/prelaunch/phase2_pages.py   -> reports/02-pages.json (+ a count on stdout)
"""
from __future__ import annotations

import json
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts" / "v2"))
from lib import queue as q  # noqa: E402

MANDATORY = {
    "voting-in-ithaca-cornell-student-register-polling-place": "MANDATORY (spec Phase 2): add New York registration deadlines, how to register, and how to find a polling place, sourced to the NYS Board of Elections (elections.ny.gov) and the Tompkins County Board of Elections; link the official polling place lookup instead of listing locations.",
    "is-collegetown-safe-cornell-dorm-security-crime": "MANDATORY (spec Phase 2): add campus crime statistics from Cornell's most recent Annual Security and Fire Safety Report (Clery Act), with the report year stated, plus any official Ithaca Police data available; keep the existing building-safety and late-night-transit content.",
    "ithaca-landlords-to-avoid-collegetown-reviews": "MANDATORY (spec Phase 2): keep the approach (no naming without evidence). The page is being renamed by the orchestrator to how-to-check-an-ithaca-landlords-record (new title: How to check an Ithaca landlord's record before you sign); you edit the body under its NEW path and do not rename anything yourself; do not touch the images block (the lead photo is replaced in Phase 6).",
}


def main() -> int:
    out = subprocess.run([sys.executable, str(REPO / "scripts" / "lint-content.py"), "--json"], capture_output=True, text=True, cwd=REPO)
    hits = json.loads(out.stdout)["hits"]
    by_file = defaultdict(list)
    for h in hits:
        by_file[h["file"]].append({"line": h["line"], "match": h["match"], "snippet": h["snippet"]})
    pages = []
    for f, ms in sorted(by_file.items()):
        p = REPO / f
        fm = q.frontmatter(p)
        parts = f.split("/")
        if parts[1] == "articles":
            section, slug, url = parts[2], p.stem, f"/cornell/{parts[2]}/{p.stem}/"
        elif parts[1] == "tools":
            section, slug, url = str(fm.get("topic") or ""), parts[2], f"/tools/{parts[2]}/"
        elif parts[1] == "datasets":
            section, slug, url = str(fm.get("topic") or ""), p.stem, f"/datasets/{p.stem}/"
        else:
            section, slug, url = parts[1], p.stem, f"/{parts[1]}/{p.stem}/"
        topic = str(fm.get("topic") or section)
        intel = REPO / "intel"
        brief = next((str(d.relative_to(REPO)) for d in intel.glob("*/brief.md") if (q.frontmatter(p) or True) and d.parent.name in (topic, {"housing": "off-campus-housing"}.get(topic, topic))), "")
        facts = next((str(d.relative_to(REPO)) for d in intel.glob("*/facts.csv") if d.parent.name in (topic, {"housing": "off-campus-housing"}.get(topic, topic))), "")
        pages.append({"file": f, "url": url, "section": section, "slug": slug, "title": str(fm.get("title") or ""), "kind": str(fm.get("kind") or ("idea-run" if fm.get("idea_id") else "v2")),
                      "queue_id": str(fm.get("queue_id") or ""), "idea_id": str(fm.get("idea_id") or ""), "brief": brief, "facts": facts, "matches": ms,
                      "mandatory": MANDATORY.get(slug, "")})
    dest = REPO / "reports" / "02-pages.json"
    dest.write_text(json.dumps(pages, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"{len(pages)} page(s), {len(hits)} matches -> {dest.relative_to(REPO)}; mandatory present: {[p['slug'] for p in pages if p['mandatory']]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
