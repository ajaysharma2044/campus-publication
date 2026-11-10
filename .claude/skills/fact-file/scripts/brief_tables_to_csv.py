#!/usr/bin/env python3
"""Convert the sourced tables inside an existing topic brief into a fact file.

Usage:
    python3 brief_tables_to_csv.py intel/<topic>/brief.md intel/<topic>/facts.csv

Your current briefs already hold their facts as markdown tables
(| Fact | Value | Source URL | Applies to | Checked |). This pulls every table that
has a source column into one CSV in the fact-file format, so the rebuild can start
from the research you already paid for instead of researching again.

Rows without a source URL are kept but marked confidence=unsourced so the checker
treats them as unverified.
"""
import csv
import re
import sys

COLUMNS = ["fact_id", "topic", "section", "fact", "value", "applies_to", "period",
           "source_url", "source_title", "checked", "confidence", "notes"]
OFFICIAL = re.compile(r"\.(gov|edu|us)(/|$)|ecode360|nysenate|dhcr|ny\.gov", re.I)


def cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def main(src, dst):
    topic = src.rstrip("/").split("/")[-2]
    lines = open(src, encoding="utf-8").read().split("\n")
    section, rows, header, n = "", [], None, 0
    for line in lines:
        m = re.match(r"#{2,3} (\d+(?:\.\d+)?)", line)
        if m:
            section, header = m.group(1), None
            continue
        if not line.lstrip().startswith("|"):
            header = None
            continue
        c = cells(line)
        if header is None:
            low = [x.lower() for x in c]
            if any("source" in x for x in low):
                header = low
            continue
        if set("".join(c)) <= set("-: "):
            continue
        rec = dict(zip(header, c))
        url = next((v for k, v in rec.items() if "source" in k), "")
        url = (re.search(r"https?://\S+", url) or [""])[0].rstrip(").,") if url else ""
        fact = rec.get("fact") or rec.get(header[0], "")
        value = rec.get("value") or " | ".join(v for k, v in rec.items() if k not in (header[0],) and "source" not in k and k not in ("checked",))
        n += 1
        rows.append({
            "fact_id": f"{topic}-{section or '0'}-{n:04d}",
            "topic": topic, "section": section, "fact": fact, "value": value,
            "applies_to": rec.get("applies to", ""), "period": "",
            "source_url": url, "source_title": "", "checked": rec.get("checked", ""),
            "confidence": "official" if url and OFFICIAL.search(url) else ("secondary" if url else "unsourced"),
            "notes": "",
        })
    with open(dst, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} facts from {src} -> {dst}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(2)
    main(sys.argv[1], sys.argv[2])
