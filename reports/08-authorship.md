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

- Legal-rights pages carrying the line 'This page is general information, not legal advice.' (or the tool form 'This is not legal advice.'): 39.

## Data labels (beds vs residents)

- Pages labeled: 7; bed-count source: https://www.buildwelliver.com/projects/integrated-acquisition-and-development-cornell-university-north-campus-residential-expansion (fetched 2026-11-11; lists 'Toni Morrison Hall: 314 beds' and 'Ganędagǫ: Hall 577 beds'; McClintock 311, Hu Shih 429 and RBG 504 beds match Cornell's resident counts); skeptic verdict: NOT SOUND: One failure. File content/articles/housing/ganedago-hall-vs-toni-morrison-hall-cornell.md, line 136: the body links https://scl.cornell.edu/residential-life/housing/housing-and-residential-life-and-faculty-involvement-campus/rates-amenities-licenses/housing-rates ("Cornell housing rates"), and that URL is not in the frontmatter sources. It is the only URL in any of the 7 files that is missing. Thi

- content/articles/housing/cornell-north-campus-dorms-compared.md: Added 'These are Cornell Housing's resident counts.' before the 306/564/311/429/504 paragraph. Added one sentence saying Welliver, the construction manager, counts beds and lists 314 for Toni Morrison and 577 for Ganędagǫ:. Labeled the big table's source line 'Residents column: Cornell Housing resid (source: Cornell Housing hall pages (re-fetched 2026-11-11); https://www.buildwelliver.com/projects/integrated-acquisition-and-development-cornell-university-north-campus-residential-expansion)
- content/articles/housing/cornell-north-campus-new-dorms-vs-old-dorms.md: In 'How big are the halls?' added 'These are Cornell Housing's resident counts:' and inline links to the Ganędagǫ: and Toni Morrison hall pages, plus one sentence saying Welliver lists beds instead, 577 and 314. Added the Ganędagǫ:, Toni Morrison, Welliver and the already-cited Balch Hall page (prev (source: Cornell Housing hall pages; Welliver project page)
- content/articles/housing/cornell-north-campus-residential-expansion-what-changed.md: Rewrote the figure's source line to 'Cornell Housing resident counts from the [Toni Morrison], [Ganędagǫ:], [Barbara McClintock], [Hu Shih] and [Ruth Bader Ginsburg] hall pages', linking each one, and added one Welliver bed-count sentence (314 and 577). Added the 5 hall pages and Welliver to sources (source: Cornell Housing hall pages; Welliver project page)
- content/articles/housing/ganedago-hall-cornell.md: Opening sentence now reads 'holds 564 students by Cornell Housing's resident count'. The glance figure row is now 'Residents (Cornell Housing count)'. Added one Welliver sentence (577 beds) after the 'biggest residence building' line. The hall-page source now has accessed 2026-11-11, and the Wellive (source: Cornell Housing Ganędagǫ: page; Welliver project page)
- content/articles/housing/ganedago-hall-vs-toni-morrison-hall-cornell.md: '564 residents against 306 in Cornell Housing's resident counts' in the opening paragraph. One Welliver sentence (577 and 314 beds). Table row is now 'Residents (Cornell Housing count)' and the table source line reads 'Cornell Housing hall pages (resident counts)'. The two Ganędagǫ: links went to an (source: Cornell Housing hall pages; Welliver project page)
- content/articles/housing/how-cornell-assigns-first-year-roommates.md: Added 'By Cornell Housing's resident counts,' before 'Ganędagǫ: Hall holds 564 residents, Risley Hall 194 and Akwe:kon 35'. Added the three already-cited hall pages (Ganędagǫ:, Risley, Akwe:kon), which were missing from sources, with accessed 2026-11-11 (re-verified: 564, 194, 35). No bed count adde (source: Cornell Housing hall pages)
- content/articles/housing/toni-morrison-hall-cornell.md: Opening sentence now reads 'holds 306 students by Cornell Housing's resident count'. Added one Welliver sentence (314 beds). The glance figure row is now 'Residents (Cornell Housing count)'. The hall-page source now has accessed 2026-11-11, and the Welliver source was added. updated was already 2026 (source: Cornell Housing Toni Morrison page; Welliver project page)

## Acceptance

- No article shows a generic byline: PASS.
- Author pages render with structured data: the Astro build (site/scripts/check-build.mjs) renders /authors/ajay-sharma/ with the Person node; verified in the preview build.

