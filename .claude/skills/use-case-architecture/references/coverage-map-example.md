# Coverage map example

A coverage map for the security deposit page, built from the housing fact file. Fact ids are illustrative; real ones come from `facts.csv`.

```json
{
  "slug": "ithaca-security-deposit-rules-tenants",
  "topic": "housing",
  "page_type": "how-to",
  "length_tier": "guide",
  "primary_query": "ithaca tenant rights security deposit law",
  "use_case": "get-deposit-back",
  "answer_first": "New York caps a deposit at one month's rent, and the landlord has 14 days after move-out to return it with an itemized list or lose the right to keep any of it.",
  "sub_questions": [
    {"id": "q1", "question": "How much can a landlord charge as a deposit?", "fact_ids": ["housing-2.7-0101", "housing-2.7-0102"]},
    {"id": "q2", "question": "Which fees are banned or capped?", "fact_ids": ["housing-2.7-0105", "housing-2.7-0106", "housing-2.7-0107"]},
    {"id": "q3", "question": "When must the deposit come back, and what happens if it's late?", "fact_ids": ["housing-2.7-0110", "housing-2.7-0111"]},
    {"id": "q4", "question": "Can the landlord raise the deposit at renewal?", "fact_ids": ["housing-2.7-0114"]},
    {"id": "q5", "question": "What can be deducted, and how do I dispute a deduction?", "fact_ids": ["housing-2.7-0116", "housing-2.24-0402"]},
    {"id": "q6", "question": "How do I take a landlord to small claims court?", "fact_ids": ["housing-2.24-0405", "housing-2.24-0406"]},
    {"id": "q7", "question": "Why do some sources say 30 days instead of 14?", "fact_ids": ["housing-2.7-0112"], "note": "conflict: old rule vs 2019 law; follow 14"}
  ],
  "reader_blocks": [
    {"reader": "international", "covers": "paying a deposit before arrival safely", "fact_ids": ["housing-6.11-0530"]},
    {"reader": "alum-landlord", "covers": "the landlord's side of the 14-day rule", "fact_ids": ["housing-2.7-0110"]}
  ],
  "leave_to_siblings": [
    {"question": "Move-out checklist and inspection timing", "slug": "moving-out-ithaca-apartment-deposit-back"},
    {"question": "Reading the lease before signing", "slug": "how-to-read-ithaca-lease-before-signing"}
  ]
}
```

Notice: every sub-question cites facts; reader blocks hold only what differs; the move-out checklist goes to its own page instead of being repeated here.
