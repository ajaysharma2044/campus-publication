# To read: Ajay's spot check (docs/v3/spec.md, step 8)

Every newly published page lands here with a one-line summary. Ajay reads all of the first topic, then 1 in 5, and marks each one.

## How to mark a page

Each entry is three lines. Write your mark on the `Ajay:` line and leave the other two alone:

- `Ajay: 👍` means the page is good. The learn step Ajay runs copies it to `docs/v3/best/` with a two-line note on why.
- `Ajay: <one line>` means something is wrong or weak ("the rent table is 2024 numbers", "reads like a memo after the reader blocks"). The page goes to `docs/v3/worst/` with that note, and the note becomes a style-guide, exemplar or brief edit. Notes never become code rules.
- An empty `Ajay:` line means not read yet.

Entry shape (`scripts/v3/run.sh` appends one per newly published page after each publish step; `worker/.venv/bin/python scripts/v2/render_site.py --to-read` rebuilds the whole list from the published queue rows, newest first, articles, tools and datasets alike, and keeps every mark already written for a page path):

```
- <published date> | <title> | <site path> | <kind> | <topic dir> (<queue id>)
  Summary: <the page's one-line meta>
  Ajay: <👍 or a one-line note>
```

`kind` is pillar, spoke, reader_guide or rewrite for v3 articles, tool or dataset for those pages, and `v2` for pages not yet rewritten. A rewrite keeps its path, so a mark written for the old page stays on the entry until you change it. Nothing below the entries is read by the scripts; keep general remarks in `reports/lessons.md`.

## Entries

- 2026-11-08 | Do I need a car at Cornell? Quiz with 2026-27 costs | /tools/do-i-need-a-car-at-cornell-quiz/ | tool | getting-around
  Summary: Enter your year, where you live, trips home, errands and license: get no car, Carshare, a B permit or a resident permit, with yearly costs.
  Ajay: 

- 2026-11-08 | Cornell bus home cost calculator: C2C vs OurBus, FlixBus | /tools/cornell-bus-home-cost-calculator/ | tool | getting-around
  Summary: Enter round trips a year, NetID or public fare, Thanksgiving and bags; get your year's bus cost home on C2C, OurBus, FlixBus and Greyhound, 2026 fares.
  Ajay: 

- 2026-11-08 | OmniRide break-even calculator: $200 pass vs $1.50 fares | /tools/omniride-break-even-calculator/ | tool | getting-around
  Summary: Enter your Cornell status, paid daytime TCAT rides a week and weeks of riding; get pass or pay-as-you-go, each yearly cost and the 134-ride break-even.
  Ajay: 

- 2026-11-08 | Ithaca Carshare calculator: Just In Case or It's My Car | /tools/ithaca-carshare-plan-calculator/ | tool | getting-around
  Summary: Enter hours, miles and vehicle to get the yearly cost of each Ithaca Carshare student plan with tax, the break-even and whether you qualify.
  Ajay: 

- 2026-11-08 | ITH or SYR trip cost calculator: parking, bus and airfare | /tools/ith-or-syr-trip-cost-calculator/ | tool | getting-around
  Summary: Enter days away, how you get to the airport and both airfares. Get the total trip cost from Ithaca (ITH) and Syracuse (SYR) and which is cheaper.
  Ajay: 

- 2026-11-08 | Cornell break travel and parking dates, 2026-27, by term | /tools/cornell-break-travel-timeline-2026-27/ | tool | getting-around
  Summary: Pick your start term, whether you have a car and which breaks you stay for; get every 2026-27 Cornell travel, parking and housing deadline, dated.
  Ajay: 

- 2026-11-08 | Before-break checklist: Cornell travel, car, housing | /tools/before-break-travel-checklist/ | tool | getting-around
  Summary: Pick your break, bus, plane or car, where your car is and whether you stay. Get a dated to-do list: C2C links, deadlines, parking, mail, storage.
  Ajay: 

- 2026-11-08 | Ithaca to NYC bus fares, Nov 8 2026: 6 carriers plus C2C | /datasets/ithaca-nyc-bus-fares-nov-2026/ | dataset | getting-around
  Summary: Ithaca to NYC bus fares by carrier: floor, average and departures for 6 carriers (Wanderu, Nov 8 2026) plus Cornell C2C's three fare tiers.
  Ajay: 

- 2026-11-08 | Thanksgiving bus fare premium from Ithaca, 2026 | /datasets/thanksgiving-bus-fare-premium-ithaca-2026/ | dataset | getting-around
  Summary: Lowest advertised Ithaca bus fares for 51 priced dates on 3 routes, read Nov 8, 2026: Thanksgiving week ran 27.9% to 37.9% higher, mean +33.4%.
  Ajay: 

- 2026-11-08 | A year of getting around Cornell, 2026-27: 4 profiles | /datasets/cost-of-getting-around-cornell-2026-27/ | dataset | getting-around
  Summary: What a year of getting around Cornell costs in 2026-27: four profiles from $264 to $948, built from 18 posted and sampled prices read Nov 8, 2026.
  Ajay: 

