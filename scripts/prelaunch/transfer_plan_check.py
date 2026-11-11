"""Phase 7a of docs/v5/prelaunch-spec.md: does the transfer plan (intel/transfer/plan.md) carry every page the spec names?

    worker/.venv/bin/python scripts/prelaunch/transfer_plan_check.py

Prints each required page with the plan row that covers it, or MISSING. The spec's list: an admissions overview; one page per
undergraduate college with transfer requirements and recommended coursework (CALS, Arts and Sciences, Engineering, Human Ecology,
ILR, Nolan Hotel and Dyson within SC Johnson, Brooks, AAP; confirm the structure from Cornell's site); a Common Data Set section D
dataset over several years with a trend chart; the Guaranteed Transfer option; transferring from community college; transfer credit
by college; transfer housing (links the existing page), orientation and a first-semester checklist; a transfer deadlines tool or timeline.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts" / "v3"))
import plan as P  # noqa: E402

REQUIRED = [
    ("admissions overview (pillar)", r"overview|how (transfer )?admission|apply(ing)? as a transfer|transfer admissions", "pillar"),
    ("CALS page", r"\bcals\b|agriculture and life sciences", None),
    ("Arts and Sciences page", r"arts and sciences|\ba&s\b|arts-and-sciences|arts-sciences", None),
    ("Engineering page", r"engineering", None),
    ("Human Ecology page", r"human ecology", None),
    ("ILR page", r"\bilr\b|industrial and labor", None),
    ("Nolan Hotel page", r"hotel|nolan", None),
    ("Dyson page", r"dyson", None),
    ("Brooks page", r"brooks", None),
    ("AAP page", r"\baap\b|architecture, art,? and planning|architecture art", None),
    ("CDS section D dataset", r"common data set|\bcds\b|acceptance rate|admit rate", "dataset"),
    ("Guaranteed Transfer option", r"guaranteed transfer|transfer option|\bgt\b", None),
    ("community college transfer", r"community college|\btc3\b|associate", None),
    ("transfer credit evaluation", r"transfer credit|credit evaluation|credits transfer|credit transfer", None),
    ("orientation", r"orientation", None),
    ("first-semester checklist", r"first[- ]semester|first semester|checklist", None),
    ("deadlines tool or timeline", r"deadline|timeline", "tool"),
    ("transfer housing link (existing page)", r"housing", None),
]


def main() -> int:
    plan = REPO / "intel" / "transfer" / "plan.md"
    if not plan.exists():
        print("no intel/transfer/plan.md yet"); return 1
    rows, problems = P.parse_plan(plan.read_text(encoding="utf-8"))
    print(f"{len(rows)} plan rows; parse problems: {problems or 'none'}")
    missing = 0
    for name, pat, kind in REQUIRED:
        hits = [r for r in rows if re.search(pat, f"{r.get('slug','')} {r.get('title','')} {r.get('question','')}", re.I) and (kind is None or r.get("kind") == kind)]
        if hits:
            print(f"  ok       {name:<40} {hits[0].get('kind'):<13} {hits[0].get('slug')}")
        else:
            missing += 1
            print(f"  MISSING  {name}")
    print(f"{missing} required page(s) missing")
    return 0


if __name__ == "__main__":
    sys.exit(main())
