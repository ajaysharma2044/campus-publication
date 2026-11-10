# Build spec: EduExplained pipeline v4

**For:** Claude Code, run in the `campus-publication` repo with `claude --model fable`.
**Owner:** Ajay Sharma. **Written:** Nov. 10, 2026.
**How to execute:** work stage by stage, in order. Finish each stage's acceptance checks before starting the next, commit at the end of each stage with a message naming the stage, and stop at every **OWNER CHECKPOINT** to wait for approval. Don't redesign anything this spec decides; if something here is impossible or wrong, stop and say why instead of improvising.

---

## FAST MODE (owner's instruction: build it and run it now)
Execute in this order and do not stop for checkpoints:
1. Stages 0, 1, 2, 4, 5 first. Write only the tests that protect against data loss (state files, resume, handoff validation); skip the rest of the test suites for now.
2. Skip stage 3 for housing: its research already exists. Run the architect directly on the migrated `intel/off-campus-housing/facts.csv`, **auto-approve** every page the architect proposes that passes the entity bar, then run search-strategist and layering, then stage 5 in review mode. The first pages should exist within the same session.
3. Use the existing image finder as is and render with the existing renderer; stages 6 and 7 are done after the first pages are reviewed.
4. Stages 8 and 9 next, then stage 3 in full for new topics.
5. The only hard stop: never publish to the live site without the owner saying so. Review pages go to `review/<topic>/`.
6. Post progress to `build/v4/PROGRESS.md` after every stage and every 10 pages: what's done, what failed, usage so far.

---

## 1. What we're building

A pipeline that turns a topic into published EduExplained pages: researched, sourced, written to the house standard, checked, illustrated and paced into publication. It replaces the v3 batch-cycle pipeline in `scripts/v3/` with a streaming pipeline in `scripts/v4/`. The v3 pipeline stays runnable until the switchover in stage 11.

Everything Claude does runs as `claude -p` sessions on the owner's Claude subscription. No Anthropic API key. Never use `--bare` (it skips subscription login). Everything with a right answer is done in Python, not by an agent.

### The kit (already written, install it in stage 0)
- `.claude/agents/`: 14 agent definitions (job, inputs, output, done condition, model, effort, turn limit, preloaded skills).
- `.claude/skills/`: 20 skills with references and scripts, including `page_check.py`, `match_facts.py`, `brief_tables_to_csv.py`, `validate_facts.py`.
- `schemas/`: 11 JSON schemas, one per handoff.
- `scripts/validate_handoff.py`: validates any handoff file against its schema.
- `CLAUDE.md.proposed`, `PILOT.md`, `README.md`.

Read `README.md` and every agent file before starting. Do not edit agent or skill files unless a stage says to; they are the owner's editorial rules.

### The flow
```
topic-scout -> researcher x5 lanes (parallel) -> fact-extractor -> reader-analyst
  -> architect -> [code: matrix finalizer] -> OWNER approves plan
  -> search-strategist (batches of 10) -> layering (batches of 10)
  -> per page, streaming:
       [code: packet] -> writer -> [code: page_check] -> editor (if needed)
       -> [code: match_facts] -> checker (if needed) -> reader-tester (sampled)
       -> [code: images + charts] -> ready queue -> [code: paced publish]
```
Writers by page type: `guide-writer` for answer-mode pages (packet only, one pass), `feature-writer` for feature-mode pillars (web access, section loop), `batch-writer` for data pages (15 to 20 per session).

---

## 2. Global rules

1. **Directory layout** (create as needed):
   - `intel/<topic>/topic.json`, `raw/`, `facts.csv`, `readers.json`, `usecases.json`, `coverage/<slug>.json`, `search/<slug>.json`, `layers/<slug>.json`
   - `build/v4/packets/<slug>.json`, `build/v4/batches/<id>.json`, `build/v4/state/<slug>.json`, `build/v4/runs/` (logs), `build/v4/usage.jsonl`
   - `content/articles/<topic>/<slug>.md`, `content/checks/<slug>.json`, `content/reader-tests/<slug>.json`, `content/index.json`
   - `review/<topic>/` (pilot pages land here, not on the live site)
