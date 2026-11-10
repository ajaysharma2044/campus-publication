---
name: topic-selection
description: How the topic scout finds, scores and scopes EduExplained topics before any research starts - demand, the absence of a clear authority, data availability, ad value and fit with existing pages - and writes the topic brief that frames the research. Load for the topic scout agent.
user-invocable: false
---

# Topic selection

Choosing the wrong topic wastes every agent's work after you. Your job is to pick topics where EduExplained can become the best answer, and to scope each one so the researchers know exactly what to cover.

## What makes a good topic
Score each candidate from 1 to 5 on each factor and write one sentence of evidence per score:
| Factor | A 5 looks like |
|---|---|
| Demand | many distinct real questions about it, from search suggestions, "People also ask" boxes and question titles in search results |
| No clear authority | top results are thin, outdated, scattered across several sites, or official pages that never state the answer plainly |
| Data available | official sources and public datasets cover the core facts, so pages can be built on hard data |
| Ad value | the topic touches money decisions (aid, loans, costs, scholarships, housing costs), which advertisers pay more to reach (see `ad-revenue-layout`) |
| Fit | it connects to existing EduExplained pages and readers, so internal links help both |
| Durability | answers stay useful for a year or more, or the topic recurs every year (deadlines, cycles) |

Demand, no clear authority, and data available are gates: a topic scoring 2 or lower on any of them doesn't proceed, however high its ad value.

## Scope the winner
A topic is a cluster of related questions one research effort can cover: "Off-campus housing at Cornell," "Transferring into UNC system schools," "The 2026 federal student loan changes." Too broad ("college") can't be researched in one pass; too narrow ("the Dryden Road garage daily cap") is a page, not a topic.

The topic brief states:
- the topic name and slug, and one sentence on who it serves
- the scope: what's in and what's out (with the existing page or future topic that owns each excluded piece)
- the 20 to 40 seed questions, in readers' words, with the signal for each
- the official sources and datasets researchers should start from
- the competitors that currently rank and what they miss
- the scores with their evidence
- any time pressure (a deadline season, a law taking effect)

## Output
`intel/<topic>/topic.json` following `schemas/topic-brief.schema.json`, validated with `python3 scripts/validate_handoff.py`. When asked to compare candidates, also write `intel/_candidates/<date>.json` ranking them.

## Never
Pick a topic only because it pays well, scope a topic so broadly the research can't finish, or rely on forum posts for anything but evidence of what people ask.
