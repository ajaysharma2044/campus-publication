# Calibration exercises (SPEC §32)

Run at 2026-11-02T19:56:54.854830+00:00 against the development database with **synthetic fixtures** and the **FixtureProvider** (scripted model responses). No real model call was made (no credential). Everything below is traceable by id in the database.

## Exercise 1 — research one hall from a primary source and build a profile

- Source `f5561289-a3a2-4368-86cb-f44a10dda2eb` → snapshot `e58e27d4-99cc-4d23-ae68-9f4767fbac80` (outcome ok, confidence 0.664125, tables 1).
- Deterministic extraction: 6 money claims, warnings none; actions ['confirmed', 'superseded', 'confirmed', 'confirmed', 'confirmed', 'confirmed'].
- Scoped per academic year and room type; per-person basis and academic-year period detected from the page text.
- Brief `6bd5bdda-9d0a-4aa1-bf47-5b6484a8dbd2` ready=True; critical claims 6; unknowns listed: 3.
- Draft v1 (writer model claude-sonnet-5-5): verifier status **failed** — deterministic hard findings: ['fabricated_consensus']. The verifier model was not called (no spend on an unpublishable draft).
- Correction: editor (model claude-opus-5-5) removed the fabricated consensus and quote → v2 `813a8ba3-0e92-48eb-9776-ccabc484aa43`.
- Draft v2: verifier **ok**, rubric total 21/24, hard failures none; page status staged.
- Staging publication: cms id 1, created=True; repeat publish changed=False (idempotent). Job `72589b00-1c95-431d-8a20-17a569ed02fa` run `fc7e8768-6ed6-4e8f-b4e9-7e4d5db2139e`.
- Spend: 24 minor units today (fixture provider priced via the reservation path; real spend would be reconciled from provider usage).

## Exercise 2 — compare two halls on shared records and equivalent periods

- Entities: ['Fixture Hall', 'Riverside Hall']; basis per_person, period per_academic_year.
- Rate row: ['$12,042 per academic year, per person (2026-27)', '$11,582 per academic year, per person (2026-27)'] (Riverside stored per semester, converted to the academic year for an equivalent comparison).
- Unknown cells: 10 — shown as unknown, never as absent.
- Tradeoffs produced from records only: On the same per academic year, per-person basis, Riverside Hall is $460 less than Fixture Hall for a double room. | Air conditioning differs — Fixture Hall: Yes; Riverside Hall: No.

## Exercise 3 — transfer-specific housing guide: page or section?

- Before any transfer-scoped claim exists: justified=True — transfer rules differ on: eligibility.guaranteed_housing. **Decision: no separate page; improve the general housing coverage.**
- After a verified transfer-scoped eligibility claim that differs from the general rule: justified=True — transfer rules differ on: eligibility.guaranteed_housing. **Decision: a transfer guide is now justified by a material rule difference, not by relabeling.**

## Exercise 4 — commuter community college configuration (synthetic)

- Identity status: synthetic_fixture (never published).
- Topic applicability: housing=not_applicable, dining=unknown, transfer=applicable.
- Housing hypotheses generated: 0 (skipped: topic_not_applicable). Transfer hypotheses generated: 0, all labeled hypotheses, observed count 0.
- The workflow prioritised transfer/programs/commuting and produced no dorm coverage.

## Source change → dependent output update

- Re-fetch: material_change=True; 1 claim superseded (old marked stale).
- Propagation: affected pages 1, revalidate jobs 1; tick ran [('revalidate_page', 'succeeded')].
- Page after revalidation: status held, revalidation_required=True (the current version still cites the superseded, now-stale claim, so it is held until a new version is drafted from the new claim; the dependency edge was inherited by the new claim so the rewrite job knows which page to update).

## Deployment state

- All of the above ran locally against the development PostgreSQL and an in-memory CMS. Real WordPress round-trip is verified separately (docs/ops/run.md). No external service was contacted.
- Next work: connect a model credential, run the same four exercises with the real router, compare rubric outcomes against these scripted ones, then enable bounded auto-publication for the entity_profile and comparison templates only.
