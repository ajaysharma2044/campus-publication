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

