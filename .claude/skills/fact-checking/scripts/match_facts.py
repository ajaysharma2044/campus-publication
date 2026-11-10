#!/usr/bin/env python3
"""Match every hard number on a page against the fact file. Code first, Claude second.

Usage:
    python3 match_facts.py <article.md> <facts.csv> [<more facts.csv> ...] [--json]

Extracts money amounts, counts with units, percentages, dates and phone numbers from
the page (frontmatter excluded), normalizes them, and looks for each one in the
fact file values. Output lists every number that is NOT in the fact file, with its
line, so the checker agent only spends effort on those.

A number can be legitimately absent when it is the page's own arithmetic (a total,
a per-month figure). The checker recomputes those from fact-file inputs rather than
looking them up.
"""
import csv
import json
import re
import sys

TOKEN = re.compile(
    r"\$[\d,]+(?:\.\d+)?"
    r"|\b\d{3}-\d{3}-\d{4}\b"
    r"|\b\d[\d,]*(?:\.\d+)?(?= ?(?:%|percent|days?|weeks?|months?|years?|hours?|minutes?|miles?|credits?|units?|mph|lb|W)\b)"
    r"|\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.? \d{1,2}\b")
MONTHS = {m: i for i, m in enumerate(["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], 1)}


def norm(tok):
    t = tok.lower().replace(",", "").replace(".", " ").strip()
    m = re.match(r"([a-z]{3})[a-z]* ?(\d{1,2})$", t)
    if m and m.group(1) in MONTHS:
        return f"date:{MONTHS[m.group(1)]}-{int(m.group(2))}"
    num = re.sub(r"[^\d ]", "", tok.replace(",", ""))
    if tok.startswith("$"):
        v = float(tok[1:].replace(",", "") or 0)
        return f"money:{v:.2f}"
    if re.match(r"\d{3}-\d{3}-\d{4}", tok):
        return f"phone:{tok}"
    try:
        return f"num:{float(tok.replace(',', '')):g}"
    except ValueError:
        return f"raw:{num}"


def fact_tokens(paths):
    known = set()
    for p in paths:
        with open(p, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                for field in ("value", "fact", "applies_to", "period"):
                    for tok in TOKEN.findall(row.get(field, "") or ""):
                        known.add(norm(tok))
                for tok in re.findall(r"\b\d[\d,]*(?:\.\d+)?\b", row.get("value", "") or ""):
                    known.add(norm(tok))
    return known


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) < 2:
        print(__doc__)
        return 2
    page, facts = args[0], args[1:]
    known = fact_tokens(facts)
    text = open(page, encoding="utf-8").read()
    m = re.search(r"^---[ \t]*$", text[3:], flags=re.M) if text.startswith("---") else None
    body_start = 3 + m.end() if m else 0  # the frontmatter ends at a line that is only ---, not at a --- inside a URL
    offset = text[:body_start].count("\n")
    unmatched, total = [], 0
    for i, line in enumerate(text[body_start:].split("\n"), start=offset + 1):
        plain = re.sub(r"\]\([^)]*\)", "]", line)
        for tok in TOKEN.findall(plain):
            total += 1
            if norm(tok) not in known:
                unmatched.append({"line": i, "token": tok, "context": plain.strip()[:160]})
    result = {"page": page, "numbers": total, "matched": total - len(unmatched), "unmatched": unmatched}
    if "--json" in sys.argv:
        print(json.dumps(result, indent=2))
    else:
        print(f"{result['matched']}/{total} numbers matched the fact file; {len(unmatched)} for the checker")
        for u in unmatched:
            print(f"  line {u['line']}: {u['token']}  ::  {u['context']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
