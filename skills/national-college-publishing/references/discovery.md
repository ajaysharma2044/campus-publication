# Question discovery (role B)
- Ingest observed questions with origin (official_faq, search_suggestion, related_question, discussion, competitor_gap). Each origin means something different; none is complete demand.
- `discovery.normalize` folds synonyms (dorm → residence hall, AC → air conditioning, freshman → first-year) and keeps the raw wording on the question row.
- One occurrence per post/crosspost (`occurrence_key`); five mirrors are one occurrence.
- Clusters group by answer (`answer_key`); audience splits a cluster only where rules differ for that topic (`AUDIENCE_SPLIT_TOPICS`), otherwise the audience marker is folded out.
- Hypotheses (`generate_hypotheses`) are bounded, labeled `is_hypothesis`, counted separately, and skipped for not-applicable topics.
- Follow-up tasks become `coverage_edges` with state answered / unknown / not_applicable / stale / worth_researching.