- 2026-11-08 | Bus fares from Ithaca by route, Nov 2026: 9 routes | /datasets/ithaca-bus-fares-by-route-nov-2026/ | dataset | getting-around
  Summary: Bus fares from Ithaca to 9 places, SYR airport to Toronto: low, range, time and cost per mile, from 88 fare readings taken Nov 8, 2026.
  Ajay: 

- 2026-11-08 | Cornell to Ithaca airport: TCAT 32 and 72, taxis, parking | /getting-around/cornell-to-ithaca-airport-tcat-taxi-parking/ | spoke | getting-around
  Summary: TCAT Route 32 (weekdays) and 72 (weekends) link ITH and the Commons for $1.50. No bus meets dawn flights; prebook a taxi. Parking is $40 a week.
  Ajay: 

- 2026-11-08 | Cornell grad students: free TCAT, parking and what you pay | /getting-around/getting-around-ithaca-cornell-grad-students/ | reader_guide | getting-around
  Summary: PhD students and assistants ride TCAT free; a full assistantship gets a free A or E permit. Others pay $200 for OmniRide or $359.77 to park.
  Ajay: 

- 2026-11-08 | Cornell C2C bus: who can ride, fares and how to book | /getting-around/cornell-c2c-bus-booking-fares-rules/ | spoke | getting-around
  Summary: Anyone can ride Cornell's C2C bus to NYC: $93.50 one way with a NetID, $101 for the public. Since Nov 4, 2026 every rider needs a new account.
  Ajay: 

- 2026-11-08 | ITH, SYR or ELM: which airport to fly into for Cornell | /getting-around/ith-syr-or-elm-which-airport-for-cornell/ | spoke | getting-around
  Summary: Fly ITH if JFK or Dulles connections suit you; pick Syracuse for its 27 nonstop destinations and a backup. Elmira has no confirmed bus to Ithaca.
  Ajay: 

- 2026-11-08 | Syracuse airport to Cornell: OurBus, car service, driving | /getting-around/syracuse-airport-to-cornell-ourbus-car-service/ | spoke | getting-around
  Summary: OurBus runs from Syracuse airport to Cornell six days a week for $46.70 to $62.10, about 1.5 hours. Or book Big D's car service or drive 50 to 65 miles.
  Ajay: 

- 2026-11-08 | Ithaca to JFK, LaGuardia or Newark airport without a car | /getting-around/ithaca-to-jfk-lga-newark-airport-bus/ | spoke | getting-around
  Summary: Only Newark Airport has a direct bus from Cornell (OurBus). For JFK or LaGuardia, bus to Manhattan and transfer, or fly Delta from Ithaca to JFK.
  Ajay: 

- 2026-11-08 | Cornell to Boston, Philadelphia, DC or Toronto by bus | /getting-around/ithaca-bus-to-boston-philadelphia-dc-toronto/ | spoke | getting-around
  Summary: FlixBus runs direct from Cornell to Boston ($44 to $88), Philadelphia (from $41) and DC (from $49); Toronto, $43 to $55. C2C stops at NYC.
  Ajay: 

- 2026-11-08 | Cornell student parking permits: cost, rules, who qualifies | /getting-around/cornell-student-parking-permit-cost-rules/ | spoke | getting-around
  Summary: Cornell resident permits cost $752.98 a year, commuter $359.77. First-years are discouraged from bringing a car but not banned; sales open Aug 4 at 9 a.m.
  Ajay: 

- 2026-11-08 | Cornell and Ithaca winter parking: odd/even, bays, breaks | /getting-around/ithaca-winter-parking-rules-cornell-odd-even/ | spoke | getting-around
  Summary: Dec 1 to Apr 1, park overnight on campus in nine listed areas; Ithaca's odd/even rule runs Nov 1 to Apr 1. Never leave a car on a street over break.
  Ajay: 

- 2026-11-08 | Cornell Thanksgiving travel: when to book and what it costs | /getting-around/cornell-thanksgiving-break-bus-tickets-when-to-book/ | spoke | getting-around
  Summary: Book by mid-November: Cornell's break runs Nov 25 to 29, 2026, Wednesday is the peak day, and Thanksgiving-week bus floors ran about 33% higher.
  Ajay: 

- 2026-11-08 | Staying in Ithaca over Cornell breaks: housing, food, rides | /getting-around/staying-in-ithaca-over-cornell-breaks/ | spoke | getting-around
  Summary: Yes: Cornell winter break housing is $125 a week or $500, apply Oct 1 to Dec 1. Halls close Dec 20, meals stop, and TCAT skips Thanksgiving and Christmas.
  Ajay: 

- 2026-11-08 | Getting home for Cornell winter break, 2026-27 | /getting-around/cornell-winter-break-travel-home-2026/ | spoke | getting-around
  Summary: Cornell dorms close Dec 20, 2026 at 2 p.m. Book the last day of finals early, ride C2C by Dec 23 on its 2026 link, and return from Jan 19.
  Ajay: 

