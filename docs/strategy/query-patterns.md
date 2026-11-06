# Query pattern library (specs/continuous-local-run.md R19, R33) — version 1

Deterministic code (`worker/campus_worker/expand.py`) applies these patterns to every harvested entity and every
school or town. Every generated query is stored as a **hypothesis** (`questions.is_hypothesis = TRUE`,
`origin = 'hypothesis'`, `pattern_key`, `pattern_version`) and is never counted as observed demand until search
observation finds evidence (R20). Changing a pattern bumps the version; old hypotheses keep theirs.

Placeholders: `<entity>` entity name · `<school>` school short name · `<town>` town name · `<other>` another entity
of the same type in the same group (vs-pairs only, never all combinations) · `<audience>` an audience phrase.

## Entity patterns (by entity type)

| key | pattern | entity types | audiences |
|---|---|---|---|
| review | `<entity> review` | residence_hall, dining_location, gym, program, club, neighborhood, park, employer | — |
| vs | `<entity> vs <other>` | residence_hall, dining_location, program, neighborhood, bus_route (same group only) | — |
| room_size | `<entity> room size` | residence_hall | — |
| cost | `<entity> cost` | residence_hall, dining_location, parking_lot, gym, program, bus_route, course, employer | — |
| good_for_transfers | `is <entity> good for transfers` | residence_hall, program, club | prospective_transfer |
| parking | `<entity> parking` | residence_hall, library, gym, dining_location, park, event, office | — |
| how_to_get_to | `how to get to <entity>` | residence_hall, library, dining_location, gym, park, trail, office, event | — |
| hours | `<entity> hours` | dining_location, library, gym, student_service, town_service, office | — |
| prereq | `<entity> prerequisites` | course, program | — |
| schedule | `<entity> schedule` | bus_route, event, course | — |
| apply | `how to apply <entity>` | program, transfer_pathway, student_service, employer, club | — |
| requirements | `<entity> requirements` | program, transfer_pathway, course | — |
| safety | `<entity> safety rules` | park, trail | — |

## Audience and situation patterns (R33 extension)

| key | pattern | scope | audiences |
|---|---|---|---|
| audience_entity | `<entity> for <audience>` | any entity | prospective_transfer, international, grad, parent |
| alumni_benefit | `<school> alumni <entity>` | entities in alumni_* topics | alumni |
| parent_task | `<school> parent <entity>` | entities in parents_* topics | parent |
| student_jobs | `<school> student jobs <entity>` | entities in jobs_student / careers | undergrad |
| jobs_at | `jobs at <school> <entity>` | entities in jobs_university | faculty_staff |
| town_jobs_for | `<town> jobs for <audience>` | town | undergrad, grad, resident, international |

## Rules
- `vs` pairs are generated only inside the same entity type and the same `attributes.group` (for example halls in the
  same campus area). Comparison *pages* additionally require an observed query for the pair (R42).
- A pattern applies only when its entity type and (if given) audience are listed; topics not applicable to a school are
  skipped (`registry.topic_applicability`).
- Generation is idempotent: the occurrence key is `hyp:<scope>:<entity>:<pattern_key>:<audience>`.
- New patterns run on 3 items first (R27); if they produce usable clusters they scale to the batch.
