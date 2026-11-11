"""Compile reports/gaps.md (docs/v5/prelaunch-spec.md, Phase 1b): every gap decision the writers and the Phase 2 rework logged.

    worker/.venv/bin/python scripts/prelaunch/gaps.py

A gap decision is a line under a "## Gaps" heading in content/edits/<slug>.md (the writer's edit log), in the form
    - <missing item> | sources tried: <list> | outcome: <answered with <source> | section removed, title changed | merged into /path/ with a 301>
Phase 2 writes the same lines into reports/gaps-phase2.md directly. This script merges both into reports/gaps.md, one table, sorted by page.
"""
from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
EDITS = REPO / "content" / "edits"
PHASE2 = REPO / "reports" / "gaps-phase2.md"
OUT = REPO / "reports" / "gaps.md"
LINE_RE = re.compile(r"^- (.+?) \| sources tried: (.+?) \| outcome: (.+)$")


def gaps_in(text: str) -> list[tuple[str, str, str]]:
    out = []
    section = False
    for line in text.split("\n"):
        if line.startswith("## "):
            section = line.strip().lower().startswith("## gaps")
            continue
        if section:
            m = LINE_RE.match(line.strip())
            if m:
                out.append((m.group(1).strip(), m.group(2).strip(), m.group(3).strip()))
    return out


def main() -> int:
    rows: list[tuple[str, str, str, str, str]] = []
    if EDITS.exists():
        for f in sorted(EDITS.glob("*.md")):
            for item, tried, outcome in gaps_in(f.read_text(encoding="utf-8")):
                rows.append((f.stem, item, tried, outcome, "writer edit log"))
    if PHASE2.exists():
        page = ""
        for line in PHASE2.read_text(encoding="utf-8").split("\n"):
            if line.startswith("## "):
                page = line[3:].strip()
            m = LINE_RE.match(line.strip())
            if m and page:
                rows.append((page, m.group(1).strip(), m.group(2).strip(), m.group(3).strip(), "Phase 2 rework"))
    rows.sort()
    L = [f"# Research gaps and what was done about them", "",
         f"Compiled {date.today().isoformat()} by scripts/prelaunch/gaps.py from the writers' edit logs (content/edits/<slug>.md, \"## Gaps\") and reports/gaps-phase2.md. "
         "Rule (docs/v5/prelaunch-spec.md, Phase 1b): a page never tells the reader what the sources or the page lack; a gap is answered from the source checklist or the promise is removed.", "",
         f"{len(rows)} gap decision(s).", "",
         "| Page | Missing item | Sources tried | Outcome | Logged by |", "|---|---|---|---|---|"]
    for page, item, tried, outcome, by in rows:
        L.append(f"| {page} | {item.replace('|', '/')} | {tried.replace('|', '/')} | {outcome.replace('|', '/')} | {by} |")
    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"{len(rows)} gap decision(s) -> {OUT.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
