export const meta = {
  name: 'ideas-fix-round',
  description: 'One editor pass on review pages whose page checks fail, then a re-check',
  phases: [{ title: 'Edit' }, { title: 'Check' }],
}
const REPO = '/Users/ajaysharma/Ads/campus-publication'
const { pages } = args  // [{id, page, title, primary_query, mode, rewrite_target}]
const CHECK_SCHEMA = { type: 'object', properties: { pass: { type: 'boolean' }, words: { type: 'integer' }, reading_grade: { type: 'number' }, counts: { type: 'object' }, problems: { type: 'array', items: { type: 'object', properties: { check: { type: 'string' }, line: { type: ['integer', 'null'] }, msg: { type: 'string' } }, required: ['check', 'msg'] } } }, required: ['pass', 'words', 'problems'] }
const EDIT_SCHEMA = { type: 'object', properties: { slug: { type: 'string' }, words_before: { type: 'integer' }, words_after: { type: 'integer' }, cut: { type: 'object' }, missing: { type: 'array', items: { type: 'string' } }, kept_flags: { type: 'array', items: { type: 'object', properties: { check: { type: 'string' }, line: { type: ['integer', 'null'] }, reason: { type: 'string' } }, required: ['check', 'reason'] } } }, required: ['slug', 'words_before', 'words_after', 'missing', 'kept_flags'] }
const editorPrompt = (p) => `You are the EduExplained editor. You did not write this draft; read it the way a reader would. Cut and sharpen; never add facts, numbers, sources or claims. Repository: ${REPO}; run every command from there.
Read first: .claude/skills/eduexplained-voice/SKILL.md, .claude/skills/editing/SKILL.md and references/cut-list.md, .claude/skills/page-checks/SKILL.md.
Draft: ${p.page} (mode ${p.mode}). Its question: "${p.title}" (primary query "${p.primary_query}"); it must still answer it.${p.rewrite_target ? ` It rewrites the live page ${p.rewrite_target}: every question the live page answered must still be answered.` : ''}
Run python3 .claude/skills/page-checks/scripts/page_check.py ${p.page} first; its flags are your list. Fix each one in place with Edit calls (a repeated fact keeps its main statement plus at most one reference; an unsourced paragraph gets the link the page already uses for that fact elsewhere, or the figures move to where they are sourced, or the sentence goes; a hedge becomes a flat statement or states exactly what the answer depends on). Change nothing else. Run the check again until it passes or every remaining flag is one you can defend under accuracy or coverage, listed in kept_flags with its reason.
Return JSON: slug, words_before, words_after, cut {repetition, hedges, narration, planner, other}, missing, kept_flags.`
const checkPrompt = (p) => `Run from ${REPO}: python3 .claude/skills/page-checks/scripts/page_check.py ${p.page} --json and report its result exactly; change no file. Return JSON: pass, words, reading_grade, counts, problems (up to 40 as {check, line, msg}).`
const results = await pipeline(pages,
  (p) => agent(editorPrompt(p), { label: `edit:${p.id}`, phase: 'Edit', schema: EDIT_SCHEMA, model: 'opus', effort: 'medium' }),
  (e, p) => agent(checkPrompt(p), { label: `check:${p.id}`, phase: 'Check', schema: CHECK_SCHEMA, model: 'haiku', effort: 'low' }).then(c => ({ id: p.id, page: p.page, editor: e, check: c })))
return results.filter(Boolean)
