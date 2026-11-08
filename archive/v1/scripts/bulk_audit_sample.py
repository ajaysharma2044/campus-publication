#!/usr/bin/env python3
"""B4 (specs/bulk-mode.md): pick a random sample of pages published by a bulk run and write an audit packet for a FRESH review.

    worker/.venv/bin/python scripts/bulk_audit_sample.py --run-id <run> [--n 10] [--seed 7]

Writes build/runs/bulk/audit-<run>/: one folder per page with the rendered page text, the page's claims with their verbatim quotes
and source URLs, and the source page texts; plus prompt.md for the reviewer (a fresh `claude -p` with Read/Grep only, or a subagent),
which must return findings as JSON: facts that do not match their sources, prose that reads badly, and internal terms. The findings are
logged in the day's digest by `--log-findings <file>` once the reviewer has replied.
"""
from __future__ import annotations

import argparse
import html as htmlmod
import json
import random
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "worker"))

from campus_worker.config import get_settings  # noqa: E402
from campus_worker.db import connect  # noqa: E402

INTERNAL_TERMS = ("pages we opened", "could not verify", "snapshot", "snippet", "claim id", "verifier", "rubric", "no human editor", "automated system", "staging")


def page_text(path: str) -> str:
    f = ROOT / "build" / "site" / path.strip("/") / "index.html"
    if not f.exists():
        return ""
    s = f.read_text()
    m = re.search(r"<main.*?</main>", s, re.S)
    body = m.group(0) if m else s
    body = re.sub(r"<script.*?</script>|<style.*?</style>", "", body, flags=re.S)
    body = re.sub(r"<(h[1-6]|p|li|tr|caption|figcaption)[^>]*>", "\n", body)
    return re.sub(r"\n{3,}", "\n\n", htmlmod.unescape(re.sub(r"<[^>]+>", " ", body))).strip()


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--n", type=int, default=10)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--log-findings", help="a JSON file of reviewer findings to append to today's digest")
    args = ap.parse_args(argv)
    out = ROOT / "build" / "runs" / "bulk" / f"audit-{args.run_id}"
    if args.log_findings:
        findings = json.loads(Path(args.log_findings).read_text())
        day = datetime.now(timezone.utc).date().isoformat()
        digest = ROOT / "docs" / "digest" / f"{day}.md"
        lines = [f"\n## Bulk-mode audit sample ({args.run_id}, {len(findings.get('pages', []))} pages, fresh review)\n"]
        for p in findings.get("pages", []):
            lines.append(f"- `{p.get('path')}`: facts match sources: {p.get('facts_match')}; reads well: {p.get('reads_well')}; internal terms: {p.get('internal_terms') or 'none'}; notes: {p.get('notes', '')[:300]}")
        lines.append(f"- Verdict: {findings.get('verdict', '')}\n")
        digest.parent.mkdir(parents=True, exist_ok=True)
        with digest.open("a") as fh:
            fh.write("\n".join(lines))
        print(f"logged {len(findings.get('pages', []))} page findings to {digest}")
        return 0
    settings = get_settings()
    conn = connect(settings.database_url)
    with conn.cursor() as cur:
        cur.execute("SELECT bp.path, bp.version_id, bp.page_id, bp.draft FROM bulk_pages bp WHERE bp.run_id=%s AND bp.stage='published' ORDER BY bp.path", (args.run_id,))
        pages = [dict(r) for r in cur.fetchall()]
    if not pages:
        print("no published pages for that run"); return 1
    random.Random(args.seed).shuffle(pages)
    sample = pages[: args.n]
    out.mkdir(parents=True, exist_ok=True)
    index = []
    for i, p in enumerate(sample, start=1):
        folder = out / f"{i:02d}-{p['path'].strip('/').rsplit('/', 1)[-1][:50]}"
        folder.mkdir(exist_ok=True)
        (folder / "page.txt").write_text(page_text(p["path"]))
        with conn.cursor() as cur:
            cur.execute("""SELECT c.id, c.field, cs.excerpt, COALESCE(s.final_url, r.canonical_url) AS url, s.id AS snapshot_id, s.retained_text
                           FROM page_claims pc JOIN claims c ON c.id=pc.claim_id JOIN claim_sources cs ON cs.claim_id=c.id JOIN fetch_snapshots s ON s.id=cs.snapshot_id JOIN source_registry r ON r.id=s.source_id
                           WHERE pc.page_version_id=%s AND r.source_kind LIKE 'official%%' ORDER BY c.field""", (p["version_id"],))
            rows = [dict(r) for r in cur.fetchall()]
        (folder / "claims.json").write_text(json.dumps([{"claim_id": str(r["id"]), "field": r["field"], "quote": r["excerpt"], "source_url": r["url"], "source_file": f"source-{str(r['snapshot_id'])[:8]}.txt"} for r in rows], indent=1))
        for r in rows:
            (folder / f"source-{str(r['snapshot_id'])[:8]}.txt").write_text(r["retained_text"] or "")
        flagged = [t for t in INTERNAL_TERMS if t in (folder / "page.txt").read_text().lower()]
        index.append({"folder": folder.name, "path": p["path"], "claims": len(rows), "internal_terms_found_by_code": flagged})
    (out / "index.json").write_text(json.dumps(index, indent=1))
    (out / "prompt.md").write_text(f"""# Audit {len(sample)} bulk-mode pages (fresh review, specs/bulk-mode.md B4)

You have not seen these pages before. For each folder under {out} read `page.txt` (the rendered page), `claims.json` (every fact the page
relies on, with the exact quote and the source file) and the `source-*.txt` files. Judge three things per page and nothing else:
1. facts_match: does every number, date, dollar amount, rule and name on the page appear in a quote that is really on its source page? List each mismatch.
2. reads_well: would a student get a direct, practical answer in the first paragraph and find the rest clear? Name awkward or repetitive passages.
3. internal_terms: any of {', '.join(INTERNAL_TERMS)} or audit language on the page.
Reply with ONE JSON object: {{"pages": [{{"path": "...", "facts_match": true|false, "mismatches": ["..."], "reads_well": true|false, "notes": "...", "internal_terms": ["..."]}}], "verdict": "<one sentence>"}}.
Then the coordinator runs: worker/.venv/bin/python scripts/bulk_audit_sample.py --run-id {args.run_id} --log-findings <your json file>
""")
    print(json.dumps({"audit_dir": str(out), "pages": index}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
