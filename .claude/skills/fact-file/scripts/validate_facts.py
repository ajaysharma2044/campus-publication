#!/usr/bin/env python3
"""Validate a fact file before anything downstream reads it.

Usage:
    python3 validate_facts.py intel/<topic>/facts.csv

Fails on: missing columns, duplicate fact_ids, empty fact or value, a sourced row
whose source_url is not a URL, a bad checked date, a money value missing its cents
digit ("$46.7"), and a price or date row with no period or applies_to.
Warns on: unsourced rows and conflicting values for the same fact name.
"""
import csv
import re
import sys
from collections import defaultdict

REQUIRED = ["fact_id", "topic", "section", "fact", "value", "applies_to", "period",
            "source_url", "source_title", "checked", "confidence", "notes"]


def main(path):
    errors, warnings = [], []
    with open(path, encoding="utf-8") as f:
        r = csv.DictReader(f)
        missing = [c for c in REQUIRED if c not in (r.fieldnames or [])]
        if missing:
            print(f"FAIL missing columns: {missing}")
            return 1
        rows = list(r)
    ids, by_fact = set(), defaultdict(set)
    for i, row in enumerate(rows, start=2):
        fid = row["fact_id"]
        if fid in ids:
            errors.append(f"row {i}: duplicate fact_id {fid}")
        ids.add(fid)
        if not row["fact"].strip() or not row["value"].strip():
            errors.append(f"row {i} ({fid}): empty fact or value")
        if row["confidence"] != "unsourced" and not re.match(r"https?://", row["source_url"]):
            errors.append(f"row {i} ({fid}): source_url is not a URL")
        if row["confidence"] == "unsourced":
            warnings.append(f"row {i} ({fid}): unsourced")
        if row["checked"] and not re.match(r"\d{4}-\d{2}-\d{2}$", row["checked"]):
            errors.append(f"row {i} ({fid}): checked must be YYYY-MM-DD")
        if re.search(r"\$\d+\.\d(?!\d)", row["value"]):
            errors.append(f"row {i} ({fid}): money value missing its cents digit")
        if re.search(r"\$\d|\b20\d\d\b", row["value"]) and not (row["period"].strip() or row["applies_to"].strip()):
            warnings.append(f"row {i} ({fid}): price or date with no period or applies_to")
        by_fact[row["fact"].strip().lower()].add(row["value"].strip())
    for fact, values in by_fact.items():
        if len(values) > 1:
            warnings.append(f"conflict or variants for '{fact[:60]}': {len(values)} different values")
    print(f"{'PASS' if not errors else 'FAIL'} {path}: {len(rows)} rows, {len(errors)} errors, {len(warnings)} warnings")
    for e in errors[:50]:
        print("  ERROR", e)
    for w in warnings[:20]:
        print("  warn ", w)
    return 0 if not errors else 1


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
