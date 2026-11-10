# EduExplained agent kit

Agent definitions, skills, handoff schemas and check scripts for the rebuilt EduExplained pipeline. Built Nov. 10, 2026 from the `campus-publication` repo's existing v3 prompts, the audit of all 108 published articles, the current Claude Code documentation for subagents and skills, a review of public agent skills on GitHub, and an analysis of how Investopedia, Niche, The New York Times, CNN, Fox News and NerdWallet-style guides build explainers.

**To just write pages now:** follow `RUN-NOW.md` (it works through `IDEAS.md`, 291 ideas, with no pipeline build).

**To build the full pipeline later:** open Claude Code in the repo with `claude --model fable` and say: "Execute SPEC.md stage by stage. Stop at every owner checkpoint."

Test it on three topics first: see `PILOT.md`.

The house standard is set by the owner-approved feature pillar in `.claude/skills/gold-set/examples/feature-pillar.md`. Paste its full text into that file before the pilot.

## What's in it

```
.claude/agents/          14 agent definitions (job, inputs, output, done condition, model, effort, turn limit, skills)
.claude/skills/          21 skills the agents preload, with references and scripts
schemas/                 11 JSON schemas for every handoff between agents
scripts/validate_handoff.py   validates any handoff file against its schema (no dependencies)
CLAUDE.md.proposed       a slim replacement for the current 4.6 KB CLAUDE.md
PILOT.md                 the three-topic test plan and pass bars
SPEC.md                  the build spec for Claude Code, stage by stage with acceptance checks
```

### The agents, in pipeline order
| # | Agent | Model | Effort | Skills it loads |
|---|---|---|---|---|
| 1 | topic-scout | sonnet | medium | topic-selection, ad-revenue-layout |
| 2 | data-scout (data engine) | sonnet | medium | data-inventory |
| 3 | researcher (one per lane) | sonnet | medium | research-lanes, fact-file |
| 4 | fact-extractor | haiku | low | fact-file |
| 5 | reader-analyst | sonnet | medium | reader-map, fact-file |
| 6 | architect | opus (test fable) | high | use-case-architecture, fact-file, reader-map |
| 7 | search-strategist | sonnet | low | search-analysis |
| 8 | layering | sonnet (test opus on pillars) | medium | layering, publisher-patterns, ad-revenue-layout, visuals, eduexplained-voice, gold-set |
| 9 | guide-writer | opus | high | eduexplained-voice, guide-writing, publisher-patterns, visuals, page-checks, gold-set |
| 9a | feature-writer (pillars, feature mode) | opus | high | eduexplained-voice, feature-writing, publisher-patterns, visuals, page-checks, gold-set |
| 9b | batch-writer (data pages) | sonnet | medium | eduexplained-voice, batch-verdicts, visuals, gold-set |
| 10 | editor | opus | medium | eduexplained-voice, editing, publisher-patterns, page-checks, gold-set |
| 11 | reader-tester | haiku | low | reader-test |
| 12 | checker | sonnet | low | fact-checking, fact-file |

Code (not an agent) runs between every step: it validates each handoff, builds the packet from the coverage map, layer plan, search brief and fact rows, finalizes the reader matrix, scores the reader test, and places ads only at the layer plan's marks.

### Where the new pieces came from
- **Feature writer:** the outline-first, section-by-section workflow that produced the approved "Where Cornell Sleeps" pillar, written down so it repeats, plus the three upgrades its own review called for: a data step before writing, full-page verification of every citation, and an adversarial source review after drafting.
- **Layering agent:** decides how each page presents its information (takeaways, spine, the right table, chart or calculator for each kind of data, reader blocks, ad breaks, links). Built from the publisher analysis in `publisher-patterns`.
- **Topic scout:** scores and scopes topics on demand, missing authority, data availability, ad value, fit and durability before any research is spent.
- **Reader tester:** adapted from Anthropic's public `doc-coauthoring` skill, which tests documents on a fresh reader with no context. A fast model answering real questions from the page alone is a direct test of digestibility.
- **Publisher patterns:** Investopedia's trust strip and Key Takeaways, Fox's "The Brief" and labeled scan sections, CNN and AP's situation-segmented sections, the Times' calculators, Niche's entity stat bands. Patterns only, never their text.
- **Ad revenue layout:** what raises RPM (deep reading, second pageviews, tools, high-value topics), where ad breaks may go, and what never to do.
- **Rejected from GitHub:** popular community "SEO content writer" skills recommend keyword density targets, hook intros, word-count goals and CTA conclusions; all four produce the padded pages the audit found, so none were used.

### The scripts (all tested on the real repo)
| Script | What it does | Result on current content |
|---|---|---|
| `page-checks/scripts/page_check.py` | repetition, opener, takeaways, hedges, narration, "Not confirmed", time-bound text, planner leaks, filler, formatting, reading grade | 0 of 108 current pages pass; flags match the audit |
| `fact-file/scripts/brief_tables_to_csv.py` | migrates an existing brief's tables into a fact file | 635 facts (housing), 667 (getting-around) |
| `fact-file/scripts/validate_facts.py` | blocks bad fact rows at the source | caught the "$46.7" fare that spread to 7 pages |
| `fact-checking/scripts/match_facts.py` | matches every number on a page to the fact file | about 77% of numbers on housing pages confirmed with zero Claude usage |
| `scripts/validate_handoff.py` | checks any handoff file against its schema | verified on the coverage map example |

