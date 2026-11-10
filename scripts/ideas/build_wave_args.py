"""Build the ideas-wave workflow's args for one wave from IDEAS.md and review/ideas-plan.json.
Usage: python3 build_wave_args.py <wave number> [ids...] > args.json
Only ideas whose decision is write or rewrite are included (and only the ids given, when given)."""
import json, os, re, sys
REPO = "/Users/ajaysharma/Ads/campus-publication"
ROW = re.compile(r"^(\d+) \| ([FA]) \| ([a-z-]+) \| (.+?)(?: \| ([A-Z ]+))?\s*$")
wave = int(sys.argv[1]); only = {int(x) for x in sys.argv[2:]}
plan = json.load(open(f"{REPO}/review/ideas-plan.json"))
ideas, cur = [], 0
for line in open(f"{REPO}/IDEAS.md", encoding="utf-8"):
    m = re.match(r"^## Wave (\d+)", line)
    if m: cur = int(m.group(1)); continue
    m = ROW.match(line.rstrip("\n"))
    if m and cur == wave:
        ideas.append({"id": int(m.group(1)), "mode": m.group(2), "topic": m.group(3), "title": m.group(4).strip(), "tags": (m.group(5) or "").split()})
items = []
for it in ideas:
    p = plan.get(str(it["id"]), {})
    if p.get("action") not in ("write", "rewrite"): continue
    if only and it["id"] not in only: continue
    topic = it["topic"]
    it.update({"decision": p["action"], "rewrite_target": p.get("rewrite_target", ""), "slug": p["slug"], "primary_query": p["primary_query"],
               "page_type": p.get("page_type", "how-to"), "related": p.get("related", []), "tools": p.get("tools", []), "datasets": p.get("datasets", []),
               "note": p.get("note", ""), "facts": f"intel/{topic}/facts.csv",
               "brief": f"intel/{topic}/brief.md" if os.path.exists(f"{REPO}/intel/{topic}/brief.md") else "",
               "inventory": topic == "off-campus-housing" and os.path.exists(f"{REPO}/intel/off-campus-housing/inventory.csv")})
    items.append(it)
facts = sorted({f"intel/{t}/facts.csv" for t in ("off-campus-housing", "getting-around", "dining") if os.path.exists(f"{REPO}/intel/{t}/facts.csv")})
print(json.dumps({"wave": f"Wave {wave}", "items": items, "factsByTopic": {t: f"intel/{t}/facts.csv" for t in ("off-campus-housing", "getting-around", "dining")}, "extraFacts": facts}, indent=1))
