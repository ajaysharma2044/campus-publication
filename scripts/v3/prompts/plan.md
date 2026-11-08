You are planning every article, tool, dataset and start-here path for one topic of Footnote Daily (docs/v3/spec.md, section 4), a research-first publication for students, parents and alumni of Cornell University and the town of Ithaca, New York. Today is {{today}}. The owner, Ajay, reads this plan once, in about ten minutes, and approves it; then everything in it is queued and written from the brief. Plan for completeness, not volume: every reader in the reader map finds their path, and no two pages answer the same question.

TOPIC: {{topic_title}} (slug {{topic_slug}}; article files go under content/articles/{{topic_dir}}/ and site paths are /{{topic_dir}}/<slug>/)
SCOPE: {{topic_scope}}
BRIEF: {{brief_path}} (read it in full; the plan can only promise what the brief holds)
READER MAP: {{readers_path}} (reader keys: {{reader_keys}})
DEMAND ROWS (what people search and what ranks today): {{demand_path}}
EXISTING ARTICLES on the site (site path | title | queue status); one this topic should re-cover is a rewrite, not a new slug:
{{existing_articles}}
EXISTING START-HERE PAGES (one page per reader across all topics; when a housing reader is the same person as one of these, use that page's key and the page gets this topic's path added):
{{existing_start}}
OUTPUT: {{out_path}}
STATUS: {{status}}

WHAT TO PLAN
- Exactly one pillar, kind pillar: the whole topic in 3,000 to 5,000 words with a table of contents.
- Spokes, kind spoke: {{min_spokes}} to {{max_spokes}}. Each answers one specific question, decision, process, comparison, place or scenario that the brief can answer with depth (at least 1,200 useful words and 8 sources). No two spokes answer the same question; when two candidates overlap, merge them. Start from the demand rows (a spoke that matches a demand row names its id in notes) and from the gaps in brief section 9, then cover what the reader map asks that nobody ranks for yet. A question the brief cannot answer at depth is not a spoke; it goes under "Open questions for research".
- Reader guides, kind reader_guide: one "[Topic] for [reader]" guide for every reader whose answer changes a lot (the reader map's overview table, high), 1,500 words or more each.
- Tools, kind tool: calculators, quizzes and checklists built from the brief's numbers, each showing the date its numbers are from. For housing the spec names a rent + commute calculator, a "when should I sign a lease" timeline by start term and a move-in checklist by situation; for dining and money a meal plan calculator; for getting around a "do I need a car" quiz; otherwise whatever this brief's numbers can feed. Notes name the brief sections that hold the numbers, the inputs and the outputs.
- Datasets, kind dataset: at least one original table from brief section 10 (our own analysis) that other sites and AI answers will cite, titled with its date and sample size ("Ithaca rent by neighborhood, fall 2026, from N listings").
- Start-here paths, kind start_here: one per reader key that gets a reader guide, or whose path through the guides differs; slug = the reader key, or the key of an existing /start/ page (list above) when it is the same kind of reader, so that /start/ never holds two pages for one person; a new key only for a reader no topic has yet; notes list the guides in reading order.
- Rewrites, kind rewrite: an existing article under /{{topic_dir}}/ (the first group of the list above) whose question this topic owns; slug = its existing slug, exactly; notes say what the brief adds. It is rewritten in place. An article under another topic's dir is rewritten by that topic, never here: do not list it, and do not plan a new page that answers its question.
- Slugs are unique across the whole site (images are stored by slug): a new slug may not match any slug in the list above, in any dir.

FORMAT (exact; a script parses the table)
# Content and data plan: {{topic_title}}
Three to six lines: what the plan covers, the pillar, how many of each kind, which rows wait on a research lane that is still thin.

## Plan
One Markdown table with exactly these columns:
| kind | slug | title | question | primary_query | type | readers | brief_sections | notes |
- kind: pillar, spoke, reader_guide, tool, dataset, start_here or rewrite.
- slug: lowercase letters, digits and hyphens, 60 characters or fewer, unique in the table; for a rewrite, the existing slug.
- title: the page title, 60 characters or fewer, saying what the page answers.
- question: the question in the reader's words.
- primary_query: the short phrase the reader types into Google (the matching demand row's query when there is one).
- type: for pillar, spoke, reader_guide and rewrite one of how-to, decision, scenario, comparison, place, checklist, roundup; for a tool one of calculator, quiz, checklist, timeline; for a dataset, table; for start_here, path.
- readers: the reader keys the page serves, comma-separated, no spaces; every key comes from the reader map.
- brief_sections: the brief section numbers it draws on, comma-separated ("2,3,4").
- notes: one line: the angle (what the page does that nothing ranking today does), the demand row id when there is one, for a tool the inputs and outputs, for start_here the ordered slugs. No pipe character inside any cell; use commas and semicolons.

## Open questions for research
Questions readers ask that the brief cannot answer at depth yet, each with the reader key and where the gap is.

## Acceptance check
How the plan meets docs/v3/spec.md: one pillar, at least 12 spokes, at least 3 reader guides, the tools the spec names, at least one dataset.

RULES
- Every promise in the plan is backed by the brief: name the sections. Never invent numbers, sources or demand.
- Titles say what the page answers; no clever titles.
- Write the file with Write when it is complete (if it exists, Read it first and keep the rows that are already queued, with their slugs). Then reply with one line: PLANNED <rows> rows: 1 pillar, <s> spokes, <r> reader guides, <t> tools, <d> datasets, <h> start-here, <w> rewrites.

For every row, end the notes column with `image: <two to five words naming a photographable thing for the page, as a Wikimedia Commons title would>` (a bus, airport, building, street or neighborhood); the image step searches that first.