- 2026-11-08 | Ithaca Carshare for Cornell students: plans, cost, rules | /getting-around/ithaca-carshare-cornell-students-cost/ | spoke | getting-around
  Summary: No Zipcar in Ithaca. Ithaca Carshare student plans cost $30 or $310 a year plus $6 to $9 an hour; under about 93 hours a year, pick Just In Case.
  Ajay: 

- 2026-11-08 | Uber, Lyft or taxi in Ithaca: what works and when | /getting-around/uber-lyft-taxi-ithaca-cornell/ | spoke | getting-around
  Summary: Uber and Lyft run in Ithaca but thin out outside downtown and late at night. Prebook a local cab for flights; the free Blue Light bus runs to 2:30 a.m.
  Ajay: 

- 2026-11-08 | Cornell move-out: storage, shipping and loading zones | /getting-around/cornell-move-out-storage-shipping-options/ | spoke | getting-around
  Summary: Big Red Shipping and Storage charges $39 to $49 a box for the summer with free room pickup. Book by early April; clear out by the 2 p.m. closing.
  Ajay: 

- 2026-11-08 | Where intercity buses stop in Ithaca and at Cornell | /getting-around/ithaca-intercity-bus-stops-cornell-downtown/ | spoke | getting-around
  Summary: OurBus moves downtown to 235 S. Cayuga St on Nov 9, 2026. Greyhound and FlixBus list 131 E Green St; campus stops are on Jessup Rd and West Ave.
  Ajay: 

- 2026-11-08 | Getting around Ithaca: start here as a first-year | /start/first-year/ | start_here | getting-around
  Summary: For Cornell first-years on campus without a car: read these in order and you will have your bus home booked, TCAT sorted and the car question settled.
  Ajay: 

- 2026-11-08 | Getting around Ithaca: start here as a transfer | /start/transfer-spring/ | start_here | getting-around
  Summary: For Cornell transfers and January starters: which transit guides to read first, when your free TCAT ends, and how winter parking rules change your plan.
  Ajay: 

- 2026-11-08 | Getting around Ithaca: start here without a car | /start/upper-year-no-car/ | start_here | getting-around
  Summary: For Cornell sophomores, juniors and seniors without a car: the order to read our guides to decide on OmniRide, Carshare, bikeshare and the bus home.
  Ajay: 

- 2026-11-08 | Getting around Ithaca: start here if you have a car | /start/car-on-campus/ | start_here | getting-around
  Summary: For Cornell students with a car in university housing: read in order to settle the permit, winter parking, storms and whether the car is worth it.
  Ajay: 

- 2026-11-08 | Getting around Ithaca: start here if you live off campus | /start/off-campus/ | start_here | getting-around
  Summary: For Cornell students renting in Collegetown, downtown, Fall Creek or West Hill: which guides to read to choose a commute and where to park.
  Ajay: 

- 2026-11-08 | Getting around Ithaca: start here as a grad student | /start/grad-student/ | start_here | getting-around
  Summary: For Cornell grad and professional students: the guides to read, in order, to decide on TCAT, a parking permit, Carshare or a car, and C2C for work trips.
  Ajay: 

- 2026-11-08 | Getting to Cornell from abroad: start here | /start/international/ | start_here | getting-around
  Summary: For international students flying in: the order to read our guides on airports, the NYC bus and breaks, ending with a route and a plan for each break.
  Ajay: 

- 2026-11-08 | Getting around Ithaca: start here if you fly home | /start/far-from-home/ | start_here | getting-around
  Summary: For Cornell students who fly home for breaks: the guides to read, in order, to pick ITH, SYR or another airport and book the ride to it.
  Ajay: 

- 2026-11-08 | Getting around Ithaca: start here if home is not NYC | /start/beyond-nyc/ | start_here | getting-around
  Summary: For Cornell students whose home is Boston, Philadelphia, New Jersey, DC or Toronto: the guides to read, in order, to pick a bus route, a stop and a date.
  Ajay: 

- 2026-11-08 | Getting around Ithaca: start here on a tight budget | /start/low-budget/ | start_here | getting-around
  Summary: For Cornell students who pay their own way: the guides to read, in order, to find the cheapest bus home and decide whether to stay over breaks.
  Ajay: 

- 2026-11-08 | Getting around Ithaca: start here if you stay over break | /start/staying-over-break/ | start_here | getting-around
  Summary: For Cornell students staying in Ithaca over Thanksgiving or winter break: the guides to read, in order, for break housing, groceries, rides and parking.
  Ajay: 

- 2026-11-08 | Getting around Ithaca: start here as a cyclist | /start/cyclist/ | start_here | getting-around
  Summary: For Cornell students who bike, ride an e-bike or scooter: read our guides in this order and settle your lock, winter plan, Bikeshare use and bus rack.
  Ajay: 

- 2026-11-08 | Getting around Ithaca: start here for accessibility | /start/accessibility/ | start_here | getting-around
  Summary: For Cornell students with a disability: read in order to settle an accessible parking permit, wheelchair space on C2C, TCAT fares and move-in.
  Ajay: 

- 2026-11-08 | Getting around Ithaca: start here as a parent or visitor | /start/parent/ | start_here | getting-around
  Summary: For parents, families and visiting alumni coming to Cornell: the guides to read, in order, to pick an airport, a ride or a car, and where to park.
  Ajay: 

