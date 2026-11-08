# Owner photos: drop them here

Photos that Ajay or the team took go in this folder. They beat any photo found on the internet: `scripts/v2/find_images.py
--article` (write.sh runs it after each writer session, publish.sh before each lint) turns an inbox file named after an article
into that article's photo, replacing the internet photo at that position and keeping the alt text and caption the writer wrote.
Drop the file, run `scripts/v2/publish.sh --render` (or the script by hand, below), done. The original stays here untouched.

## Naming

`<slug>.<ext>` replaces the article's first image and `<slug>-<n>.<ext>` its n-th, where `<slug>` is the article's file name
without `.md`:

- `content/articles/housing/mews-hall-guide.md` has images 1 and 2 (`content/images/mews-hall-guide/1.webp`, `2.webp`)
- `mews-hall-guide.jpg` or `mews-hall-guide-1.jpg` replaces image 1, `mews-hall-guide-2.jpg` replaces image 2

The article must list an image at that position in its frontmatter (`images:`), because the alt text and caption come from there.
For an article that has no photo yet, add the entry yourself (the script fills in the credit fields):

```yaml
images:
  - file: 1.webp
    alt: "Mews Hall on North Campus, a brick residence hall behind a line of trees"
    caption: "Mews Hall, one of the North Campus halls transfers are placed in"
    credit: "Footnote Daily"
    credit_url: ""
    license: "All rights reserved"
    license_url: ""
```

By hand: `worker/.venv/bin/python scripts/v2/find_images.py --article content/articles/housing/mews-hall-guide.md`. It converts
the inbox file to `content/images/mews-hall-guide/<n>.webp` (under about 150 KB, 1600 px wide at most, turned the right way up),
writes the ledger entry below and sets the article entry's `credit`, `credit_url`, `license` and `license_url`. Running it again
changes nothing; to convert a replaced inbox file again, delete the `.webp` first.

## Files

- JPEG, PNG, WebP or TIFF. iPhone HEIC is not readable here: export it as JPEG first. Keep the original under about 10 MB.
- Landscape and at least 1200 px wide is best. Portrait photos work but take the whole column height.
- No recognizable people without their consent, no license plates, no screenshots, nothing taken from cornell.edu, a landlord,
  a news site or Google Images. A photo someone else took needs their written permission first: `docs/v2/photo-permission-email.md`.

## Credit

The page shows "Photo: <credit>, <license>" under every photo. For an inbox photo the script writes this ledger entry in
`content/images/credits.yml` (author and credit default to the site name; dates are the day the file was dropped and converted):

```yaml
- file: 2.webp
  article_slug: mews-hall-guide
  source: owner
  page_url: ''
  author: Footnote Daily
  license: All rights reserved
  license_url: ''
  found_at: '2026-11-07'
  fetched_at: '2026-11-07T21:40:12'
  credit: Footnote Daily
```

If someone else on the team took the photo, edit `author` and `credit` ("Jane Doe / Footnote Daily"); a `page_url` makes the
credit a link. The next run (publish.sh does one before each lint) copies `credit`, `page_url`, `license` and `license_url` from the
entry into the article, so the ledger is the one place to edit.

Going back to the internet photo: delete the inbox file and `content/images/<slug>/<n>.webp`, put the candidate's `page_url`
(from `content/images/candidates/<queue_id>.json`) back into the entry's `credit_url`, and publish again. The owner entry stays in
the ledger as the record until the script writes the internet photo's entry over it.
