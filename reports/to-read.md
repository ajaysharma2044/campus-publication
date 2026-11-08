# To read: Ajay's spot check (docs/v3/spec.md, step 8)

Every newly published page lands here with a one-line summary. Ajay reads all of the first topic, then 1 in 5, and marks each one.

## How to mark a page

Each entry is three lines. Write your mark on the `Ajay:` line and leave the other two alone:

- `Ajay: 👍` means the page is good. The weekly lessons step copies it to `docs/v3/best/` with a two-line note on why.
- `Ajay: <one line>` means something is wrong or weak ("the rent table is 2024 numbers", "reads like a memo after the reader blocks"). The page goes to `docs/v3/worst/` with that note, and the note becomes a style-guide, exemplar or brief edit. Notes never become code rules.
- An empty `Ajay:` line means not read yet.

Entry shape (`scripts/v2/publish.sh` appends one per published page; `worker/.venv/bin/python scripts/v2/render_site.py --to-read` rebuilds the list from the published queue rows, newest first, and keeps every mark already written):

```
- <published date> | <title> | <site path> | <kind> | <topic dir>
  Summary: <the page's one-line meta>
  Ajay: <👍 or a one-line note>
```

`kind` is pillar, spoke, reader_guide or rewrite for v3 pages and `<type> (v2)` for pages not yet rewritten. Nothing below the entries is read by the scripts; keep general remarks in `reports/lessons.md`.

## Entries

