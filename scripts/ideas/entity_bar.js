export const meta = {
  name: 'entity-bar',
  description: 'Judge every ENTITY idea against the entity bar: five reader-relevant facts in the fact file that differ from its category, plus one demand signal',
  phases: [{ title: 'Judge', detail: 'eight entities per session' }],
}
const REPO = '/Users/ajaysharma/Ads/campus-publication'
const { entities } = args
const SCHEMA = {
  type: 'object',
  properties: {
    entities: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          id: { type: 'integer' }, title: { type: 'string' }, category: { type: 'string' },
          facts_distinct: { type: 'array', items: { type: 'object', properties: { fact_id: { type: 'string' }, value: { type: 'string' } }, required: ['fact_id', 'value'] } },
          distinct_count: { type: 'integer' },
          demand: { type: 'array', items: { type: 'object', properties: { type: { type: 'string' }, evidence: { type: 'string' } }, required: ['type', 'evidence'] } },
          verdict: { type: 'string', enum: ['pass', 'hub-row'] },
          hub_idea_id: { type: 'integer' },
          note: { type: 'string' },
        },
        required: ['id', 'title', 'category', 'facts_distinct', 'distinct_count', 'demand', 'verdict', 'hub_idea_id', 'note'],
      },
    },
  },
  required: ['entities'],
}
const batches = []
for (let i = 0; i < entities.length; i += 8) batches.push(entities.slice(i, i + 8))
phase('Judge')
const results = await parallel(batches.map((b, i) => () => agent(`You apply the EduExplained entity bar to the entity ideas below. Repository: ${REPO}; run every command from there. An entity page is written only if it clears the bar; otherwise it becomes a row in its hub page's table.

The bar (owner's idea-runner skill): the entity needs at least five reader-relevant facts in the fact file that differ from its category's defaults, AND at least one demand signal (a search suggestion, a "People also ask" question, a demand row in queue/queue.csv, or reporting about it).

For each entity:
1. Facts: grep the fact files intel/off-campus-housing/facts.csv, intel/getting-around/facts.csv, intel/dining/facts.csv and intel/off-campus-housing/inventory.csv (if it exists) for the entity's name and its variants (spellings, abbreviations, street address). Read the matching rows. Count only facts that are about this entity and would change a reader's decision (its address, year opened, beds or units, room types, its own rate when it differs from the category rate, dining room, amenities, policies specific to it, lease terms, price per bed, owner), not facts every member of its category shares (the two-year live-on rule, the campus-wide meal plan rule, a category-wide rate). List them with fact_id and value.
2. Demand: grep queue/queue.csv (columns question, demand_evidence, topic) for the name; run one web search for "<entity name> Cornell" and note any autocomplete-style suggestions, "People also ask" questions or reporting (Cornell Daily Sun, Cornell Chronicle, Ithaca Voice, Ithaca Times) about it; record each signal with its evidence in one line.
3. Verdict: pass when distinct_count >= 5 and at least one demand signal exists; otherwise hub-row, naming the hub idea whose table must carry its row: 1 North Campus dorms compared; 2 West Campus houses compared; 3 South Campus halls near Collegetown; 4 Cornell program houses; 5 Cornell co-ops; 6 Collegetown apartments guide (private buildings); 7 Cornell graduate housing guide (Hasbrouck, Maplewood, grad buildings); 9 Fraternity and sorority housing (chapter houses); 125 the West Campus dining rooms (dining entities), or 6 for private Collegetown buildings.
Do not search for new facts to add; the bar is about what the fact file already holds. Change no files.

Entities: ${JSON.stringify(b)}
Return JSON with one entry per entity, in order.`, { label: `bar:${i + 1}`, phase: 'Judge', schema: SCHEMA, model: 'sonnet', effort: 'medium' })))
const out = results.filter(Boolean).flatMap(r => r.entities)
log(`${out.filter(e => e.verdict === 'pass').length} entities pass, ${out.filter(e => e.verdict === 'hub-row').length} become hub rows`)
return out
