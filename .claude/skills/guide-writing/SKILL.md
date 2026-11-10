---
name: guide-writing
description: How the guide writer turns one packet into one complete EduExplained guide or pillar section. Load for the guide writer agent. Covers reading the packet, page shape by type, using facts and links, reader blocks, figures, frontmatter and the finish checklist.
user-invocable: false
---

# Guide writing

You write one page (or one section of a pillar) from one packet. The packet is everything you need. You don't search the web and you don't read other files, because everything true that the page can say is already in the packet's fact rows.

## Read the packet in this order
1. `layer_plan`: how the page is built: headline, dek, takeaways, the spine, every section in order with its form (table, steps, tool, prose), reader blocks, ad breaks and link placements. Follow it exactly; it is your outline.
2. `coverage_map`: what each section must answer. This is your definition of done.
3. `search_brief`: the intent, what current results miss, the title and meta to use. Use it to shape the page; never repeat its SEO language on the page.
4. `facts`: the only facts you may state. Each has a fact_id, value and source URL.
5. `readers`: the reader cards for the blocks the layer plan assigns.
6. `links`: internal pages you may link to, with their titles.

Then read the gold-set example for your page type in `.claude/skills/gold-set/examples/` (or `eduexplained-voice/references/before-after.md` until the gold set exists).

## Write
1. **Headline, dek and takeaways:** use the layer plan's headline and dek. Write the 3 or 4 Key takeaways it lists as a ```glance block: each bullet one decision or number, under 20 words.
2. **Opening:** the coverage map's `answer_first`, sharpened into the page's first paragraph. 60 words or fewer, one link at most. It must not simply repeat the takeaways: the takeaways list the key points, the opening answers the question in a sentence or two.
3. **Sections:** one per sub-question or group of related sub-questions, in the order a reader needs them (what to do first, what it costs, when it's due, what goes wrong). Headings are the plain questions a reader would search: "How much can a landlord charge?" Each section opens with its own answer.
4. **Facts:** state each fact once, in full, linked to its source_url the first time. Use the value exactly as written in the fact row. Our own math is shown with its inputs.
5. **Reader blocks:** only those the layer plan lists, using the ```reader fence, holding only what differs for that reader.
6. **Forms:** build each section in the form the layer plan names: a table, numbered steps, a ```figure block, a ```tool block, or prose. Use labeled scan lines (**By the numbers**, **What changes for you**, **Watch out**) where the layer plan asks for them.
7. **Ad breaks and links:** put an `<!-- ad-break -->` line exactly where the layer plan marks one, and place the internal links where it says.
8. **FAQ:** only questions the page hasn't already answered, each answered in two or three sentences. If every likely question is already answered above, skip the FAQ.
9. **Leave to siblings:** where the coverage map sends a question to another page, give one sentence and a link, not a summary.
10. **Next step:** end with the layer plan's next step: one short "What to do next" section, then the related guides.

Page-type shapes are in `references/page-types.md`. If you're writing a pillar section, also read `references/pillars.md`.

## Frontmatter
Use the frontmatter fields from the packet (`title`, `mode`, `dek`, `meta`, `primary_query`, `topic`, `type`, `updated`, `queue_id`, `sources`, `images`). `sources` lists every source_url you linked. Don't invent fields.

## Finish
Write the whole page in one pass and save it with a single Write call. Before saving, walk the coverage map in your head: every sub-question answered, every reader block present, every sibling link placed, every number a fact-row value or arithmetic on fact-row values. Don't run the page checks or reread the file: code runs `page_check.py` the moment you finish and the editor fixes what it flags. Rewriting your own draft costs time and rarely improves it as much as a fresh editor does. Then return the output object required by your agent file.

## If the packet is wrong
If a sub-question has no facts that answer it, or two fact rows conflict without a note telling you which to follow, don't guess and don't write around it. Write the page without that piece and report it in `blocked` in your output. A missing answer is fixable; a wrong one damages trust in every page.
