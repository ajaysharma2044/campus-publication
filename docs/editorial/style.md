# Style guide (specs/continuous-local-run.md R39)

The writer and editor agents load this before every draft and edit. The deterministic filler check in
`worker/campus_worker/editorial/checks.py` enforces the "no filler" rule; the rest is judgment the editor applies and
the competitor-beat review scores (R38).

## 1. Answer first
The opening sentence answers the question the page targets, in plain words, within 50 words of the start. If the
answer is "it depends", the first sentence says what it depends on. The deck repeats the answer in one line.

## 2. Specifics over adjectives
Numbers, names, distances, dates and prices, each with its academic year or effective date. "$6,872 per semester per
person (2026-27)" beats "affordable". Every figure in prose matches the fact table and carries a claim id.

## 3. Local terms, explained once
Use the local name and explain it the first time: "Collegetown (the neighborhood just south of campus)", "the Slope
(Libe Slope, the hill below the Arts Quad)", "TCAT (the county bus system)". After that, the plain local term.

## 4. Short paragraphs, tables, numbered steps
Paragraphs of one to four sentences. Comparisons are tables with one basis (per person, per semester). Procedures are
numbered steps with the office that owns each step. Definitions are one sentence.

## 5. No filler, no AI tells
Banned openings and filler phrases are rejected by code (`BANNED_OPENINGS`, `FILLER_PHRASES`). Among them: "in today's
world", "navigating", "delve", "it's important to note", "whether you're … or …", "a plethora of", "vibrant",
"state-of-the-art", "look no further", "game-changer", "seamless", "elevate your", "unlock", "in conclusion".
Also banned: rhetorical questions as openers, "here's what you need to know", and restating the question before
answering it.

## 6. Byline policy
Pages carry a desk credit ("Housing desk", "Transfer desk"), never a human reporter's name, and the production note
discloses automation: how the page was researched, checked, and whether a human reviewed it.

## 7. Unknown is a value
"Unknown — no verified source states it" is correct. Guessing is not. Never write "likely", "typically" or "usually"
about a fact the sources do not state.

## 8. Reviews and experiences
No invented ratings, "students agree", first-person stays or quotes. A "what residents report" section exists only
with permitted, attributed sources and states the sample, period and limits (SPEC §09). Without them the page says the
section is omitted and why.

## 9. Exemplars
Two accepted and two rejected passages per page type are added here as the first pages pass review (R39). Until
then, the fixture pages in `fixtures/synthetic/` and the editorial calibration report (`docs/editorial/calibration.md`)
are the reference.

### Accepted (guide, opening) — fixture
> Transfers who have not lived on campus elsewhere must live in Cornell housing for one academic year; spring entrants
> for the incoming spring and the following year. Housing is guaranteed for first-years but not stated as guaranteed
> for transfers. The 2026-27 double rate is $6,872 per semester per person.

### Rejected (guide, opening) — fixture
> Navigating the world of Cornell transfer housing can feel overwhelming. Whether you're a sophomore or a junior,
> it's important to note that there are a plethora of options to delve into.

_(filler: "navigating the world of", "whether you're … or", "it's important to note", "a plethora of", "delve into")_


## Reader-first rules (owner decision 2026-11-06; these win over anything above that conflicts)
- Lead with the direct, practical answer a student can act on, built from what the sources do say. The first paragraph answers the question; the next ones give the steps, numbers and dates.
- Never write "the pages we opened do not say" or any variant of it in the body. Gaps go in one short **Not confirmed** note at the end: at most 3 bullets, each one line, no apology.
- Voice: a knowledgeable upperclassman explaining it to a friend, not an auditor. No audit trail in prose (no "snippet", "snapshot", "claim", "verified against"), no rubric talk, no "this publication".
- Dates in prose as "November 6, 2026" (month name, day, year). Money as "$6,872 per person per semester".
- Fact table rows: plain labels a reader would use ("Double room, 2026-27"), one value each.
- The page ends with the Not confirmed note (if any), then What to do next.
