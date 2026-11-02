# Synthetic fixtures — NOT REAL DATA

Everything under `fixtures/synthetic/` is labeled test data. Institutions, buildings, prices,
questions and sources here are invented or copied into an IPEDS-like layout for tests. Records
imported from here are stored with `identity_status = 'synthetic_fixture'` /
`status = 'synthetic_fixture'` and must never be published or compared with real institutions.

The one real identity referenced (Cornell University, IPEDS UNITID 190415) is seeded in
`school_configs/cornell.yaml` with `identity_status: pending_verification` because the IPEDS
release could not be downloaded from the build environment. It must be re-verified against a
downloaded IPEDS HD file before any Cornell page is published.
