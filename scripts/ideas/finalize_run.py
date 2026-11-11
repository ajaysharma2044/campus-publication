"""Final statuses for the idea run (2026-11-11): every idea still 'writing' becomes done or rewrite-done, pointed at its
content/ copy (the canonical page since publication), with words and page_check from that copy, unmatched numbers from
match_facts.py against the topic's fact file, and a note carrying the page's verification counts: cited sources opened
(build/ideas/verify/v*.json), values corrected in place (commit 048847f) and claims rewritten, relinked or removed in the
fix round (build/ideas/verify/fix_claims.json). Done, rewrite-done and needs-review ideas get the same page path and note.
Run from the repo root; then `python3 scripts/ideas_status.py --note "..."` for the progress paragraph."""
import json, glob, os, re, subprocess, collections, datetime
REPO = os.getcwd()
plan = json.load(open('review/ideas-plan.json'))
FACTS = {'off-campus-housing': 'intel/off-campus-housing/facts.csv', 'getting-around': 'intel/getting-around/facts.csv', 'dining': 'intel/dining/facts.csv'}
opened = collections.defaultdict(set)
for f in glob.glob('build/ideas/verify/v*.json'):
    for u in json.load(open(f)).get('urls', []):
        for c in u.get('cites', []): opened[c['page']].add(u['url'])
fixed_vals = collections.Counter()
for line in subprocess.run(['git', 'show', '048847f', '--numstat', '--format='], capture_output=True, text=True).stdout.splitlines():
    parts = line.split('\t')
    if len(parts) == 3: fixed_vals[parts[2]] += int(parts[0])
claims = collections.Counter()
for b in json.load(open('build/ideas/verify/fix_claims.json'))['batches']:
    for p in b['pages']: claims[p['page']] += len(p['claims'])
now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
rows = []
for f in sorted(glob.glob('review/_status/*.json')):
    d = json.load(open(f))
    if d['status'] not in ('writing', 'done', 'rewrite-done', 'needs-review'): continue
    slug = os.path.basename(d['page']).replace('.md', '')
    hits = glob.glob(f'content/articles/*/{slug}.md') + glob.glob(f'content/tools/{slug}.md')
    if len(hits) != 1:
        print('no single content copy for', d['id'], d['page'], hits); continue
    page = hits[0]
    pc = subprocess.run(['python3', '.claude/skills/page-checks/scripts/page_check.py', page], capture_output=True, text=True).stdout
    m = re.search(r'^(PASS|FAIL) .*?\((\d+) prose words', pc, flags=re.M)
    page_check, words = (m.group(1), m.group(2)) if m else ('?', d.get('words', ''))
    topic = d['page'].split('/')[1] if d['page'].startswith('review/') else ''
    unmatched = d.get('unmatched', '')
    if topic in FACTS:
        mf = subprocess.run(['python3', '.claude/skills/fact-checking/scripts/match_facts.py', page, FACTS[topic]], capture_output=True, text=True).stdout
        mm = re.search(r'(\d+) for the checker', mf)
        if mm: unmatched = mm.group(1)
    verif = f"verification 2026-11-11: {len(opened.get(page, ()))} cited sources opened, {fixed_vals.get(page, 0)} values corrected, {claims.get(page, 0)} claims rewritten, relinked or removed"
    if d['status'] == 'writing':
        action = plan.get(str(d['id']), {}).get('action', 'write')
        status = 'rewrite-done' if action == 'rewrite' else 'done'
        note = f"sprint batch, written from the fact files; published 2026-11-11 to eduexplained.netlify.app; {verif}"
    else:
        status = d['status']
        note = (d.get('note', '') + f" | published 2026-11-11; {verif}").strip(' |')
    d.update({'status': status, 'page': page, 'words': words, 'page_check': page_check, 'unmatched': unmatched, 'note': note, 'updated': now})
    json.dump(d, open(f, 'w'), indent=1, ensure_ascii=False)
    rows.append((d['id'], status, words, page_check, unmatched))
print(len(rows), 'ideas updated;', collections.Counter(r[1] for r in rows), 'page_check', collections.Counter(r[3] for r in rows))