2. **Every handoff is validated** with `scripts/validate_handoff.py` before the next step reads it. An invalid handoff gets one retry of the producing agent with the validator's errors appended to the task; a second failure marks the item `failed` with the errors in its state file.
3. **No em dashes** in any file you write: code, comments, docs, pages.
4. **Brand:** EduExplained everywhere in new code and templates. Leave old "Footnote Daily" strings in v3 files alone.
5. **Config, not constants:** every tunable lives in `config/pipeline.yml` (stage 1).
6. **Tests:** every stage adds pytest tests under `tests/v4/`. Agent calls are tested with a stub binary through the existing `CLAUDE_BIN` environment variable in `scripts/v2/lib/sessions.py`; tests never call real Claude.
7. **Idempotent and resumable:** rerunning any command skips finished work and picks up failed or unfinished items from their state files.
8. **Secrets:** never read or print `.env` files (the existing hook blocks it; don't work around it).

---

## Stage 0: install the kit
1. Copy `.claude/agents/`, `.claude/skills/`, `schemas/` and `scripts/validate_handoff.py` from the kit into the repo root. Keep the existing `.claude/settings.json` and `.claude/hooks/`.
2. Do **not** replace `CLAUDE.md` yet (v3 depends on it). Save `CLAUDE.md.proposed` at the repo root as is.
3. Copy `PILOT.md` and the kit's `README.md` to `docs/v4/`.

**Acceptance:** `claude --agent guide-writer -p "Reply with the word ready"` returns "ready" (proves agent discovery works on the subscription); every skill's YAML frontmatter parses; `python3 scripts/validate_handoff.py schemas/layer-plan.schema.json .claude/skills/layering/references/layer-plan-example.json` prints VALID.

---

## Stage 1: agent runner and config
1. Create `config/pipeline.yml`:
   ```yaml
   workers: 8                      # concurrent claude sessions
   publish_per_day: 25             # paced publishing, raised by the owner over time
   reader_test_sample: 1.0         # 1.0 in the pilot; 0.2 after go-live (pillars and new page types always)
   editor_policy: on_fail_or_feature   # editor runs when page_check fails, and always on feature pages
   batch_size: {search: 10, layering: 10, data_pages: 20}
   models: {}                      # optional per-agent overrides, e.g. {architect: fable}
   thresholds_file: .claude/skills/page-checks/scripts/page_check.py
   ```
2. Add `scripts/v4/lib/agents.py` with `run_agent(agent, task, *, return_schema=None, timeout_s, label)`:
   - builds `claude -p <task> --agent <agent> --output-format json` (plus `--json-schema` with the schema's JSON when given, plus `--model` when `models` overrides it),
   - reuses the existing usage-limit pause, retry and thread pool logic from `scripts/v2/lib/sessions.py` (import or refactor it; don't duplicate it),
   - appends one line per session to `build/v4/usage.jsonl`: timestamp, agent, item id, model, duration, turns, cost field from the CLI JSON, exit status.
3. Add `scripts/v4/lib/state.py`: per-item state files with `status` (`queued`, `running`, `done`, `failed`, `skipped`), `step`, `attempts`, `errors`, `history`.

**Acceptance:** with a stub `CLAUDE_BIN`, tests prove: the exact command line per agent; the usage line is written; a usage-limit message triggers the existing pause; an invalid JSON return triggers one retry; state files survive a crash mid-step and resume.

---

## Stage 2: migrate existing research and index the site
1. Run `brief_tables_to_csv.py` on `intel/off-campus-housing/brief.md` and `intel/getting-around/brief.md` into each topic's `facts.csv`.
2. Run `validate_facts.py` on each. Fix every error **in the CSV** by reading the row's source page (example: the "$46.7" fare must become the exact value on the operator's page, "$46.70"). Log each fix in `intel/<topic>/facts-fixes.md` with the source URL.
3. Add `scripts/v4/build_index.py` that writes `content/index.json`: every live article's slug, URL, title, primary query, topic, type, mode and the fact_ids it cites (where available). Run it after every publish.

**Acceptance:** both fact files validate with zero errors; `content/index.json` lists all 108 current articles; a test proves the index rebuild is deterministic.

---

## Stage 3: planning
Add `scripts/v4/plan.py <topic>` that runs, in order, skipping anything already done:
1. `topic-scout` (skip when `intel/<topic>/topic.json` exists).
2. Five `researcher` sessions in parallel, one per lane (A to E), writing `raw/<lane>.md`. Skip lanes whose raw file exists unless `--refresh`.
3. `fact-extractor`, then `validate_facts.py` (must pass).
4. `reader-analyst`.
5. `architect`.
6. **Matrix finalizer (code):** read `usecases.json` and produce `intel/<topic>/plan.md` for the owner: every proposed page (slug, mode, length tier, primary query, use case, reader cells), the entity inventory with each decision, merges of live pages, and gaps. Pages whose coverage maps fail validation are listed as blocked.
7. **OWNER CHECKPOINT:** the owner edits `plan.md` (deletes rows to reject, marks rows `approved`). Parse it back; only approved rows continue.
8. `search-strategist` over approved pages in batches of `batch_size.search`. Drop pages it recommends `kill`; apply `merge` by attaching the page's coverage to the target and logging it.
9. `layering` over the remaining pages in batches of `batch_size.layering`.

**Acceptance:** with stubs, a test topic flows from scout to layer plans with every handoff validated; `plan.md` round-trips (owner edits are respected); killed and merged pages never reach layering.

---

## Stage 4: the packet builder
Add `scripts/v4/packet.py <topic> <slug>` producing `build/v4/packets/<slug>.json` per `schemas/packet.schema.json`:
- `frontmatter` from the search brief (title, meta, primary query) and layer plan (mode, kicker, dek); `updated` = today.
- `layer_plan`, `coverage_map`, `search_brief` verbatim.
- `facts`: only the rows whose fact_ids appear in the coverage map or layer plan, full columns.
- `readers`: only the reader cards the layer plan's reader blocks name.
- `links`: internal link candidates computed by code: live pages sharing a use case or at least two fact_ids, ranked by overlap, top 8, from `content/index.json`.
- `images`: the layer plan's image slots.
- Order keys so the stable parts come first and page-specific parts last (helps prompt caching).

**Acceptance:** packet validates; a test proves no fact outside the coverage map leaks in; link ranking is deterministic.

---

## Stage 5: the streaming production orchestrator
Add `scripts/v4/run.py <topic> [--limit N] [--slugs a,b]`. Each approved page moves through this state machine on its own; there are no batch barriers.

| Step | What runs | Rule |
|---|---|---|
| packet | `packet.py` | |
| write | `feature-writer` if mode is feature; `guide-writer` if answer; data pages go through `batch-writer` in batches of `batch_size.data_pages` | return JSON validated against the agent's documented return shape |
| check | `page_check.py` | |
| edit | `editor` | runs when page_check fails, or always for feature mode (per `editor_policy`); afterwards page_check must pass or every remaining flag must be in the editor's `kept_flags` with a reason |
| facts | `match_facts.py` against the topic's `facts.csv` | |
| verify | `checker` | runs only when match_facts reports unmatched numbers, or the writer listed `snippet_only_facts`; verdict `reject` marks the page failed; `fix` sends it back to edit once |
| reader test | `reader-tester` | sampled per `reader_test_sample` (always for pillars and page types not yet seen); test questions come from the coverage map; score with stage 8's code; a fail sends the page to edit once with the misses |
| images | stage 6 image step | |
| ready | move to the ready queue | |

Orchestrator rules:
- Up to `workers` sessions at once across all pages and topics.
- Start each page's write the moment its own layer plan and packet exist.
- Run `checker` and `reader-tester` concurrently when both are needed.
- Group pages of the same page type consecutively to reuse cached instructions.
- Pilot mode (`--review`) writes finished pages to `review/<topic>/` instead of `content/articles/`.

**Acceptance:** with stubs, tests cover every branch (pass, edit, checker fix, reject, reader-test fail, usage pause, crash and resume); a 5-page stub run finishes with correct state files and no barrier waits.

---

## Stage 6: images and charts
Add `scripts/v4/images.py <slug>` implementing the `visuals` skill:
1. For each photo slot: an owner photo in `content/images/inbox/` wins; otherwise call the existing `scripts/v2/find_images.py` (it already accepts only CC0, public domain, CC BY and CC BY-SA, filters for relevance and logs credits). Leave the slot empty rather than placing an off-topic photo.
2. Lead image at least 1,200 pixels wide; body images WebP around 150 KB; record width and height.
3. Chart slots: render an SVG from the named fact rows (bar or line, house styling, source line under it) into `content/images/<slug>/`.
4. Write alt text and caption from the writer's slot text; captions end with the credit.

**Acceptance:** tests with fixture candidates prove license filtering, owner-photo priority, empty-slot behavior and chart rendering from fact rows.

---

## Stage 7: rendering
Update whichever renderer deploys the live site (check `scripts/v2/publish.sh`; currently `render_site.py` builds the pages lint reads) to support:
- frontmatter `mode`, `kicker` (small line above the H1), `dek`, and an H1 equal to `title`;
- the ```glance block rendered as **Key takeaways**;
- ```reader blocks as styled "If you're..." boxes;
- `<!-- ad-break -->` rendered as an ad slot container (empty placeholder until the ad network is chosen), never inside tables, lists or blocks;
- the sources list and markdown checklists (`- [ ]`) rendered properly;
- fixed image dimensions (no layout shift) and the 1,200-pixel lead image in `og:image` with `max-image-preview:large`.

**Acceptance:** render the two gold-set pages and one answer page to HTML; a test asserts kicker, H1, takeaways, reader boxes, ad slots and image dimensions are present; no layout shift attributes missing.

---

## Stage 8: gates and scoring
1. Replace the word, source, reader and visual floors in `scripts/v2/lint.py` for v4 pages (frontmatter `mode` present) with a call to `page_check.py`; keep lint's link, frontmatter and image-license checks.
2. Add `scripts/v4/score_reader_test.py`: compare each answer in the reader test to the coverage map's expected answer (the fact values for that sub-question), and its `found_in` against the expected layer; output pass/fail per question and a page verdict (pass at 90 percent or better with no miss on the opening answer).

**Acceptance:** v3 pages still lint exactly as before; v4 pages are gated by page_check; scoring tests cover pass, partial and fail.

---

## Stage 9: paced publishing
Add `scripts/v4/publish.py`: each run moves at most `publish_per_day` pages from the ready queue to the live site (oldest approved first, pillars before their spokes), rebuilds `content/index.json`, runs the existing deploy and IndexNow steps. Never publish a page whose checker verdict is not `pass`.

**Acceptance:** tests prove the daily cap, ordering, and that failed or unchecked pages never publish.

---

## Stage 10: the pilot
Run the three topics in `docs/v4/PILOT.md` in review mode, in its run order: housing first (from the migrated fact file, starting at the architect), then the 2026 federal student loan changes and UNC system transfer in parallel.

Produce:
- `reports/pilot/<topic>.md` with every measure in PILOT.md's table, computed from state files, `usage.jsonl`, page_check, match_facts, checker and reader-test results;
- `reports/pilot/scorecard.csv` for the owner: one row per new page with the old page or best competitor beside it, and empty `verdict` (win, tie, lose) and `why` columns.

**OWNER CHECKPOINT:** the owner fills in the scorecard and approves or rejects the switch against PILOT.md's pass bars. Also settle there: architect on opus or fable, layering on sonnet or opus for pillars, writer effort, and page_check thresholds.

---

## Stage 11: switchover (only after the owner approves)
1. Replace `CLAUDE.md` with `CLAUDE.md.proposed`.
2. Run every existing article through v4 as a rewrite (housing and getting-around first, then the rest), keeping URLs stable; publish through stage 9's pacing.
3. Repo hygiene: add `reports/lighthouse/`, `reports/templates/` build outputs and `build/` to `.gitignore` and remove them from git history going forward; move `archive/v1` out of the repo; keep one renderer.
4. Mark `scripts/v3/` deprecated in its README.

**Acceptance:** all 108 pages rewritten, checked and queued; the repo's tracked size drops accordingly; the deprecated pipeline no longer runs by default.

---

## 3. Owner checkpoints, summarized
1. After stage 3 step 6, per topic: approve `plan.md`.
2. After stage 10: fill the scorecard; go or no-go.
3. Before stage 11: confirm the switch.

## 4. Non-goals for this build
- The analyst and learner agents and any weekly loop (deferred by the owner).
- Choosing an ad network or ad code (stage 7 renders empty slots).
- The data engine at national scale (the pilot's UNC transfer topic exercises it; scaling waits for go-live).
- Changing any editorial rule in `.claude/skills/` (the owner owns those).

## 5. Before stage 10
The gold set must be complete: paste the full text of "Where Cornell Sleeps" into `.claude/skills/gold-set/examples/feature-pillar.md`, and add the dining article as a second feature example if the owner approves it. Pages written before the gold set is complete don't count toward the pilot.
