# Design system

Source of truth: `worker/campus_worker/render/static/campus.css` (copied into the theme at `wp/themes/campus-editorial/assets/`). Fonts: Source Serif 4 (display + text, optical sizing) and Source Sans 3 (UI), self-hosted WOFF2 under the SIL OFL (`static/fonts/`).

## Tokens
paper #F8F7F3 · surface #FFFFFF · ink #171717 · secondary #575757 · metadata #6B6B6B · rules #D9D6D0 / #B8B4AC · navy #1E3C52 (links, buttons, eyebrows) · stale/unknown #7A4B00 on #F6EEDC · verified #1F5A3A · error #8A1C1C. All text pairs ≥ 4.97:1 (`scripts/check_css.py`).

Spacing: 4/8/12/16/24/32/48/64/96px. Radius 2px. Container 1240px, 12-column grid, 16px gutters (24px ≥768px). Measure 42rem (~68 characters). Body 19px/1.6 desktop, 17px/1.62 mobile. Display sizes fluid via clamp.

## Page patterns
Utility row → masthead (full on home, compact elsewhere; H1 only on home) → section nav (horizontal scroll on phones) → main → footer with the independence/automation disclosure. Article: eyebrow, H1, deck, byline strip (desk, published, substantively updated, read time, audience), prose in measure, fact table with status tags and checked dates, next actions, sources + production note + corrections link. Comparison: side-by-side table with per-cell evidence tags, tradeoffs the records support, what it cannot tell you. Calculator: server-rendered form (works without JS), result block with mandatory/optional/deposits/unknowns, method and limitations beside it.

## States
Empty home (typographic cover, no fake stories) · school hub with no guides · topic hub not applicable · search blank / disambiguation / empty · 404 · stale notice · unknown values in warm ink · consent bar (only when ads enabled) · skeleton shimmer (the only animation; disabled under reduced motion).

## Rules
No gradients, glass, blobs, pills, emoji headers, animated counters, repeated card grids, justified text, AI imagery. Missing photography → typography-led cover. Keyboard focus ring 2px navy; skip link; `main#main`; one H1; labelled inputs; `aria-live` results; 44px touch targets; no horizontal overflow at 360px.

QA evidence: `docs/design/qa.md`, screenshots in `build/qa/` (regenerate with `node scripts/qa_screens.js`).
