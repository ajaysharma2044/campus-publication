"""Phase 7 of docs/v5/prelaunch-spec.md, the record: reports/07-sections.md. The transfer section (7a) page by page with its kind and queue
status, the spec's required-page check (scripts/prelaunch/transfer_plan_check.py), the acceptance test (at least 10 published pages including
the Common Data Set dataset), the TransferringUp rule (no promotion in any body), and the other hubs (7b): visible hubs with their article
counts and the hubs hidden from navigation until they reach five.

    worker/.venv/bin/python scripts/prelaunch/phase7_report.py
"""
from __future__ import annotations

import re
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts" / "v2"))
from lib import queue as q  # noqa: E402


def fm_of(p: Path) -> dict:
    try:
        return q.frontmatter(p)
    except Exception:
        return {}


def main() -> int:
    rows = {r["id"]: r for r in q.read(q.QUEUE)}
    # transfer pages on disk
    pages = []
    for p in sorted((REPO / "content" / "articles" / "transfer").glob("*.md")):
        fm = fm_of(p); r = rows.get(str(fm.get("queue_id") or ""), {})
        pages.append((f"/transfer/{p.stem}/", str(fm.get("kind") or "article"), r.get("status", "no queue row"), str(fm.get("title") or "")))
    for p in sorted((REPO / "content" / "tools").glob("*/tool.md")):
        fm = fm_of(p); r = rows.get(str(fm.get("queue_id") or ""), {})
        if r.get("topic") == "transfer" or "transfer" in p.parent.name:
            pages.append((f"/tools/{p.parent.name}/", "tool", r.get("status", "no queue row"), str(fm.get("title") or "")))
    for p in sorted((REPO / "content" / "datasets").glob("*.md")):
        fm = fm_of(p); r = rows.get(str(fm.get("queue_id") or ""), {})
        if r.get("topic") == "transfer" or "transfer" in p.stem:
            pages.append((f"/datasets/{p.stem}/", "dataset", r.get("status", "no queue row"), str(fm.get("title") or "")))
    starts = []
    for p in sorted((REPO / "content" / "start").glob("*.md")):
        fm = fm_of(p)
        if "transfer" in (fm.get("topics") or []) or fm.get("topic") == "transfer" or p.stem.startswith("transfer"):
            starts.append((f"/start/{p.stem}/", str(fm.get("title") or "")))
    published = [x for x in pages if x[2] == "published"]
    cds = []
    for x in published:
        if x[1] == "dataset":
            p = REPO / "content" / "datasets" / f"{x[0].split('/')[2]}.md"
            if re.search(r"common data set", p.read_text(encoding="utf-8"), re.I):
                cds.append(x)
    # TransferringUp rule
    tu = subprocess.run(["grep", "-rli", "transferringup\\|transferring up", "content/articles", "content/tools", "content/datasets", "content/start"], cwd=REPO, capture_output=True, text=True).stdout.split()
    # required pages
    chk = subprocess.run([sys.executable, "scripts/prelaunch/transfer_plan_check.py"], cwd=REPO, capture_output=True, text=True).stdout.strip().splitlines()
    # hubs: visible topics and hidden ones from site.config.ts
    cfg = (REPO / "site" / "site.config.ts").read_text(encoding="utf-8")
    hidden = set(re.findall(r"\{ id: '([a-z-]+)', hidden: true", cfg))
    topics = re.findall(r"\{ id: '([a-z-]+)',(?: hidden: true,)? label:", cfg)
    counts = Counter()
    for r in rows.values():
        if r["status"] == "published":
            counts[r["topic"]] += 1
    on_disk = Counter(p.parent.name for p in (REPO / "content" / "articles").glob("*/*.md"))
    L = [f"# Phase 7: the empty sections ({date.today().isoformat()})", "",
         "7a. The transfer section was built with the v3 pipeline (scripts/v3: research in five lanes, brief, readers, plan, write, check, publish) as topic `transfer` in topics.yml, "
         "data-first: a Common Data Set section D dataset with its CSV and trend chart, one page per undergraduate college (the college structure confirmed from Cornell's site during research), "
         "the Guaranteed Transfer option, community college transfer, credit evaluation by college, housing (linking the existing page), orientation, a first-semester checklist, and a deadlines tool. "
         "Every page carries the v3 publish requirements (lint, lead photo or figures, reader blocks, sources) and passed the check step before publish.sh took it.", "",
         f"- Transfer pages on disk: {len(pages)} ({Counter(x[1] for x in pages)})",
         f"- Published: {len(published)} (articles {sum(1 for x in published if x[1] not in ('tool', 'dataset'))}, tools {sum(1 for x in published if x[1] == 'tool')}, datasets {sum(1 for x in published if x[1] == 'dataset')}); not yet published: {[x[0] for x in pages if x[2] != 'published'] or 'none'}",
         f"- Common Data Set dataset published: {'yes: ' + ', '.join(x[0] for x in cds) if cds else 'NO'}",
         f"- Start paths that include the transfer section: {len(starts)}",
         f"- Acceptance (at least 10 published pages including the CDS dataset): {'PASS' if len(published) >= 10 and cds else 'FAIL'}",
         f"- TransferringUp rule (no promotion in any body; the only mention is the labeled line in the author bio): pages mentioning it: {tu or 'none'}", "",
         "## Required pages (scripts/prelaunch/transfer_plan_check.py)", "", "```"] + chk + ["```", "",
         "## Transfer pages", "", "| URL | Kind | Queue status | Title |", "|---|---|---|---|"]
    for url, kind, st, title in pages:
        L.append(f"| {url} | {kind} | {st} | {title.replace('|', '/')} |")
    L += ["", "## Start paths", ""] + [f"- {u}: {t}" for u, t in starts] + ["",
          "## 7b. Other hubs", "",
          "Rule: a hub with fewer than five quality articles is hidden from navigation and stays unindexed (Phase 9 keeps every page noindex until a wave releases it). "
          "Hidden topics are set with `hidden: true` in site/site.config.ts (Phase 3); their pages still build at their URLs.", "",
          "| Topic | Published queue rows (all kinds) | Articles on disk | Navigation |", "|---|---|---|---|"]
    for t in sorted(set(topics) | set(on_disk) | set(counts)):
        L.append(f"| {t} | {counts.get(t, 0)} | {on_disk.get(t, 0)} | {'hidden' if t in hidden else 'visible'} |")
    thin = [t for t in topics if t not in hidden and on_disk.get(t, 0) < 5]
    L += ["", f"- Visible hubs with fewer than 5 articles: {thin or 'none'}", f"- Hidden hubs: {sorted(hidden) or 'none'}", ""]
    out = REPO / "reports" / "07-sections.md"
    out.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"written {out.relative_to(REPO)}: {len(published)} published of {len(pages)}; CDS {'yes' if cds else 'NO'}; TransferringUp pages: {tu}; thin visible hubs: {thin}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
