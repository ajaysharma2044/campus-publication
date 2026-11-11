# Idea run scripts (docs/v4/RUN-NOW.md)

The coordinator session runs IDEAS.md wave by wave with Claude Code's Workflow tool. These files are what it uses, kept here so a later session can continue from IDEAS-STATUS.md.

- `wave_runner.js`: the workflow for one wave. Five writers at a time (feature-writer for mode F, guide-writer for mode A, TOOL ideas build a calculator under review/tools/<slug>/); each page then goes through page_check.py and match_facts.py, one editor round when checks fail or the page is a feature, one checker round when numbers are unmatched, and a status sidecar in review/_status/. Launch with `Workflow({scriptPath: "scripts/ideas/wave_runner.js", args: <output of build_wave_args.py>})`.
- `build_wave_args.py <wave> [ids...]`: builds that args object from IDEAS.md and review/ideas-plan.json (only ideas whose action is write or rewrite).
- `finalize_wave.py <workflow output file>`: after a wave, sets each idea's final status, appends the writers' and checkers' new facts to intel/<topic>/facts.csv (section "new", ids from 9001) and rebuilds IDEAS-STATUS.md.
- `entity_bar.js`: the workflow that judges ENTITY ideas against the entity bar (args: {entities: [{id, title, topic}]}); pass becomes write, hub-row becomes a row in the hub page's table.
- `merge_inventory.py`: merges build/ideas/inventory/*.csv into intel/off-campus-housing/inventory.csv with Census geocoding and straight-line distance to Ho Plaza.
- `fix_facts.py <topic...>`: the one-off cleanup applied to the converted fact files (annotated dates, inherited 'same' URLs).
- `batch_writer.js`: the sprint writer (Ajay's one-hour instruction of 2026-11-10): one Sonnet session per batch of 10 to 12 pages, written from the fact files with no web research, one page_check fix pass per page. `fix_batch.js`: one Sonnet editor per batch of pages that fail page_check, fixing only what the check flags (args: {batches: [{batch_id, pages: [{page, flags}]}]}).
- `publish_review.py`: copies review pages and calculators into content/ for the Astro build (Ajay's instruction of 2026-11-11: publish, then verify); rewrites keep their slug, queue row and photos.
- `verify_sources.js` (args {batch_ids}, batch files build/ideas/verify/vNNN.json): opens each cited source once (WebFetch, then curl, then corpus/) and fixes wrong values in place. `collect_verify.py`: totals over the verify results, rerun batches rNNN for sources that did not open, and build/ideas/verify/fix_claims.json (batches cNN of claims the cited page does not state). `fix_claims.js` (args {batch_ids}): one Sonnet editor per claim batch, relinking, relabeling, softening or removing each claim. `claims_residue.py`: lists claims whose text still carries the flagged cite, against the batch reports' claims_kept.
- `finalize_run.py`: after verification, sets every written idea to done or rewrite-done, pointed at its content/ copy, with words and page_check from that copy, unmatched numbers from match_facts.py and the page's verification counts in its note.
- `../ideas_status.py`: rebuilds IDEAS-STATUS.md from IDEAS.md, review/ideas-plan.json and review/_status/*.json; `--set <id> key=value ...` updates one idea; `--note "text"` adds a progress paragraph.

Nothing here publishes; review/ pages move to content/ only on the owner's say-so.