- 2026-11-08 | Getting around Ithaca: start here if you stay for summer | /start/summer-in-ithaca/ | start_here | getting-around
  Summary: For Cornell students in Ithaca from May to August: the order to read our guides on move-out, TCAT, bikeshare, Carshare and when permits and passes end.
  Ajay: 

- 2026-11-08 | Ithaca Bikeshare cost for Cornell students, 2026 prices | /getting-around/ithaca-bikeshare-cost-cornell-students/ | spoke | getting-around
  Summary: Ithaca Bikeshare costs $1.50 to start plus $0.25 a minute, $25 a day or $60 a month. Cornell students get no discount; a 20-minute ride is $6.50.
  Ajay: 

- 2026-11-08 | Biking at Cornell: e-bike rules, scooters and theft | /getting-around/cornell-bike-ebike-scooter-rules-theft/ | spoke | getting-around
  Summary: Cornell e-bikes: 750 W max, 36 in wide. Scooters: under 100 lb, 20 mph. Lock to racks only, never charge in rooms; 51 thefts hit campus in fall 2024.
  Ajay: 

- 2026-11-08 | Cornell move-in day parking: where to unload and park | /getting-around/cornell-move-in-day-parking-unloading/ | spoke | getting-around
  Summary: Print the Move-In Ticket after Aug 1, unload at your building, then move to the 3-hour lot it names. Uber and taxi arrivals go to A Lot.
  Ajay: 

- 2026-11-08 | Biking in Ithaca in winter: what it's like at Cornell | /getting-around/biking-in-ithaca-winter-cornell/ | rewrite | getting-around
  Summary: Yes, with good brakes, warm layers and a bike you don't mind salting. Cornell has no winter cycling guidance; free TCAT bike racks get you up the hills.
  Ajay: 

- 2026-11-08 | Is TCAT free for Cornell students? Hours, routes, passes | /getting-around/tcat-free-for-cornell-students-hours-routes/ | spoke | getting-around
  Summary: First-years and PhD students ride TCAT free all day. Other Cornell students ride free after 6 p.m. weekdays and weekends, or pay $1.50 a ride.
  Ajay: 

- 2026-11-08 | Parking in Collegetown and downtown Ithaca: 2026 rates | /getting-around/parking-collegetown-downtown-ithaca-garages-permits/ | spoke | getting-around
  Summary: City garages are $2.25 an hour with a $12 or $18 daily cap, streets $2.50, Saturdays now paid, Seneca garage closed; a city resident permit is $45.
  Ajay: 

- 2026-11-08 | Winter storms and Cornell travel: driving, buses, flights | /getting-around/cornell-winter-storms-travel-driving-ithaca/ | spoke | getting-around
  Summary: Storms have hit Cornell's Thanksgiving and January returns. Travel a day early, watch for added earlier buses, check 511NY and park in winter lots.
  Ajay: 

- 2026-11-08 | Off-campus at Cornell: commute, buses and parking by area | /getting-around/getting-around-ithaca-off-campus-renters/ | reader_guide | getting-around
  Summary: Walk 15 to 20 minutes from Collegetown, bus from downtown, plan around the suspended West Hill routes, and park on a $359.77 B permit or $45 city permit.
  Ajay: 

- 2026-11-08 | Ithaca rent + commute calculator for Cornell students | /tools/ithaca-rent-commute-calculator/ | tool | housing
  Summary: Pick a neighborhood, unit size, roommates, lease, bus pass and car; get rent, power, bus and parking per month and the gap to Cornell's $13,744 double.
  Ajay: 

- 2026-11-08 | When to sign a lease at Cornell: timeline by start term | /tools/when-to-sign-lease-timeline-cornell/ | tool | housing
  Summary: Enter your year, start term, transfer and exemption status and where you want to live; get the dated months to look, sign and cancel a backup room.
  Ajay: 

- 2026-11-08 | Off-campus move-in checklist: Cornell renters, by situation | /tools/off-campus-move-in-checklist-cornell/ | tool | housing
  Summary: Enter your address type, move-in date, bills, car and household. Get a dated to-do list: inspection, NYSEG, trash tags, insurance, permits, occupants.
  Ajay: 

- 2026-11-08 | Can I live off campus at Cornell? 2026-27 eligibility quiz | /tools/can-i-live-off-campus-cornell-quiz/ | tool | housing
  Summary: Enter your year, transfer status, age, family and service: see if you may sign a lease, which Cornell exemption to file, and the cost of signing early.
  Ajay: 

- 2026-11-08 | Good Cause Eviction checker: Ithaca coverage and notice | /tools/ithaca-good-cause-coverage-checker/ | tool | housing
  Summary: Answer eight questions about your Ithaca rental: see if Good Cause Eviction covers it, which exemption applies, and the 30, 60 or 90 days' notice owed.
  Ajay: 

