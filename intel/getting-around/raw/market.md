# Lane B: Market and data. Getting to Ithaca and getting around it

Checked date for all rows: 2026-11-07. Raw notes, appended as found. Paraphrased.

## 0. Method notes
- Corpus check: grep of corpus/ for TCAT, airport, parking-permit, C2C pages found almost nothing useful (only fcs.cornell.edu announcements 2018-2025 about parking/transit events, and fcs.cornell.edu/departments/transportation-delivery-services). tcatbus.com and flyithaca.com are NOT in the corpus; must be fetched live.
- Bash is disabled in this session; used Glob/Grep/Read/WebFetch/WebSearch only.

## 1. Cornell Campus-to-Campus (C2C) bus

| Fact | Value | Source URL | Applies to | Checked |
|---|---|---|---|---|
| Booking method | Online in a browser, no app; everyone needs a new account in the new system, even past riders; one reservation can cover several passengers; interactive seat selection | https://fcs.cornell.edu/departments/transportation-delivery-services/campus-campus-bus-service | page undated; new system launches 2026-11-04 | 2026-11-07 |
| Who gets discounts | Cornell students, faculty and staff sign in via Cornell single sign-on to get eligible discounts; public books at standard public fare | same | same | 2026-11-07 |
| Reservation links split | Trips departing Nov through Dec 23, 2026 use the "2026" link (including changes); trips on/after Jan 6, 2027 use the "2027" link | same | winter break 2026-27 | 2026-11-07 |
| Page says transition does not change schedules, rates, stop locations | stated | same | same | 2026-11-07 |
| Contact | 607-254-8747; c2cbus@cornell.edu; office 209 Solidago Rd (311 E Palm Rd), M-F 8:00-4:00 | same | page undated | 2026-11-07 |
| Business travel | can be charged to a department but not by procurement card | same | page undated | 2026-11-07 |
| Fares/schedule on this page | NOT on this page (links to separate rates/schedule pages) | same | | 2026-11-07 |

## 2. TCAT and airport pages: fetch failures
| Fact | Value | Source URL | Checked |
|---|---|---|---|
| tcatbus.com/learn/college-students/ | WebFetch returned HTTP 403 | https://www.tcatbus.com/learn/college-students/ | 2026-11-07 |
| flyithaca.com/ground/bus-service/ | WebFetch returned HTTP 404 | https://flyithaca.com/ground/bus-service/ | 2026-11-07 |
