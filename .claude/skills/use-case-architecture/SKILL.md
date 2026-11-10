---
name: use-case-architecture
description: How the architect turns a topic's facts, readers and demand into every use case, a layered hierarchy, one page per intent, and a coverage map for each page. Load for the architect agent. Covers finding use cases, layering, deduplicating against live pages, the reader matrix proposal, length tiers and coverage map format.
user-invocable: false
---

# Use-case architecture

You decide what EduExplained builds for a topic. Every page, every reader block and every sub-question a page must answer comes from your output, so your mistakes spread into every page and your clarity makes every writer's job easy. Work slowly and check yourself.

## Inputs
- `intel/<topic>/facts.csv` (the fact file)
- `intel/<topic>/readers.json` (the reader map)
- `intel/<topic>/raw/C-demand.md` and `D-competition.md` (what people ask, what's missing)
- `content/index.json` (every live page: slug, title, primary query, topic) so you never duplicate one

## Step 1: find every use case
A use case is a job the reader is trying to get done: find a place, budget the rent, sign a lease, get the deposit back, break a lease. Find them from three sources and note which source each came from:
1. **Asked:** the demand themes.
2. **Implied by process:** every deadline, form or rule in the fact file implies a job ("what do I do before the 120-day notice?").
3. **Gaps:** facts that exist but nobody explains clearly. These are our best openings.

## Step 2: layer them
Arrange use cases into a hierarchy: topic, then use case, then sub-questions, then edge cases. The hierarchy becomes the site structure: the topic gets a pillar, big use cases get guides, small ones become sections. Every fact in the fact file should land under at least one use case; facts that land nowhere are either trivia (drop) or a missed use case (add).

## Step 3: one page per intent
Two pages that answer the same question split our search traffic and confuse readers. Before proposing any page, compare its intent to every live page in `content/index.json` and every other page you're proposing. If they overlap, merge them or give each a clearly different job, and say which. Our audit found six groups of pages competing with each other; you are the agent that prevents this.

## Step 4: the reader matrix proposal
Cross every use case with every reader whose change_level is medium or high. For each cell propose:
- **page:** the combination is its own search intent ("international student lease Ithaca") with demand evidence
- **block:** the answer changes for this reader but nobody searches it separately; it becomes a short reader block inside the main page
- **blank:** the answer doesn't change; nothing is written
Give a one-line reason for every page and block. The search strategist and code confirm demand before anything is final.

## Step 5: a coverage map for every page
For each proposed page, write a coverage map: the sub-questions it must answer, each with the fact_ids that answer it, the reader blocks it carries and what goes in each, and the questions it deliberately leaves to a sibling page (with that page's slug). Size the page by its map, not by a word target:
- **quick answer:** up to about 6 sub-questions
- **guide:** about 7 to 20
- **pillar:** more than 20, written in parallel sections (give each section its own sub-question list)

A worked example is in `references/coverage-map-example.md`.

## Step 6: entity and comparison pages
Many topics are made of named things: dorms, houses, co-ops, apartment buildings, dining rooms, schools. Readers search for them by name ("Mews Hall review," "Collegetown Terrace rent"), so each can deserve its own page, plus comparisons between them. Build them as a hub-and-spoke tree:
- **Pillar** (the feature page for the whole topic) links to
- **Category hubs** (North Campus halls, West Campus houses, co-ops, Collegetown buildings), which link to
- **Entity pages** (one per dorm, house or building), which link sideways to
- **Comparison pages** (two or three entities a reader is choosing between).

**Make an entity inventory first.** List every entity with the facts you hold for it, then score each one. An entity gets its own page only if it has at least five reader-relevant facts that differ from its category's defaults (opening year, beds, room types, price, location and distance, dining, ownership, code or safety record, recent reporting) and at least one demand signal. Entities below that bar appear as a row in their category hub's table instead. A thin page for every name is exactly what search engines remove from their index, and it can drag the whole site down with it.

**Comparisons only where readers compare.** Propose a comparison page only when people actually search the pairing or the entities compete for the same reader (two North Campus halls, two Collegetown towers in the same price band), and the data shows real differences. Never generate every possible pair: 70 entities make 2,415 pairs, almost all of them pointless.

Write the inventory, with each entity's score and decision (own page, hub row, or merge), into `usecases.json` under `entities`, and give every approved entity and comparison page its own coverage map.

## Output
- `intel/<topic>/usecases.json` (the hierarchy and matrix proposal)
- `intel/<topic>/coverage/<slug>.json` for every page
Both follow the schemas in `schemas/`. Validate every file:
`python3 scripts/validate_handoff.py schemas/coverage-map.schema.json intel/<topic>/coverage/<slug>.json`

## Done when
Every fact belongs to a use case or is marked as trivia, no two pages (new or live) share an intent, every page has a coverage map whose sub-questions each cite fact_ids, and every matrix cell has a value and a reason.

## Never
Invent sub-questions the facts can't answer (send them back to research as gaps instead), or propose a page whose only difference from another is the reader's label.
