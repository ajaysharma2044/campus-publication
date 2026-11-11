export const meta = {
  name: 'ideas-batch-writer',
  description: 'Sprint mode: one Sonnet session per batch of 10 to 12 pages of one topic, written from the fact files only, no web research, no editor',
  phases: [{ title: 'Write', detail: 'one session per batch, all batches at once' }],
}
const REPO = '/Users/ajaysharma/Ads/campus-publication'
const { batches } = args
const SCHEMA = {
  type: 'object',
  properties: {
    batch_id: { type: 'string' },
    pages: { type: 'array', items: { type: 'object', properties: { id: { type: 'integer' }, page: { type: 'string' }, words: { type: 'integer' }, page_check_pass: { type: 'boolean' }, blocked: { type: 'array', items: { type: 'string' } } }, required: ['id', 'page', 'words', 'page_check_pass', 'blocked'] } },
    notes: { type: 'string' },
  },
  required: ['batch_id', 'pages', 'notes'],
}
const URL = p => {
  p = p.replace(/^content\//, '').replace(/^articles\//, '').replace(/\.md$/, '').replace(/^\/+/, '').replace(/\/+$/, '')
  const parts = p.split('/')
  if (parts[0] === 'tools' || parts[0] === 'datasets' || parts[0] === 'start') return '/' + parts[0] + '/' + parts[1] + '/'
  if (parts[0] === 'pages') return '/' + parts[1] + '/'
  return '/cornell/' + p + '/'
}
const CT = { 'off-campus-housing': 'housing', 'getting-around': 'getting-around', dining: 'dining' }
const itemBlock = (it, topic) => `### Page ${it.id}: ${it.title}
- slug ${it.slug}; file ${REPO}/review/${topic}/${it.slug}.md; page type ${it.pt}; primary query "${it.pq}"${it.rw ? `; REWRITE of the live page ${it.rw} (read it first; keep its slug, queue_id, readers, pillar and subject frontmatter and its facts where they still hold; every question it answers must still be answered)` : ''}${it.ent ? '; ENTITY page (shape below)' : ''}
- link to (each at most once, where its subject comes up): ${(it.rel || []).map(p => `${p.split('/').pop()} -> ${URL(p)}`).join('; ') || 'none'}${it.tools && it.tools.length ? `; tools you may embed with a \`\`\`tool <slug>\`\`\` line: ${it.tools.join(', ')}` : ''}${it.ds && it.ds.length ? `; datasets you may draw on: ${it.ds.map(d => 'content/datasets/' + d + '.md').join(', ')}` : ''}
- note: ${it.note || 'none'}`

const prompt = (b) => `You are the EduExplained guide writer in sprint mode: you write every page in this batch, one after another, from the fact files only. No web research: do not call WebFetch or WebSearch at all. Repository: ${REPO}; run every command from there. Publish nothing.

Read once, before the first page: .claude/skills/eduexplained-voice/SKILL.md and its references/before-after.md and references/edge-cases.md; .claude/skills/guide-writing/SKILL.md and references/page-types.md; .claude/skills/gold-set/examples/feature-pillar.md (annotations only: real names, reporting-style attribution, prose over templates).