- 2026-11-08 | Is this lease fee legal? Ithaca deposit and fee checker | /tools/ithaca-lease-fee-deposit-checker/ | tool | housing
  Summary: Enter your rent, deposit and each fee your Ithaca landlord asks for; see which are over New York caps, your deposit due date and the 2x penalty.
  Ajay: 

- 2026-11-08 | Ithaca sublet request: 10- and 30-day dates, what to send | /tools/ithaca-sublet-request-timeline/ | tool | housing
  Summary: Enter your building size, sublet start and mailing date; get the landlord's 10-day and 30-day deadlines, the consent-by-silence date and what to include.
  Ajay: 

- 2026-11-08 | Cornell housing cancellation fee calculator, 2026-28 | /tools/cornell-housing-license-cancellation-fee-calculator/ | tool | housing
  Summary: Enter class year, reason, cancel date and room rate; get your Cornell housing license cancellation fee, penalty-free deadline or a no-cancel answer.
  Ajay: 

- 2026-11-08 | Collegetown rent per bed, 2027-28, from 38 listings | /datasets/collegetown-rent-per-bed-2027-28/ | dataset | housing
  Summary: Per-bed asking rent in Collegetown for 2027-28 by unit size, studio to 10BR: median, mean and range from 38 Ithaca Renting rows read Nov 8, 2026.
  Ajay: 

- 2026-11-08 | Collegetown vs downtown rent per bed, Nov 2026, 58 listings | /datasets/collegetown-vs-downtown-rent-per-bed-2026/ | dataset | housing
  Summary: Ithaca Renting per-bed asking rents, downtown vs Collegetown: downtown runs about 20% to 28% cheaper for studios to 2BRs. 58 listings read Nov 8, 2026.
  Ajay: 

- 2026-11-08 | Cost of a year of housing at Cornell, 28 options, Nov 2026 | /datasets/ithaca-housing-cost-by-living-situation-2026-27/ | dataset | housing
  Summary: Per-person cost of a year of housing at Cornell, 28 ways to live: $5,530 co-op triple to $28,104 Collegetown 1BR average. 79 prices, read Nov 8, 2026.
  Ajay: 

- 2026-11-08 | How early Collegetown leases are signed, 2017-2025: 9 cases | /datasets/collegetown-lease-signing-lead-times-2017-2025/ | dataset | housing
  Summary: Collegetown leases signed 6 to 16 months before an August move-in, mostly 10 to 11: 9 dated cases from 6 Cornell Daily Sun stories, 2017 to 2025.
  Ajay: 

- 2026-11-08 | Off-campus housing at Cornell: the 2026-27 guide | /housing/cornell-off-campus-housing-guide/ | pillar | housing
  Summary: Juniors, seniors and grads rent off campus. Collegetown leases go 8 to 16 months early; Cornell's $13,744 double equals $1,145 a month over 12 months.
  Ajay: 

- 2026-11-08 | When to sign a Collegetown lease, and when waiting is fine | /housing/when-to-sign-collegetown-lease-cornell/ | spoke | housing
  Summary: Popular Collegetown units sign 8 to 16 months ahead, mostly in September or October. Downtown, Fall Creek, Lansing and grad housing can wait.
  Ajay: 

- 2026-11-08 | Reading an Ithaca lease before you sign: what to check | /housing/how-to-read-ithaca-lease-before-signing/ | spoke | housing
  Summary: Check page one for a 120-day waiver, a deposit over one month's rent, banned fees and joint liability. Free lease advice before you sign: 607-301-1560.
  Ajay: 

- 2026-11-08 | When an Ithaca landlord won't fix heat, mold or bed bugs | /housing/ithaca-landlord-wont-fix-heat-mold-bed-bugs/ | spoke | housing
  Summary: Put it in writing, call code enforcement, then get free advice. Ithaca heat must hit 68F by day from Sept 15 to May 31; don't withhold rent first.
  Ajay: 

- 2026-11-08 | Breaking an Ithaca lease to study abroad or leave Cornell | /housing/breaking-a-lease-early-ithaca-cornell/ | reader_guide | housing
  Summary: Ask the landlord for a written release, then sublet or assign. If you just leave, the landlord must try to re-rent, but housemates still owe your share.
  Ajay: 

- 2026-11-08 | Finding off-campus roommates at Cornell: joint liability | /housing/cornell-off-campus-roommates-joint-liability/ | spoke | housing
  Summary: Find Cornell housemates on the Off-Campus Living list or the marketplace, then plan for a dropout: each co-tenant owes the full rent.
  Ajay: 

- 2026-11-08 | Cornell sophomores: how to get a good junior-year lease | /housing/off-campus-housing-cornell-sophomores/ | reader_guide | housing
  Summary: Pick your group and area by October of sophomore year, sign by Jan 31 to drop a backup Cornell room for $50, and refuse the fees New York bans.
  Ajay: 

- 2026-11-08 | Already renting near Cornell: renewals, repairs and deposits | /housing/off-campus-housing-cornell-juniors-seniors-renting/ | reader_guide | housing
  Summary: In the City of Ithaca, renewal needs 120 days' notice unless you waived it, heat is owed Sept 15 to May 31, and your deposit is due back within 14 days.
  Ajay: 

