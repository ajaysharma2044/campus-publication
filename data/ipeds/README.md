# IPEDS institution directory (real data, mirrored)

`HD2024_mirror_cshirky_a812f69.csv` is the IPEDS HD2024 institutional-characteristics file as found in the public GitHub repository `cshirky/college-dashboard` (path `data/raw/HD2024.csv`, commit `a812f699…`, committed 2026-09-27). It was obtained on 2026-11-04 because `nces.ed.gov` is not reachable from the build environment. SHA-256 in `SHA256SUMS`.

What this is and is not:
- It **is** real institution directory data (6,072 rows; UNITID, name, alias, city, state, sector, control, web address, system membership), suitable for seeding the national registry.
- It is **not** an NCES-verified download. Every institution imported from it carries `identity_status = pending_verification` and the external-id row records the mirror as the release. Before any school's pages are published, the row must be re-verified against the file downloaded from https://nces.ed.gov/ipeds/use-the-data (the checksum of the official file should be recorded alongside).
- IPEDS covers U.S. Title IV institutions only; it is not a global or complete training-provider list.

Coverage note: the registry having 6,000 institutions does not mean the publication covers them; a school hub is published only when verified pages exist (SPEC §02).
