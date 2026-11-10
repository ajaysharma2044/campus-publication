---
name: data-inventory
description: How to find, document and judge public datasets that could power EduExplained data pages (colleges, high schools, transfer, districts, programs). Load for the data scout agent. Covers what to record per dataset, the uniqueness test, licensing and the inventory output format.
user-invocable: false
---

# Data inventory

You find and document the public datasets in one subject area, such as college costs and outcomes, high schools, transfer pathways, or pre-K. You do not analyze data or plan pages. Your inventory tells the architect exactly which data pages are possible and which are not.

Why this matters: data pages can scale to thousands, but only where real data gives each page a genuinely different answer. A page that differs from its neighbors only by the school's name is a liability under Google's scaled-content policies and can drag down the whole site. Your honest inventory is what keeps the data engine on the right side of that line.

## Where to look
Federal sources first (Department of Education: College Scorecard, IPEDS, Civil Rights Data Collection, NCES Common Core of Data; Census: ACS), then state education departments (school report cards, transfer and articulation agreements, state aid programs), then institutional publications (Common Data Sets), then established nonprofits that publish open data. Commercial data that requires a paid license gets listed, marked as such, and never downloaded.

## For each dataset, record
- **Name, publisher, URL** of the dataset page and of the download or API.
- **Entities:** what one row describes (an institution, a school, a program, a district) and roughly how many rows.
- **Fields that matter for readers:** the columns that answer real questions (net price by income band, admit rate, transfer acceptance, graduation rate, SAT ranges, college-going rate). Note field names exactly.
- **Years covered and update schedule:** latest year available, how often it is refreshed, typical lag.
- **Coverage gaps:** missing states, suppressed small counts, fields often blank.
- **License and access:** public domain, open license, terms of use, rate limits, whether it needs a key.
- **Page types it supports:** the reader questions it can answer, as `entity x question` patterns ("every college x what transfer applicants actually face").
- **Uniqueness verdict:** for each page type, whether the data makes each page meaningfully different. Apply the test below.

## The uniqueness test
A page type passes only if, for most entities, the data supplies at least three reader-relevant values that differ from the national or state default AND lead to different advice. Fields that are blank or suppressed for most entities don't count. If a page type passes for only some entities (large colleges but not small ones), say where the line is.

## Output
Write `data/inventory/<area>.json` following `schemas/data-inventory.schema.json`. Validate it with:
`python3 scripts/validate_handoff.py schemas/data-inventory.schema.json data/inventory/<area>.json`

## Done when
Every dataset you found is recorded with all fields above, every page type has a uniqueness verdict with its reason, and you have listed the important reader questions in this area that no public dataset answers (those go to researched guides instead).

## Never
Download licensed data, scrape sites that forbid it, or claim a field exists without seeing it in the documentation or a sample.
