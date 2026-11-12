"""Cornell Student and Campus Life moved its housing site (checked 2026-11-11, build/linkcheck/scl-status.txt: 67 of 270 cited SCL URLs
returned 404). Three kinds of fix, all verified with curl on 2026-11-11:
  1. the prefix .../housing/housing-and-residential-life-and-faculty-involvement-campus/ became .../housing/housing-details/ (26 URLs, all 200);
  2. the Off-Campus Living pages moved under .../housing/living-off-campus/ (ithaca-neighborhoods, safe-living-environments, signing-lease,
     rental-listings-resources, checklists-and-considerations, moving-and-out, the housemate questionnaire, subletting), two program-house pages
     moved under upperlevel-undergraduate-campus-housing, apply-housing became apply-housing-campus, and the Access Fund is at /FGLI/access-fund
     (build/linkcheck/scl-map.json "live");
  3. pages Cornell removed with no live successor (the housing directory, the RA employment pages, the central campus service center) point at
     the Wayback Machine snapshot closest to 2025-11-01 (build/linkcheck/scl-map.json "wayback"); a page with neither stays for the rework agents.

    worker/.venv/bin/python scripts/prelaunch/fix_scl_urls.py            # dry run
    worker/.venv/bin/python scripts/prelaunch/fix_scl_urls.py --apply
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
OLD = "https://scl.cornell.edu/residential-life/housing/housing-and-residential-life-and-faculty-involvement-campus/"
NEW = "https://scl.cornell.edu/residential-life/housing/housing-details/"
APPLY = "--apply" in sys.argv


def main() -> int:
    m = json.loads((REPO / "build" / "linkcheck" / "scl-map.json").read_text(encoding="utf-8"))
    table = dict(m["live"]); table.update(m["wayback"])
    # longest first so a landing-page URL never clips a deeper one
    # not preceded by "/" (a URL already wrapped in a Wayback snapshot keeps its inner URL) and not followed by more path
    pat = re.compile(r"(?<![/A-Za-z0-9])(?:" + "|".join(re.escape(k) for k in sorted(table, key=len, reverse=True)) + r")(?![A-Za-z0-9/-])")
    files = hits = 0
    for p in sorted((REPO / "content").rglob("*")):
        if p.suffix not in (".md", ".html", ".yml", ".json", ".csv") or not p.is_file():
            continue
        s = p.read_text(encoding="utf-8")
        t = s.replace(OLD, NEW).replace(OLD.replace("https://scl.cornell.edu/", "https://scl.cornell.edu/sub/"), NEW)   # the /sub/ mirror of the old path
        t, n = pat.subn(lambda mm: table[mm.group(0)], t)
        n += s.count(OLD)
        if t != s:
            files += 1; hits += n
            if APPLY:
                p.write_text(t, encoding="utf-8")
    print(f"{hits} URL(s) in {files} file(s) {'rewritten' if APPLY else 'to rewrite (dry run)'}; unresolved (left for the rework agents): {m['unresolved']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
