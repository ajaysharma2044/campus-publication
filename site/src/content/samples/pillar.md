---
title: "Sample pillar guide: how a complete guide is laid out"
meta: "Sample content for the pillar template. Every element of the reference article layout appears once, with sample text that describes itself."
primary_query: sample pillar guide
topic: housing
school: cornell-university
page_type: pillar
updated: 2026-11-08
sample: true

facts_title: "Sample facts table"
facts:
  - { label: "Sample rate per semester", value: "$0,000 (sample figure)", note: 1 }
  - { label: "Sample deadline", value: "Month 00 (sample)", note: 2 }
  - { label: "Sample capacity", value: "000 students (sample)" }
  - { label: "Sample distance", value: "0.0 miles to a sample landmark" }
sources:
  - { url: "https://example.org/sample-source-1", title: "Sample source 1 (official page, not real)", accessed: 2026-11-08 }
  - { url: "https://example.org/sample-source-2", title: "Sample source 2 (official page, not real)", accessed: 2026-11-08 }
  - { url: "https://example.org/sample-source-3", title: "Sample source 3 (student newspaper, not real)", accessed: 2026-11-08 }
  - { url: "https://example.org/sample-source-4", title: "Sample source 4 (public forum, not real)", accessed: 2026-11-08 }
  - { url: "https://example.org/sample-source-5", title: "Sample source 5 (listing, not real)", accessed: 2026-11-08 }
images_from: cornell-transfer-housing
images:
  - { file: 1.webp, alt: "Cornell University West Campus entrance (a real licensed photo used as the sample lead)", caption: "Cornell University West Campus entrance", credit: "颐园居 / Wikimedia", credit_url: "https://commons.wikimedia.org/wiki/File:Cornell_University_West_Campus_entrance.jpg", license: "CC BY 4.0", license_url: "https://creativecommons.org/licenses/by/4.0" }
---

This is sample content. **The short answer** is the opening paragraph of every guide: it answers the question in two or three sentences, with the **two most important phrases** marked, before the detail begins. A real guide would cite its first fact here [to a source](https://example.org/sample-source-1).

The paragraphs between the short answer and the first heading set up the detail. They read as one block with the short answer on the page and are counted toward the first in-content ad.

## What a section looks like

Body sections are H2s separated by hairlines. The text is Libre Franklin at 17px; headings are Newsreader. Hard facts carry a gold footnote marker [like this one](https://example.org/sample-source-2), which links to the Sources list; the list links back.

### A subsection

H3s divide a long section. Lists keep their hanging indent:

- A sample bullet with a fact and [a source](https://example.org/sample-source-3).
- A second sample bullet.
- A third sample bullet, because three is a list.

```figure
kind: cost_table
title: Sample cost table drawn from a figure block
rows:
  - {label: "Sample item one", value: "$0,000 a year (sample)"}
  - {label: "Sample item two", value: "$000 a month (sample)"}
  - {label: "Sample item three", value: "$00 one time (sample)"}
```

## A note and a sequence

```glance
- Sample glance bullet one
- Sample glance bullet two
- Sample glance bullet three
- Sample glance bullet four
```

Steps appear only when the content is a real sequence:

```figure
kind: steps
title: Sample steps
rows:
  - {label: "Sample first step", value: "What to do first and why (sample)."}
  - {label: "Sample second step", value: "What happens next (sample)."}
  - {label: "Sample third step", value: "The last step (sample)."}
```

## A timeline and a table

```figure
kind: timeline
title: Sample timeline
rows:
  - {label: "Sample event one", date: "Month 1"}
  - {label: "Sample event two", date: "Month 2"}
  - {label: "Sample event three", date: "Month 3"}
```

| Sample column | Number | Note |
| --- | ---: | --- |
| Sample row one | 1,234 | Tabular numerals line up |
| Sample row two | 567 | Hairline rows |
| Sample row three | 89,012 | No tinted header |

## Where ads land

An in-content ad appears after the short answer and then roughly every 700 words, only ever between sections. This sample is short, so you will see at most two. A blockquote looks like this:

> Sample quotation from an attributed public source, paraphrased in a real guide and linked [to where it was read](https://example.org/sample-source-4).

## How to read the rest of this sample

The remaining elements are the FAQ (below, from the body's own FAQ section), the Sources list with two-way links, and the related grid, which is filled from real guides in the same topic.

## FAQ

### Is this sample content?

Yes. Every sentence on this page describes the template. Nothing here is a fact about Cornell or Ithaca.

### Where does the FAQ schema come from?

From this section: each H3 becomes a Question and its paragraph the Answer in the FAQPage JSON-LD.

### How many questions should a real FAQ have?

Three to six, each answering something the body did not, with [a source](https://example.org/sample-source-5) where a fact appears.
