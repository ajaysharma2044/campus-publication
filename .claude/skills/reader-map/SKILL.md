---
name: reader-map
description: How to define and size EduExplained's readers for a topic by situation, and the reader map output format. Load for the reader analyst agent. Covers situations versus demographics, sizing with official data, questions in readers' words, and what changes for each reader.
user-invocable: false
---

# Reader map

You define who reads about this topic and what is different about their situation. The architect uses your map to decide which readers get their own pages, which get a short block inside a page, and which need nothing special.

## Define readers by situation
A reader type is a situation that changes the answer: transfer student, international student on an F-1 visa, graduate student with a stipend, parent paying the bills, first-generation student, student on a tight budget, student with a car, commuter. Situations, not identities: we write for what someone faces, never for a protected characteristic. Reuse existing reader keys across topics when the person is the same (look at `intel/*/readers.json`); coin a new key only for a genuinely new situation.

## Size every reader with data
Give each reader type an estimated size for this topic's population and the source: the institution's Common Data Set or fact book (transfer enrollment, international share, graduate share), IPEDS, Census ACS for local populations, state data for K-12. A size with no source is written as "unknown" with the reason. Size plus the demand signals decides priority, so guesses here distort the whole plan.

## For each reader, record
- **key** (lowercase-hyphen, stable) and **name**
- **situation:** their constraints in one or two lines (year, start term, budget, visa, car, family, who pays, what they already know)
- **size:** estimate, source URL, and the population it refers to
- **questions:** five or more questions in their own words, each tied to a demand signal (a queue row id or a lane C theme)
- **what_changes:** each decision where the right answer differs for this reader, with the fact_id that makes it different ("deadline is Dec. 1 instead of Jan. 31: fact housing-2.4-0031")
- **mistakes:** their most likely costly mistakes and what each costs, with fact_ids
- **change_level:** high (most answers differ), medium (some), low (almost none)

A reader whose change_level is low still gets recorded, so the architect knows not to give them blocks.

## Output
Write `intel/<topic>/readers.json` following `schemas/reader-map.schema.json`, then validate:
`python3 scripts/validate_handoff.py schemas/reader-map.schema.json intel/<topic>/readers.json`

## Done when
Every reader has a sized estimate or a stated "unknown" with its reason, every what_changes item cites a fact_id, and no reader exists only because it sounds plausible: each has demand signals behind it.