- 2026-11-08 | Renting near Cornell as an international student | /housing/off-campus-housing-cornell-international-students/ | reader_guide | housing
  Summary: No SSN needed. New York caps deposit plus any prepaid rent at one month. Check the unit's certificate and Cornell safety tool before you wire money.
  Ajay: 

- 2026-11-08 | Where Cornell grad students live in Ithaca, and when to look | /housing/off-campus-housing-cornell-grad-students/ | reader_guide | housing
  Summary: Most Cornell grads rent off campus. Start in March or April for August; Fall Creek, downtown and Hasbrouck ($1,415 a 1BR, utilities in) beat Collegetown.
  Ajay: 

- 2026-11-08 | Cornell family housing in Ithaca: costs and options | /housing/cornell-student-family-housing-ithaca/ | reader_guide | housing
  Summary: Hasbrouck family units run $1,475 to $1,530 a month for 2026-27; a private Ithaca 2BR averages $2,459. Where Cornell families live and what it costs.
  Ajay: 

- 2026-11-08 | The cheapest ways to live off campus at Cornell | /housing/cheapest-off-campus-housing-cornell/ | reader_guide | housing
  Summary: Cornell's cheapest options: co-op triples, a $620 Hasbrouck single, and $695 to $800 beds in big shares. Aid covers rent, not deposits or summer.
  Ajay: 

- 2026-11-08 | Ithaca's 120-day lease renewal rule and the waiver | /housing/ithaca-120-day-lease-renewal-notice-rule/ | spoke | housing
  Summary: In the City of Ithaca a landlord must give tenants 120 days' written notice before renewing, showing or re-letting, unless you initial a page-one waiver.
  Ajay: 

- 2026-11-08 | Ithaca Good Cause Eviction: renewals and rent increases | /housing/ithaca-good-cause-eviction-rent-increase-students/ | spoke | housing
  Summary: Ithaca's Good Cause law covers private student rentals: a right to renew, and raises above 10% or 5% plus CPI presumed unreasonable. Who is exempt.
  Ajay: 

- 2026-11-08 | Ithaca security deposit rules: the cap, 14 days, banned fees | /housing/ithaca-security-deposit-rules-tenants/ | spoke | housing
  Summary: New York caps an Ithaca deposit at one month's rent and bans application and cleaning fees; a deposit not returned itemized in 14 days is forfeit.
  Ajay: 

- 2026-11-08 | Is off-campus housing cheaper than a Cornell dorm? | /housing/is-off-campus-cheaper-than-cornell-dorm/ | spoke | housing
  Summary: Only big shares beat Cornell's $13,744 double: a Collegetown 6BR bed at $800 a month does; a 4BR share or a 1BR alone does not.
  Ajay: 

- 2026-11-08 | Who can live off campus at Cornell: the rule and exemptions | /housing/cornell-residential-requirement-exemptions-live-off-campus/ | spoke | housing
  Summary: Sophomores must live in Cornell or affiliated housing unless exempt: 21+, married, dependents, veterans, commuters. Sign first and you're billed anyway.
  Ajay: 

- 2026-11-08 | Cornell co-ops and Greek houses: cost and how to get in | /housing/cornell-co-ops-greek-houses-cost-how-to-join/ | spoke | housing
  Summary: A Cornell co-op double costs $6,974 to $9,962 for 2026-27 vs $13,744 in a dorm. Co-ops pick in November and February; Greek houses need membership.
  Ajay: 

- 2026-11-08 | Ithaca renter rules: trash tags, snow, noise and parties | /housing/ithaca-trash-tags-snow-noise-rules-renters/ | spoke | housing
  Summary: Ithaca trash needs a $6 tag per bag in 2026, out no more than 24 hours early. Clear sidewalks within 24 hours; quiet hours are 10 p.m. to 7:30 a.m.
  Ajay: 

- 2026-11-08 | Eviction or a vacate order in Ithaca: what happens next | /housing/ithaca-eviction-vacate-order-what-to-do/ | spoke | housing
  Summary: Ithaca evictions run through City Court: a 14-day demand, a hearing, 14 days' notice. If the City orders a building vacated, landlords owe double rent.
  Ajay: 

- 2026-11-08 | Short-term furnished housing near Cornell for scholars | /housing/visiting-scholar-postdoc-furnished-housing-ithaca/ | spoke | housing
  Summary: Cornell guarantees visiting scholars no housing. Try International Scholar House (month-to-month), Hasbrouck ($1,490 furnished 1BR) or a semester sublet.
  Ajay: 

- 2026-11-08 | Where to find off-campus housing listings at Cornell | /housing/cornell-off-campus-housing-listings-where-to-find/ | spoke | housing
  Summary: Start with Cornell's College Pads marketplace and the Off-Campus Living email list, then Ithaca Renting's per-bed price list.
  Ajay: 

- 2026-11-08 | Summer housing in Ithaca: sublets and lease gaps | /housing/summer-sublet-ithaca-finding-housing-may-august/ | spoke | housing
  Summary: Cornell dorms closed May 17, 2026 and most Ithaca leases end July 31. Get a written sublease and landlord consent, and plan storage for the gap.
  Ajay: 

