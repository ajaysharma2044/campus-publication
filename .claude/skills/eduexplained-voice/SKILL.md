---
name: eduexplained-voice
description: The EduExplained house voice and page rules. Load for any agent that writes or edits reader-facing text (guide writer, batch writer, editor). Covers how to open a page, stating each fact once, handling uncertainty with confidence, attribution, dates, reader blocks and formatting.
user-invocable: false
---

# EduExplained voice

EduExplained answers practical education questions, pre-K through doctoral, for students, parents and alumni across the United States. Readers arrive with one question and a decision to make. They are smart, busy and skeptical, and they compare us against the official page, a forum thread and an AI answer. We win when our page is the clearest, most complete and most trustworthy answer of the four.

Write like an expert who has done this a hundred times and is explaining it to a friend: direct, specific, calm, and sure of what the facts support.

## When rules conflict, this order wins
1. **Accuracy.** Never trade a true statement for a smoother one.
2. **Coverage.** Every sub-question on the page's coverage map gets answered.
3. **Directness.** The answer comes first, in plain words.
4. **Length.** Shorter is better only when nothing in 1 to 3 is lost. Length follows scope: a narrow question gets a short page, a big topic gets a long one.

## Two modes: feature and answer
Every page is one of two modes, and the layering agent names which.

**Feature mode** (pillars, topic overviews, "how this whole system works" pages). Write like a newspaper feature: open with a short, specific, true scene or tension that makes the reader care ("Every October... thousands of Cornell undergraduates sign a lease for an apartment they will not move into for nearly a year"), then state the frame of the whole page by the second or third paragraph (the nut graf: "Housing at Cornell is a two-tier system with a hard seam down the middle"), then the stakes in numbers. The body follows a story spine, usually time or the reader's path ("Year One," "Year Two," "Collegetown"), and explains why things are the way they are: the history, the policy decisions, the people who made them, the forces pushing on them now, and the open questions. End with what comes next, then the service layer: a calendar, a checklist, the sources. A feature's evocative name goes in the `kicker` line above the headline; the title itself follows the title formula in the `search-analysis` skill. The approved example is `gold-set/examples/feature-pillar.md`.

**Answer mode** (specific questions: a deadline, a fee, a rule, a how-to). The rest of this section applies.

## The opening (answer mode)
The first paragraph is the answer. It holds the verdict, the number or the recommendation the reader came for, plus at most one supporting fact, in 60 words or fewer, with at most one link. Then stop. Everything else moves down the page.

Why: most readers decide whether to trust the page in the first few seconds, and AI tools quote the opening sentence more than any other line. A paragraph that crams three rules and four links forces the reader to decode instead of decide.

Never open with what does not exist ("Nobody publishes...", "There is no list..."). Open with what the reader can do; mention the gap later, once.

## Each fact once
State every fact in one place, in full, with its link. After that, refer back to it ("the 14-day deadline above") or leave it out. A fact may appear at most twice on a page: its main statement and one other mention, which is either its Key takeaways bullet or a later reference the reader needs, such as inside a calculation. Tables and figures may repeat a number the prose states, because they serve scanning, not reading.

Why: our audit found the same price stated up to 23 times on one page. Repetition is the single biggest source of bloat, and readers read it as filler.

## Reader blocks
A reader block ("If you're an international student") exists only where the answer actually changes for that reader. It contains only what is different for them: their deadline, their cost, their exception, their mistake. It never restates general facts the page already gave. Two or three strong blocks beat six weak ones. If nothing changes for a reader, they get no block.

## Confidence
- **Solid fact, sourced:** state it flatly. "The deposit cap is one month's rent." Not "generally" or "typically."
- **Sources disagree:** say so in one sentence and tell the reader which to follow and why. "The city's website says six unrelated tenants trigger a certificate. The city code says five. Go by five."
- **Unknown:** say once, in a plain sentence, what is not known and exactly what to do about it. "Ithaca Bikeshare doesn't post a winter schedule, so check the app before you count on it in January." Never use a "Not confirmed:" label.
- **Advice:** give it, clearly as advice, tied to the reader's situation. "If you need a single in Collegetown, sign by October."

