# Owner-supplied questions (specs/bulk-mode.md D4)

Drop YAML files here; `python -m campus_worker.bulk dossier` merges them into the question map and dedupes by answer key and audience.

```yaml
questions:
  - question: "How do I change my major at Cornell?"
    school: cornell-university          # registry slug; omit for every school
    topic: courses                      # a topics.key; defaults to housing
    audience: general                   # general | transfer | international | parent | alumni | staff | resident
    page_type: process_guide            # question_guide | entity_guide | process_guide | comparison
    answer_key: change-major            # optional; questions with the same key become one page
```
