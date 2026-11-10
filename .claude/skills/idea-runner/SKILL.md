---
name: idea-runner
description: How the main Claude Code session works through IDEAS.md - preparing each topic's fact file, deduplicating against live pages, applying the entity bar, sending each idea to the right writer subagent in parallel, building calculators, checking every page and tracking status. Load in the main session when asked to run the idea list.
---

# Running the idea list

You are the coordinator. You don't write pages yourself; you prepare facts, decide what each idea needs, dispatch writer subagents five at a time, check their work and keep the status file current. Speed matters: keep five subagents busy at all times.

## 1. Prepare facts once per topic (before its first wave)
| Topic folder | Research that exists | What to do |
|---|---|---|
| off-campus-housing | brief.md with sourced tables | `brief_tables_to_csv.py` into `facts.csv`, then `validate_facts.py`; fix errors from the source pages |
| getting-around | brief.md with sourced tables | same as above |
| dining | raw/ lane notes (official, market, voice, competition, analysis) | run the fact-extractor agent on `intel/dining/raw/` into `facts.csv` |
| money | raw/ lane notes | run the fact-extractor agent on `intel/money/raw/` into `facts.csv` |

A feature-writer may research beyond the fact file; guide-writers use only the fact file plus the source pages behind the rows they cite.

## 2. Before dispatching an idea
1. **Duplicate check.** Compare the idea with every live page in `content/articles/` (title and `primary_query`) and every page already written in `review/`. If a live page answers the same question, the job becomes a **rewrite** of that page to the new standard, keeping its URL slug. If two ideas overlap, write one page and mark the other `merged`.
2. **Entity bar (ENTITY ideas).** The entity needs at least five reader-relevant facts in the fact file that differ from its category's defaults, and at least one demand signal (a search suggestion, a "People also ask" question, a demand row in `queue/queue.csv`, or reporting about it). Below the bar: mark it `hub-row` and make sure its row appears in the hub page's table instead.
3. **DATA ideas** wait until their data exists. Wave 1's "every apartment building" idea starts the Ithaca apartment inventory: build `intel/off-campus-housing/inventory.csv` (address, owner, units, unit sizes, prices with dates, lease dates, distance to campus, source URLs) from landlord websites, the City of Ithaca's rental certificate records and Tompkins County property records. Never invent a building, price or owner. Budget-tier, landlord and building pages draw on it.
4. **TOOL ideas.** Copy the conventions of an existing calculator in `content/tools/` (read two first), build the new one there, and have the page embed it with a ```tool block. Every number a tool uses must come from the fact file, with its source shown in the tool.

## 3. Dispatch
- Mode F goes to the `feature-writer` agent; mode A to the `guide-writer` agent.
- Give each subagent: the idea title, its topic folder, the path to `facts.csv` (and `inventory.csv` when relevant), the live page it rewrites if any, the related pages to link to, and the output path `review/<topic>/<slug>.md`.
- Tell guide-writers to read only the fact rows relevant to the idea and to open the source page for any fact they cite.
- Run five at a time. When one finishes, start the next idea immediately.

## 4. Check every page as it lands
1. `python3 .claude/skills/page-checks/scripts/page_check.py <page>`
2. `python3 .claude/skills/fact-checking/scripts/match_facts.py <page> intel/<topic>/facts.csv`
3. If page_check fails, or the page is a feature, send it to the `editor` agent once. If numbers are unmatched, send it to the `checker` agent once.
4. A page that still fails after one round is marked `needs-review` with the reasons.

## 5. Track status
Keep `IDEAS-STATUS.md` with one row per idea: id, title, status (`queued`, `writing`, `done`, `rewrite-done`, `merged`, `hub-row`, `waiting-data`, `needs-review`, `failed`), the page path, word count, page_check result, unmatched facts, and a note. Update it every time a page finishes. After every 10 pages, add a one-paragraph progress note at the top: pages done, pages left, problems.

## Never
Publish to the live site, invent facts to fill a page, write a page whose only difference from another is a name, or use forum posts as sources.
