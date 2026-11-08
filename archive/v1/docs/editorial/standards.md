# Editorial standards (as enforced in code)

| Standard | Where enforced |
|----------|----------------|
| Answer the decision early; concrete next action | `editorial/checks.check_next_action`, verifier rubric (clarity, usefulness) |
| No empty openings / filler | `checks.check_openings`, `checks.check_filler` (BANNED_OPENINGS, FILLER_PHRASES) |
| No invented quotes, experiences, consensus, ratings | `checks.check_fabrication` — hard failure |
| Truthful desk byline, never a person | `checks.check_byline` (ALLOWED_BYLINES) — hard failure for person-like bylines |
| No superlatives/clickbait headlines | `checks.check_headline` |
| Prose matches the fact table | `checks.check_money_in_prose_matches_table` |
| Every fact traceable to an approved claim | `checks.check_claim_refs` — hard failure for unknown claim ids |
| Arithmetic correct | `checks.check_arithmetic` — hard failure |
| Right school, right year | `checks.check_scope` |
| No label-swapped audience duplicates | `checks.check_duplicate_audience` (≥82% similarity) — hard failure |
| No padding/repetition | `checks.check_length_padding` |
| Critical claims unconflicted and current | `claims.blocking_claims` in `gates.evaluate` |
| Rubric ≥20/24, none <3 | `gates.evaluate` |
| Automation disclosure | `roles/runners.PRODUCTION_NOTE` rendered on every page; `/about/methods/` |
| Corrections never silent | `page_versions.change_summary`, `pages.last_material_update_at`, correction_requests |

Calibration outcomes and rejected/accepted examples: `docs/editorial/calibration.md`, `skills/national-college-publishing/references/writing.md`.
