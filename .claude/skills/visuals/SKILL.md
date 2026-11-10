---
name: visuals
description: How EduExplained pages get pictures and visuals - licensed photos (found and credited by code), charts and diagrams drawn from our own fact data, maps, and owner photos - plus the rules for relevance, alt text, captions and image size. Load for the layering agent, guide writer and batch writer.
user-invocable: false
---

# Visuals

Every page gets a lead image, and most get at least one more visual. Pictures make a page feel trustworthy and finished, keep people reading, and qualify it for image-heavy surfaces like Google Discover. But a wrong or unlicensed picture costs more than it adds, so every visual follows the rules below.

## The four sources, in order of preference
1. **Charts, diagrams and tables built from our fact data.** Rendered by code from fact rows, so they are always accurate, always ours, and the most citable thing on the page. Use them wherever numbers drive the answer.
2. **Owner photos.** Photos the site owns or has written permission for, dropped into `content/images/inbox/`. They replace any found photo for the same slot.
3. **Openly licensed photos, found by code.** The existing `scripts/v2/find_images.py` searches Wikimedia Commons and Openverse and accepts only licenses that allow commercial use with credit: CC0, public domain, CC BY and CC BY-SA. Anything non-commercial, no-derivatives or unclear is dropped. It records the author, source and license for the credit line.
4. **Maps** from OpenStreetMap data, credited as its license requires, for any page where location decides the answer (neighborhoods, bus stops, campus distances).

**Never:** use a photo just because it is online and credited (a credit is not permission); use stock-site or news photos; or use AI-generated images that look like photographs of real places, people or events. An AI-made illustration is acceptable only for an abstract idea (a concept diagram), clearly styled as an illustration.

## How each agent uses this
- **Layering agent:** in the layer plan's `images`, name the lead image subject as a specific, findable scene ("Collegetown apartment buildings, College Avenue, Ithaca"), not a vague one ("student housing"). Mark which sections get a chart (with its fact_ids) and which could use a photo. If a topic is unlikely to have licensed photos (a federal loan rule, a fee schedule), plan a chart or diagram as the lead visual instead.
- **Writers:** reference images only by the slots in the layer plan; code fills them. Write the alt text and caption for each slot.
- **Code:** runs `find_images.py` for each photo slot, uses an owner photo when one exists, renders charts from fact rows, and leaves a slot empty rather than placing an off-topic photo.

## Alt text and captions
- **Alt text** describes what the picture shows for someone who can't see it, in one sentence: "Four-story apartment buildings along College Avenue in Collegetown."
- **Captions** add information the picture alone doesn't give, then the credit: "Most Collegetown leases for 2027-28 sign by October. Photo: Author / Wikimedia Commons, CC BY-SA 4.0."

## Size and speed
The lead image is at least 1,200 pixels wide (large images qualify pages for Google Discover); body images are compressed (WebP, about 150 KB) so pages stay fast, because slow pages lose readers and ad revenue. Every image has fixed dimensions so the page doesn't jump as it loads.
