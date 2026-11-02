# Institution onboarding (role A)
Goal: an immutable institution record, verified identity, campus boundaries, topic applicability, source map, calendar.
- Seed from an IPEDS HD release via `registry.import_ipeds_hd` with the release name and date; identity stays `pending_verification` until matched to a downloaded release row.
- SECTOR 0 = administrative unit → `is_system=TRUE`; systems never own campuses (`registry.ensure_campus` refuses).
- Same name ≠ same entity: slugs carry the UNITID; `disambiguate` lists candidates.
- Topic applicability per school: applicable / not_applicable / unknown with a rationale (commuter college: housing not_applicable; dining unknown until sourced).
- Source map: domains in `school_configs.source_domains` and permission rows in `source_permissions`. Reddit stays disabled.
- Calendar: semester/quarter/trimester/rolling/unknown — never assume semesters.
Output contract: onboarding (summary, findings, proposed_changes). Proposed registry edits are applied by code after review.