- 2026-11-08 | Cornell off-campus housing for parents: cost, lease, safety | /housing/cornell-off-campus-housing-for-parents/ | reader_guide | housing
  Summary: Off campus beats the $13,744 Cornell double only in big shared units. Parents: wait until junior year, cap the deposit at a month, check the COC.
  Ajay: 

- 2026-11-08 | Collegetown vs Fall Creek vs downtown Ithaca: where to live | /housing/collegetown-vs-fall-creek-vs-downtown-ithaca-where-to-live/ | rewrite | housing
  Summary: Collegetown is the walk-to-class choice and signs a year early; downtown beds cost 20% to 28% less at one landlord; Fall Creek is the quiet grad pick.
  Ajay: 

- 2026-11-08 | How to sublet an Ithaca apartment and get landlord consent | /housing/cornell-summer-sublet-how-to-sublet-apartment-ithaca/ | rewrite | housing
  Summary: In a New York building of 4+ units your landlord can't unreasonably refuse a sublet: mail the request certified; silence after 30 days is consent.
  Ajay: 

- 2026-11-08 | Cornell transfer housing: on campus, exemptions, leases | /housing/cornell-transfer-housing/ | rewrite | housing
  Summary: Most Cornell transfers live on campus one year ($13,744 for a double in 2026-27). Junior and senior transfers are exempt but must reapply every year.
  Ajay: 

- 2026-11-08 | Moving out of an Ithaca apartment: inspection to deposit | /housing/moving-out-ithaca-apartment-deposit-back/ | spoke | housing
  Summary: Ask for the move-out inspection 1 to 2 weeks before your lease ends, photograph every room, and expect the deposit or a list of charges within 14 days.
  Ajay: 

- 2026-11-08 | Collegetown rent in 2026: one-bedroom and per-bed prices | /housing/collegetown-rent-prices-per-bed-one-bedroom/ | spoke | housing
  Summary: A Collegetown 1BR asks about $2,025 to $2,342 a month in Nov 2026; a bed in a 6BR about $800. What each price includes, by unit size and source.
  Ajay: 

- 2026-11-08 | Renters insurance off campus at Cornell: need and cost | /housing/cornell-off-campus-renters-insurance-cost/ | spoke | housing
  Summary: Cornell recommends but doesn't require renters insurance off campus. Ithaca quotes run $5 to $27 a month; your lease decides if you must buy it.
  Ajay: 

- 2026-11-08 | City of Ithaca or not: why your rental's address matters | /housing/city-of-ithaca-vs-town-lansing-cayuga-heights-renters/ | spoke | housing
  Summary: Ithaca's 120-day rule, Certificate of Compliance, safety tool, parking permits and trash tags stop at the city line. Here is what changes outside it.
  Ajay: 

- 2026-11-08 | Renting to Cornell students: an Ithaca landlord checklist | /housing/becoming-ithaca-landlord-student-rental-rules/ | spoke | housing
  Summary: City of Ithaca rentals need a Certificate of Compliance ($100 to $2,500), 120 days' renewal notice, a one-month deposit cap and a 14-day return.
  Ajay: 

- 2026-11-08 | Off-campus housing: start here as a sophomore | /start/sophomore/ | start_here | housing
  Summary: For Cornell sophomores planning a junior-year lease: the guides to read in order, so you know where, when, with whom and on what terms you will sign.
  Ajay: 

- 2026-11-08 | Off-campus housing: start here with a partner or children | /start/student-family/ | start_here | housing
  Summary: For Cornell students moving to Ithaca with a spouse, partner or children: the guides to read, in order, to choose Hasbrouck or a private rental.
  Ajay: 

- 2026-11-08 | Off-campus housing: start here if you'll be away a term | /start/away-semester/ | start_here | housing
  Summary: For Cornell students going abroad or away mid-lease: what to read, in order, to decide between a sublet, an early exit or a penalty-free cancellation.
  Ajay: 

- 2026-11-08 | Off-campus housing: start here with an exemption | /start/exempt-underclass/ | start_here | housing
  Summary: For Cornell first- and second-years who may qualify to live off campus: confirm the exemption, get approval, then know when and what to sign.
  Ajay: 

- 2026-11-08 | Off-campus housing: start here in a co-op or Greek house | /start/affiliated-housing/ | start_here | housing
  Summary: For Cornell students in, or seeking, a co-op or Greek house: what to read, in order, to get a room, meet Cornell's housing rules and plan junior year.
  Ajay: 

- 2026-11-08 | Off-campus housing: start here for a short stay | /start/short-stay/ | start_here | housing
  Summary: For visiting scholars, postdocs and one-semester students at Cornell: the guides to read to pick furnished housing, a sublet or a lease you can leave.
  Ajay: 

- 2026-11-08 | Off-campus housing: start here as an alum landlord | /start/alum-landlord/ | start_here | housing
  Summary: For Cornell alumni who own or may buy an Ithaca rental: the order to read our guides on City rules, Good Cause, deposits, renewal notices and rents.
  Ajay: 

