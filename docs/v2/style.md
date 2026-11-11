# EduExplained style guide (DRAFT stand-in)

> This file is a stand-in written from the v2 spec's content rules. The spec says to copy the owner's `footnote-style-guide.md` here exactly; that file has not been provided yet (open question in STATE.md). Replace this whole file with it when it arrives.

## Who we write for
A student, parent or alum with one practical question about Cornell or Ithaca. They are smart, busy and skeptical. Write like a sharp upperclassman who has done it, not like an office or a brochure.

## Shape of every article
1. The first paragraph answers the question directly, in plain words, with the number, date or recommendation the reader came for.
2. Then the details in the order the reader needs them: what to do first, what it costs, when it is due, what goes wrong.
3. Sections carry plain headings a reader would search for ("How much it costs", "If you missed the deadline"). No clever titles.
4. End with the related questions the reader will have next (a short FAQ) and links to our related articles.

## Facts and sources
- Every hard fact (number, date, fee, deadline, rule, phone, address) links inline to the official page it came from, the first time it appears. No fact without a source.
- Prices and dates carry their period and year ("$6,872 per semester for 2026-27"). Say when something changes each year.
- Student experience is paraphrased, attributed and linked ("Several 2025 r/Cornell threads say..."). It is experience, never the source of a hard fact.
- Never invent quotes, people, ratings or numbers. Never copy more than a short phrase. When sources disagree, say so and say which to trust.

## Precision when you paraphrase (the pilot's reviewers rejected articles for exactly this)
- Say who said it, as the source does: name and role, and only the pronoun the source uses. If the source does not say, write "the article" or "one poster".
- Do not add detail a paraphrase does not contain. "Wash and re-lube after every ride" is not "wash the chain"; "most would say the buildings are nice" is not "most would say the company rips people off".
- Definitions, categories, rules and eligibility use the official page's own words or a tight paraphrase of them, never your summary of what the category "covers".
- Two posters are two posters. Never merge quotes or opinions from different people into one voice.
- When a reviewer lists fixes, apply every item, then re-read the list and check each one off before you finish.

## Voice
- Direct, specific, warm, a little dry. Second person is fine ("you apply within ten days").
- Advice is welcome when it is clearly advice and follows from the facts ("If you need a single, apply in the first window").
- Short paragraphs, one idea each. Tables for costs and comparisons, numbered steps for processes, "if you are X, do Y" for decisions.
- No em dashes. No filler: navigating, it's important to note, delve, vibrant, journey, seamless, robust, leverage, unlock, dive into, in today's.
- No hedging stacks ("may potentially"). One caveat where it matters, stated once.

## Length and format
- Length fits the question; most pages 700 to 1,500 words.
- Title 60 characters or fewer, says what the page answers. Meta 120 to 155 characters, states the answer.
- At least one useful visual (a photo we have the rights to, a cost chart or timeline built from the facts, a map). Every image has alt text and a caption with its credit.
- At least two internal links to related articles when they exist.

## Part 6: the seven editing passes (run on every draft, in this order)
1. Structure: does the first paragraph answer the question in 3 sentences or fewer? Is the "At a glance" box the whole page in six lines? Do the "If you're..." blocks come before the long sections? Move, merge or cut sections until a hurried reader gets the answer, then their situation, then the detail.
2. Cut 20 to 30 percent: every sentence that restates another, every paragraph that explains what the page is about to do, every hedge stacked on a hedge. Keep every fact, number, date and link.
3. Line edit: one idea per sentence, average under 18 words, verbs not nouns, the specific word not the category ("Collegetown Terrace" not "a large complex").
4. Slop sweep: remove the banned words and every research-narration phrase ("we found", "our research shows", "the pages we checked", "sources say", "it is worth noting", "as of our review"). State the fact and link it.
5. Specificity: every claim that could carry a number, date, name or place carries it. Replace "many students", "often", "recently" with the count, the frequency or the date from the brief.
6. Read-aloud: read the page as the target reader would; wherever you stumble, rewrite the sentence.
7. Visual: one table, figure or tool for every long run of numbers; lists for parallel items; a photo caption that adds information the picture alone does not.

## Part 7: the swap test and research narration
- Swap test: if a paragraph would read the same with another school's name swapped in, it is generic; cut it or make it specific to Cornell and Ithaca.
- Research narration (banned): "we found", "we checked", "our research", "the pages we opened", "sources say", "according to our review", "we were unable to confirm", "it is worth noting", "as of our review", "we looked at". Say what is true and link the source; put gaps in one short "Not confirmed" line, not in the prose.
- Research gaps (banned, docs/v5/prelaunch-spec.md): a page never tells the reader that the sources, the guide, the page or our research lack something: no "Not confirmed:" lines, no "the sources behind this guide do not list", no "the page gives no", no "we could not find", no "not in the sources", no "honest limit". scripts/lint-content.py fails the build and the publish lint on them. When a promised answer is missing, search the source checklist (crime and safety: Cornell's Annual Security and Fire Safety Report, Cornell Police, Ithaca Police; voting: the NYS and Tompkins County Boards of Elections; local rules: City of Ithaca, Town of Ithaca, Tompkins County; tenant law: NY General Obligations Law, Real Property Law, the NYS Attorney General's tenant guides; Cornell policy: the office's own page, current-year PDFs, the Cornell Chronicle); if found, add it with a citation; if not, remove the section and change the title and headings so the page no longer promises it, and log the decision (page, missing item, sources tried, outcome) under "## Gaps" in the edit log.
