# Images for Footnote Daily v2

Every article gets at least one useful visual, and we never publish an image we do not have the right to use
(docs/v2/spec.md, "Images and visuals"). This folder holds the photos, their proof of license, and the owner inbox.

## Layout

| path | what it is | who writes it |
|------|------------|---------------|
| `candidates/<queue_id>.json` | photos the finder found for one article, with their license data straight from the API | `scripts/v2/find_images.py --query` (write.sh runs it before each writer session) |
| `<slug>/<n>.webp` | the photos an article uses, resized to WebP under about 150 KB | `find_images.py --article` (write.sh runs it right after the session) |
| `credits.yml` | the ledger: one entry per stored file | `find_images.py`; owner adds permission photos by hand |
| `inbox/` | photos Ajay or the team drop in as `<slug>.jpg` or `<slug>-<n>.jpg`; `find_images.py --article` makes them image 1 or n of that article, credited to the site (see `inbox/README.md`) | owner |

`candidates/<queue_id>.json` is a list of `{source, title, page_url, file_url, thumb_url, author, license, license_url, width, height}`
where `source` is `wikimedia`, `openverse`, `unsplash` or `pexels`. Only accepted licenses appear there: CC0, Public Domain / PDM,
CC BY, CC BY-SA, Unsplash License, Pexels License. Never NC or ND, and never anything without a clear license.

`credits.yml` is a list of `{file, article_slug, source, page_url, author, license, license_url, found_at, fetched_at}`. The license
data comes from the API response; nobody guesses it. For a permission photo, `source` is `permission`, `page_url` is where the
photo came from, and the email granting permission is saved next to it.

## How an article uses its photos

The writer picks 1 to 4 images from the candidates and lists them in the article's frontmatter, with alt text and a caption:

```yaml
images:
  - file: 1.webp                       # relative to content/images/<slug>/
    alt: "Mews Hall on North Campus, a brick residence hall behind a line of trees"
    caption: "Mews Hall, one of the North Campus halls transfers are placed in"
    credit: "Jane Doe / Wikimedia Commons"
    credit_url: "https://commons.wikimedia.org/wiki/File:..."
    license: "CC BY-SA 4.0"
    license_url: "https://creativecommons.org/licenses/by-sa/4.0/"
```

`credit` may also be the finder's full line, "Photo: Jane Doe / Wikimedia Commons, CC BY-SA 4.0"; the renderer prints the credit
once either way. `file` may say `1.jpg` when the stored file is `1.webp` (same stem): the renderer finds it.

`scripts/v2/render_site.py` copies the files to `build/site/images/<slug>/<n>.webp` (a non-WebP file, or a WebP over 150 KB, is
turned the right way up, capped at 1600 px wide and re-encoded until it is under 150 KB) and renders each as a figure with lazy
loading and a caption that ends with the credit and license, both linked: "Mews Hall ... Photo: Jane Doe / Wikimedia Commons,
CC BY-SA 4.0". Placement:

- The first image not referenced in the body is the lede, under the title.
- An image referenced in the body with `![alt](1.webp)` on its own line is rendered in place.
- Any other image is placed between sections (before the second, third, ... heading), in order.

A CC BY-SA photo that we crop or resize stays under CC BY-SA; the caption's license link covers that.

Other visuals: a fenced `figure` block in the body (`kind: cost_table | timeline | steps`) becomes an inline SVG drawn from the
article's own facts, and a YouTube or Instagram embed pasted as its official `<iframe>` HTML passes through the Markdown as it is.

## Never

Photos copied from cornell.edu, landlords, news sites or Google Images without a reuse license or written permission
(a credit is not permission). AI-generated images that look like photos of real places. Files over about 150 KB on the page.
