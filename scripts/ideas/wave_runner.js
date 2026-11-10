export const meta = {
  name: 'ideas-wave',
  description: 'Write one wave of EduExplained ideas with a pool of five writers, then check, edit, fact-check and record each page as it lands',
  phases: [
    { title: 'Write', detail: 'five writers at a time, next idea starts the moment one finishes' },
    { title: 'Check', detail: 'page_check.py and match_facts.py on every page' },
    { title: 'Fix', detail: 'editor once when checks fail or the page is a feature; checker once when numbers are unmatched' },
    { title: 'Status', detail: 'IDEAS-STATUS.md row per page' },
  ],
}
const REPO = '/Users/ajaysharma/Ads/campus-publication'
const WRITERS = 5
const { wave, items, factsByTopic, extraFacts } = args
const CONTENT_TOPIC = { 'off-campus-housing': 'housing', 'getting-around': 'getting-around', dining: 'dining', money: 'money' }
const URL = p => {
  p = p.replace(/^content\//, '').replace(/^articles\//, '').replace(/\.md$/, '').replace(/^\/+/, '').replace(/\/+$/, '')
  const parts = p.split('/')
  if (parts[0] === 'tools' || parts[0] === 'datasets' || parts[0] === 'start') return '/' + parts[0] + '/' + parts[1] + '/'
  if (parts[0] === 'pages') return '/' + parts[1] + '/'
  return '/cornell/' + p + '/'
}
const relatedList = it => (it.related || []).map(p => `  - ${p} -> link as ${URL(p)}`).join('\n') || '  (none)'

const CHECK_SCHEMA = {
  type: 'object',
  properties: {
    pass: { type: 'boolean' }, words: { type: 'integer' }, reading_grade: { type: 'number' },
    counts: { type: 'object' },
    problems: { type: 'array', items: { type: 'object', properties: { check: { type: 'string' }, line: { type: ['integer', 'null'] }, msg: { type: 'string' } }, required: ['check', 'msg'] } },
    numbers: { type: 'integer' }, matched: { type: 'integer' },
    unmatched: { type: 'array', items: { type: 'object', properties: { line: { type: 'integer' }, token: { type: 'string' }, context: { type: 'string' } }, required: ['line', 'token', 'context'] } },
  },
  required: ['pass', 'words', 'problems', 'numbers', 'matched', 'unmatched'],
}
const FACT = { type: 'object', properties: { fact: { type: 'string' }, value: { type: 'string' }, applies_to: { type: 'string' }, period: { type: 'string' }, source_url: { type: 'string' }, source_title: { type: 'string' }, checked: { type: 'string' }, confidence: { type: 'string' } }, required: ['fact', 'value', 'source_url'] }
const WRITER_SCHEMA = {
  type: 'object',
  properties: {
    slug: { type: 'string' }, words: { type: 'integer' },
    sub_questions_answered: { type: 'array', items: { type: 'string' } },
    reader_blocks: { type: 'array', items: { type: 'string' } },
    blocked: { type: 'array', items: { type: 'string' } },
    new_facts: { type: 'array', items: FACT },
    snippet_only_facts: { type: 'array', items: { type: 'string' } },
    unsourced_cut: { type: 'array', items: { type: 'string' } },
    searches: { type: 'integer' }, pages_opened: { type: 'integer' },
    tool_files: { type: 'array', items: { type: 'string' } },
  },
  required: ['slug', 'words', 'sub_questions_answered', 'blocked', 'new_facts', 'snippet_only_facts'],
}
const EDIT_SCHEMA = {
  type: 'object',
  properties: {
    slug: { type: 'string' }, words_before: { type: 'integer' }, words_after: { type: 'integer' },
    cut: { type: 'object' },
    missing: { type: 'array', items: { type: 'string' } },
    kept_flags: { type: 'array', items: { type: 'object', properties: { check: { type: 'string' }, line: { type: ['integer', 'null'] }, reason: { type: 'string' } }, required: ['check', 'reason'] } },
  },
  required: ['slug', 'words_before', 'words_after', 'missing', 'kept_flags'],
}
const CHECKER_SCHEMA = {
  type: 'object',
  properties: {
    verdict: { type: 'string', enum: ['pass', 'fix', 'reject'] },
    numbers_total: { type: 'integer' }, matched_by_code: { type: 'integer' }, verified: { type: 'integer' }, fixed: { type: 'integer' }, removed: { type: 'integer' },
    new_facts: { type: 'array', items: FACT },
    fact_file_updates: { type: 'array', items: { type: 'object', properties: { fact_id: { type: 'string' }, new_value: { type: 'string' }, source_url: { type: 'string' }, reason: { type: 'string' } }, required: ['fact_id', 'new_value', 'reason'] } },
    fix_instructions: { type: 'array', items: { type: 'string' } },
    reason: { type: 'string' },
  },
  required: ['verdict', 'numbers_total', 'matched_by_code', 'verified', 'fixed', 'removed', 'new_facts', 'fact_file_updates', 'fix_instructions', 'reason'],
}
const STATUS_SCHEMA = { type: 'object', properties: { ok: { type: 'boolean' }, output: { type: 'string' } }, required: ['ok', 'output'] }

const SKILLS_COMMON = `Read first, in this order (all paths under ${REPO}):
1. .claude/skills/eduexplained-voice/SKILL.md, then its references/before-after.md and references/edge-cases.md
2. .claude/skills/publisher-patterns/SKILL.md
3. .claude/skills/visuals/SKILL.md
4. .claude/skills/gold-set/SKILL.md and examples/feature-pillar.md (the texture to copy: real names, reporting-style attribution, prose over templates)`

const PAGE_RULES = (it, page) => `Page rules (the checks enforce them)
- Frontmatter (YAML, the keys live pages use): title (at most 60 characters, starting with the primary query's words), mode: ${it.mode === 'F' ? 'feature' : 'answer'}, ${it.mode === 'F' ? 'kicker (the feature\'s evocative name, a few words), ' : ''}dek (one sentence), meta (120 to 155 characters), primary_query, topic: ${CONTENT_TOPIC[it.topic] || it.topic}, school: cornell-university, type: ${it.page_type}, updated: 2026-11-10, idea_id: ${it.id}, rewrites: "${it.rewrite_target || ''}", readers (list of reader keys the page serves, from the live /start/ keys such as first-year, sophomore, off-campus, grad-student, international, parent, low-budget, transfer-spring, car-on-campus, upper-year-no-car), subject (one specific, findable photo subject such as "Collegetown apartment buildings, College Avenue, Ithaca"), tools (slugs of tools embedded), sources (every source URL you linked: a list of {url, title, accessed: '2026-11-10'}), images (a list of {slot, alt, caption}: a lead slot and any body slots; code fills the photos later).
- Body blocks, exactly as live pages write them: a \`\`\`glance block with 3 or 4 Key takeaways bullets (one decision or number each, under 20 words); \`\`\`reader "If you're ..." blocks only where the answer changes for that reader, holding only what differs; \`\`\`figure blocks (kind: cost_table with rows {label, value}; kind: timeline with rows {label, date}; kind: steps with rows {label}; each with a title) wherever numbers compare, dates sequence or steps order, built from fact rows; a \`\`\`tool <slug>\`\`\` line to embed a tool where the decision is personal; <!-- ad-break --> lines only between complete sections, never inside a table, list or block.
- Each fact stated once in full with its source linked the first time, in the house parenthetical style ("...$21,348 (Cornell Chronicle)." with the name linked); refer back after that or leave it out; tables and figures may repeat a number. Our own math shown with its inputs. Tables carry a one-line source note underneath.
- Never: hedge words without the condition they depend on; "Not confirmed:" labels; research narration ("we found", "per X's page read on Nov 8"); time-bound phrases ("this week", "right now"); planner or SEO talk; em dashes; money missing its cents ("$46.7"); filler (navigate, delve, vibrant, journey, seamless, robust, leverage, unlock, dive into, in today's); forum posts, Reddit or College Confidential as sources; a fact from memory; an opening that leads with what does not exist; "hypothetical" examples (use a concrete setup instead).
- Reading level eighth to tenth grade: one idea per sentence, average under 18 words, every term of art defined in plain words the first time. Dates in AP style ("Nov. 25," "Aug. 1, 2027"); prices carry their period ("$6,872 per semester for 2026-27"). Real names of buildings, streets, offices and officials.
- Output file: ${page} (create the directory if needed). This is a review draft, not a live page; publish nothing.`

const guidePrompt = (it, page) => `You are the EduExplained guide writer. Repository: ${REPO}; run every command from there. Write one complete EduExplained page for the idea below, in the house voice, in a single pass, and save it with one Write call. You may open the source page behind any fact you cite (WebFetch) so the value, period and who it applies to are exact, but you do not search the web for new facts: every number, date, rule and name on the page comes from the fact file rows you cite${it.datasets && it.datasets.length ? ', the datasets named below' : ''}${it.inventory ? ', the apartment inventory' : ''}, or is arithmetic on them with the inputs shown.

${SKILLS_COMMON}
5. .claude/skills/guide-writing/SKILL.md and references/page-types.md (the shape for page type "${it.page_type}")
${it.rewrite_target ? `6. The live page you are rewriting: ${it.rewrite_target}. Read all of it. Keep its slug, URL, queue_id, readers, pillar and subject frontmatter and its facts where they still hold; rewrite everything else to the new standard. The old page is also your coverage map: every question it answers must still be answered unless the fact behind it has no source.` : ''}
${it.tags.includes('TOOL') ? `7. Two existing calculators, whose conventions you copy exactly: content/tools/ithaca-rent-commute-calculator/tool.md and tool.html, and content/tools/omniride-break-even-calculator/tool.md and tool.html.` : ''}

The idea
- id ${it.id}: "${it.title}" (${wave}, answer mode); page type ${it.page_type}; primary query "${it.primary_query}"; slug ${it.slug}
- fact file: ${it.facts}. Read only the rows relevant to this idea: grep the CSV by keywords in the fact and value columns, read those rows in full, and open the source page for every fact you cite. Prefer confidence official, then secondary; a row marked unsourced may not be stated as fact (mention the gap once with a next step, at most).
${it.datasets && it.datasets.length ? `- datasets you may draw on: ${it.datasets.map(d => `content/datasets/${d}.md (its CSV sits alongside)`).join('; ')}` : ''}
${it.inventory ? `- the Ithaca apartment inventory: intel/off-campus-housing/inventory.csv (every row carries its source URLs; cite them)` : ''}
- live pages to link to, each at most once where its subject comes up:
${relatedList(it)}
- live tools you may embed with a \`\`\`tool <slug>\`\`\` line: ${(it.tools || []).join(', ') || '(none)'}
- coordinator's note: ${it.note || '(none)'}
${it.tags.includes('TOOL') ? `
This idea builds a calculator. Build it under ${REPO}/review/tools/${it.slug}/ as tool.html and tool.md, copying the two existing tools' conventions (tool.md frontmatter with kind: tool, numbers_as_of, sources; self-contained HTML with no external scripts; inputs with labels; the math and every number's source shown in the tool itself). Every number the tool uses comes from a fact row with its source shown. Then the page embeds it with a \`\`\`tool ${it.slug}\`\`\` line and explains the inputs, the numbers and the math, as the live tool pages do. Publish nothing.` : ''}