Facts: ${b.facts} is the fact file for this batch's topic (${b.topic}); the other fact files are intel/off-campus-housing/facts.csv, intel/getting-around/facts.csv and intel/dining/facts.csv, and the apartment inventory is intel/off-campus-housing/inventory.csv (every row carries its source URLs). For each page, grep the fact files for the page's subject (fact and value columns), read the matching rows in full, and build the page from them: every number, date, rule and name on the page is a fact-row value (cited with that row's source_url, in the house parenthetical style, linked), a dataset or inventory value (cited with its source URL), or arithmetic on them with the inputs shown. Prefer confidence official, then secondary; a row marked unsourced may not be stated as fact. When the fact file lacks what a section needs, say so once in a plain sentence with a next step (who to ask, where to look) and move on. Never invent a fact, a number, a quote or a person. Never cite forum posts.

Page rules (page_check.py enforces them): frontmatter in YAML with the keys live pages use: title (at most 60 characters, starting with the primary query's words), mode: answer, dek (one sentence), meta (120 to 155 characters), primary_query, topic: ${CT[b.topic] || b.topic}, school: cornell-university, type (the page type), updated: 2026-11-10, idea_id, rewrites ("" or the live path), readers (reader keys such as first-year, sophomore, off-campus, grad-student, international, parent, low-budget, transfer-spring), subject (one specific, findable photo subject), tools (slugs embedded), sources (every URL you linked: list of {url, title, accessed: '2026-11-10'}), images (a list of {slot, alt, caption}; code fills photos later). Body: a \`\`\`glance block with 3 or 4 Key takeaways bullets (one decision or number each, under 20 words); the opening paragraph is the answer in 60 words or fewer with at most one link; sections headed by the plain questions a reader would search, each opening with its own answer; \`\`\`reader "If you're ..." blocks only where the answer changes for that reader; \`\`\`figure blocks (kind: cost_table rows {label, value}; kind: timeline rows {label, date}; kind: steps rows {label}; each with a title) where numbers compare, dates sequence or steps order; tables for costs and comparisons with a one-line source note underneath; <!-- ad-break --> lines only between complete sections; an FAQ only for questions not already answered; end with a short "What to do next" and the related guides. Each fact stated once in full with its source linked the first time; refer back after that. Never: hedge words without the condition they depend on; "Not confirmed:" labels; research narration ("we found", "per X's page read on Nov 8"); time-bound phrases ("this week"); planner or SEO talk; em dashes; money missing its cents ("$46.7"); filler (navigate, delve, vibrant, journey, seamless, robust, leverage, unlock, dive into, in today's); "hypothetical"; a fact stated more than twice; an opening that leads with what does not exist. Reading level eighth to tenth grade: one idea per sentence, average under 18 words, every term of art defined in plain words the first time. Dates in AP style ("Nov. 25," "Aug. 1, 2027"); prices carry their period ("$6,872 per semester for 2026-27"). Real names of buildings, streets, offices and officials. Length 900 to 1,600 words for a narrow question, up to 2,500 for a broad one; no padding.

Entity page shape (pages marked ENTITY): one named place, for a reader deciding whether to live or eat there. Open with what it is and who it is for in one or two sentences. Then a facts band as a figure (kind: cost_table rows {label, value}) or a short table: address or location, opened, residents or beds, room or unit types, rate or price with its period, dining, who lives there, how to get in; every value a fact row. Sections headed by the questions people search: what living (or eating) here is like and what sets it apart, what it costs, how to get a spot, what to watch (from reporting in the fact file, attributed). State only the facts that differ from the category default; the category-wide rules get one sentence and a link to the category hub named in the note. Link up to the hub and sideways to one or two sibling entities.

Workflow per page: grep and read the facts; write the whole page and save it with ONE Write call; run python3 .claude/skills/page-checks/scripts/page_check.py <file> once and fix only the lines it flags with Edit calls (no rerun, no rewriting); then the next page. Keep going until every page in the batch is saved.

${b.items.map(it => itemBlock(it, b.topic)).join('\n\n')}

Return JSON: batch_id "${b.batch_id}", pages (one entry per page: id, page (the file path relative to the repo), words, page_check_pass, blocked (questions the fact file could not answer)), notes.`

phase('Write')
const results = await parallel(batches.map(b => () => agent(prompt(b), { label: `batch:${b.batch_id}`, phase: 'Write', schema: SCHEMA, model: 'sonnet', effort: 'medium' })))
const out = results.filter(Boolean)
log(`${out.reduce((n, r) => n + r.pages.length, 0)} pages written in ${out.length} of ${batches.length} batches`)
return out
