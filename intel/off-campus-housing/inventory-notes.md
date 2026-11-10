# Ithaca apartment inventory: how it was built

Built 2026-11-10 for the idea run (docs/v4/RUN-NOW.md, idea 10). File: inventory.csv, 413 buildings or houses, one row each.

## Sources
- A scout session listed 63 candidate sources (landlord and property-manager sites, listing services, city and county records) and checked each one's robots.txt, login and terms gates. Aggregators whose terms forbid automated access (Zillow, Apartments.com, Rent.com, Craigslist, RentCafe and the like) were not opened.
- 35 landlord and listing sources were read by one session each, as a prospective tenant would, at most 40 pages per source, recording only what a page states: address, building name, manager, units, unit sizes, prices as printed with their lease year, lease dates and term, what rent includes, and the page URLs. Nothing was inferred.
- Owner of record, property class and year built come from the Tompkins County 2026 final assessment rolls, the Tompkins County Open Data parcels layer and the NYS Tax Parcels Public feature service, looked up by address (131 rows). Rental certificate status comes from the Cornell and City of Ithaca Safety Program for Off-Campus Living lookup (92 rows). The City's Certificate of Compliance page has no public list, and the county's online search sits behind a disclaimer gate, so neither was used.
- Coordinates: the US Census Geocoder batch service (402 rows matched). distance_miles_straight_line is the straight-line distance to Ho Plaza (42.4467, -76.4847), not a walking distance. area_by_location is assigned from the coordinates with approximate boundaries and is labeled (approx.); the neighborhood column holds what a page said.

## Limits
- 281 rows carry a price; many are listing-page ranges without a lease year, and the prices column says so row by row. Per-bed and per-unit bases are kept distinct.
- Lease dates are printed for 70 rows only.
- Addresses were normalized lightly; a building listed under two address forms may appear twice.
- Per-source extraction files sit in build/ideas/inventory/ (not committed).
