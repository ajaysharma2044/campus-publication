# Search intelligence (new role: search-intel · contract `serp_intel.json`)
Spec: continuous-local-run R13, R15, R20, R21, R26, R36. Permitted sources only: the WebSearch tool, official pages, supplied keyword exports. Never scrape Google result pages, autocomplete, or paid tools. Reddit and any community site: **search-result observation only** (titles, URLs, dates, visible snippets) unless the permissions registry says `fetch_permitted` or `api_authorized`.

## Per cluster
1. Query variants students actually use (from the packet's hypotheses and observed questions; add wording you see in results). Pick **2** variants to observe (sample first, never the whole list — R25).
2. For each variant, record up to 10 results as they appear: position, url, title, publisher, result_type (official | aggregator | forum | news | other), `dedicated` (a page about exactly this question?), answer_quality (complete | partial | none | navigational_official), freshness (current | stale | unknown; stale = older than 18 months or wrong academic year), evidence_quality (sourced | unsourced | unknown), and the **exact missing contribution**. "More words" is not a contribution.
3. "People also ask"-style follow-up questions when visible. Community occurrences (forum threads asking the question) with url, title, site, date: these are demand evidence (R20), never content.
4. Seasonality notes (when the question peaks; what cycle it follows).
5. `demand_evidence`: one item per independent occurrence (related_question | forum_thread | official_faq | keyword_export). Independent threads count separately; the same thread twice counts once.
6. Label everything `observed via search tool on <date>`. It is not Google rank and not measured volume.

## Reddit site: searches (R36)
`site:reddit.com/r/Cornell <topic>` and `site:reddit.com/r/ithaca <topic>` (and the town's other subs). Record thread title, URL, date, visible snippet. Do not open the thread.

## Cache (R26)
Before searching, check the packet's `cached_queries`: a query observed inside the last `CAMPUS_SERP_CACHE_DAYS` (14) is reused, not re-searched. Report `search_calls_made` and `cache_hits` truthfully.

## Rank re-check (R15)
For a published page, observe its target variants and record whether our page appears (position or absent). No causal claims.
