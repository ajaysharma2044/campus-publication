# Opportunity selection (role C)
Scores 0–5 with a written observation per score (`scoring.ANCHORS`); null when unassessed — never 0 by default.
Priority = 20 × (.25D + .25G + .20W + .20E + .10M). Advance needs priority ≥ 65 (configurable, unvalidated) and E ≥ 3 and G ≥ 3. Editorial exceptions are recorded with a rationale, never hidden in the score.
Demand: use `adapters.search.demand_summary` — variant groups are counted once; suppressed/unknown volumes are reported, not summed. SERP: ≤10 results per query variant, record result types, direct-answer quality (`navigational_official` satisfies navigational intent), freshness, and the **exact missing contribution**. "More words" is not a contribution.
Decision (`scoring.decide`): update · improve_section · new page (advance) · new_tool · merge · watch · reject · hold, with existing coverage checked and listed.
