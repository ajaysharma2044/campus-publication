# Photo permission request (landlords and local businesses)

Use this when an article needs a photo that only the landlord, restaurant, shop or venue has (their listing photos, their
storefront, the inside of a building) and nothing suitable exists on Wikimedia Commons or Openverse. A credit is not
permission: we publish their photo only after a written yes. Send from the site's editor address; keep the thread.

## The email

Subject: `Permission to use your photo of <place> on EduExplained`

> Hello <name or "team at <business>">,
>
> I edit EduExplained (<site URL>), a guide for Cornell students, parents and alumni about living in Ithaca. We are
> publishing an article on <topic, e.g. "apartments on College Avenue"> and would like to show readers what <place>
> looks like. Your photo at <URL of the photo or page> is the best one we have found.
>
> May we use it on that article page? We would:
>
> - credit it under the photo as "Photo: <business or photographer name>", linking the credit to <their URL>;
> - resize and, if needed, crop it to fit the page (no other edits);
> - keep it only on EduExplained pages about <place>, not sell it or pass it on;
> - take it down within a week if you ask us to at any time.
>
> EduExplained is a free site supported by advertising. A reply saying "yes" to the points above is all we need. If
> you would rather send a different or higher-resolution photo, that is welcome too.
>
> Thank you,
> <name>
> Editor, EduExplained
> <editor email> | <site URL>

Keep it to this length. Do not offer money, do not promise coverage or a review, do not accept conditions that change what
the article says (spec: a sponsor never changes an article; a photo owner does not either).

## When they say yes

1. Save the whole reply thread as `content/images/permissions/<article-slug>-<their-domain>-<YYYY-MM-DD>.eml`
   (or `.txt` / `.pdf` if the mail client cannot export `.eml`). Create the folder the first time. The file is the proof;
   nothing is published without it.
2. Save the approved photo as `content/images/inbox/<article-slug>-<n>.jpg` (JPEG, PNG, WebP or TIFF), where `<n>` is the
   position of the article image it replaces, or `<article-slug>.jpg` for the first. The article's frontmatter must list an
   image at that position (alt text and caption come from it); `content/images/inbox/README.md` has the details. Then run
   `worker/.venv/bin/python scripts/v2/find_images.py --article content/articles/<topic>/<article-slug>.md` (publish.sh also
   runs it before each lint): it converts the photo to `content/images/<article-slug>/<n>.webp` and writes a `source: owner`
   entry in `content/images/credits.yml`.
3. Edit that ledger entry so the page credits them and the proof is on record; the next run copies `credit`, `page_url`,
   `license` and `license_url` into the article, and the page shows "Photo: <credit>, <license>" with the credit linked to
   `page_url`:

```yaml
- file: 1.webp
  article_slug: college-ave-apartments
  source: permission
  page_url: "https://example-landlord.com/college-ave"
  author: "Example Landlord LLC"
  license: "Used with permission"
  license_url: ""
  found_at: "2026-11-10"
  fetched_at: "2026-11-12T10:02:00"
  credit: "Example Landlord LLC"
  permission_file: content/images/permissions/college-ave-apartments-example-landlord.com-2026-11-12.eml
```

## When they say no, or do not answer

No reply within two weeks is a no. Use a Commons or Openverse photo of the street or neighborhood instead, a generated
figure built from the article's facts (cost table, timeline, steps), or a map. Never use their photo anyway, and never
use a photo copied from their site, a news site, cornell.edu or Google Images "with credit".

## Taking a photo down

If an owner asks, delete the inbox file and `content/images/<article-slug>/<n>.webp`, remove that `images` entry from the
article (or point it at another photo), set the ledger entry's `license` to `"Permission withdrawn <date>"` (keep the entry and
the email as the record), and publish again the same day.
