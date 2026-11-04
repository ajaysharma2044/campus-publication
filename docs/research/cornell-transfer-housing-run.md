# In-session run — Cornell transfer housing (2026-11-04)

Executed with `python -m campus_worker.session_run`. The language-judgment roles (discovery synthesis, writing, editing, rubric scoring) were performed by the Claude Code session; all storage, checks and gating are the repository's deterministic code. Ids below are in the development database; the JSON twin of this report is `cornell-transfer-housing-run.json`.

## Access state (the blocker, exactly)
`scl.cornell.edu`, `faq.enrollment.cornell.edu`, `admissions.cornell.edu`, `news.cornell.edu`, `assembly.cornell.edu`, `cornellsun.com` and `nces.ed.gov` do not resolve from this session (environment network policy). Web search works and returned snippet text attributed to the official pages. The run records each official page as a `source_registry` row with a **blocked** snapshot and a parallel `search_snippet` source holding the snippet, so provenance is truthful. Fix: add those hosts under Allowed domains in the environment's Network access settings, then rerun the collector on the six registered official URLs; the stored claims will be superseded by deterministically extracted ones from the opened pages.

## Discovery
8 observed questions (origins: official_faq, related_question, search_suggestion, competitor_gap) → clusters by answer; the target cluster is "Is housing guaranteed for transfer students at Cornell?" (audience split on housing because transfer eligibility differs). Reddit was not used.

## Opportunity (cluster c40dfc34…)
D=2 (repeated independent questions; no authorized demand provider) · G=4 (official answer split across four pages; transfer non-guarantee only implied; secondary coverage dated) · W=3 · **E=2** (synthesis would be verifiable, but primary pages were not opened) · M=2 → priority **54.0**, decision **hold** ("evidence advantage 2 below 3; research before drafting"). The draft was still produced so the owner has an inspectable article; it cannot advance until E≥3, i.e. until the pages are opened.

## Research
17 claims stored as `estimate`, extraction method `import`, confidence 0.5, each linked to its snippet snapshot with the excerpt. Scope kept explicit: rates per person per semester for 2026-27 with room type; residency years split by audience (transfer=1, general=2); guarantee split by audience (first_year=true, transfer=false/not stated); deadlines as text/date; fees in minor units. Cooperative-residence figures on the rates page recorded as a scope exception, not as claims.

## Draft, edit, verification
- Page `/schools/cornell-university/housing/transfer-housing/` (guide, audience transfer), version 1, byline "Housing desk", production note states in-session production and that primary pages were not opened.
- Deterministic checks (`editorial.checks.run_all`): **0 findings** (no banned openings/filler, no fabricated consensus or quotes, no superlatives, no prose/table money mismatch, scope clean, next actions present).
- Session rubric: clarity 4, specificity 4, structure 4, **attribution 2**, usefulness 4, prose 4 = 22/24. Attribution is below 3 because no claim was checked against an opened source.
- Gate: **failed** — hard failure `unsupported_critical_claim` (rate, eligibility, deadline and fee claims are estimates). Rubric also fails on attribution < 3. Page status **held**, `revalidation_reason = primary sources unopened (network policy)`.
- Publication: not attempted; `publisher.publish_version` refuses non-passed versions. Nothing about Cornell is on the local WordPress or anywhere public.

## Rendered preview
`build/preview/schools/cornell-university/housing/transfer-housing/index.html` renders the full article with a prominent "Draft held, not published" notice, every fact-table row tagged **estimate** (or unknown), and sources labelled "snippet-attributed; page not opened". Screenshots: `build/qa/cornell_transfer_housing__1280.png`, `__390.png`.

## What the article would need to pass
1. Open S1–S7 directly; extract rates with `claims.extract_rate_table` (expect six money claims scoped 2026-27) and confirm the eligibility/deadline sentences; the new verified claims supersede the estimates (same source family rule) and `propagation.on_claim_changed` flags this page for re-verification.
2. Re-run the verifier with source excerpts → attribution ≥ 3 → gate passes → staged draft in WordPress.
3. Two follow-ups are already queued as next tasks: a West vs South Campus hall comparison, and meal-plan cost in the calculator.
