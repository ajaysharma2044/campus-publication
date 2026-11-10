---
name: layering
description: How the layering agent decides how each EduExplained page presents its information so readers can understand and use it fast - the layers from headline to deep detail, the right visual or tool for each kind of data, the reading order, and ad-friendly page rhythm. Load for the layering agent.
user-invocable: false
---

# Layering

The architect decides **what** a page must answer. You decide **how the reader will see and use it.** The same facts can produce a page people skim in 20 seconds and act on, or a wall they abandon. Your layer plan is the difference.

Think about the reader's moment: they arrive from search or an AI answer with one question, often on a phone, often mid-task. Most will read the top and leave; some will scan for their situation; a few will read everything. A good page serves all three without making any of them wade through what the others need.

## The layers (top to bottom)
| Layer | What it holds | Who it serves |
|---|---|---|
| 0. Headline + dek | What the page answers, and for whom | everyone, in search results and at the top |
| 1. Key takeaways | 3 or 4 bullets: the decisions and numbers that matter most | the 10-second reader |
| 2. Opening answer | the verdict in 60 words or fewer | the 30-second reader |
| 3. Scan layer | the one table, tool or chart that holds the core numbers | the reader comparing options |
| 4. Sections | one per sub-question, each opening with its answer | the reader with a specific question |
| 5. Situations | reader blocks or "If you're..." sections | the reader whose answer differs |
| 6. Edge cases and watch-outs | exceptions, deadlines people miss, costly mistakes | the careful reader |
| 7. Next step | what to do now, then related guides | everyone who finished |

Every layer must stand alone. A reader who stops after layer 2 has a correct, usable answer. A reader who jumps straight to layer 4 from the table of contents doesn't need anything above it to understand the section.

## Match each kind of data to its form
Look at the facts each sub-question cites and pick the form that makes them easiest to use. The full table is in `references/data-to-format.md`. The core rules:
- Options compared on the same attributes: **table**.
- A process with an order: **numbered steps**, each with its deadline or cost.
- Dates across months: **timeline**.
- A change over time: **line chart**.
- An answer that depends on the reader's own numbers: **calculator or tool**. This is the strongest engagement asset we have, so ask for one whenever the decision is genuinely personal.
- A few key values about one entity: **stat band** (4 to 6 values with year and source).
- Situations that change the whole answer: **"If you're..." sections** as the main structure.
- A single number with context: a sentence. Not everything needs a visual.

## Choose the mode first
- **Feature** for pillars and "how this whole system works" pages: a scene-led opening, a nut graf by paragraph 3, a story spine, context and current events, then the service layer (calendar, checklist, sources). Model: `gold-set/examples/feature-pillar.md`.
- **Answer** for a specific question (a deadline, a fee, a rule, a how-to): takeaways, then the answer in the first paragraph.
Write the mode into the layer plan; the writer and page checks follow it.

## Choose the page's spine
Pick one organizing principle and say why:
- **By question** (default): sections follow the coverage map's sub-questions.
- **By situation:** when most sub-questions have different answers for different readers, organize by reader instead.
- **By time:** when the reader's main need is sequencing ("what to do when"), organize by phase.
- **By option:** for decision pages, one section per option after the comparison table.

## Page rhythm and ad revenue
EduExplained earns from display ads, so how a page reads also determines what it earns. Ads pay most on pages people read deeply and on visits that continue to a second page. Design for that, never against the reader:
- Mark **ad breaks** only between complete sections, after the opening layers, never inside a table, list, tool, steps or a reader block. The renderer places ads only at your marks. Details are in the `ad-revenue-layout` skill.
- Plan **2 to 4 internal links** inside the body where a reader naturally wants the next guide, plus the related-guides module at the end.
- Length follows the coverage map. A longer page earns more only if every section is worth reading; padding raises exits and lowers ad value.

## Output
A complete worked example is in `references/layer-plan-example.json`.

`intel/<topic>/layers/<slug>.json` following `schemas/layer-plan.schema.json`: headline, dek, the takeaways (as fact_ids plus the point each makes), the spine and its reason, every section in order with its sub-questions, form and fact_ids, reader blocks, tools or charts requested with their inputs, the lead image and body visuals (see the `visuals` skill), ad break positions, internal link placements, and the next step. Validate it:
`python3 scripts/validate_handoff.py schemas/layer-plan.schema.json intel/<topic>/layers/<slug>.json`

## Done when
Every sub-question on the coverage map appears in exactly one section, every section has a form chosen for its data, the takeaways and opening could stand alone as a correct answer, and ad breaks sit only between complete sections.

## Never
Add sub-questions or facts the coverage map doesn't have, or choose a visual to fill space. If the coverage map makes a clear layer plan impossible (sub-questions that belong on different pages, a missing answer), report it in `problems` instead of working around it.
