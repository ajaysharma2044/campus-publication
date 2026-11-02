# Task contracts

Every specialist role returns one JSON object validated against `worker/campus_worker/contracts/schemas/envelope.json` plus its role schema (`<role>.json`) before anything is persisted (`contracts/validate.py`). Validation runs inside the model router, so a malformed response gets at most one same-tier repair and then holds the job.

## Envelope (all roles)
| key | meaning |
|-----|---------|
| `schema_version` | `"1.x"` |
| `run_id` | the `runs.id` the orchestrator passed in |
| `role` | one of onboarding, discovery, opportunity, researcher, planner, writer, editor, verifier, seo, tool_engineer, ad_ops, analyst |
| `input_ids` | artifact ids the task was given (briefs, claims, snapshots) |
| `institution_id`, `campus_id` | scope; never inferred from names |
| `decision` | advance · update · merge · watch · reject · hold |
| `hold` | required when decision = hold: `{reason: snake_case, retry_condition: text}` |
| `output` | role-specific object (below) |
| `evidence_ids` | claim/snapshot ids actually relied on |
| `uncertainties` | plain statements of what is unknown |
| `next_jobs` | **proposals only**: `{job_type ∈ fixed enum, payload, rationale, priority}`; the orchestrator re-checks authorization, dependencies, spend and quotas; payloads that mention budget/cap/quota/permission/grant/api_key/shell/command are rejected |
| `usage` | tokens and model as reported by the provider |

Shell-like lines anywhere in `output` strings fail validation (`sanitize.model_output_is_safe`). Nothing in a contract is ever executed.

## Role outputs
- **researcher** — `claims[]` (typed `claim_item`: field, value_type, value, unit/currency, billing_period, price_basis, room_type, academic_year, audience_applicability, effective dates, evidence_category, **source_locator required**, excerpt ≤600 chars, confidence, conflicts_with), `not_found[]`, `not_applicable[]`, `scope_notes[]`, `injection_observed`.
- **discovery** — `observed_questions[]` (raw_text, origin ∈ official_faq/search_suggestion/related_question/discussion/competitor_gap, audience, constraints, source_ref, observed_at) and `hypotheses[]` kept separate.
- **opportunity** — `scores{demand, answer_gap, winnability, evidence_advantage, commercial}` each 0–5 or null, `observations{}` per score, `confidence`, `missing_contribution`, `action`, `existing_coverage_checked[]`, optional `editorial_exception_rationale`.
- **planner** — page_format, audience, reader_decision, verified_answer, unique_contribution, critical/supporting claim ids, exceptions, unresolved_facts, `structure[]` (heading, purpose, claim_ids), comparisons, allowed_subjective_evidence, next_tasks, overlap_page_ids, headline_candidates ≤5.
- **writer** — headline (15–110), deck (20–300), body_markdown (200–40k), `claim_refs[]` (every fact used), `fact_table[]` (label, value, claim_id), `next_actions[]` 1–6 (text, target), sources_used, writer_notes.
- **editor** — revised_headline, revised_deck, revised_body_markdown, `findings[]` (kind ∈ clarity/specificity/structure/attribution/usefulness/prose/filler/unsupported/duplicate/headline), substantive_changes, unresolved.
- **verifier** — `claim_checks[]` (claim_id, status ∈ supported/unsupported/stale/conflicted/arithmetic_error/wrong_scope, source_opened), `hard_failures[]` from the fixed list (unsupported_critical_claim, unresolved_conflict, wrong_school_campus_year, invented_quote_or_experience, missing_rights, incorrect_arithmetic, deceptive_headline, superficial_duplicate, unsafe_code, broken_interaction, inaccessible_layout, ads_obscure_task, missing_privacy_behavior, fake_byline, fabricated_consensus), `rubric{clarity, specificity, structure, attribution, usefulness, prose}` 0–4, rubric_notes, publishable, corrections_required.
- **onboarding / seo / tool_engineer / ad_ops / analyst** — `summary`, `findings[]` (kind, detail, severity), `proposed_changes[]` (target, change). Proposals are applied by code paths with their own checks, never by the model.

## Gate policy (editorial/gates.py)
Deterministic checks (`editorial/checks.py`) run before any verifier model call; a hard finding stops the draft without spend. Release requires: no hard failures, no blocking critical claims (open conflict / stale / superseded), rubric total ≥ 20/24 with no dimension < 3, fewer than three major findings, and a known template (novel templates hold for owner calibration).
