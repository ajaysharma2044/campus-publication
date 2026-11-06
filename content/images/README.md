# Photos for the site

Drop photographs in this folder and describe each one in `credits.yml`. The preview
(`python -m campus_worker.render.preview`, or the live preview server) uses a photo whenever
`credits.yml` lists one for a slot; otherwise it falls back to the labeled synthetic placeholder.

## Slots used by the preview fixtures

| slot                   | where it shows                                   |
|------------------------|--------------------------------------------------|
| `fixture-hall`         | home hero, Fixture Hall profile lede             |
| `riverside-hall`       | "Also verified recently" card                    |
| `quad`                 | "Also verified recently" card (housing hub)      |
| `fixture-state-campus` | school card on home, school hub header           |
| `library`              | spare                                            |

## File guidance

- JPEG, landscape, at least 1600×1000 (16:10). Portrait or square photos are cropped to 16:10 with `object-fit: cover`.
- Keep the file under ~400 KB. The renderer also writes an 800px-wide copy for cards.
- Name files in lowercase with hyphens, e.g. `fixture-hall.jpg`.

## Photos on published pages: keyed by page path

The site build (`render/site.py`) never uses the synthetic placeholders. A published page shows a
photograph only when `credits.yml` lists one for that page's path under `pages:`:

```yaml
pages:
  "/schools/cornell-university/housing/transfer-housing/":
    file: cornell-north-campus.jpg
    alt: "Low brick residence halls along a tree-lined path on North Campus"
    caption: "North Campus, where first-year halls are"      # optional
    credit: "Photo: Jane Doe for Footnote Daily"
    license: "CC BY-SA 4.0"                                  # the rights record; rendered as data-rights on the <img>
    rights_holder: "Jane Doe"
    source_url: "https://commons.wikimedia.org/wiki/File:..."
```

`file`, `alt`, `credit` and `license` are required; without any one of them, or without the file in this
folder, the page renders with no image (never a placeholder). The build copies the file to
`/static/img/photos/<file>` and writes the `<img>` with `alt`, pixel `width`/`height` and
`data-rights="<license>"`, which the SEO gate's image check requires. Only rights-cleared photographs:
no stock imagery, nothing model-generated.

## Every photo needs rights and a credit

Fill in `credits.yml` for each file. `credit` is shown on the page; `license`, `rights_holder`
and `source_url` are recorded for the rights log (SPEC §04). A photo without a credit entry is ignored.
