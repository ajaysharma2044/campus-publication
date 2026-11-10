"""After an ideas-wave workflow completes: read its output file, set each idea's final status from the check results
(honest gaps reported by a writer do not fail a page), append the checkers' and writers' new facts to the topic fact
files (validated, ids numbered from 9001 in section 'new'), rebuild IDEAS-STATUS.md and print a summary.
Usage: python3 finalize_wave.py <workflow output file>"""
import csv, json, re, subprocess, sys
REPO = "/Users/ajaysharma/Ads/campus-publication"
COLUMNS = ["fact_id", "topic", "section", "fact", "value", "applies_to", "period", "source_url", "source_title", "checked", "confidence", "notes"]
OFFICIAL = re.compile(r"\.(gov|edu|us)(/|$)|ecode360|nysenate|dhcr|ny\.gov", re.I)

def load_results(path):
    doc = json.load(open(path, encoding="utf-8"))
    res = doc["result"]
    if isinstance(res, str): res = json.loads(res)
    return res["wave"], res["results"]

def append_facts(topic, facts):
    path = f"{REPO}/intel/{topic}/facts.csv"
    rows = list(csv.DictReader(open(path, encoding="utf-8")))
    known = {(r["fact"].strip().lower(), r["value"].strip().lower()) for r in rows}
    nums = [int(r["fact_id"].rsplit("-", 1)[1]) for r in rows if r["section"] == "new" and r["fact_id"].rsplit("-", 1)[1].isdigit()]
    n = max(nums) if nums else 9000
    added = 0
    for f in facts:
        fact, value, url = (f.get("fact") or "").strip(), (f.get("value") or "").strip(), (f.get("source_url") or "").strip()
        if not fact or not value or not re.match(r"https?://", url): continue
        if (fact.lower(), value.lower()) in known: continue
        if re.search(r"\$\d+\.\d(?!\d)", value): value = re.sub(r"\$(\d+)\.(\d)(?!\d)", lambda m: "$" + m.group(1) + "." + m.group(2) + "0", value)
        checked = f.get("checked") or "2026-11-10"
        if not re.match(r"\d{4}-\d{2}-\d{2}$", checked): checked = "2026-11-10"
        n += 1
        rows.append({"fact_id": f"{topic}-new-{n:04d}", "topic": topic, "section": "new", "fact": fact, "value": value,
                     "applies_to": f.get("applies_to") or "", "period": f.get("period") or "", "source_url": url, "source_title": f.get("source_title") or "",
                     "checked": checked, "confidence": f.get("confidence") if f.get("confidence") in ("official", "secondary") else ("official" if OFFICIAL.search(url) else "secondary"),
                     "notes": "added from a writer or checker session during the idea run"})
        known.add((fact.lower(), value.lower())); added += 1
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNS); w.writeheader(); w.writerows(rows)
    out = subprocess.run(["python3", ".claude/skills/fact-file/scripts/validate_facts.py", f"intel/{topic}/facts.csv"], cwd=REPO, capture_output=True, text=True).stdout.splitlines()[0]
    return added, out

def main(path):
    wave, results = load_results(path)
    by_topic = {}
    summary = []
    for r in results:
        if not r: continue
        page = r.get("page") or ""
        topic = page.split("/")[1] if page.startswith("review/") and page.count("/") >= 2 else "off-campus-housing"
        if topic == "tools": topic = "off-campus-housing"
        notes = " ".join(r.get("notes") or [])
        if r.get("status") == "failed":
            status = "failed"
        else:
            checks_ok = bool(r.get("page_check")) or "PASS (kept flags)" in notes or "kept flags" in notes
            facts_ok = ("checker pass" in notes) or (r.get("unmatched", 1) == 0)
            if "checker fix" in notes or "checker reject" in notes or "page_check still fails" in notes: facts_ok = facts_ok and "checker reject" not in notes and "checker fix" not in notes; checks_ok = checks_ok and "page_check still fails" not in notes
            status = ("rewrite-done" if "rewrite of" in notes or json.load(open(f"{REPO}/review/ideas-plan.json")).get(str(r["id"]), {}).get("rewrite_target") else "done") if (checks_ok and facts_ok) else "needs-review"
        subprocess.run(["python3", "scripts/ideas_status.py", "--set", str(r["id"]), f"status={status}", f"page={page}", f"words={r.get('words') or ''}",
                        f"page_check={'PASS' if r.get('page_check') else ('PASS (kept flags)' if 'kept flags' in notes else 'FAIL')}", f"unmatched={r.get('unmatched', '')}", f"note={notes[:900]}"], cwd=REPO, capture_output=True)
        by_topic.setdefault(topic, []).extend(r.get("new_facts") or [])
        summary.append((r["id"], status, r.get("words"), r.get("unmatched"), len(r.get("new_facts") or [])))
    for topic, facts in by_topic.items():
        if facts:
            added, out = append_facts(topic, facts)
            print(f"{topic}: {added} new fact rows appended ({len(facts)} offered); {out}")
    out = subprocess.run(["python3", "scripts/ideas_status.py"], cwd=REPO, capture_output=True, text=True).stdout.strip()
    print(out)
    for s in summary: print("  idea %3s %-13s %5s words, %3s unmatched, %2s new facts" % s)
    print(f"{wave}: {sum(1 for s in summary if s[1] in ('done', 'rewrite-done'))} done, {sum(1 for s in summary if s[1] == 'needs-review')} needs-review, {sum(1 for s in summary if s[1] == 'failed')} failed")

if __name__ == "__main__":
    main(sys.argv[1])