Hedge words (may, might, typically, generally, usually, often, likely, roughly) are allowed only when the sentence then says exactly what the answer depends on.

## Sources and attribution
Attribute every hard fact, cleanly. The house style is a short parenthetical source name at the end of the sentence or paragraph, linked: "Cornell's trustees set average housing and dining costs at $21,348 (Cornell Chronicle)." It reads like reporting, costs the reader nothing, and tells them at a glance how much to trust the claim. Name the source in the sentence itself when who said it is part of the news: a rule ("Cornell requires..."), a decision ("President Michael I. Kotlikoff canceled..."), a quote from reputable reporting ("one resident told The Cornell Daily Sun..."), or a disputed claim. Tables carry a one-line source note underneath.

Never narrate the research: no "we found", "we checked", "our arithmetic", "per X's listings read on Nov 8". Our own calculations are presented as facts with the inputs shown ("four rides at $1.50 is $6.00").

Never cite forum posters, Reddit users or College Confidential threads as sources. Build on official pages, primary data and reputable reporting. Forums tell us what people ask, never what is true.

## Dates and time
Put the "Updated" date in the page's frontmatter, not in the prose. Prices and rules carry their period ("$6,872 per semester for 2026-27"). Time-sensitive advice is anchored to a date, never to "this week" or "right now": write "Book by Nov. 15 for Thanksgiving week," not "Book this week," because the page will still be live after this week.

## New information, every page
A page earns its place only if it tells the reader something the top results don't. Restating a statute or an office page is not new. New looks like:
- **Synthesis:** connecting facts that live on separate pages into one picture (the policy, why it was adopted, what it cost, who it squeezed).
- **Context and history:** why the system is the way it is, with dates and decision-makers.
- **Current events:** what changed this year or this month and what it means for the reader.
- **Our own math:** comparisons nobody else has done ("$1,615 a month over a 12-month lease is $19,380, against $13,744 for a campus double").
- **Original data:** samples, audits and tables we built.
- **Honest trade-offs:** what the official line says, what critics and residents say, from reputable reporting.

## Write like a reporter, not a template
Prose carries the page; lists and tables serve it. Vary paragraph length. Use real names: of buildings, streets, offices, officials, programs. Let a section have its own shape instead of forcing every section into answer, list, watch-out. Use bold lead-ins only to start list items, never as decoration in running text. Things that make a page read as AI, all found in our own drafts:
- every section built the same way (answer sentence, bullet list, bold "Watch out" box)
- clipped commands as standalone sentences ("Say yes." "Ask for it.")
- a generic "What to do next" wrap-up that adds nothing
- tidy groups of three, over and over
- bolded labels sprinkled through prose
- abstract phrasing where a name or number belongs ("a large complex" instead of "The Ivy, an eight-story building at Dryden Road and College Avenue")

## Digestible by design
Write so a reader with an eighth- to tenth-grade reading level gets it on the first pass, whatever their education: short sentences, common words, one idea at a time. Define every term of art in a few plain words the first time it appears ("a Certificate of Compliance, the city's three-year safety inspection permit"). Use labeled scan lines such as **By the numbers** or **Watch out** where the layer plan asks for them. The patterns behind these rules, drawn from Investopedia, the Times, CNN and Fox, are in the `publisher-patterns` skill.

## Words and format
- One idea per sentence. Average under 18 words. Verbs, not nouns.
- The specific word over the category: "Collegetown Terrace," not "a large complex."
- Tables for costs and comparisons, numbered steps for processes, "If you..., do..." for decisions.
- Money keeps its cents when it has them: "$46.70," never "$46.7."
- Dates in AP style: "Nov. 25," "Aug. 1, 2027," with the year whenever it isn't obvious.
- No em dashes. No filler: navigate, delve, vibrant, journey, seamless, robust, leverage, unlock, dive into, in today's.
- Never put planning or SEO talk on the page: no "the pages that rank," "primary query," "AI answers miss." That belongs in the packet, not in front of the reader.

## Before you finish
Run `python3 .claude/skills/page-checks/scripts/page_check.py <your file>` and fix everything it reports. For worked examples of every rule above, read `references/before-after.md`. For the specific failure patterns found in our existing pages, read `references/edge-cases.md`.
