"""Table cells that describe what a listing leaves out ("Not printed", "Not named", "Not stated") become reader-facing cells, by column:
a rent or price column reads "On request", a lease term or lease dates column reads "Ask", an owner or manager column goes blank, and
any other column goes blank. Trailing detail after a semicolon is kept ("Not stated; available June 11 to Aug. 13, 2027" -> "Ask; available ...").
Rule (docs/v5/prelaunch-spec.md, Phase 1b): a page describes the subject's public position or tells the reader what to do, never what a
source failed to say.

    worker/.venv/bin/python scripts/prelaunch/table_cells.py <file>...            # dry run
    worker/.venv/bin/python scripts/prelaunch/table_cells.py --apply <file>...
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

CELL_RE = re.compile(r"^(not|none|nothing) (listed|published|stated|named|printed|posted|shown|given|available|provided|disclosed|confirmed|found)\b(.*)$", re.I)


def replacement(header: str, cell: str) -> str | None:
    m = CELL_RE.match(cell.strip())
    if not m:
        return None
    rest = m.group(3).strip()
    rest = rest[1:].strip() if rest.startswith(";") else rest
    h = header.lower()
    if re.search(r"rent|price|rate|cost|\$", h):
        base = "On request"
    elif re.search(r"lease|term|dates|date|deadline|hours", h):
        base = "Ask"
    elif re.search(r"gpa|minimum|requirement|credit|exam|prereq|standing", h):
        base = "None published"
    else:
        base = ""
    if rest:
        rest = rest[0].upper() + rest[1:] if not base else rest
        return f"{base}; {rest}" if base else rest
    return base


def process(text: str) -> tuple[str, int]:
    lines = text.split("\n")
    headers: list[str] = []
    n = 0
    for i, line in enumerate(lines):
        if not line.startswith("|"):
            headers = []
            continue
        cells = line.split("|")
        inner = cells[1:-1] if line.rstrip().endswith("|") else cells[1:]
        if not headers:
            headers = [c.strip() for c in inner]
            continue
        if all(re.fullmatch(r"\s*:?-+:?\s*", c) for c in inner):
            continue
        changed = False
        for j, c in enumerate(inner):
            h = headers[j] if j < len(headers) else ""
            r = replacement(h, c)
            if r is not None:
                inner[j] = f" {r} " if r else " "
                changed = True; n += 1
        if changed:
            lines[i] = "|" + "|".join(inner) + "|"
    return "\n".join(lines), n


def main(argv: list[str]) -> int:
    apply = "--apply" in argv
    for a in argv:
        if a.startswith("--"):
            continue
        p = Path(a)
        new, n = process(p.read_text(encoding="utf-8"))
        print(f"{p}: {n} cell(s) {'rewritten' if apply else 'to rewrite'}")
        if apply and n:
            p.write_text(new, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
