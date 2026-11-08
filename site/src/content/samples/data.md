---
title: "Sample Tracker (2026): a sample data page"
meta: "Sample content for the data page template: key finding, chart, sortable table with CSV, methodology and a citation box."
primary_query: sample tracker
topic: housing
school: cornell-university
page_type: data
updated: 2026-11-08
sample: true
data:
  updated: 2026-11-08
  unit: "$"
  license: "https://creativecommons.org/licenses/by/4.0/"
  chart:
    title: "Sample values by sample category"
    unit: "$"
    source: "Sample compilation (not real data)"
    rows:
      - { label: "Sample category A", value: 1450 }
      - { label: "Sample category B", value: 1210 }
      - { label: "Sample category C", value: 980 }
      - { label: "Sample category D", value: 760 }
      - { label: "Sample category E", value: 640 }
  columns: ["Sample item", "Value ($)", "Change (%)", "Count", "Checked"]
  rows:
    - ["Sample category A", 1450, 4.2, 12, "2026-11-08"]
    - ["Sample category B", 1210, 1.1, 30, "2026-11-08"]
    - ["Sample category C", 980, -0.8, 8, "2026-11-08"]
    - ["Sample category D", 760, 2.5, 21, "2026-11-08"]
    - ["Sample category E", 640, 0.0, 5, "2026-11-08"]
sources:
  - { url: "https://example.org/sample-source-1", title: "Sample source 1 (official rates page, not real)", accessed: 2026-11-08 }
  - { url: "https://example.org/sample-source-2", title: "Sample source 2 (official listing, not real)", accessed: 2026-11-08 }
---

This is sample content. The key finding of a data page is **one sentence with the headline number** and the comparison that makes it mean something, [cited](https://example.org/sample-source-1). All numbers on this page are invented to show the template.

## How we compiled this

Sample methodology. A real data page names every page read, the date it was read, how values were normalized (per month, per semester, per person), what was excluded and why, and when the next scheduled update is. Readers can download the CSV and check every row [against the source](https://example.org/sample-source-2).

## FAQ

### Is this real data?

No. The table and chart are sample values for the template.

### How often is a tracker updated?

On the schedule named in its methodology section; the byline shows the date of the last data update.
