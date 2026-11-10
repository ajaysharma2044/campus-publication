# Brand files

- `source/`: the wordmark as the owner supplied it on 2026-11-10, two PNGs (navy on white, white on navy; 661×105 px of lettering). Not used by the build; kept so the trace can be redone.
- `wordmark.svg`: the lettering traced to an outline (18 contours, even-odd fill, `fill="currentColor"`). `src/components/Logo.astro` inlines it (masthead, footer, styleguide); `brand-assets.mjs` puts it on the Open Graph card. How it was made: the navy-on-white PNG cropped to the lettering with an 8 px margin, upscaled 8× (Pillow, Lanczos), traced with potrace (the 2.1.8 JavaScript port: threshold 128, turd size 16, alphaMax 1.0, optTolerance 0.2), scaled back to the artwork's pixel grid with the viewBox on the outline's bounds, reduced with svgo 3.3.2 (`convertPathData` precision 1).
- `favicon.svg`: the wordmark's E, white on the palette's navy, 64×64 with the E's cap height at 40 px. `brand-assets.mjs` renders every PNG icon and the social avatar from it and copies it to `public/`.
- `brand.html`: the Open Graph card (1200×630): the wordmark, the tagline in Newsreader italic, the gold rule. `brand-assets.mjs` injects `wordmark.svg` in place of its `<!--wordmark-->` comment and screenshots it to `public/og-default.png`.

Regenerate everything in `public/` with `node scripts/brand-assets.mjs` from `site/` (Playwright and sharp from the repository root).
