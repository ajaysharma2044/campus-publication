# Phase 8: authorship and trust (2026-11-11)

## Bylines

- Pages scanned: 408; frontmatter author values: {'(none: site default)': 408} (a page without an author takes site.config.ts defaultAuthor = ajay-sharma).
- Pages with a generic byline (editors, staff, team): none.
- The old organisation author entry (EduExplained editors / Footnote Daily editors) is no longer in site.config.ts; its URLs /authors/eduexplained-editors/ and /authors/footnote-daily-editors/ 301 to /authors/ajay-sharma/ (site/scripts/check-build.mjs writes dist/_redirects).
- Pages carrying edited_by: 0; reviewed_by: 0. Byline.astro prints an 'Edited by' line when the editor is not the author and a 'Reviewed by' line when a reviewer is named (present).

## Author page

- /authors/ajay-sharma/: name Ajay Sharma, kind person, role Editor-in-chief, with 3 {{BIO: ...}} placeholder(s) left for Ajay to fill ({{BIO: Cornell transfer student}}; {{BIO: public policy at the Brooks School}}; {{BIO: how he edits: official sources first, every number linked, corrections logged}}) rather than claims written for him; the one sentence stated as fact is the editor-in-chief role.
- The TransferringUp disclosure is a single labeled line in the bio (present); no article body mentions it (checked in reports/07-sections.md).
- Structured data: site/src/lib/schema.ts emits a Person (kind person) or Organization as the author of every Article and a Person node on the author page (present).

## Trust pages

- Footer (site/src/components/Footer.astro, links from site.config.ts footer.columns, on every page): about True, editorial standards True, sources True, corrections True; the footer's own 'How we work' link points at /editorial-standards/.
- Every tool page links /corrections/ under its result; the home page links the standards and corrections pages; /editorial-policy/ 301s to /editorial-standards/.

## Sensitive topics

- Legal-rights pages carrying the line 'This page is general information, not legal advice.' (or the tool form 'This is not legal advice.'): 37.

## Data labels (beds vs residents)

- reports/08-labels.json not written yet.

## Acceptance

- No article shows a generic byline: PASS.
- Author pages render with structured data: the Astro build (site/scripts/check-build.mjs) renders /authors/ajay-sharma/ with the Person node; verified in the preview build.

