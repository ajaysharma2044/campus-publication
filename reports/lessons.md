# Weekly lessons (docs/v3/spec.md, the quality ratchet, loop 4)

When Ajay runs scripts/v3/learn.sh, one session reads the edit logs since the last run (`content/edits/`), fact-check fixes (`content/checks/`), reader-test findings
(the write sessions' logs), Ajay's marks and notes (`reports/to-read.md`) and the Search Console part of `reports/weekly.md`, and
proposes at most 5 changes to `docs/v2/style.md`, `docs/v2/exemplar.md` or a topic brief, each with its evidence. Ajay writes
approve or reject next to each one; approved changes are applied in the next session and the commit is linked. Nothing here becomes
a code rule, a gate or a score: a lesson is a sentence in the style guide, a better passage in the exemplar, a fact in a brief.

Also every Monday: the 5 weakest live pages from `reports/weekly.md` are queued for a rewrite (kind rewrite, same slug), and every
page Ajay marked 👍 since the last run is copied to `docs/v3/best/`, every page with a note to `docs/v3/worst/` (see the READMEs there).

## Template (copy below, fill, keep the headings; newest week first)

### Week of YYYY-MM-DD

**What the week's evidence says** (3 to 6 lines: the patterns in the edit logs, the fixes, the reader tests, the notes, the data)

**Proposed changes** (at most 5)

| # | Change (file and the exact edit) | Evidence (pages, logs, counts) | Ajay: approve / reject | Applied (commit) |
|---|---|---|---|---|
| 1 | | | | |
| 2 | | | | |

**Rewrites queued** (the 5 weakest live pages: path, why, queue id)

**Library** (pages copied this week: `docs/v3/best/<slug>.md`, `docs/v3/worst/<slug>.md`, one line each)

**Rejected and why** (so the same proposal is not made again next week)
