You are building one {{kind}} for Footnote Daily, a research-first publication for students, parents and alumni of Cornell University and the town of Ithaca, New York, from the numbers in the topic brief. Today is {{today}}. Plain JavaScript in the page, no accounts, nothing stored or sent; every number shows the date it is from (docs/v3/spec.md, "Tools").

## The assignment (queue row {{id}}; plan kind: {{kind}})
- Slug: {{slug}}; working title: {{title}}
- What it answers for the reader: {{question}} (primary query: {{primary_query}})
- Readers it serves (names from the reader map): {{readers}}
- Brief sections with the numbers: {{brief_sections}}
- Plan notes: {{notes}}
- Topic: {{topic_title}}; site section /{{topic_dir}}/; the topic's pillar page: {{pillar_path}}

## Revision
{{revision}}

## Read first
1. docs/v2/style.md for the voice (direct, specific, no filler; no em dashes; none of: navigating, it's important to note, delve, vibrant, journey, seamless, robust, leverage, unlock, dive into, in today's).
2. The brief {{brief_path}}: Grep for the section headings to get line numbers, then Read the sections named above in full, always including section 3 (numbers, with ranges, sample sizes and how we got them) and section 10 (our original analysis). Every number you use comes from here, with its Source URL and its Applies to date.
3. The reader map {{readers_path}}: the sections for the readers above, so the inputs and the result speak their language.
4. The plan {{plan_path}}: this row, and the article rows that will embed or link this page.

{{deliverable}}

## Rules
- Numbers come from the brief, each with its source URL and the date it applies to; never from memory, never rounded beyond what the brief gives. Where the brief gives a range or a sample, keep it (low, typical, high; sample size and date shown).
- No new web research; a number the brief lacks is left out and named in the page's caveats ("Not in the brief: ...").
- Title 60 characters or fewer; meta 120 to 155 characters; frontmatter keys exactly as listed; dates ISO.
- Existing pages in this topic (path | title) you may link: 
{{existing_articles}}
  Planned siblings (path | title; the renderer shows the text without a link until the page is live):
{{planned_articles}}
- Write only the two files named above; nothing else anywhere.
