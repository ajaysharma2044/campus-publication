You are building one {{kind}} page for Footnote Daily, a research-first publication for students, parents and alumni of Cornell University and the town of Ithaca, New York, from the topic brief, the reader map and the plan. Today is {{today}}. Tools are plain JavaScript in the page, no accounts, nothing stored or sent, every number showing the date it is from (docs/v3/spec.md, "Tools"); datasets are original tables with their method and sample size; start-here pages are one reader's path through the topic's guides.

## The assignment (queue row {{id}}; plan kind: {{kind}})
- Slug: {{slug}}; working title: {{title}}
- What it answers for the reader: {{question}} (primary query: {{primary_query}})
- Readers it serves (reader keys; each matches a `Key:` line under a `## Reader:` heading in the reader map): {{readers}}
- Brief sections to draw on: {{brief_sections}}
- Plan notes: {{notes}}
- Topic: {{topic_title}}; site section /{{topic_dir}}/; the topic's pillar page: {{pillar_path}}

## Revision
{{revision}}

## Read first
1. docs/v2/style.md for the voice (direct, specific, no filler; no em dashes; none of: navigating, it's important to note, delve, vibrant, journey, seamless, robust, leverage, unlock, dive into, in today's).
2. The brief {{brief_path}}: Grep for the section headings to get line numbers, then Read the sections named above in full. A tool or dataset always reads section 3 (numbers, with ranges, sample sizes and how we got them) and section 10 (our original analysis); a start-here page reads section 1 (the topic in one page) and section 4 (timeline). Every number you use comes from here, with its Source URL and its Applies to date.
3. The reader map {{readers_path}}: Grep "Key: <key>" for each reader above and Read that section, so the inputs, the result or the path speak their language.
4. The plan {{plan_path}}: this row, and the article rows that will embed, link or follow this page.

{{deliverable}}

## Rules
- Numbers come from the brief, each with its source URL and the date it applies to; never from memory, never rounded beyond what the brief gives. Where the brief gives a range or a sample, keep it (low, typical, high; sample size and date shown).
- No new web research; a number the brief lacks is left out and named in the page's caveats ("Not in the brief: ...").
- Title 60 characters or fewer; meta 120 to 155 characters; frontmatter keys exactly as listed; dates ISO.
- Internal links only to the paths below, the pillar path and the topic index /{{topic_dir}}/; never invent a path.
  Existing pages in this topic (path | title):
{{existing_articles}}
  Pages being written in this same batch (path | title); they exist by the time this page publishes:
{{batch_articles}}
  Planned siblings not started yet (path | title; the renderer shows the text without a link until the page is live):
{{planned_articles}}
- Write only the file or files named above; nothing else anywhere.
