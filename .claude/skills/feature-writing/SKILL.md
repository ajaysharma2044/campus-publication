---
name: feature-writing
description: The outline-first, section-by-section workflow that produced the approved "Where Cornell Sleeps" pillar - skeleton with lede and nut graf, targeted research per section with full pages opened for every number, inline citations, then an adversarial source review. Load for the feature writer agent.
user-invocable: false
---

# Feature writing

This is the workflow behind the approved feature pillar in `gold-set/examples/feature-pillar.md`, written down so it can be repeated. It produced that page with 8 searches and 13 full pages read. It works because structure comes before research, so every search serves one section.

## 1. Skeleton first
Before any searching, write the page skeleton: title, dek, and every section heading in the order of the reader's life (for housing: year one, year two, the alternatives, leaving campus, other populations, money, the bigger picture, the calendar). Under each heading, one line saying what the section will hold. Then write the lede and the nut graf. Deciding the structure while it's cheap makes the research targeted instead of exhaustive.

## 2. The section loop
For each section, in order:
1. **Check what you already have.** Start from the topic's fact file and brief. Search only for what the section still needs or what may have changed.
2. **Search narrowly.** Short queries scoped to the section, with the year for anything that changes yearly ("Cornell housing rates 2026-2027"), because last year's numbers are everywhere. Use extended search only for fresh or scattered local news.
3. **Open the full page for every number, rule or quote you will cite.** Never cite a search snippet. Snippets get truncated and mix up sources: the housing run's first rates search returned a fee schedule from Cornell College in Iowa, a different school, with plausible-looking numbers.
4. **Write the section** with a citation beside every fact, in the house parenthetical style, and tables only where numbers compare.
5. **Note anything that changes another section** (a new event, a conflicting page) and fix it before moving on. In the housing run, the October 2026 fraternity suspension surfaced while reading another article and had to be added to the Greek housing section.

## 3. Source hierarchy
Official pages for every rule and price. Reputable reporting for events and what actually happened on the ground (Cornell's pages won't say a new dorm opened with broken refrigerators). Local press for the city-level picture. Forums never.

## 4. Adversarial source review (after drafting)
When the draft is done, read it as a skeptic looking for anything without a source:
- every sentence with a number, date, name, rule or ranking: is there a citation, and was its page opened in full?
- every descriptive claim from general knowledge ("a castle-like building with its own theater," "one of the oldest programs in the Ivy League"): find a source or cut it
- every comparison or superlative: sourced, or our own math with inputs shown?
- internal math: recompute it (the housing run confirmed its rate tables because room plus meal plan plus fee came within $50 of the trustees' average)
- conflicting official pages: say what each says and which applies
Run `page_check.py` too; its `unsourced` check flags paragraphs with numbers and no citation.

## 5. Finish
Add the service layer (dated calendar, checklist) and a complete sources list. List in your output every fact you could only support with a snippet, so the checker opens those pages before publishing.

## What this workflow can't do alone
It aggregates well, but aggregation is not a moat by itself. The strongest feature pages add a data step before writing: property records and assessments, archived page snapshots for price history (the Wayback Machine), our own samples and calculations. That work belongs to research lane E and arrives in the fact file.
