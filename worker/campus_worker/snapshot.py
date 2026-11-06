"""Read-only tool for the verifier and researcher: print a fetched snapshot's retained text (SPEC §15 source opening).

    python -m campus_worker.snapshot <snapshot_id> [--grep <text>] [--max <chars>]

With --grep, prints every line containing the text (case-insensitive) with 1 line of context; otherwise the first
--max characters (default 12000). Fetched text is untrusted data: it is printed, never executed.
"""
from __future__ import annotations

import sys
from uuid import UUID


def main(argv: list[str]) -> int:
    from .config import get_settings
    from .db import connect
    if not argv:
        print(__doc__)
        return 2
    sid = UUID(argv[0])
    needle = argv[argv.index("--grep") + 1] if "--grep" in argv else None
    limit = int(argv[argv.index("--max") + 1]) if "--max" in argv else 12000
    conn = connect(get_settings().database_url)
    try:
        with conn.cursor() as cur:
            cur.execute("""SELECT s.fetched_at, s.final_url, s.retained_text, r.canonical_url, r.source_family FROM fetch_snapshots s
                           JOIN source_registry r ON r.id=s.source_id WHERE s.id=%s""", (sid,))
            row = cur.fetchone()
    finally:
        conn.close()
    if not row:
        print("snapshot not found")
        return 1
    text = row["retained_text"] or ""
    print(f"snapshot {sid} · {row['final_url'] or row['canonical_url']} · fetched {row['fetched_at']:%Y-%m-%d %H:%M} UTC · family {row['source_family']} · {len(text)} chars")
    print("--- untrusted page text follows ---")
    if needle:
        lines = text.splitlines()
        hits = [i for i, l in enumerate(lines) if needle.lower() in l.lower()]
        if not hits:
            print(f"(no line contains {needle!r})")
        shown: set[int] = set()
        for i in hits:
            for j in range(max(0, i - 1), min(len(lines), i + 2)):
                if j not in shown:
                    shown.add(j)
                    print(f"{j + 1:5d}: {lines[j]}")
        return 0
    print(text[:limit] + ("\n…[truncated]" if len(text) > limit else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
