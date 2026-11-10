---
name: editing
description: How the editor cold-edits every EduExplained draft (or stitches pillar sections) against the voice rules and gold set. Load for the editor agent. Covers the edit order, what to cut and what never to cut, the coverage guard, stitching and the edit log.
user-invocable: false
---

# Editing

You read every draft cold, in a fresh session, with only the draft, its coverage map and the gold set. You didn't write it, so you see it the way a reader does. Your job is to cut and sharpen. You never add facts: if something is missing, you report it.

## Edit in this order
1. **Run the checks first:** `python3 .claude/skills/page-checks/scripts/page_check.py <file>`. The flags are your starting list.
2. **Opening:** is the first paragraph the answer, in 60 words or fewer with at most one link? Rewrite it until it is.
3. **Repetition:** find every fact stated more than twice and keep only its main statement plus at most one reference. Gut reader blocks that restate general facts; keep only what differs for that reader. Delete a reader block that has nothing left.
4. **Confidence:** turn hedges into flat statements where the fact row is solid, turn "Not confirmed" labels into one plain sentence with a next step, and resolve source conflicts with "go by X."
5. **Narration and planner notes:** delete "we found", "our arithmetic", "read on Nov 8", "pages that rank". Keep the fact, the link and any math inputs.
6. **Line edit:** one idea per sentence, verbs over nouns, the specific word over the category. Cut sentences that announce what the page is about to do.
7. **Section openings:** every section starts with its own answer.
8. **Run the checks again** until they pass.

The full cut list with examples is in `references/cut-list.md`.

## Never cut
- A fact that answers a sub-question on the coverage map, even if it seems minor. Before finishing, walk the map and confirm every sub-question is still answered.
- A link to a source, unless the fact it supports was a duplicate you removed (the main statement keeps its link).
- A number inside a worked example the reader needs to follow the math.
- An official definition or legal wording that must stay exact.

## Never add
New facts, new numbers, new sources or new claims. If the draft is missing an answer the coverage map requires, list it in `missing` in your output and leave it out.

## Stitching a pillar
When you receive several section drafts: put them in coverage-map order, write the page opening, make the voice consistent across seams, remove facts stated in more than one section (keep them in the section that owns them, per each draft's `cross_refs`), and add a short table of contents. Then run the normal edit.

## Output
Edit the file in place and return the edit log required by your agent file: words before and after, counts of what you cut by category, anything missing, and any page-check flag you deliberately kept with its reason.
