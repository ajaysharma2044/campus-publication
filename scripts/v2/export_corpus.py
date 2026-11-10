#!/usr/bin/env python
"""One-time export of the crawled page text from Postgres to corpus/<host>/<path>.txt (EduExplained v2 spec, "Repo cleanup").

    set -a; . worker/.env; set +a; worker/.venv/bin/python scripts/v2/export_corpus.py [--out corpus]

Latest successful snapshot per source; every host (official or not). Each file starts with the URL, title and fetch date.
After this, v2 reads the corpus with Grep and never needs the database for content.
"""
import argparse
import os
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit

import psycopg


def path_for(url: str) -> Path:
    u = urlsplit(url)
    host = (u.hostname or "unknown").lower()
    path = re.sub(r"[^A-Za-z0-9._/-]+", "-", u.path or "/").strip("/")
    if not path:
        path = "index"
    if path.endswith("/"):
        path += "index"
    parts = [p[:120] for p in path.split("/") if p]
    name = parts[-1]
    if re.search(r"\.(html?|php|aspx?|pdf)$", name, re.I):
        name = re.sub(r"\.(html?|php|aspx?|pdf)$", "", name, flags=re.I)
    parts[-1] = name + ".txt"
    return Path(host, *parts)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="corpus")
    ap.add_argument("--dsn", default=os.environ.get("DATABASE_URL"))
    args = ap.parse_args(argv)
    if not args.dsn:
        print("DATABASE_URL is not set (set -a; . worker/.env; set +a)", file=sys.stderr)
        return 2
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    n = 0
    seen: set[Path] = set()
    with psycopg.connect(args.dsn) as conn, conn.cursor() as cur:
        cur.execute("""SELECT DISTINCT ON (s.source_id) COALESCE(s.final_url, r.canonical_url) AS url, r.title, s.fetched_at, s.retained_text
                       FROM fetch_snapshots s JOIN source_registry r ON r.id=s.source_id
                       WHERE s.outcome='ok' AND s.retained_text IS NOT NULL AND length(s.retained_text) >= 80
                       ORDER BY s.source_id, s.fetched_at DESC""")
        for url, title, fetched_at, text in cur:
            p = path_for(url)
            stem = p
            k = 2
            while p in seen:   # two URLs that map to one file (query strings, trailing slashes) each keep their own file
                p = stem.with_name(f"{stem.stem}-{k}{stem.suffix}")
                k += 1
            seen.add(p)
            f = out / p
            f.parent.mkdir(parents=True, exist_ok=True)
            head = f"URL: {url}\nTITLE: {title or ''}\nFETCHED: {fetched_at.date().isoformat() if fetched_at else ''}\n\n"
            f.write_text(head + text.strip() + "\n", encoding="utf-8")
            n += 1
    hosts = sorted({p.parts[0] for p in seen})
    print(f"exported {n} pages to {out}/ across {len(hosts)} hosts: {', '.join(hosts[:12])}{' …' if len(hosts) > 12 else ''}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
