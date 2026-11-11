"""Copy review pages and calculators into content/ for the Astro build (Ajay's instruction of 2026-11-11: publish, then verify).
Rewrites replace their live page at the same slug and keep its topic, queue_id, pillar, kind and images; new pages carry no queue_id
and no image entries without a file; frontmatter scalars with a colon are quoted; internal links are checked against the URLs the
site will have and corrected or unlinked; a page with fewer than three internal links gets a Related guides list."""
import glob, json, os, re, shutil, sys, yaml
CT = {"off-campus-housing": "housing", "getting-around": "getting-around", "dining": "dining"}
plan = json.load(open("review/ideas-plan.json", encoding="utf-8"))
site_topics = re.findall(r"id: '([a-z-]+)', label:", open("site/site.config.ts", encoding="utf-8").read())
KEYLINE = re.compile(r"^(\s*(?:- )?[A-Za-z_]+):[ \t]+(.+?)[ \t]*$")

def split(t):
    m = re.search(r"^---[ \t]*$", t[3:], flags=re.M)
    return t[3:3 + m.start()], t[3 + m.end():]

def repair(fm_text):
    out = []
    for line in fm_text.split("\n"):
        m = KEYLINE.match(line)
        if m:
            key, val = m.group(1), m.group(2)
            if not (val[:1] in "\"'[{|>" or val in ("", "[]", "{}") or re.match(r"^-?\d+(\.\d+)?$", val) or val in ("true", "false", "null")):
                if ": " in val or val.endswith(":") or " #" in val or val[:1] in "&*!%@`" or val.startswith("- "):
                    val = '"' + val.replace("\\", "\\\\").replace('"', '\\"') + '"'
            line = f"{key}: {val}"
        out.append(line)
    return "\n".join(out)

def load_fm(text, path):
    fm_text, body = split(text)
    try:
        return yaml.safe_load(fm_text) or {}, body
    except yaml.YAMLError:
        try:
            return yaml.safe_load(repair(fm_text)) or {}, body
        except yaml.YAMLError as e:
            print("FRONTMATTER STILL BROKEN:", path, str(e)[:120]); return None, body

urls = set()
for p in glob.glob("content/articles/*/*.md"):
    fm, _ = load_fm(open(p, encoding="utf-8").read(), p)
    if fm: urls.add(f"/cornell/{fm.get('topic')}/{os.path.basename(p)[:-3]}/")
for d in glob.glob("content/tools/*/") + glob.glob("review/tools/*/"): urls.add(f"/tools/{os.path.basename(d.rstrip('/'))}/")
for p in glob.glob("content/datasets/*.md"): urls.add(f"/datasets/{os.path.basename(p)[:-3]}/")
for p in glob.glob("content/start/*.md"): urls.add(f"/start/{os.path.basename(p)[:-3]}/")
for p in glob.glob("content/pages/*.md"): urls.add(f"/{os.path.basename(p)[:-3]}/")
for t in site_topics: urls.add(f"/cornell/{t}/")
urls |= {"/", "/cornell/", "/tools/", "/datasets/", "/start/", "/search/", "/guides/", "/cornell/data/"}
pages = {}
for p in sorted(glob.glob("review/*/*.md")):
    topic_dir = p.split("/")[1]
    if topic_dir == "tools": continue
    fm, body = load_fm(open(p, encoding="utf-8").read(), p)
    if fm is None: continue
    idea = fm.get("idea_id"); pl = plan.get(str(idea), {}) if idea else {}
    rw = (pl.get("rewrite_target") or fm.get("rewrites") or "").strip()
    target = rw if rw.startswith("content/articles/") and os.path.exists(rw) else f"content/articles/{CT.get(topic_dir, topic_dir)}/{os.path.basename(p)}"
    live = load_fm(open(target, encoding="utf-8").read(), target)[0] if os.path.exists(target) else None
    ttopic = (live or {}).get("topic") or CT.get(topic_dir, topic_dir)
    pages[p] = (target, fm, body, live, ttopic)
    urls.add(f"/cornell/{ttopic}/{os.path.basename(p)[:-3]}/")
