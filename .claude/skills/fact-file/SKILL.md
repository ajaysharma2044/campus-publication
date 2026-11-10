---
name: fact-file
description: Format and rules for the topic fact file (intel/<topic>/facts.csv), the single source of truth every page is built from. Load for the fact extractor, researcher, checker and any agent that reads or writes facts.
user-invocable: false
---

# The fact file

Every hard fact EduExplained publishes (a number, price, date, deadline, rule, phone number, address, count or legal requirement) lives as one row in `intel/<topic>/facts.csv` before it can appear on a page. Writers draw only from it. The checker verifies pages against it. If a fact isn't in the file, it doesn't go on the page.

Why a file instead of a prose brief: code can select exactly the rows a page needs, match every number on a page in seconds, and catch a bad value once at the source instead of on seven pages.

## Columns (exact order)
| Column | What goes in it |
|---|---|
| fact_id | `<topic>-<section>-<4 digits>`, stable forever; never reuse or renumber |
| topic | the topic slug |
| section | which part of the topic it belongs to (e.g. `2.7`) |
| fact | what the fact is, in a few words: "Security deposit cap" |
| value | the value exactly as it should appear on a page: "One month's rent, including any rent paid in advance" or "$46.70 to $62.10 each way" |
| applies_to | who or what it covers: "City of Ithaca rentals", "Cornell undergraduates, 2026-27" |
| period | the time it is valid for: "2026-27", "from Jan. 5, 2026", "fall 2026" |
| source_url | the page the value was read from |
| source_title | that page's title |
| checked | the date the value was read, YYYY-MM-DD |
| confidence | `official` (government, the institution itself, statute), `secondary` (reputable reporting, established data publishers) or `unsourced` |
| notes | conflicts, caveats, how a derived value was computed |

## Rules
1. **One fact per row.** "Day pass $25; monthly $60" is two rows.
2. **Write the value exactly as it will print.** Money keeps its cents ("$46.70"). Units are spelled the way the page will use them.
3. **Every price, rate, date or rule has a period or applies_to.** A price with no year is a future error.
4. **Conflicts get separate rows**, one per source, each with a note pointing at the other row's fact_id. The architect and writer decide which to follow; the file records both.
5. **Derived values** (a median you computed, a per-month figure) get their own row with `notes` showing the inputs and fact_ids used.
6. **No forum posts as sources.** Reddit, College Confidential and similar can inform what people ask; they never back a value.
7. **Never copy long passages.** The value is a short factual statement, not a quote.

## Scripts
- Validate before anything downstream reads the file:
  `python3 .claude/skills/fact-file/scripts/validate_facts.py intel/<topic>/facts.csv`
- Convert an existing brief's tables into a fact file (one-time migration):
  `python3 .claude/skills/fact-file/scripts/brief_tables_to_csv.py intel/<topic>/brief.md intel/<topic>/facts.csv`
  On the Nov. 2026 briefs this produced 635 rows for housing and 667 for getting-around, and the validator immediately caught the "$46.7" fare that had spread to seven pages.
