# Pages that missed (docs/v3/spec.md, the quality ratchet, loop 3)

What goes here: a copy of every page Ajay marks with a note instead of a 👍 in `reports/to-read.md`, and the loser of a blind
compare when the reader session named something it did badly. Copy the article file as it was when Ajay read it
(`content/articles/<dir>/<slug>.md` to `docs/v3/worst/<slug>.md`), unchanged, and add the two-line note at the very top, above the
frontmatter, as an HTML comment so the file still parses:

```
<!-- WORST 2026-11-15, Ajay's note: "<the note as written>"
     What was wrong: one line a writer can check their own draft against (e.g. "the answer paragraph hedges; the number is in section 3 instead of sentence one"). -->
```

Line one: the date and the note, quoted as Ajay wrote it. Line two: what was wrong, as a check a writer can run on a draft. Nothing else.

How it is used: writers and editors read the entries closest to their assignment and check their draft against the "what was wrong"
lines; the learn step Ajay runs (`scripts/v3/learn.sh`; proposals in `reports/lessons.md`) turns recurring ones into a style-guide line, an exemplar edit or a brief fix,
never a code rule. The live page itself is fixed through a rewrite row (kind rewrite); the copy here stays as the record.

Companion: `docs/v3/best/` holds the pages to imitate.
