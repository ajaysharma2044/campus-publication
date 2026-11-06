# Search strategy (new role: search-strategist · contract `search_strategy.json`)
Spec: continuous-local-run R14, R22, R23, R37, R45. Inputs: `serp_intel.json` for the cluster(s), the opportunity scores (D, AGI, G, E, niche_score), existing pages and the current cluster map. Output per school and topic: `search_strategy.json` plus the readable `docs/strategy/<school>/<topic>.md` (the coordinator writes the file from your JSON).

## Cluster map
One page or tool per query group. Two of our pages must never target the same query. Reuse an existing page (format `section`) when a group is already covered. Paths follow the URL policy: `/schools/<school>/<topic>/<slug>/`, `/towns/<town>/<topic>/<slug>/`, comparisons under `/compare/<a>-vs-<b>/`.

## Capture format (R23)
entity_guide for "<hall> review" intent (verified facts + an attributed "what residents report" section only when permitted sources exist; otherwise the page says the section is omitted and why), comparison only for pairs with an observed query, calculator when the answer is arithmetic, section when the question is a sub-case of an existing page.

## Win plan per page
- `contribution`: the specific thing that beats the current results — a verified fact table, a calculator, a comparison, a step the others miss. Tie it to what the top 3 results already say (information gain, R37).
- `target_title` ≤ 60 characters containing the primary query in natural form; `h1` matching intent; `answer_first_intro` ≤ 50 words that answers the query and is quotable as a snippet.
- `snippet_formats`: table for comparisons, numbered_steps for procedures, definition_sentence for "what is". FAQ block only for real observed questions (`faq_real_questions`).
- `secondary_questions` from search intel become H2/H3s.

## Hub and internal-link plan
school hub → topic hub → guides/tools, with exact anchor text; at least 3 contextual links per page plus up-links, and at least one existing page that links back.

## Trust signals
sources section, methods page link, visible updated date (only on substantive updates), corrections link.

## Refresh cadence and win criteria
cadence_days from source volatility (rates: yearly; deadlines: each cycle; hours: quarterly) and season. win_criteria: the variants to re-check and when; success = our page appears for the target variants (observed via the search tool). No causal claims.
