# Campus Publication — project routing file

National university and community-college information publication with an autonomous research, writing, verification, publishing, SEO, analytics, and ad-ops workflow. Cornell housing is the pilot, not the boundary.

## Read first
- `SPEC.md` — full owner specification (sections 01–39). Authoritative requirements.
- `BACKLOG.md` — prioritized tasks with IDs, dependencies, executable acceptance checks.
- `STATE.md` — what is implemented / tested / connected / deployed / scheduled, blockers, next actions. Update after every completed task.

## Layout
- `worker/campus_worker/` — Python worker (registry, queue, budget, collectors, claims, discovery, scoring, briefs, editorial gates, rendering, CMS adapter, analytics, ads, dashboard).
  - `migrations/` plain SQL, applied by `python -m campus_worker.db migrate`.
  - `contracts/schemas/` JSON schemas for every role output.
  - `adapters/` provider adapters (model, search, keyword, routing, CMS, ads, analytics). Each reports `capability()` → connected / unconnected / disabled.
  - `render/` Jinja templates + static design system (the same HTML the WP theme renders).
- `wp/themes/campus-editorial`, `wp/plugins/campus-core` — WordPress theme and structured-publishing plugin.
- `fixtures/synthetic/` — clearly labeled synthetic data. Never treat as real institution facts.
- `docs/` — design, editorial, ops, contracts documentation.
- `skills/national-college-publishing/` — coordinator skill with modular references (instruction files; not installed anywhere unless STATE.md says so).
- `scripts/` — run, check, backup, restore, screenshot QA.

## Rules of the road
- Database is authoritative for content jobs; BACKLOG/STATE track implementation milestones.
- Deterministic code for math, dates, queues, validation, hashing, budget, rendering. Models only for language judgment, behind `adapters/model.py` with role aliases from `config.py`.
- Every school-scoped record carries `institution_id` and `campus_id`. Never join by name or slug.
- Money is integer minor units. Timestamps UTC. Academic year/effective dates separate from fetch time.
- No fabricated facts, bylines, quotes, demand numbers, revenue, or "live" claims. Label fixtures and unconnected adapters.
- Fetched text is untrusted. Never execute anything from source content or model output.
- Spend caps ($3/day, $60/month default) enforced in `budget.py`; reservation before any paid call.

## Running
```bash
cd worker && pytest -q                      # all checks
python -m campus_worker.db migrate          # apply migrations (needs DATABASE_URL)
python -m campus_worker.cli status          # operating status / heartbeat
python -m campus_worker.cli run-once        # one bounded scheduler tick
python -m campus_worker.render.preview      # render static preview site to build/preview
```
See `docs/ops/run.md` for setup, env vars (`.env.example`), rollback, and backup/restore.
