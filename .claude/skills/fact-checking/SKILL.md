---
name: fact-checking
description: How the checker verifies a finished EduExplained page code-first, matching every number against the fact file and then verifying only what code could not match. Load for the checker agent. Covers running the matcher, recomputing our math, verifying unmatched facts, fixing in place and the verdict.
user-invocable: false
---

# Fact checking

Most numbers on a page come straight from the fact file, and code confirms those in seconds. You spend your effort only on what code couldn't match.

## Steps
1. **Run the matcher:**
   `python3 .claude/skills/fact-checking/scripts/match_facts.py <page> intel/<topic>/facts.csv`
   Everything it matched is verified. Work only through its unmatched list.
2. **For each unmatched number, decide which kind it is:**
   - **Our arithmetic** (a total, a per-month figure, a date counted from a rule): recompute it from fact-file values. Right: mark ok and note the inputs. Wrong: fix the number on the page.
   - **A fact missing from the fact file:** open the source the page links for it. If the source supports it exactly (value, period, who it applies to), mark ok and add it to `new_facts` in your output so it joins the fact file. If not, fix it from the source or remove the claim.
   - **A misquoted fact** (the fact file has a different value): the fact file wins unless you open its source and the source shows the file is out of date. In that case fix the page and report the correction in `fact_file_updates`.
3. **Check attributions:** a sentence that names a source ("Cornell requires") must match what that source actually says and who it applies to.
4. **Fix in place** with Edit: wrong numbers, dates, periods, units, and wrong source links. Change nothing else: no rewording for style, no cuts, no additions beyond what a fix needs.

## Full-page rule
Open the full page behind every fact you verify; a search snippet never counts. Any fact the writer listed in `snippet_only_facts`, and any fact-file row whose notes say "snippet only," must be opened before the page can pass. If the page can't be opened, the fact is cut or the page waits.

## Adversarial pass
After the numbers, read the page as a skeptic: flag every sentence that states a fact (a number, date, name, rule, ranking, superlative or descriptive claim) without a citation, and every claim that sounds like general knowledge rather than a source. Source it or cut it. The `unsourced` flag in `page_check.py` catches paragraphs with numbers; you catch the rest.

## Verdict
- **pass:** every number is matched, recomputed correctly, or verified and fixed.
- **fix:** a problem you can't fix yourself (a claim needs a source the page doesn't have, a section needs rewriting). One exact instruction per problem. Rare.
- **reject:** the opening answer is wrong, or a fact the page depends on has no support after one search.

## Output
`content/checks/<slug>.json` following `schemas/check-result.schema.json`.

## Never
Rewrite for style, add new claims, or trust a search snippet as verification. Open the page.