- 2026-11-08 | Collegetown landlords: how to check one before you sign | /housing/ithaca-landlords-to-avoid-collegetown-reviews/ | rewrite | housing
  Summary: No current review list ranks Collegetown landlords. Call 607-274-6508 about the certificate, check the safety tool and ask past tenants before you sign.
  Ajay: 

- 2026-11-08 | What a month off campus costs at Cornell, all in | /housing/what-a-month-off-campus-costs-cornell/ | spoke | housing
  Summary: A shared Collegetown 4BR runs about $1,285 to $1,373 a person a month with power, internet and insurance; Cornell's double works out to $1,145.
  Ajay: 

- 2026-11-11 | Can I transfer to Cornell? Eligibility and college quiz | /tools/cornell-transfer-eligibility-quiz/ | tool | transfer
  Summary: Enter credits, semesters, college, major and GPA to see if you can apply as a Cornell transfer, your likely standing, closed majors and the housing rule.
  Ajay: 

- 2026-11-11 | Cornell transfer credit calculator: credits lost, semesters | /tools/cornell-transfer-credit-calculator/ | tool | transfer
  Summary: Enter credits, college, AP/IB and course load; see how many credits Cornell can accept, how many you lose and how many semesters you need.
  Ajay: 

- 2026-11-11 | Cornell transfer cost calculator: required year, 2026-27 | /tools/cornell-transfer-cost-calculator/ | tool | transfer
  Summary: Pick your Cornell college, residency, room, meal plan and health plan; see the required year's billed total, full cost and cost a month, 2026-27 prices.
  Ajay: 

- 2026-11-11 | Cornell transfer timeline: your dates, Nov 2026 to Dec 2027 | /tools/cornell-transfer-timeline/ | tool | transfer
  Summary: Pick your situation and Cornell college; get every dated step from now to December 2027: aid forms, March 15 and April 15, housing, bills, move-in.
  Ajay: 

- 2026-11-11 | Cornell transfer application checklist by college | /tools/cornell-transfer-application-checklist/ | tool | transfer
  Summary: Pick your Cornell college, major and situation. Get every transfer application piece, who completes it, and its deadline: March 15 or April 15, 2027.
  Ajay: 

- 2026-11-11 | Cornell transfer admissions, 2017 to 2026: 12 terms | /datasets/cornell-transfer-admissions-data-2017-2026/ | dataset | transfer
  Summary: Cornell transfer applicants, admits and enrollees for 12 entering terms, fall 2017 to fall 2026, each graded by source: 11.7% admitted in fall 2025.
  Ajay: 

- 2026-11-11 | Cornell transfer rules by college, 2026-27: 9 colleges | /datasets/cornell-transfer-rules-by-college-2026-27/ | dataset | transfer
  Summary: GPA figures, credit caps, time at Cornell, prerequisites and deadlines for transfers into 9 Cornell colleges, from college pages read Nov 11, 2026.
  Ajay: 

- 2026-11-11 | Cornell transfer year cost by room, 2026-27: 13 options | /datasets/cornell-transfer-year-cost-by-room-2026-27/ | dataset | transfer
  Summary: What Cornell's required transfer year costs in 13 rooms, 2026-27: halls $95,218 to $99,169 billed at endowed tuition; co-op doubles from $6,974.
  Ajay: 

- 2026-11-11 | Junior transfers to Cornell: start here | /start/transfer-junior/ | start_here | transfer
  Summary: For students entering Cornell as a junior: which college will take you, how many credits transfer, the deadlines, the cost and where you will live.
  Ajay: 

- 2026-11-11 | Community college transfers to Cornell: start here | /start/transfer-community-college/ | start_here | transfer
  Summary: For community college students eyeing Cornell: whether a pathway fits, which credits transfer, what aid covers and when to apply for fall 2027.
  Ajay: 

- 2026-11-11 | Cornell Transfer Option holders: start here | /start/transfer-option/ | start_here | transfer
  Summary: For students holding a Cornell Transfer Option: what to read, in order, from the year elsewhere to the March application, the decision and move-in.
  Ajay: 

- 2026-11-11 | Engineering and CS transfers to Cornell: start here | /start/transfer-engineering/ | start_here | transfer
  Summary: For students transferring into Cornell Engineering or CS: the required courses, which major to name, what credit counts, the deadlines and the cost.
  Ajay: 

- 2026-11-11 | New York residents transferring to Cornell: start here | /start/ny-resident/ | start_here | transfer
  Summary: For New York residents transferring to Cornell: which colleges charge contract tuition, which aid forms to file and where to apply for fall 2027.
  Ajay: 

- 2026-11-11 | Veterans and older transfers to Cornell: start here | /start/veteran-nontraditional/ | start_here | transfer
  Summary: For veterans and older students transferring to Cornell: which credits count, who writes your reference, GI Bill or aid, and where to live.
  Ajay: 

- 2026-11-11 | Switching colleges inside Cornell: start here | /start/internal-transfer/ | start_here | transfer
  Summary: For current Cornell students moving to another Cornell college: which internal transfer rules apply, your deadlines and which guide to read next.
  Ajay: 

