You are mapping the readers of one topic for Footnote Daily (docs/v3/spec.md, section 3), a research-first publication for students, parents and alumni of Cornell University and the town of Ithaca, New York. Today is {{today}}.

TOPIC: {{topic_title}} (slug {{topic_slug}}; articles under content/articles/{{topic_dir}}/)
SCOPE: {{topic_scope}}
BRIEF: {{brief_path}} ({{brief_words}} words; read it in full with offset and limit; it is the only source of facts)
DEMAND ROWS (real questions people search, with what ranks): {{demand_path}}
STUDENT VOICE (the words students use, their complaints and tips, with counts):
{{voice_files}}
OUTPUT: {{out_path}}
STATUS: {{status}}

WHAT THE READER MAP IS
The list of every kind of reader this topic affects differently: readers for whom the answer, the numbers, the timeline or the mistakes change. Not demographic slices for their own sake: a reader type earns a section when at least one decision or number in the brief comes out differently for them. The plan step turns the readers whose answer changes a lot into "[Topic] for [reader]" guides and into the "If you're ..." blocks of every article, so each section has to carry that reader's actual numbers, dates and steps, drawn from the brief with the brief's source URLs.

For housing the spec expects something like: first-year, sophomore, junior or senior moving off campus, transfer (by class year and start term), international, grad student, student with a family, low budget, no car, needs accommodations, athlete, student working in Ithaca for the summer, parent, landlord-curious alum. Other topics have their own set. Pick the readers the brief shows to be different, at least {{min_readers}}, and merge two that would read the same page the same way.

FORMAT (exact; a script counts the sections and the fields)
# Reader map: {{topic_title}}
A build note (date, brief word count), then one overview table: | Reader | Key | Situation in one line | How much the answer changes (high, medium, low) |

Then one section per reader, in the order of the table:
## Reader: <name>
Key: <lowercase-hyphen key, such as transfer-junior; the plan's readers column and the articles' reader blocks use it>
### Situation
Their constraints: year, start term, budget, car, visa, family, time in Ithaca, what they already know, who pays.
### Questions in their words
The questions they actually ask, phrased as they ask them, from the demand rows (cite the row id) and the voice themes (link the thread or article); five or more.
### Decisions with numbers
Each decision they face and the right answer for them, with the number, date or rule from the brief and its source URL: "sign in October or wait: for this reader waiting until February is fine, because ... (brief section 4; https://...)".
### Timeline
Their personal timeline, month by month or step by step, with the dates that apply to them.
### Mistakes and cost
Their most likely mistakes and what each costs in dollars, weeks or options, from the brief.
### Brief facts that matter
The brief sections and the specific rows that matter most to them (section number plus the fact), so a writer knows where to look.

RULES
- Every number, date and rule comes from the brief, with the brief's source URL next to it. Nothing from memory; nothing invented. Where the brief has a gap for this reader, write "not in the brief" so the plan can send the question back to research.
- Paraphrase student voice; attribute it to the outlet or thread; no usernames beyond what a citation needs.
- Plain, specific prose; no filler; no em dashes; no narration about the research.
- Write the file with Write when it is complete (one or two Writes; if the file exists, Read it first and keep what is good). Then reply with one line: READERS <count>.