slug_topic = {}
for u in urls:
    m = re.match(r"^/cornell/([a-z-]+)/([^/]+)/$", u)
    if m: slug_topic.setdefault(m.group(2), set()).add(m.group(1))
LINK = re.compile(r"\[([^\]]+)\]\((/[^)\s]+)\)")
rep = {"written": 0, "rewrites": 0, "links_fixed": 0, "links_unlinked": 0, "images_dropped": 0, "related_added": 0, "queue_ids_stripped": 0}
unlinked = []
for p, (target, fm, body, live, ttopic) in pages.items():
    if live:
        rep["rewrites"] += 1
        fm["topic"] = live.get("topic", fm.get("topic"))
        for k in ("queue_id", "pillar", "kind", "school"):
            if live.get(k) and not fm.get(k): fm[k] = live[k]
        fm["images"] = live.get("images") or []
    else:
        imgs = [i for i in (fm.get("images") or []) if isinstance(i, dict) and i.get("file")]
        rep["images_dropped"] += len(fm.get("images") or []) - len(imgs); fm["images"] = imgs
        if fm.pop("queue_id", None): rep["queue_ids_stripped"] += 1
    if fm.get("topic") not in site_topics: fm["topic"] = ttopic
    fm["updated"] = str(fm.get("updated") or "2026-11-10")[:10]
    if "sources" in fm and isinstance(fm["sources"], list):
        fm["sources"] = [s for s in fm["sources"] if isinstance(s, dict) and s.get("url")]
    def fix(m):
        text, h = m.group(1), m.group(2)
        h2 = re.sub(r"^/cornell/datasets/", "/datasets/", h)
        if not h2.endswith("/") and "." not in h2.split("/")[-1]: h2 += "/"
        if h2 in urls:
            if h2 != h: rep["links_fixed"] += 1
            return f"[{text}]({h2})"
        mm = re.match(r"^/(?:cornell/)?([a-z-]+)/([^/]+)/$", h2)
        if mm and mm.group(1) in site_topics:
            slug = mm.group(2)
            if f"/cornell/{mm.group(1)}/{slug}/" in urls: rep["links_fixed"] += 1; return f"[{text}](/cornell/{mm.group(1)}/{slug}/)"
            if slug in slug_topic: t2 = sorted(slug_topic[slug])[0]; rep["links_fixed"] += 1; return f"[{text}](/cornell/{t2}/{slug}/)"
        rep["links_unlinked"] += 1; unlinked.append((p, h)); return text
    body2 = LINK.sub(fix, body)
    n_links = len(set(m.group(2) for m in LINK.finditer(body2)))
    if n_links < 3:
        idea = fm.get("idea_id"); pl = plan.get(str(idea), {}) if idea else {}
        extra = []
        for r in pl.get("related", []):
            r2 = r.replace("content/articles/", "")
            u = f"/tools/{r2.split('/')[1]}/" if r2.startswith("tools/") else (f"/{r2}/" if r2.startswith(("datasets/", "start/")) else f"/cornell/{r2}/")
            if u in urls and u not in body2: extra.append(f"- [{r2.split('/')[-1].replace('-', ' ').capitalize()}]({u})")
            if n_links + len(extra) >= 3: break
        if extra: body2 = body2.rstrip() + "\n\n## Related guides\n\n" + "\n".join(extra) + "\n"; rep["related_added"] += 1
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, "w", encoding="utf-8") as f:
        f.write("---\n" + yaml.safe_dump(fm, sort_keys=False, allow_unicode=True, width=1000) + "---\n" + body2)
    rep["written"] += 1
for d in glob.glob("review/tools/*/"):
    slug = os.path.basename(d.rstrip("/")); dst = f"content/tools/{slug}"; os.makedirs(dst, exist_ok=True)
    for fn in os.listdir(d): shutil.copy2(os.path.join(d, fn), os.path.join(dst, fn))
rep["tools"] = len(glob.glob("review/tools/*/"))
print(json.dumps(rep))
for u in unlinked[:20]: print("  unlinked:", u)
