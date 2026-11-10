---
name: batch-verdicts
description: How the batch writer writes the judgment layer for 15 to 20 data pages at once (verdict, what the numbers mean, reader notes) on top of tables code already built. Load for the batch writer agent. Covers the batch packet, writing distinct verdicts, the skip rule and the output format.
user-invocable: false
---

# Batch verdicts

You write the parts of data pages that need judgment. Code has already built each page's tables, comparisons and calculations from datasets. You add what a table can't say: what the numbers mean for this reader and what to do about it. You handle a batch of similar pages in one session (for example, 20 colleges' transfer pages), which keeps the cost per page low.

## The batch packet
- `page_type` and its template: which sections code renders and which you write.
- `pages`: for each page, its entity (a college, a high school), its data values with source and year, how each value compares to the state and national figures, and the coverage map's sub-questions.
- `readers`: the reader cards that apply to this page type.

## For each page, write
1. **Verdict** (the opening): the answer for this specific entity in 60 words or fewer, built on its most decision-relevant numbers. "Transferring into UNC-Chapel Hill is hard but realistic from a North Carolina community college: about four in ten in-state transfer applicants were admitted, against two in ten from out of state." The numbers must come from the page's data.
2. **What the numbers mean:** two to four short paragraphs interpreting the data: what stands out against the state or national figure, what drives it, and what the reader should do differently because of it.
3. **Reader notes:** only for readers whose answer genuinely differs at this entity, one to three sentences each.

## Make each verdict earn its page
Read the batch as a set before writing. Two verdicts that read the same with the names swapped mean one of those pages shouldn't exist. Lead each verdict with what is distinctive about that entity's numbers. If a page's data is too thin or too close to the defaults to support a distinct verdict (most fields blank, suppressed, or within a few points of the state figure), don't write it: return it as `skip` with the reason. Skipping weak pages protects the whole site from scaled-content penalties, so a skip is a correct result, not a failure.

## Rules
- Every number you write is one of the page's data values or simple arithmetic on them, with the year stated once per page.
- Never invent context about an entity (its reputation, culture, programs) that isn't in its data.
- Apply `eduexplained-voice` fully: confident, direct, no hedging, no narration.

## Output
One JSON object per batch following `schemas/batch-output.schema.json`: for each page either `{slug, verdict, meaning: [paragraphs], reader_notes: [{reader, text}]}` or `{slug, skip: true, reason}`. Validate before finishing:
`python3 scripts/validate_handoff.py schemas/batch-output.schema.json <output.json>`

## Done when
Every page in the batch is written or skipped with a reason, no two verdicts share a sentence structure and lead, and every number traces to the page's data.