${PAGE_RULES(it, page)}
- Shape: the opening paragraph is the answer in 60 words or fewer with at most one link; sections headed by the plain questions a reader would search, each opening with its own answer; an FAQ only for questions not already answered; end with a short "What to do next" and the related guides. Length follows scope: a narrow question gets 900 to 1,600 words, a big one 2,000 to 3,500. No padding.

Finish: save the page with one Write call (no rereading loops; code runs page_check.py next and an editor fixes what it flags). Then return JSON: slug, words, sub_questions_answered (the questions the page answers), reader_blocks (reader labels used), blocked (questions you could not answer from the fact file and why), new_facts (facts you cited that are not in the fact file, each {fact, value, applies_to, period, source_url, source_title, checked, confidence}; rare, and only from a source page you opened), snippet_only_facts (facts whose source page would not open; the checker opens them)${it.tags.includes('TOOL') ? ', tool_files (the tool files you wrote)' : ''}.`

const featurePrompt = (it, page) => `You are the EduExplained feature writer. Your pages are the hubs the rest of the site links to, so they get the slow, careful treatment: skeleton first, then a section loop with full pages opened for every number, rule or quote you cite, then an adversarial source review. Repository: ${REPO}; run every command from there.

${SKILLS_COMMON}
5. .claude/skills/feature-writing/SKILL.md (the workflow you follow exactly)
6. .claude/skills/page-checks/SKILL.md
${it.rewrite_target ? `7. The live page you are rewriting: ${it.rewrite_target}. Read all of it. Keep its slug, URL, queue_id, readers, pillar and subject frontmatter and its facts where they still hold; rewrite everything else to the feature standard; every question it answers must still be answered unless the fact behind it has no source.` : ''}

