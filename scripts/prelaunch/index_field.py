"""Phase 9a of docs/v5/prelaunch-spec.md: every page carries an `index` field in its frontmatter, false by default.

    worker/.venv/bin/python scripts/prelaunch/index_field.py            # dry run: counts
    worker/.venv/bin/python scripts/prelaunch/index_field.py --apply    # adds `index: false` where the field is missing; never changes an existing value

Covers content/articles/**/*.md, content/tools/*/tool.md, content/datasets/*.md and content/start/*.md. The site build treats a missing
field as false, so this is bookkeeping for readers of the files and for scripts/prelaunch/waves.py, which flips the value per wave.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
APPLY = "--apply" in sys.argv


def main() -> int:
    files = [p for g in ("articles/*/*.md", "tools/*/tool.md", "datasets/*.md", "start/*.md") for p in sorted((REPO / "content").glob(g))]
    missing, present, bad = [], 0, []
    for f in files:
        text = f.read_text(encoding="utf-8")
        m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
        if not m:
            bad.append(str(f.relative_to(REPO))); continue
        if re.search(r"^index:\s*\S", m.group(1), re.M):
            present += 1; continue
        missing.append(f)
        if APPLY:
            fm = m.group(1).rstrip("\n") + "\nindex: false"
            f.write_text(f"---\n{fm}\n---\n" + text[m.end():], encoding="utf-8")
    print(f"{len(files)} pages: {present} already carry index, {len(missing)} {'given' if APPLY else 'lack'} index: false, {len(bad)} without frontmatter {bad[:3]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