## Speed design
Every Claude session costs startup time and usage, so the pipeline is built to run as few sessions per page as possible and to keep everything else in code.

| Per page | Current v3 pipeline | This kit |
|---|---|---|
| Writer | 1 session, reads ~20k words, 7 self-edits, 3 reader role-plays | 1 single-pass session, ~2k words of instructions plus a small packet, max 8 turns |
| Editing | cold editor on 1 page in 10, fix rounds on flagged pages | 1 editor session, max 12 turns |
| Fact check | 1 Sonnet session greps the brief for every fact | code matches numbers first; the checker runs only on pages with unmatched numbers |
| Reader test | none | Haiku; every page in the pilot, then pillars, new page types and a 1-in-5 sample |
| Search analysis and layering | inside the plan and writer prompts | batched: one session per ~10 pages of a topic |
| Run loop | batch cycles: every page waits for the slowest | streaming: each page moves on the moment its step finishes |

That is about 2 to 2.5 sessions per guide (writer, editor, sometimes the checker, sometimes the reader test) against 4 to 6 today, each much lighter. Data pages are cheaper still: one batch session writes 15 to 20.

**Orchestrator rules for speed** (for the build spec):
- Run as many workers as the usage allowance sustains, and pause cleanly at the limit (`sessions.py` already does this).
- Overlap topics: research and plan topic B while topic A is being written.
- Start each page's writer as soon as its own layer plan exists; never wait for the whole topic.
- Run the checker and the reader test at the same time, since both only read the edited page.
- Send pages of the same type through consecutively so the identical instructions at the start of each session hit Claude Code's prompt cache.
- Compute in code everything with a right answer: packets, internal link candidates, the reader matrix, tables, charts, image search, page checks, fact matching, reader test scoring.
- Reuse existing research: the housing and getting-around briefs convert straight into fact files, so those topics skip the research stage.

## How an agent is run
The orchestrator calls each agent as its own session on your subscription:

```
claude -p --agent guide-writer --output-format json \
  --json-schema "$(cat schemas/<return-schema>.json)" \
  "Write the page for packet build/packets/ithaca-security-deposit-rules-tenants.json"
```

Notes from the Claude Code docs that shape this:
- Don't use `--bare`: it skips your subscription login and needs an API key.
- `CLAUDE.md` loads into every session even with `--agent`, which is why the proposed one is short.
- Preloaded skills inject their full SKILL.md, so each SKILL.md is kept tight and detail sits in `references/`, read only when needed.
- Every agent shares one usage limit, so tokens per page is the speed lever.

## Installing
Copy `.claude/agents/`, `.claude/skills/`, `schemas/` and `scripts/validate_handoff.py` into the repo root. Keep the existing `.claude/settings.json` and hooks. Replace `CLAUDE.md` with `CLAUDE.md.proposed` once the new pipeline is live (the old pipeline still depends on the current one).

## What this kit does not do yet (the Claude Code build)
These are code changes for the build spec, not agent files:
1. **Packet builder:** code that assembles `build/packets/<slug>.json` from the coverage map, the layer plan, the fact rows its sub-questions cite, reader cards, the search brief and internal links (schema: `schemas/packet.schema.json`).
2. **Orchestrator:** replace the batch cycles in `scripts/v3/run.sh` with streaming, so each page moves through writer, editor and checker on its own; validate every handoff with `validate_handoff.py`.
3. **`sessions.py`:** add `--agent` and `--json-schema` support; log usage per agent per page.
4. **`content/index.json`:** generated list of every live page for the architect and search strategist.
5. **Matrix finalizer:** code that turns the architect's matrix proposal plus search briefs into the final page list for approval.
6. **Lint:** replace the word, source, reader and visual floors in `scripts/v2/lint.py` with `page_check.py`.
7. **Migration:** run `brief_tables_to_csv.py` on existing briefs and fix the rows `validate_facts.py` rejects.
8. **Reader test scoring:** code that compares the reader tester's answers to the coverage map's expected answers.
9. **Ad slots:** the renderer places ads only at `<!-- ad-break -->` marks.
9b. **Images:** fill each layer plan image slot: owner photo from `content/images/inbox/` first, else `scripts/v2/find_images.py` (already license-safe), charts rendered from fact rows, a 1,200-pixel-wide lead image.
10. **Benchmark:** the pilot's measurements in `PILOT.md`.

## Next steps, in order
1. **Pilot:** run the three topics in `PILOT.md` and review the pages against the pass bars.
2. **Gold set:** rewrite 3 to 5 pages (landlord guide first) and approve them into `.claude/skills/gold-set/examples/`.
3. **Test the writer and editor skills** on 2 or 3 gold-set inputs with the skill-creator tool before trusting them at scale.
4. **Build spec** for the code changes above, executed in Claude Code on Fable.
