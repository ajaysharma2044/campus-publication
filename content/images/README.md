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

## Every photo needs rights and a credit

Fill in `credits.yml` for each file. `credit` is shown on the page; `license`, `rights_holder`
and `source_url` are recorded for the rights log (SPEC §04). A photo without a credit entry is ignored.
