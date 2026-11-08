# Best pages library (docs/v3/spec.md, the quality ratchet, loop 3)

What goes here: a copy of every page Ajay marks 👍 in `reports/to-read.md`, and every draft that wins the blind compare of two
pillar drafts. Copy the article file as it was published (`content/articles/<dir>/<slug>.md` to `docs/v3/best/<slug>.md`), unchanged,
and add the two-line note at the very top, above the frontmatter, as an HTML comment so the file still parses:

```
<!-- BEST 2026-11-15, 👍 from Ajay (or: won the blind compare against <other slug>)
     Why it is good: one line naming the specific thing to copy (e.g. "the reader blocks carry different numbers for each reader, not the same advice reworded"). -->
```

Line one: the date and where the mark came from. Line two: why it is good, specific enough that a writer can imitate it. Nothing else.

How it is used: before writing or editing, a session reads the 3 pages here most like its assignment (same kind, same topic, or the
same reader) and imitates what the notes name. The learn step Ajay runs (`scripts/v3/learn.sh`, proposals in `reports/lessons.md`) copies pages here; nobody edits a copy
afterwards (a later rewrite of the live page gets its own entry when it earns one). The library grows; the bar rises.

Companion: `docs/v3/worst/` holds the pages that got a note instead of a 👍, with what was wrong.
