export const meta = {
  name: 'ideas-fix-batch',
  description: 'Sprint mode: one Sonnet editor per batch of failing pages; fixes only what page_check flags',
  phases: [{ title: 'Fix' }],
}
const REPO = '/Users/ajaysharma/Ads/campus-publication'
const { batches } = args  // [{batch_id, pages: [{page, flags}]}]
const SCHEMA = { type: 'object', properties: { batch_id: { type: 'string' }, pages: { type: 'array', items: { type: 'object', properties: { page: { type: 'string' }, pass_after: { type: 'boolean' }, kept_flags: { type: 'array', items: { type: 'string' } } }, required: ['page', 'pass_after', 'kept_flags'] } } }, required: ['batch_id', 'pages'] }
const prompt = (b) => `You are the EduExplained editor in sprint mode. Repository: ${REPO}; run every command from there. Read once: .claude/skills/eduexplained-voice/SKILL.md and .claude/skills/editing/references/cut-list.md. You never add facts, numbers, sources or claims; you fix only what the check flags.
For each page below, in order: run python3 .claude/skills/page-checks/scripts/page_check.py <page>; fix each flagged line in place with Edit calls (a repeated fact keeps its main statement plus at most one reference; an unsourced paragraph gets the link the page already uses for that fact elsewhere, or its numbers move to the sentence that is sourced, or the sentence goes; a hedge becomes a flat statement or states exactly what the answer depends on; narration, planner talk, "Not confirmed" labels, time-bound phrases, filler and em dashes are cut or rewritten; an opening over 60 words is cut to the answer; a money value missing its cents digit gets it); run the check once more; keep a flag only when fixing it would make the page wrong or drop an answer, and say why. Change nothing the check did not flag.
Pages (with their current flags):
${b.pages.map(p => `- ${p.page}: ${p.flags}`).join('\n')}
Return JSON: batch_id "${b.batch_id}", pages (page, pass_after, kept_flags with reasons).`
phase('Fix')
const results = await parallel(batches.map(b => () => agent(prompt(b), { label: `fix:${b.batch_id}`, phase: 'Fix', schema: SCHEMA, model: 'sonnet', effort: 'medium' })))
return results.filter(Boolean)
