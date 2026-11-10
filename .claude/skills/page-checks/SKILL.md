---
name: page-checks
description: Mechanical self-checks every writer and editor runs on a draft before finishing. Load with any agent that produces reader-facing pages. Flags repeated facts, long or link-heavy openings, hedging, research narration, "Not confirmed" labels, time-bound phrases, planner notes, filler words and formatting errors.
user-invocable: false
---

# Page checks

Run this on your draft before you finish, every time:

```
python3 .claude/skills/page-checks/scripts/page_check.py <path/to/article.md>
```

It prints PASS or FAIL and every problem with its line number. Fix each one, then run it again. You are done only when it passes, or when every remaining flag is a deliberate exception you can defend (see below).

## What each check means

| Check | Fails when | Why it matters |
|---|---|---|
| repetition | a fact value appears more than twice in prose, reader blocks and the summary | repeats are our biggest source of bloat |
| opener | the first paragraph is over 60 words, has more than 1 link, or opens with what doesn't exist | the opening is the answer; readers and AI tools judge the page by it |
| hedges | more than 2 hedge words per 1,000 prose words | hedges hand the decision back to the reader |
| narration | "we found", "our arithmetic", "read on Nov 8" and similar | research notes are not answers |
| not-confirmed | the "Not confirmed" label | state a gap once, plainly, with a next step |
| time-bound | "this week", "right now", "if you are reading this" | pages stay live; anchor advice to dates |
| planner-leak | "pages that rank", "primary query", "AI answers miss" | SEO talk belongs in the packet, not on the page |
| filler | banned filler words | they signal generic writing |
| format | em dashes, double periods, money missing a cents digit | small errors cost trust |

Tables and figure blocks are skipped (except for repetition, which also scans reader and glance blocks), because a table repeating a number the prose states is fine.

## Deliberate exceptions
A flag can stand only if fixing it would break a higher rule in `eduexplained-voice` (accuracy, then coverage). Examples: a hedge word that is literally part of a rule's official wording ("a landlord may not charge an application fee"), or a fact repeated a third time inside a worked calculation where the reader needs to see it. List every exception you keep, with its reason, in your output so the next step can see it.

## Thresholds
The limits live at the top of the script (MAX_REPEATS, OPENER_MAX_WORDS, OPENER_MAX_LINKS, HEDGE_PER_1000_MAX). Change them there, in one place, not in your judgment.
