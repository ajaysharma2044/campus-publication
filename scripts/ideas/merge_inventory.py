"""Merge the inventory extraction CSVs into intel/off-campus-housing/inventory.csv.
Reads build/ideas/inventory/*.csv (building rows) and records-*.csv (public records), merges by normalized address,
geocodes through the US Census Geocoder batch endpoint (public, built for batches) and adds the straight-line
distance to Ho Plaza. Nothing is invented: every field comes from a row an agent read on a page, and the distance
is labeled straight-line."""
import csv, glob, json, math, os, re, subprocess, sys, tempfile
REPO = "/Users/ajaysharma/Ads/campus-publication"
OUT = f"{REPO}/intel/off-campus-housing/inventory.csv"
HO_PLAZA = (42.4467, -76.4847)
COLS = ["address", "building_name", "neighborhood", "owner_or_manager", "owner_of_record", "units", "unit_sizes", "prices", "price_basis",
        "lease_dates", "lease_term", "amenities_included", "year_built", "property_class", "units_recorded", "certificate_status", "certificate_expires",
        "distance_miles_straight_line", "lat", "lon", "distance_note", "source_urls", "checked", "notes"]
ABBR = {"avenue": "ave", "street": "st", "place": "pl", "road": "rd", "drive": "dr", "terrace": "ter", "lane": "ln", "court": "ct", "boulevard": "blvd", "north": "n", "south": "s", "east": "e", "west": "w"}

def norm(a):
    a = re.sub(r"[.,]", "", (a or "").lower()).replace("ithaca ny", "").replace("ithaca", "").strip()
    a = re.sub(r"\s+", " ", a)
    return " ".join(ABBR.get(w, w) for w in a.split())

def join(a, b):
    a, b = (a or "").strip(), (b or "").strip()
    if not a: return b
    if not b or b in a: return a
    return a + "; " + b

def main():
    rows = {}
    for p in sorted(glob.glob(f"{REPO}/build/ideas/inventory/*.csv")):
        if os.path.basename(p).startswith("records-"): continue
        for r in csv.DictReader(open(p, encoding="utf-8")):
            k = norm(r.get("address"))
            if not k: continue
            d = rows.setdefault(k, {c: "" for c in COLS})
            d["address"] = d["address"] or r.get("address", "").strip()
            for c in COLS:
                if c in r and r[c]: d[c] = join(d[c], r[c])
    for p in sorted(glob.glob(f"{REPO}/build/ideas/inventory/records-*.csv")):
        for r in csv.DictReader(open(p, encoding="utf-8")):
            k = norm(r.get("address"))
            if k not in rows: continue
            d = rows[k]
            for src, dst in (("owner_of_record", "owner_of_record"), ("property_class", "property_class"), ("year_built", "year_built"), ("units_recorded", "units_recorded"), ("certificate_status", "certificate_status"), ("certificate_expires", "certificate_expires")):
                if r.get(src): d[dst] = join(d[dst], r[src])
            if r.get("source_url"): d["source_urls"] = join(d["source_urls"], r["source_url"])
            if r.get("notes"): d["notes"] = join(d["notes"], r["notes"])
    # geocode in one Census batch
    keys = list(rows)
    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, newline="") as f:
        w = csv.writer(f)
        for i, k in enumerate(keys):
            w.writerow([i, rows[k]["address"], "Ithaca", "NY", ""])
        batch = f.name
    try:
        out = subprocess.run(["curl", "-s", "--form", f"addressFile=@{batch}", "--form", "benchmark=Public_AR_Current",
                              "https://geocoding.geo.census.gov/geocoder/locations/addressbatch"], capture_output=True, text=True, timeout=300).stdout
        for rec in csv.reader(out.splitlines()):
            if len(rec) >= 6 and rec[2] == "Match" and rec[5]:
                lon, lat = (float(x) for x in rec[5].split(","))
                d = rows[keys[int(rec[0])]]
                d["lat"], d["lon"] = f"{lat:.5f}", f"{lon:.5f}"
                dlat, dlon = math.radians(lat - HO_PLAZA[0]), math.radians(lon - HO_PLAZA[1])
                a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat)) * math.cos(math.radians(HO_PLAZA[0])) * math.sin(dlon / 2) ** 2
                d["distance_miles_straight_line"] = f"{3958.8 * 2 * math.asin(math.sqrt(a)):.2f}"
    except Exception as e:
        print("geocoding skipped:", e)
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS); w.writeheader()
        for k in sorted(rows, key=lambda k: (rows[k]["neighborhood"], rows[k]["address"])): w.writerow(rows[k])
    geo = sum(1 for k in rows if rows[k]["lat"])
    rec = sum(1 for k in rows if rows[k]["owner_of_record"])
    print(f"{len(rows)} buildings written to {OUT}; {geo} geocoded; {rec} with an owner of record")

if __name__ == "__main__":
    main()
