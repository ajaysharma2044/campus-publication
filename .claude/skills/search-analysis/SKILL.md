---
name: search-analysis
description: How the search strategist analyzes what currently answers a page's query (intent, top results, gaps, AI answers) and writes the search brief that goes into the writer's packet. Load for the search strategist agent.
user-invocable: false
---

# Search analysis

For each planned page, you find out what the page has to beat and hand the writer a short, specific brief. You don't write the page and you don't rewrite the plan, but you can recommend merging or killing a page when the evidence says it can't win or isn't needed.

## Steps
1. **Search the primary query** and two close variants from the coverage map.
2. **Read the top results** (up to 8). For each: URL, publisher, type (official page, news, forum, blog, aggregator, tool), date, what it covers, and what it gets wrong, leaves out or has outdated.
3. **Classify the intent:** quick fact, how-to, decision or comparison, cost, checklist, or tool. The writer shapes the page to match it.
4. **Check AI answers where they show in results:** if an AI summary or answer box appears, note what it says and which sources it cites. Never log in to any service to check.
5. **Name the gap:** what a reader still can't get from the current results. This is the one thing our page must do better. Be concrete: "No result gives the 14-day rule and the 2019 change together; the top two still say 30 days."
6. **Recommend:** `build` (gap is real), `merge` (another of our pages or a planned page already covers the intent; name it), or `kill` (no demand evidence, or no way to be meaningfully better). Explain in one sentence.
7. **Packaging:** a title, a meta description (120 to 155 characters, states the answer and includes the primary query), and the structured data types that fit (Article, plus Dataset or HowTo-style steps where relevant). Internal link candidates are computed by code from shared use cases and facts; you don't need to choose them.

## Titles that rank
The title is the single strongest on-page signal and the line people decide to click on, so it follows a formula, even on feature pages:
- **Primary query first.** Lead with the words people actually search: "Cornell Meal Plans," "Cornell Housing," "Ithaca Security Deposit Rules." Put the most-searched entity and noun at the very start, where both Google and readers weigh them most.
- **The year, when the answer changes yearly.** Prices, rates and deadlines get "2026-27"; a timeless explainer doesn't.
- **A specific promise after the colon:** what the reader gets ("Costs Compared," "Every Dorm, Co-op and Apartment Option," "Deadlines and Fees").
- **60 characters or fewer,** so it isn't cut off in results.
- **The H1 matches the title,** so Google uses our title instead of rewriting it.
- **No clever-only titles.** A feature's evocative name ("The Swipe Economy," "Where Cornell Sleeps") moves to the kicker line above the H1, where it adds voice without costing rankings.

Write 2 or 3 candidates and pick the one that best matches the primary query and the top competitors' wording.

## Output
`intel/<topic>/search/<slug>.json` following `schemas/search-brief.schema.json`. Validate:
`python3 scripts/validate_handoff.py schemas/search-brief.schema.json intel/<topic>/search/<slug>.json`

## Done when
Intent is classified, at least 5 results are recorded (or fewer with the reason), the gap is one concrete sentence, and the recommendation has its reason.

## Never
Put SEO language into anything that reaches the page. Your brief informs the writer; the writer never repeats it to readers.
