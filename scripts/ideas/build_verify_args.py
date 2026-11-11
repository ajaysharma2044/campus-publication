"""Build the verify_sources workflow's args: every external URL cited in the pages that still await verification,
each once, with the sentences that cite it. Writes <out_dir>/verify<N>.json launch files of at most `per_launch` batches.
Usage: python3 build_verify_args.py <out_dir> [urls_per_batch=12] [per_launch=8]"""
import json, os, re, sys
REPO = "/Users/ajaysharma/Ads/campus-publication"
out_dir = sys.argv[1]; per_batch = int(sys.argv[2]) if len(sys.argv) > 2 else 12; per_launch = int(sys.argv[3]) if len(sys.argv) > 3 else 8
pages = []
for p in sorted(os.listdir(f"{REPO}/review/_status")):
    sc = json.load(open(f"{REPO}/review/_status/{p}"))
    if "awaiting" in (sc.get("note") or "") and sc.get("page") and os.path.exists(f"{REPO}/{sc['page']}"):
        pages.append(sc["page"])
LINK = re.compile(r"\[([^\]]+)\]\((https?://[^)\s]+)\)")
cites = {}
for page in pages:
    text = open(f"{REPO}/{page}", encoding="utf-8").read()
    body_start = 0
    m = re.search(r"^---[ \t]*$", text[3:], flags=re.M) if text.startswith("---") else None
    if m: body_start = 3 + m.end()
    offset = text[:body_start].count("\n")
    for i, line in enumerate(text[body_start:].split("\n"), start=offset + 1):
        if line.lstrip().startswith(("```", "<!--")): continue
        for lm in LINK.finditer(line):
            url = lm.group(2).rstrip(".,")
            sent = re.sub(r"\]\([^)]*\)", "]", line).strip()
            cites.setdefault(url, []).append({"page": page, "line": i, "text": sent[:320]})
urls = sorted(cites.items(), key=lambda kv: -len(kv[1]))
batches = []
for j in range(0, len(urls), per_batch):
    chunk = urls[j:j + per_batch]
    batches.append({"batch_id": f"v{len(batches) + 1:03d}", "urls": [{"url": u, "cites": c[:12]} for u, c in chunk]})
os.makedirs(out_dir, exist_ok=True)
launches = [batches[k:k + per_launch] for k in range(0, len(batches), per_launch)]
for n, L in enumerate(launches, 1):
    s = json.dumps({"batches": L}, separators=(",", ":"))
    open(f"{out_dir}/verify{n}.json", "w").write(s)
print(f"{len(pages)} pages, {sum(len(c) for c in cites.values())} citations, {len(urls)} distinct URLs, {len(batches)} batches, {len(launches)} launches of up to {per_launch}")
for n, L in enumerate(launches, 1): print(f"  verify{n}.json: {len(L)} batches, {len(json.dumps({'batches': L}, separators=(',', ':')))} bytes")
