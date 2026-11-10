"""One-off cleanup of the converted fact files: annotated Checked cells, 'same' source cells, one million-dollar value."""
import csv, re, sys, datetime
COLUMNS = ["fact_id", "topic", "section", "fact", "value", "applies_to", "period", "source_url", "source_title", "checked", "confidence", "notes"]
OFFICIAL = re.compile(r"\.(gov|edu|us)(/|$)|ecode360|nysenate|dhcr|ny\.gov", re.I)
SAME = re.compile(r"^\s*\(?(same|ditto|as above|see above|idem)\b", re.I)

def cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]

def inherited(src):
    """Replicate brief_tables_to_csv.py's walk so fact_ids line up; return {fact_id: (url, raw cell)} for 'same'-style cells."""
    topic = src.rstrip("/").split("/")[-2]
    section, header, n, last, out = "", None, 0, "", {}
    for line in open(src, encoding="utf-8").read().split("\n"):
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
                header, last = low, ""
            continue
        if set("".join(c)) <= set("-: "):
            continue
        rec = dict(zip(header, c))
        raw = next((v for k, v in rec.items() if "source" in k), "")
        url = (re.search(r"https?://\S+", raw) or [""])[0].rstrip(").,") if raw else ""
        n += 1
        fid = f"{topic}-{section or '0'}-{n:04d}"
        if url:
            last = url
        elif last and SAME.match(raw):
            out[fid] = (last, raw)
    return out

def main(topic):
    brief, path, log = f"intel/{topic}/brief.md", f"intel/{topic}/facts.csv", f"intel/{topic}/facts-fixes.md"
    rows = list(csv.DictReader(open(path, encoding="utf-8")))
    inh = inherited(brief)
    fixes = []
    for r in rows:
        fid = r["fact_id"]
        m = re.search(r"\d{4}-\d{2}-\d{2}", r["checked"] or "")
        if r["checked"] and not re.match(r"\d{4}-\d{2}-\d{2}$", r["checked"]):
            rest = (r["checked"].replace(m.group(0), "", 1) if m else r["checked"]).strip(" ;,(")
            r["notes"] = "; ".join(x for x in [r["notes"], f"checked cell said: {r['checked']}"] if x)
            r["checked"] = m.group(0) if m else ""
            fixes.append(f"- {fid}: Checked cell held an annotation ({rest[:60]}); kept the date, moved the rest to notes. Source: {r['source_url'] or 'none'}")
        if not r["source_url"] and fid in inh:
            url, raw = inh[fid]
            r["source_url"] = url
            r["confidence"] = "official" if OFFICIAL.search(url) else "secondary"
            r["notes"] = "; ".join(x for x in [r["notes"], f"source cell said '{raw}': URL inherited from the row above in the same table"] if x)
            fixes.append(f"- {fid}: source cell said '{raw}'; inherited the previous row's URL {url}")
        if "$464.4 million" in r["value"]:
            r["value"] = r["value"].replace("$464.4 million", "about $464 million")
            r["notes"] = "; ".join(x for x in [r["notes"], "source figure $464.4 million; written without the decimal so the cents rule holds"] if x)
            fixes.append(f"- {fid}: '$464.4 million' written as 'about $464 million' (cents rule). Source: {r['source_url']}")
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS); w.writeheader(); w.writerows(rows)
    with open(log, "a", encoding="utf-8") as f:
        f.write(f"# Fact-file fixes: {topic}\n\nConverted from brief.md with brief_tables_to_csv.py on 2026-11-10; fixes below keep fact_ids stable.\n\n## Mechanical cleanup, {datetime.date.today()}\n" + "\n".join(fixes) + "\n")
    print(topic, len(rows), "rows;", len(fixes), "fixes;", sum(1 for r in rows if r["confidence"] == "unsourced"), "still unsourced")

for t in sys.argv[1:]:
    main(t)
