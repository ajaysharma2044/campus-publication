# Design QA log

Run: `python -m campus_worker.render.preview && node scripts/qa_screens.js build/preview build/qa && python scripts/check_css.py`

## 2026-11-02 — first pass (18 pages × 5 widths = 90 screenshots, inspected)
Defects found and fixed:
1. Home "Also verified recently" heading inherited the lead-story display size → scoped `.lead-story > h2:not(.section-head)`.
2. Fact table rendered after all prose instead of under "Building facts" → `[[fact-table]]` marker in body splits prose around the table.
3. Fact tables clipped at 360/390 (status column off-screen) → stacked row layout below 600px (comparison keeps horizontal scroll with visible caption).
4. Compact masthead wrapped to three lines beside the tagline at 360 → tagline hidden under 768px, name nowrap.
5. Status column "checked …" wrapped to three lines on desktop → nowrap ≥768px.
6. Home and 404 had no H1 → masthead is the H1 on home; 404 has a real H1.
7. Mobile stacked caption broke per word → caption display:block.
8. QA script took screenshots after pressing Tab (skip link visible in every shot) → screenshot first, then focus check.

Final report: 90 page/width renders, 0 problems: no horizontal overflow, one H1 per page, skip link and `main` present, every input labelled, first Tab stop shows a focus outline, no ad or analytics scripts, both self-hosted fonts loaded.
Contrast: all 16 text/background pairs ≥ 4.97:1 (`scripts/check_css.py`). No gradients/glass/pills/justified text.

Not yet verified: real-user Core Web Vitals (needs a deployed site), long real school names (only synthetic names tested), photography states (no images in v1; typography-led cover used).
