export const meta = {
  name: 'ideas-verify-sources',
  description: 'One batched fact verification pass: each cited source opened once, every sentence that cites it checked, wrong values fixed in place',
  phases: [{ title: 'Verify' }],
}
const REPO = '/Users/ajaysharma/Ads/campus-publication'
const { batch_ids } = args  // each id names build/ideas/verify/<id>.json: {batch_id, urls: [{url, cites: [{page, line, text}]}]}
const batches = batch_ids.map(id => ({ batch_id: id }))
const SCHEMA = {
  type: 'object',
  properties: {
    batch_id: { type: 'string' },
    urls: { type: 'array', items: { type: 'object', properties: {
      url: { type: 'string' }, opened: { type: 'boolean' }, status: { type: 'string' },
      cites_checked: { type: 'integer' },
      fixed: { type: 'array', items: { type: 'object', properties: { page: { type: 'string' }, line: { type: 'integer' }, before: { type: 'string' }, after: { type: 'string' } }, required: ['page', 'line', 'before', 'after'] } },
      unsupported: { type: 'array', items: { type: 'object', properties: { page: { type: 'string' }, line: { type: 'integer' }, text: { type: 'string' }, reason: { type: 'string' } }, required: ['page', 'line', 'text', 'reason'] } },
    }, required: ['url', 'opened', 'status', 'cites_checked', 'fixed', 'unsupported'] } },
    notes: { type: 'string' },
  },
  required: ['batch_id', 'urls', 'notes'],
}
const prompt = (b) => `You are the EduExplained checker in a batched verification pass. Repository: ${REPO}; run every command from there. Read once: .claude/skills/fact-checking/SKILL.md. Never rewrite for style, never add claims; a search snippet never counts as verification.
Your batch file is ${REPO}/build/ideas/verify/${b.batch_id}.json: read it first; it lists the source URLs and, under each, the sentences (page path, line number, text) that cite it.
For each source URL in the file: open it ONCE with WebFetch (the full page). Then, for every sentence listed under it (page, line number, text), check each fact the sentence attributes to that source: numbers, dates, names, rules, who it applies to. If the page supports it, move on. If the page shows a different value, fix the value in place with an Edit call on that page and line (change only the value; keep the sentence otherwise). If the page does not support the claim at all, do not edit; list it under unsupported with the reason. If WebFetch fails (certificate rejected, 403, timeout), fetch the page with Bash instead: curl -sL --max-time 40 -A 'Mozilla/5.0 EduExplained-checker' '<url>' | python3 -c "import sys,re,html; t=sys.stdin.read(); t=re.sub(r'<script[\\s\\S]*?</script>|<style[\\s\\S]*?</style>','',t); print(html.unescape(re.sub(r'<[^>]+>',' ',t)))" | head -c 80000. If that fails too, read the crawled copy in the repo's corpus: corpus/<host>/<path>.txt (2,522 pages crawled on 2026-11-06; list corpus/<host>/ and grep for the slug). Record in status which route opened the page (webfetch, curl or corpus, with the corpus crawl date). Only when all three fail: opened false, sentences unverified. Line numbers were taken before any edits; re-grep for the sentence text if a line has shifted.
Return JSON: batch_id "${b.batch_id}", urls (one entry per URL: url, opened, status, cites_checked, fixed, unsupported), notes.`
phase('Verify')
const results = await parallel(batches.map(b => () => agent(prompt(b), { label: `verify:${b.batch_id}`, phase: 'Verify', schema: SCHEMA, model: 'sonnet', effort: 'low' })))
return results.filter(Boolean)
