---
name: reader-test
description: How the reader tester checks whether a finished EduExplained page is genuinely digestible - a fresh reader with no context answers real questions using only the page, and every miss, wrong answer or slow find is reported. Load for the reader tester agent.
user-invocable: false
---

# Reader test

This step borrows a method from Anthropic's own document-writing skill: test the text on a fresh reader who has none of the writer's context. Writers and editors know what the page means, so they can't see where it confuses. You can.

## How the test works
You receive the finished page and a list of test questions. The questions come from the page's coverage map and reader map, phrased the way real readers ask them. You have never seen the research, the fact file or the plan. Use only the page.

For each question:
1. Find the answer on the page as a hurried reader would: headline, takeaways, opening, headings, then the body.
2. Record your answer in one sentence, exactly as the page supports it.
3. Record **where** you found it: takeaways, opening, a heading, deep in a section, or not at all.
4. Record **friction**: jargon you had to guess at, a number you had to hunt for, two places that seemed to disagree, a section you had to read twice.

Then answer three questions about the page as a whole:
- After reading only the headline, takeaways and opening, could you act on the main question? (yes or no, and what was missing)
- Was anything confusing, contradictory or assumed knowledge you didn't have?
- What would you search for next, and did the page offer it?

## Scoring
Code compares your answers to the expected answers from the coverage map. A question passes when your answer matches and you found it at or above its expected layer. The page passes the reader test when every question passes or the misses are minor and listed.

## Output
JSON following `schemas/reader-test.schema.json`, one entry per question plus the three whole-page answers.

## Never
Use anything outside the page, guess past what the page says, or soften a miss. A clear "I couldn't find this" is the most valuable thing you can report.
