# Review of the housing plan, 2026-11-08

Three independent reviewers read intel/off-campus-housing/plan.md against the brief (36,032 words), the reader map (18 readers), the spec and the pages already on the site, each through one lens: coverage, overlap, feasibility from the brief. A skeptic then tried to refute each finding of weight against the files. 20 sessions, 18 minutes. 6 findings survived (1 high, 5 medium); 12 were refuted and are listed at the end so nobody re-raises them.

The plan as it stands meets every acceptance item in the spec. The findings below are about getting more out of the same writing budget, and about two things the writer could not have done right from the plan as written (the inverted discount, the Good Cause arithmetic).

## Already fixed (facts, not plan choices)

- **The downtown discount was stated backwards.** Brief section 10.10 computes Collegetown per-bed asking prices at 25% to 39% above the same landlord's downtown prices, which makes downtown about 20% to 28% cheaper (studio 21%, 1BR 20%, 2BR 28%). The brief's one-page summary, its section 5.1, the reader map (three places) and two plan rows (the sophomore guide, the neighborhoods rewrite) said "downtown 25% to 39% cheaper". All six places now carry the right direction; the brief's change log records it.

## Findings for the approve-or-strike decision, with the recommended edit

1. **High. The most-asked question has no page.** The monthly cost of living off campus (demand row q-housing-0027) is in the question list of 8 of the 18 readers, more than any other question. The plan routes it to the money topic's cost-of-living page, but that page is rejected and unpublished, so the writer would link nothing. The brief has the inputs ready (per-bed rents 10.9, electricity 10.11, insurance and internet 3.7, TCAT 10.4, trash tags and parking 2.14, the $13,744 double and $1,145 break-even 10.3). Edit: add one spoke, what-a-month-off-campus-costs-cornell, owning q-housing-0027; point plan line 4 and the is-off-campus-cheaper notes at it.
2. **Medium. The international reader guide promises what the brief cannot deliver.** Its question is renting "without an SSN or US credit history", but the brief holds one Cornell line on that (no SSN needed) and three recorded gaps (guarantor and credit-check practice in Ithaca not found; no student voice on it). The brief does answer the rest for this reader (deposits and advances that are legal to ask for, checking a unit from abroad, the visa-status line, immigrant-tenant rights, break housing, first-year TCAT). Edit: keep the guide, retitled "Renting near Cornell as an international student: deposits, documents, timing", with one "Not confirmed" line on guarantor practice and the "no ssn" query dropped. Alternative: hold the row until a research pass on the official and voice lanes answers the guarantor question.
3. **Medium. Four start-here rows would create a second /start/ page for a reader who already has one.** The housing reader map used its own keys, so upper-year-renter, no-car, transfer and car-owner sit beside getting-around's off-campus, upper-year-no-car, transfer-spring and (for the car) off-campus, which open with the same person. Start pages are one per reader across topics (spec §4), and the pipeline now extends an existing page when the slug matches. Edit: re-key upper-year-renter to off-campus (taking the car-owner links; readers upper-year-renter and car-owner), no-car to upper-year-no-car, transfer to transfer-spring; drop the car-owner row; record the key mapping in readers.md. The planner prompt now shows existing start pages so the next topic reuses keys from the start.
4. **Medium. The breaking-a-lease spoke and the study-abroad reader guide are one page written twice.** Same readers (the guide's are a subset of the spoke's), same question, same answer order, same brief sections; both queries chase the abroad reader, so they would split one ranking. Edit: make breaking-a-lease-early-ithaca-cornell the away-semester reader guide (its reader blocks: abroad with housemates, leaving school for good, a Cornell license holder, a one-semester tenant) and strike cornell-study-abroad-off-campus-lease; the away-semester start path lists one page. Reader guides stay at 8.
5. **Medium. Three new pages rank the same beds against the $13,744 double.** The is-off-campus-cheaper spoke, the cheapest-ways reader guide and the cost-by-situation dataset all promise the same ranking and the same aid rules. Edit: keep the guide and the dataset; narrow the spoke to the yes/no comparison with the dataset's table embedded, and leave aid rules to the guide. (Two money pages touch the same number in a sentence each; link to the housing pages once they publish, no strike.)
6. **Medium. The Good Cause checker promises two outputs the brief cannot compute.** The 345%-of-fair-market-rent line needs HUD rents the brief marks "unverified, avoid printing", and the rent-increase line needs a CPI figure the brief does not have for 2025 or 2026. The exemption logic is fully sourced (certificate of occupancy year, owner-occupied small buildings, condos and co-ops, City of Ithaca or not, the 226-c notice days). Edit: keep the tool as an exemption screener: drop the rent and bedroom inputs, show the rent standard as a formula with "this year's CPI figure is not in our sources", show the 345% line only as the brief's 2023 1BR illustration ($1,276 x 3.45 = $4,402) with the note that almost no student unit crosses it.

Also from the feasibility pass, folded into the edits: the Collegetown-vs-downtown dataset's notes gave only the Collegetown premium while its question asks how much cheaper downtown is; the table now shows both directions.

## The plan after the edits

63 rows: 1 pillar, 21 spokes, 8 reader guides, 8 tools, 4 datasets, 17 start-here paths (7 extend getting-around's pages; 3 more after the re-keying), 4 rewrites. Every spec acceptance item still holds. Five queued rows that the edits replace (the study-abroad guide and the four re-keyed start rows, all still proposed and unwritten) are removed from the queue; the new and re-keyed rows queue as proposed, then the approval flips them with the rest.

Nothing in this review changes a published page.

## Refuted (checked and dropped)

- Renters-insurance spoke too thin: the brief gives a sourced $5 to $27 range and marks the question a win over Cornell's page; thinness is an edit-time call.
- Parent and student-family guides only half-answerable: the plan rows already name the gaps and the open questions list them.
- Shared start pages cannot carry housing / accessibility facts homeless: handled by the extend-in-place step; the accessibility facts live on linked getting-around pages and in the neighborhoods rewrite.
- Lead-times dataset duplicates the when-to-sign spoke; the timeline tool repeats the fee calculator: by design (every dataset pairs with a spoke; the tool outputs differ).
- Two datasets from the same 38 rows with mixed year labels: three scopes, three labels; reuse is a merge option, not a defect.
- Summer-housing spoke collides with the summer-sublet rewrite: the plan splits them by side (subtenant vs subletter).
- Rent-and-commute calculator infeasible: the row promises no bus times; the brief carries the rent, fare and electricity inputs with their caveats.
- When-to-sign timeline lacks 2027 dates: the exact-date promises hold for 2027-28; month-named steps are labelled as 2026 dates in the reader map.
- Move-in checklist's non-City branches thin: six of eight outputs apply at any address; the brief says which stop at the city line.
- Datasets count price rows, not listings: "from N listings" is the spec's own template; every row and percent was fact-checked.
