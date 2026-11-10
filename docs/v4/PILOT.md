# Pilot plan: three topics before the switch

Nothing replaces the current pipeline until the new one beats it on real pages. The pilot runs three topics chosen to test different things, then compares the results against the current site and against the best existing pages for the same questions.

## The three topics
| Topic | What it tests | Pages |
|---|---|---|
| **Off-campus housing at Cornell** (rebuild) | Direct before/after: the same questions the current site already answers, so every new page has an old page to beat | 6 to 8: the pillar, the deposit rules, when to sign, the landlord guide, cheapest housing, what a month costs |
| **The 2026 federal student loan changes** | Competing with the top publishers on a high-value national topic: CNN, Fox, NBC, NPR and NerdWallet-style guides already cover it, and finance advertisers pay the most | 4 to 6: the overview, repayment options by when you borrowed, borrowing caps for graduate and parent loans, a repayment calculator page |
| **Transferring into UNC system universities** | The data engine: entity pages built from public data, plus one researched guide that ties them together | 1 guide plus 10 to 16 data pages (one per campus), with the batch writer free to skip campuses whose data is too thin |

## Run order (for speed)
1. **Housing first, today's research reused.** Convert the existing brief into a fact file and start at the architect. No research stage, so the first reviewable pages come out within hours of the build finishing.
2. **Loans and UNC transfer in parallel with your housing review.** Their research runs while you read the housing pages.
3. **Review with a scorecard, not an essay.** For each page: new versus old (or versus the best competitor), win, tie or lose, plus one line on why. About 3 minutes a page.

## How each topic runs
1. Topic scout writes the topic brief (for the housing rebuild, start from the existing brief and convert its tables with `brief_tables_to_csv.py`).
2. Researchers, fact extractor, reader analyst, architect, search strategist, layering.
3. Writer (or batch writer), editor, reader tester, checker.
4. Pages go to a review folder, not to the live site.

## What gets measured
| Measure | How | Pass bar |
|---|---|---|
| Page checks | `page_check.py` on every final page | 100% pass, or every kept flag justified |
| Digestibility | reader tester answers the coverage map questions using only the page | 90%+ of questions answered correctly at or above their expected layer |
| Fact accuracy | `match_facts.py` plus the checker's verdict | zero wrong numbers on review; every page a "pass" |
| Leanness | words cut by the editor, repeated facts flagged | no fact stated more than twice |
| Cost and speed | usage and minutes per page, per agent, from `sessions.py` logs | at least 2x fewer session-minutes per page than the current 6.6 to 9.1 |
| Quality (owner) | you read each new page beside the old page or the best competing page, without knowing which agent settings made it | the new page wins on at least 8 of 10 |
| Ad readiness | ad breaks only between sections, 2 to 4 internal links, a next step, a tool where the decision is personal | all pages |

## Decisions the pilot settles
- Opus or Fable for the architect; Sonnet or Opus for layering on pillars.
- Sonnet draft plus Opus edit versus Opus throughout, per page type.
- Whether the thresholds in `page_check.py` (60-word opening, 2 hedges per 1,000 words, grade 10) are right or need adjusting.
- Which rewritten pages become the gold set.

## Go or no-go
Switch the pipeline over only if every pass bar is met on all three topics. If one topic fails, fix the agent or skill responsible, rerun that topic, and compare again.
