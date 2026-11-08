# Learn run template (docs/v3/spec.md, steps 9 and 10; runs only when Ajay starts scripts/v3/learn.sh)

Each run writes its own reports/learn-<date>.md from the template below;
the findings go back into the topic briefs (`intel/<topic>/brief.md`, section 11 change log) and the queue (`queue/queue.csv`:
rewrites, new spokes, new reader types). Before launch on the real domain only the speed and reader-question parts have data.

Owner access needed: Google Search Console (queries, impressions, clicks, positions) is tied to the owner's Google account, so the
export (or a read-only user for the service account) comes from Ajay; the step reads what is exported to `reports/search-console/`
(CSV, one file per week) and never logs in. The same goes for the contact-form inbox: paste or export the week's reader questions.

## Template (copy below, fill, keep the headings)

### Week of YYYY-MM-DD

**Search Console** (owner export; `reports/search-console/YYYY-MM-DD.csv`)
- Pages live: N. Impressions: N (last week N). Clicks: N (N). Average position: N.N (N.N).
- Top 10 queries by impressions, with position and the page that ranks:
  | query | impressions | clicks | position | page |
  |---|---|---|---|---|
- Queries we have no page for (impressions > 50, position > 10): list them; each becomes a queue row or a brief hole.
- The 5 weakest live pages (low clicks for their impressions, or position 8 to 20): path, impressions, clicks, position, what the #1 result has that we do not. These are the week's rewrites.

**AI citation check** (the same 10 questions every week, asked to a fresh ChatGPT, Claude and Google AI Overview session)
- Questions where our page is cited or paraphrased: N of 10 (last week N). List which, and the fact or table that was used.
- Questions answered wrongly for Cornell or Ithaca by the AI answer: list the error and the brief fact that corrects it. Each one is a spoke or dataset candidate.

**Reader questions** (contact form, corrections form, "No, I still need..." answers from the feedback box)
- Total: N. Grouped by topic and page.
- Questions no page answers: list; each becomes a queue row.
- "No, I still need..." texts by page: path, count of No, count of Yes, the recurring need in one line. A page under 60 percent Yes with 10 or more answers joins the rewrites.
- Corrections received and what was fixed (link the commit).

**Speed and cost** (from `build/runs/v2/*.log`)
- Articles published this week: N. Session-minutes per article: N (write+edit), N (check). Usage-limit pauses: N, totalling N minutes.
- Articles per hour of wall time while under the limit: N.

**Back into the briefs and the queue**
- Brief updates made (topic, section, what changed, source).
- Queue rows added: ids and one line each (rewrite | new spoke | new reader guide | new tool or dataset).
- New reader types found: name and which brief's readers.md gained them.

**For Ajay**
- Up to 3 decisions that need the owner (a topic order change, a tool worth building, a sponsor approach, an account or key).
