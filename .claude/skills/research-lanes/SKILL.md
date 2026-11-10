---
name: research-lanes
description: How EduExplained researches a topic in parallel lanes and what each lane must deliver. Load for the researcher agent. Covers lane assignments, source quality rules, how to record facts for the fact file, and how to mark gaps.
user-invocable: false
---

# Research lanes

You research one lane of one topic. Other researcher sessions run the other lanes at the same time, so stay inside yours. Your notes become fact-file rows, so every value you record needs a source URL and the date you read it.

## The five lanes
| Lane | Job in one line |
|---|---|
| A. Official | Every rule, price, fee, deadline, process and contact from the institution and government bodies that touch the topic |
| B. Market and data | Everything countable from the market: prices by category, providers, timing, recurring costs, with sample sizes and dates |
| C. Demand | What real people ask about this topic, in their words, and how often. Signals only, never sources |
| D. Competition | For the topic's most-asked questions, what currently answers them and what those answers miss |
| E. Original analysis | New information built by combining public sources, with every step shown so it can be redone |

Your lane's full playbook is in `references/lanes.md`. Read only your lane's section. Source rules for all lanes are in `references/source-rules.md`; read them before you open your first page.

## What you deliver
Write `intel/<topic>/raw/<lane-letter>-<lane-name>.md` with:
1. **Fact rows** in a markdown table with exactly these columns: `| Fact | Value | Source URL | Applies to | Period | Checked |`. One fact per row, the value written exactly as it should print (money with cents), the period stated for every price or rule.
2. **Process notes** for anything with steps (how to apply, how to appeal), in order, each step linked to its source.
3. **Conflicts:** where two sources disagree, both rows, each noting the other.
4. **Gaps:** a final table of what you looked for and could not find: `| Question | Where you looked | What a reader should do instead |`. A gap is useful information; never fill one with a guess.
5. **Pages read:** URL, title, date read.

The fact extractor turns your tables into the fact file, so a malformed table means lost facts.

## Done when
- Every subtopic in your lane has rows or an entry in the gaps table.
- Every row has a source URL, a checked date, and a period or applies_to.
- Nothing in your notes comes from memory. If you know something but can't find a source today, it goes in gaps.

## Never
- Cite forum posters (Reddit, College Confidential, Discord) as the source of a fact. Lane C records what people ask, not what is true.
- Copy more than a short phrase from any source. Record the fact, not the prose.
- Log in anywhere, bypass paywalls, or fetch pages a site blocks.
