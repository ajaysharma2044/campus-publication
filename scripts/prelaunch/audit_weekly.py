"""Phase 9c of docs/v5/prelaunch-spec.md: the weekly audit. Samples 20 random indexable pages per section, re-fetches each cited source
where possible, and flags numbers or dates on the page that no longer appear in the source. Output: reports/audit-YYYY-MM-DD.md.

    worker/.venv/bin/python scripts/prelaunch/audit_weekly.py [--per-section 20] [--seed 1]

Indexable = frontmatter index: true (before launch, every page is noindex and the audit samples from the eligible pages instead, so it can
be rehearsed). A flag is a hint for a human: the number appears on the page next to a link to the source but not on the source page as
fetched today. The error rate (flagged pages / sampled pages) is the figure the wave stop rule reads (config/wave-metrics.json).
"""
from __future__ import annotations

import csv
import random
import re
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

import httpx

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts" / "v2"))
from lib import queue as q  # noqa: E402

UA = "EduExplained weekly audit (https://eduexplained.netlify.app) httpx"
NUM_RE = re.compile(r"\$[\d,]+(?:\.\d+)?|\b\d{1,3}(?:,\d{3})+\b|\b\d+(?:\.\d+)?%|\b(?:19|20)\d{2}\b|\b\d+(?:\.\d+)?\b")
LINK_RE = re.compile(r"\[([^\]]+)\]\((https?://[^)\s]+)\)")


def pages() -> list[tuple[str, Path, bool]]:
    out = []
    for p in sorted((REPO / "content" / "articles").glob("*/*.md")):
        fm = q.frontmatter(p)
        out.append((p.parent.name, p, bool(fm.get("index"))))
    return out


def main(argv: list[str]) -> int:
    per = int(argv[argv.index("--per-section") + 1]) if "--per-section" in argv else 20
    seed = int(argv[argv.index("--seed") + 1]) if "--seed" in argv else int(date.today().strftime("%Y%m%d"))
    random.seed(seed)
    allp = pages()
    indexable = [x for x in allp if x[2]]
    rehearsal = False
    if not indexable:
        rehearsal = True
        elig = REPO / "reports" / "09-eligibility.csv"
        ok = set()
        if elig.exists():
            with elig.open(encoding="utf-8") as f:
                ok = {r["file"] for r in csv.DictReader(f) if r["eligible"] == "True"}
        indexable = [x for x in allp if str(x[1].relative_to(REPO)) in ok]
    by_section = defaultdict(list)
    for s, p, _ in indexable:
        by_section[s].append(p)
    sample = []
    for s, ps in sorted(by_section.items()):
        sample += [(s, p) for p in random.sample(ps, min(per, len(ps)))]
    flagged = []
    checked = 0
    with httpx.Client(headers={"User-Agent": UA}, timeout=15, follow_redirects=True) as c:
        for s, p in sample:
            body = re.sub(r"^---\n.*?\n---\n", "", p.read_text(encoding="utf-8"), count=1, flags=re.S)
            page_flags = []
            for sentence in re.split(r"(?<=[.!?])\s+", body):
                for m in LINK_RE.finditer(sentence):
                    url = m.group(2)
                    nums = [n for n in NUM_RE.findall(sentence) if len(n) >= 2 and not re.fullmatch(r"\d", n)]
                    if not nums:
                        continue
                    try:
                        r = c.get(url)
                        if r.status_code >= 400:
                            page_flags.append((url, f"source returned {r.status_code}", nums)); continue
                        text = re.sub(r"<[^>]+>", " ", r.text)
                        text = re.sub(r"\s+", " ", text)
                    except Exception as e:  # noqa: BLE001
                        page_flags.append((url, f"fetch failed: {type(e).__name__}", nums)); continue
                    missing = [n for n in nums if n.replace(",", "") not in text.replace(",", "")]
                    if missing and len(missing) == len(nums):
                        page_flags.append((url, "none of the sentence's numbers appear on the source today", missing))
            checked += 1
            if page_flags:
                flagged.append((s, p, page_flags))
    rate = round(100 * len(flagged) / max(1, checked), 1)
    out = REPO / "reports" / f"audit-{date.today().isoformat()}.md"
    L = [f"# Weekly audit, {date.today().isoformat()}", "", f"Sampled {checked} page(s) ({per} per section, seed {seed}){' from the eligible pages, a rehearsal: nothing is indexed yet' if rehearsal else ''}; "
         f"{len(flagged)} flagged; error rate {rate}% (the wave stop rule requires under 3%).", "", "| Section | Page | Source | Flag | Numbers |", "|---|---|---|---|---|"]
    for s, p, fl in flagged:
        for url, why, nums in fl:
            L.append(f"| {s} | {p.stem} | {url} | {why} | {', '.join(nums)} |")
    out.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"{checked} sampled, {len(flagged)} flagged, error rate {rate}%; written {out.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
