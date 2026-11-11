"""Collect the batched verification results: (1) URLs that did not open, rebatched into build/ideas/verify/r<N>.json for a re-run;
(2) unsupported claims grouped by page, batched for the fix round (printed as JSON for the fix_claims workflow); (3) a summary.
Usage: python3 collect_verify.py <task output files...>"""
import json, os, sys, collections
S = "build/ideas/verify"
results = []
for path in sys.argv[1:]:
    doc = json.load(open(path, encoding="utf-8"))
    res = doc.get("result"); res = json.loads(res) if isinstance(res, str) else res
    results.extend(res or [])
batch_specs = {b["batch_id"]: b for b in results}
opened = fails = fixed = cites = 0
unsupported = collections.defaultdict(list)
failed_urls = []
for b in results:
    spec = json.load(open(f"{S}/{b['batch_id']}.json"))
    spec_by_url = {u["url"]: u for u in spec["urls"]}
    for u in b["urls"]:
        cites += u.get("cites_checked", 0); fixed += len(u.get("fixed", []))
        if u.get("opened"): opened += 1
        else:
            fails += 1
            if u["url"] in spec_by_url: failed_urls.append(spec_by_url[u["url"]])
        for x in u.get("unsupported", []):
            unsupported[x["page"]].append({"line": x["line"], "text": x["text"][:200], "reason": x["reason"][:260], "url": u["url"]})
print(f"{len(results)} batches: {opened} sources opened, {fails} not opened, {cites} sentences checked, {fixed} values fixed, {sum(len(v) for v in unsupported.values())} unsupported claims on {len(unsupported)} pages")
rerun = []
for j in range(0, len(failed_urls), 12):
    bid = f"r{len(rerun) + 1:03d}"; json.dump({"batch_id": bid, "urls": failed_urls[j:j + 12]}, open(f"{S}/{bid}.json", "w"), ensure_ascii=False); rerun.append(bid)
print("rerun batches:", rerun)
pages = sorted(unsupported.items(), key=lambda kv: -len(kv[1]))
fix_batches = [{"batch_id": f"c{n + 1:02d}", "pages": [{"page": p, "claims": c} for p, c in pages[i:i + 6]]} for n, i in enumerate(range(0, len(pages), 6))]
json.dump({"batches": fix_batches}, open(f"{S}/fix_claims.json", "w"), ensure_ascii=False)
print(f"{len(fix_batches)} fix batches written to {S}/fix_claims.json")
