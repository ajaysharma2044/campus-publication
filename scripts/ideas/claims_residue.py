"""Residue: claims whose text is still on the page and whose first link after the text is still the flagged url."""
import json, re, sys, glob, os
def norm(s):
    s = s.replace('’', "'").replace('‘', "'").replace('“', '"').replace('”', '"')
    return re.sub(r'\s+', ' ', s).strip().lower()
def nurl(u): return (u or '').strip().rstrip('/').lower().replace('http://','https://').replace('://www.','://')
kept = {}; notes = {}
def take(results):
    for r in results:
        for p in r.get('pages', []):
            key = os.path.basename(p['page'].split(' ')[0])
            kept[key] = kept.get(key, 0) + int(p.get('claims_kept') or 0)
            notes[key] = (notes.get(key, '') + ' ' + p.get('notes', '')).strip()
T = '/private/tmp/claude-501/-Users-ajaysharma-Ads/b423b21c-58d2-4753-a413-3d409f0f8512/tasks/'
for f in ['w9xx50yfe.output', 'w1mo84wl3.output', 'wdl23f9cg.output', 'wg1i99pyc.output']:
    d = json.loads(open(T + f).read()); take(d['result'])
batches = sys.argv[1:] or sorted(glob.glob('build/ideas/verify/c*.json'))
same = {}; total = 0; n_same = 0; n_gone = 0; n_other = 0
LINK = re.compile(r'\]\((https?://[^)\s]+)\)')
for b in batches:
    d = json.load(open(b)); bid = d['batch_id']
    for p in d['pages']:
        path = p['page']
        if not os.path.exists(path): continue
        lines = open(path).read().split('\n'); nl = [norm(l) for l in lines]
        for c in p['claims']:
            total += 1
            t = norm(c['text']); u = nurl(c.get('url'))
            probe = t if len(t) <= 80 else t[len(t)//2-30: len(t)//2+30]
            hits = [i for i, l in enumerate(nl) if probe in l]
            if not hits: n_gone += 1; continue
            flagged = False
            for i in hits:
                pos = nl[i].find(probe)
                rest = lines[i][pos:]
                m = LINK.search(rest)
                first = nurl(m.group(1)) if m else ''
                if u and first == u:
                    flagged = True; break
            if flagged:
                n_same += 1
                same.setdefault((bid, os.path.basename(path)), []).append((hits[0]+1, c['text'][:100], c['reason'][:120]))
            else: n_other += 1
residue = 0
for (bid, page), items in sorted(same.items()):
    k = kept.get(page, 0)
    if len(items) <= k and k > 0:
        continue  # the agent reported keeping at least this many on the page
    residue += len(items)
    print(f'== {bid} {page}: {len(items)} with the flagged cite, agent kept={k}')
    for ln, text, reason in items:
        print(f'   L{ln} "{text}"\n        reason: {reason}')
    if page in notes: print('   notes:', notes[page][:260])
print(f'TOTAL {total} claims: {n_gone} text gone, {n_other} text present with another cite or none, {n_same} with the flagged cite; residue beyond reported keeps: {residue}')