The idea
- id ${it.id}: "${it.title}" (${wave}, feature mode hub); page type ${it.page_type}; primary query "${it.primary_query}"; slug ${it.slug}
- start from what exists: ${it.facts} (grep it for the subject and read the rows in full) and the topic brief ${it.brief} (grep its headings for the subject); then search narrowly for what each section still needs, with the year for anything that changes yearly. Official pages for every rule and price; reputable reporting for events and history; local press for the city picture; forums never. Open the full page for every fact you cite; a search snippet never counts (a snippet once returned Cornell College in Iowa's fees for a Cornell University query).
${it.datasets && it.datasets.length ? `- datasets you may draw on: ${it.datasets.map(d => `content/datasets/${d}.md (its CSV sits alongside)`).join('; ')}` : ''}
${it.inventory ? `- the Ithaca apartment inventory: intel/off-campus-housing/inventory.csv (every row carries its source URLs; cite them)` : ''}
- live pages to link to, each at most once where its subject comes up:
${relatedList(it)}
- live tools you may embed with a \`\`\`tool <slug>\`\`\` line: ${(it.tools || []).join(', ') || '(none)'}
- coordinator's note: ${it.note || '(none)'}
- a hub compares its whole set: include a reference table with one row per entity in scope (every hall, house, co-op, building or option the title promises), giving the facts the fact file or official pages state (name, address, year opened, beds or units, room or unit types, rate band, who lives there) with a source line under the table; entity pages that fall below the site's entity bar live on in this table.

${PAGE_RULES(it, page)}
- Shape (feature mode): a short, specific, true scene or tension in the lede, the frame of the whole page by the second or third paragraph (the nut graf), then the stakes in numbers; a story spine (time or the reader's path); why things are the way they are (history, decisions, the people who made them, the forces on them now); current events woven in where they matter; our own math as insight; fair trade-offs from reputable reporting; it ends forward, then turns to service: a dated calendar or checklist and a complete sources list. Length: 3,000 to 6,000 words, set by the scope, no padding.

Finish: run python3 .claude/skills/page-checks/scripts/page_check.py ${page} and fix what it flags (keep only flags you can defend under accuracy or coverage). Then return JSON: slug, words, searches, pages_opened, sub_questions_answered (the questions the page answers), blocked (what you could not establish from a full page), snippet_only_facts (facts you could support only with a snippet; the checker opens them), unsourced_cut (claims removed in the adversarial review), new_facts (facts found that are not in the fact file, each {fact, value, applies_to, period, source_url, source_title, checked, confidence}).`

const checkPrompt = (it, page) => `Run two scripts from ${REPO} and report their results exactly; change no file.
1. python3 .claude/skills/page-checks/scripts/page_check.py ${page} --json
2. python3 .claude/skills/fact-checking/scripts/match_facts.py ${page} ${it.facts}${(extraFacts || []).map(f => ' ' + f).join('')} --json
Return JSON: pass (script 1's pass), words, reading_grade, counts (script 1's counts object), problems (up to 40 of script 1's problems as {check, line, msg}), numbers, matched, unmatched (up to 40 of script 2's unmatched as {line, token, context}). If a script fails to run, set pass false and put its error in problems with check "script-error".`

const editorPrompt = (it, page, check, writer) => `You are the EduExplained editor. You did not write this draft; read it the way a reader would. Your job is to cut and sharpen so it reads like the gold set: answer first, each fact once, confident, no narration, nothing that fails to add a fact, step or decision. You never add facts, numbers, sources or claims; if something is missing you report it. Repository: ${REPO}; run every command from there.

Read first: .claude/skills/eduexplained-voice/SKILL.md (and references/before-after.md, references/edge-cases.md), .claude/skills/editing/SKILL.md and references/cut-list.md, .claude/skills/page-checks/SKILL.md, .claude/skills/publisher-patterns/SKILL.md, .claude/skills/gold-set/examples/feature-pillar.md.

Draft: ${page} (mode ${it.mode === 'F' ? 'feature' : 'answer'}). Its question: "${it.title}" (primary query "${it.primary_query}"). It must still answer that and the sub-questions the writer set out to answer: ${JSON.stringify(writer?.sub_questions_answered || [])}.${it.rewrite_target ? ` It rewrites the live page ${it.rewrite_target}: every question the live page answered must still be answered.` : ''}
page_check.py reports (${check.words} prose words, grade ${check.reading_grade}): ${JSON.stringify(check.problems.slice(0, 30))}

Edit in the order the editing skill gives: run the checks; make the opening the answer (feature pages keep their scene but state the frame by paragraph three); cut repetition (a fact's main statement plus at most one reference; gut reader blocks that restate general facts and delete empty ones); turn hedges into flat statements where the fact is solid or state exactly what the answer depends on; delete narration, planner notes and announcements; line edit (one idea per sentence, verbs over nouns, the specific word over the category); make every section open with its answer; run the checks again until they pass or every remaining flag is one you can defend under accuracy or coverage. Never cut a fact that answers a sub-question, a source link's main statement, a number inside a worked example, or exact legal wording. Edit the file in place with Edit calls.
Return JSON: slug, words_before, words_after, cut {repetition, hedges, narration, planner, other} (integers), missing (sub-questions no longer answered or never answered), kept_flags (page_check flags you deliberately kept, each {check, line, reason}).`

const checkerPrompt = (it, page, check, writer) => `You are the EduExplained checker: make sure every number and attribution on the page is right, spending effort only where code could not confirm it. Never rewrite for style, add claims, or treat a search snippet as verification; open the page. Repository: ${REPO}; run every command from there.
Read first: .claude/skills/fact-checking/SKILL.md and .claude/skills/fact-file/SKILL.md.

Page: ${page}. Fact file: ${it.facts}${(extraFacts || []).length ? ' (also ' + extraFacts.join(', ') + ')' : ''}.${it.inventory ? ' The apartment inventory intel/off-campus-housing/inventory.csv also counts as a fact source (each row carries its source URLs).' : ''}
match_facts.py matched ${check.matched} of ${check.numbers} numbers; unmatched: ${JSON.stringify(check.unmatched.slice(0, 40))}
The writer listed these snippet-only facts: ${JSON.stringify(writer?.snippet_only_facts || [])} and these new facts with sources: ${JSON.stringify((writer?.new_facts || []).slice(0, 40))}

For each unmatched number decide which kind it is: our arithmetic (recompute from fact-row values; fix the page if wrong); a fact missing from the fact file (open the source the page links, in full; if it supports the value, period and who it applies to, mark ok and add it to new_facts; otherwise fix it from the source or remove the claim); a misquoted fact (the fact file wins unless you open its source and the source shows the file is out of date; then fix the page and report it in fact_file_updates). Every snippet-only fact must be opened before the page can pass. Check attributions ("Cornell requires...") against the source. Then the adversarial pass: flag every sentence that states a fact without a citation and source it or cut it. Fix in place with Edit calls: wrong numbers, dates, periods, units, source links; change nothing else.
Write ${REPO}/review/checks/${it.slug}.json following schemas/check-result.schema.json and validate it: python3 scripts/validate_handoff.py schemas/check-result.schema.json review/checks/${it.slug}.json (fix until it prints VALID).
Verdict: pass when every number is matched, recomputed correctly, or verified and fixed; fix when a problem needs a rewrite you may not do (one exact instruction per problem); reject when the opening answer is wrong or a fact the page depends on has no support after one search.
Return JSON: verdict, numbers_total, matched_by_code, verified, fixed, removed, new_facts, fact_file_updates, fix_instructions, reason.`

const statusPrompt = (it, fields) => `Record one idea's status for the EduExplained idea run. From ${REPO}: write the file review/_status/${String(it.id).padStart(3, '0')}.json with the Write tool containing exactly this JSON object plus an "updated" field set to the current local time as "YYYY-MM-DD HH:MM": ${JSON.stringify(Object.assign({ id: it.id }, fields))}
Then run: python3 scripts/ideas_status.py
Change nothing else. Return JSON: ok (true when the script printed "IDEAS-STATUS.md rebuilt"), output (the script's one-line output).`

const setStatus = (it, fields) => agent(statusPrompt(it, fields), { label: `status:${it.id}`, phase: 'Status', schema: STATUS_SCHEMA, model: 'haiku', effort: 'low' })

async function afterWrite(it, page, writer) {
  const notes = []
  if (!writer) {
    await setStatus(it, { status: 'failed', page: '', page_check: '', unmatched: '', note: 'writer session returned nothing (skipped or died); re-run' })
    return { id: it.id, status: 'failed' }
  }
  let check = await agent(checkPrompt(it, page), { label: `check:${it.id}`, phase: 'Check', schema: CHECK_SCHEMA, model: 'haiku', effort: 'low' })
  if (!check) check = { pass: false, words: writer.words || 0, problems: [{ check: 'script-error', msg: 'check runner returned nothing' }], numbers: 0, matched: 0, unmatched: [] }
  let kept = []
  let editor = null
  if (!check.pass || it.mode === 'F') {
    editor = await agent(editorPrompt(it, page, check, writer), { label: `edit:${it.id}`, phase: 'Fix', schema: EDIT_SCHEMA, model: 'opus', effort: 'medium' })
    if (editor) {
      kept = editor.kept_flags || []
      notes.push(`editor cut ${editor.words_before}->${editor.words_after} words`)
      if (editor.missing && editor.missing.length) notes.push(`editor reports missing: ${editor.missing.slice(0, 3).join('; ')}`)
    } else notes.push('editor session returned nothing')
    const re = await agent(checkPrompt(it, page), { label: `recheck:${it.id}`, phase: 'Check', schema: CHECK_SCHEMA, model: 'haiku', effort: 'low' })
    if (re) check = re
  }
  let checker = null
  if (check.unmatched.length || (writer.snippet_only_facts || []).length) {
    checker = await agent(checkerPrompt(it, page, check, writer), { label: `verify:${it.id}`, phase: 'Fix', schema: CHECKER_SCHEMA, model: 'sonnet', effort: 'low' })
    if (checker) {
      notes.push(`checker ${checker.verdict}: ${checker.verified} verified, ${checker.fixed} fixed, ${checker.removed} removed, ${checker.new_facts.length} new facts`)
      if (checker.verdict !== 'pass') notes.push((checker.reason || checker.fix_instructions.join('; ')).slice(0, 200))
      const fin = await agent(checkPrompt(it, page), { label: `final:${it.id}`, phase: 'Check', schema: CHECK_SCHEMA, model: 'haiku', effort: 'low' })
      if (fin) check = fin
    } else notes.push('checker session returned nothing')
  }
  const keptKinds = new Set(kept.map(k => k.check))
  const remaining = check.problems.filter(p => !keptKinds.has(p.check))
  const checksOk = check.pass || remaining.length === 0
  const factsOk = checker ? checker.verdict === 'pass' : check.unmatched.length === 0
  const ok = checksOk && factsOk
  const status = ok ? (it.rewrite_target ? 'rewrite-done' : 'done') : 'needs-review'
  if (!ok) {
    if (!checksOk) notes.push(`page_check still fails: ${remaining.slice(0, 4).map(p => p.check + (p.line ? ' l' + p.line : '')).join(', ')}`)
    if (!factsOk) notes.push(checker ? `checker verdict ${checker.verdict}` : `${check.unmatched.length} numbers unmatched`)
  }
  if (writer.blocked.length) notes.push(`gaps the writer reports (no source states them): ${writer.blocked.slice(0, 3).join('; ')}`)
  if (kept.length) notes.push(`kept flags: ${kept.map(k => k.check).join(', ')}`)
  await setStatus(it, { status, page, words: check.words || writer.words || 0, page_check: check.pass ? 'PASS' : (checksOk ? 'PASS (kept flags)' : 'FAIL'), unmatched: check.unmatched.length, note: notes.join('. ') })
  return { id: it.id, status, page, words: check.words || writer.words, page_check: check.pass, unmatched: check.unmatched.length, new_facts: [...(writer.new_facts || []), ...((checker && checker.new_facts) || [])], fact_file_updates: (checker && checker.fact_file_updates) || [], notes }
}

const chains = []
const results = []
let next = 0
phase('Write')
const worker = async () => {
  while (next < items.length) {
    const it = items[next++]
    const page = `review/${it.topic}/${it.slug}.md`
    await setStatus(it, { status: 'writing', page, note: it.note || '' })
    const prompt = it.mode === 'F' ? featurePrompt(it, page) : guidePrompt(it, page)
    const opts = it.mode === 'F' ? { label: `feature:${it.id}`, phase: 'Write', schema: WRITER_SCHEMA, model: 'opus', effort: 'high' } : { label: `guide:${it.id}`, phase: 'Write', schema: WRITER_SCHEMA, model: 'opus', effort: 'medium' }
    const writer = await agent(prompt, opts)
    log(`idea ${it.id} written (${writer ? writer.words + ' words' : 'no result'}); ${items.length - next} left to start`)
    chains.push(afterWrite(it, page, writer).then(r => { results.push(r); return r }))
  }
}
await parallel(Array.from({ length: Math.min(WRITERS, items.length) }, () => worker))
await parallel(chains.map(c => () => c))
const done = results.filter(r => r.status === 'done' || r.status === 'rewrite-done').length
log(`${wave}: ${done} of ${items.length} pages done; ${results.filter(r => r.status === 'needs-review').length} need review; ${results.filter(r => r.status === 'failed').length} failed`)
return { wave, results }
