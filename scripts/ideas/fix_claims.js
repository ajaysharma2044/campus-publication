export const meta = {
  name: 'ideas-fix-claims',
  description: 'After the source verification: one Sonnet editor per batch of pages, fixing each claim the cited source did not support',
  phases: [{ title: 'Fix' }],
}
const REPO = '/Users/ajaysharma/Ads/campus-publication'
const { batches } = args  // [{batch_id, pages: [{page, claims: [{line, text, reason, url}]}]}]
const SCHEMA = { type: 'object', properties: { batch_id: { type: 'string' }, pages: { type: 'array', items: { type: 'object', properties: { page: { type: 'string' }, claims_fixed: { type: 'integer' }, claims_removed: { type: 'integer' }, claims_relinked: { type: 'integer' }, claims_kept: { type: 'integer' }, page_check_pass: { type: 'boolean' }, notes: { type: 'string' } }, required: ['page', 'claims_fixed', 'claims_removed', 'claims_relinked', 'claims_kept', 'page_check_pass', 'notes'] } } }, required: ['batch_id', 'pages'] }
const prompt = (b) => `You are the EduExplained checker finishing the source verification. Repository: ${REPO}; run every command from there. Read once: .claude/skills/fact-checking/SKILL.md and .claude/skills/eduexplained-voice/SKILL.md (confidence, sources and attribution). You never add a new fact; you make each sentence say only what its source supports.

For each page below, the verification pass found sentences whose cited source does not state the claim. For each listed claim, open the page at the line (re-grep for the text if the line moved) and do exactly one of these, in this order of preference:
1. RELINK: if the sentence or paragraph already cites another source that does support the claim (the reason often says so, e.g. "cited to Cornell Law", "cited to the Sun"), or the fact file intel/<topic>/facts.csv holds the value with a different source_url, change the link to that source. Do not open new web pages beyond the one linked.
2. LABEL: if the claim is our own arithmetic on sourced inputs (a median, a per-bed division, a straight-line distance from the inventory), keep the value, drop the misleading link from it, and show the inputs in the sentence ("$2,600 a month split four ways is $650 a bed"; "1.35 miles in a straight line from Ho Plaza, from the address"), citing the inputs' source where one exists.
3. SOFTEN: if the source supports a weaker statement, rewrite the sentence to that statement (what the page states, no more).
4. REMOVE: otherwise delete the claim (the sentence, or the table cell with a plain "not stated"), keeping the surrounding text readable.
Keep a claim unchanged only when you can show from the cited page that the verifier was wrong; say why in notes. No em dashes, no hedges, no "Not confirmed" labels; money keeps its cents. After editing a page run python3 .claude/skills/page-checks/scripts/page_check.py <page> once and fix only what it flags on lines you touched.

Pages and claims:
${b.pages.map(p => `### ${p.page}\n${p.claims.map(c => `- line ${c.line}: "${c.text}" | source ${c.url} | verifier: ${c.reason}`).join('\n')}`).join('\n\n')}

Return JSON: batch_id "${b.batch_id}", pages (page, claims_fixed, claims_removed, claims_relinked, claims_kept, page_check_pass, notes).`
phase('Fix')
const results = await parallel(batches.map(b => () => agent(prompt(b), { label: `claims:${b.batch_id}`, phase: 'Fix', schema: SCHEMA, model: 'sonnet', effort: 'medium' })))
return results.filter(Boolean)
