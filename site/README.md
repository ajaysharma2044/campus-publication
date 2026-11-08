# Footnote Daily site templates (Astro)

The Astro build of the site: 14 page templates built from shared components, one global stylesheet, and build-time checks. It reads the same `content/articles/**` Markdown and `content/images/` photos as the Python renderer (`scripts/v2/render_site.py`) and runs beside it; nothing here changes the Jinja build or the Netlify publish dir.

## Commands (Node 22 from `~/.local/node/bin`)

```
cd site
npm install
npm run build        # prebuild: photo variants; astro build; check-build; postbuild: Pagefind index -> dist/
SITE_PRODUCTION=1 npm run build   # same, with indexing on (no noindex, robots allow, sitemap filled)
npm run dev          # live preview at http://localhost:4321 (ad slots outlined, labels shown)
npm run preview      # serve dist/
npm run screenshots  # reports/templates/*.png at 375 and 1280 (Playwright from the repo root)
npm run lighthouse   # reports/lighthouse/*.report.html + README.md (Chrome for Testing)
```

## Where things are

- `site.config.ts`: site name, URL, production switch, ad provider (`none | adsense | other`), newsletter endpoint, schools, topics, audience stages, place fact fields, authors, nav and footer.
- `src/content.config.ts`: the collections (`articles` from `../content/articles`, `pages` from `../content/pages` plus `src/content/pages-extra`, `samples` for the styleguide).
- `src/lib/model.ts`: content-to-template mapping, URLs, validation (a throw fails the build), hub groupings.
- `src/lib/markdown.ts`: Markdown rendering, figure blocks, footnote markers, FAQ and related extraction.
- `src/components/`: the shared components; `src/layouts/`: the 14 templates; `src/pages/`: the routes.
- `src/styles/global.css`: the only stylesheet.
- `scripts/check-build.mjs`: post-build checks (one H1, no inline styles, meta tags, link integrity, orphans, hub completeness).
- `/styleguide/`: every component and template with labeled sample content (noindex).

Judgment calls are logged in the repository's `DECISIONS.md`.
