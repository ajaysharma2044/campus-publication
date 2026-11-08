"""Valid fixture envelopes for every agent role (AT10). Synthetic, clearly labeled; never institution facts."""
from __future__ import annotations

import json

BODY = ("Fixture Hall's double room costs $12,042 per person for the 2026-27 academic year (synthetic fixture). " * 6).strip()


def envelope(role: str, output: dict, *, decision: str = "advance", institution_id: str | None = "inst-fixture", **kw) -> dict:
    d = {"schema_version": "1.0", "run_id": "run-fixture-0001", "role": role, "input_ids": ["b1"], "institution_id": institution_id, "campus_id": None,
         "decision": decision, "hold": None, "output": output, "evidence_ids": ["c1"], "uncertainties": [], "next_jobs": [], "usage": {"model": "fixture"}}
    d.update(kw)
    return d


GENERIC = {"summary": "Fixture review complete.", "findings": [{"kind": "info", "detail": "synthetic fixture finding", "severity": "info"}], "proposed_changes": []}

OUTPUTS: dict[str, dict] = {
    "onboarding": GENERIC,
    "discovery": {"observed_questions": [{"raw_text": "Do transfer students have to live on campus?", "origin": "official_faq", "audience": "transfer", "source_ref": "fixture:faq"}],
                  "hypotheses": [{"raw_text": "Fixture Hall room size", "audience": None}]},
    "opportunity": {"scores": {"demand": 2, "answer_gap": 4, "winnability": 3, "evidence_advantage": 3, "commercial": 1}, "observations": {"demand": "two independent threads (fixture)"},
                    "confidence": "low", "missing_contribution": "a verified per-person rate table", "action": "new_page", "existing_coverage_checked": []},
    "researcher": {"claims": [{"field": "rate.room", "value_type": "money", "value": 1204200, "unit": "minor_units", "currency": "USD", "billing_period": "per_academic_year",
                               "price_basis": "per_person", "room_type": "double", "academic_year": "2026-27", "evidence_category": "verified_fact",
                               "source_locator": "fixture_hall_rates_v1.html#rates", "excerpt": "Double $12,042 per person (fixture)", "confidence": 0.9}],
                   "not_found": [], "not_applicable": [], "scope_notes": ["synthetic fixture source"], "injection_observed": False},
    "planner": {"page_format": "guide", "audience": "transfer", "reader_decision": "Whether to apply for Fixture Hall as a transfer student.",
                "verified_answer": "Fixture Hall double rooms cost $12,042 per person for 2026-27 and transfers may apply (fixture).",
                "unique_contribution": "A per-person rate table with what the rate includes.", "critical_claim_ids": ["c1"], "supporting_claim_ids": [],
                "structure": [{"heading": "What it costs", "purpose": "answer the cost question", "claim_ids": ["c1"]}, {"heading": "Who can apply", "purpose": "eligibility", "claim_ids": []}],
                "next_tasks": ["compare with Riverside Hall"], "information_gain": [{"item": "per-person rate", "claim_id": "c1"}, {"item": "what the rate includes", "claim_id": "c1"}, {"item": "deposit refund rule", "claim_id": "c1"}]},
    "writer": {"headline": "Fixture Hall: what the double-room rate includes", "deck": "Per-person academic-year rate and what we could not verify (fixture).",
               "body_markdown": BODY, "claim_refs": ["c1"], "fact_table": [{"label": "Double", "value": "$12,042", "claim_id": "c1"}],
               "next_actions": [{"text": "Compare with Riverside Hall", "target": "/schools/fixture-state/housing/compare/fixture-vs-riverside/"}]},
    "editor": {"revised_headline": "Fixture Hall: what the double-room rate includes", "revised_deck": None, "revised_body_markdown": BODY,
               "findings": [{"kind": "specificity", "detail": "state the billing period in the first sentence", "resolved": True}], "substantive_changes": ["moved the rate to sentence one"], "unresolved": []},
    "verifier": {"claim_checks": [{"claim_id": "c1", "status": "supported", "detail": "matches fixture rate sheet", "source_opened": True}], "hard_failures": [],
                 "rubric": {"clarity": 4, "specificity": 4, "structure": 4, "attribution": 4, "usefulness": 4, "prose": 4}, "publishable": True, "corrections_required": []},
    "seo": GENERIC, "tool_engineer": GENERIC, "ad_ops": GENERIC, "analyst": GENERIC,
    "skill_scout": {"candidates": [{"name": "example-seo-skill", "url": "https://github.com/example/example-seo-skill", "author": "example", "license": "MIT", "last_commit": "2026-10-01",
                                    "stars": 12, "what_it_does": "on-page SEO checklist (fixture)", "ships_hooks": False, "ships_scripts": True, "kind": "skill", "capabilities": ["on-page SEO"]}],
                    "source_reviews": [{"name": "example-seo-skill", "decision": "reject", "reasons": ["undisclosed network call in scripts/fetch.sh (fixture)"], "network_calls_disclosed": False,
                                        "writes_in_scope": True, "license_clear": True, "paid_required": False, "files_read": ["SKILL.md", "scripts/fetch.sh"]}],
                    "benchmarks": [], "adoptions": [], "rejections": [{"name": "example-seo-skill", "reason": "undisclosed network call"}], "coverage_gaps": ["technical SEO audit"]},
    "search_intel": {"cluster_id": "cl-fixture", "observed_on": "2026-11-06", "label": "observed via search tool on 2026-11-06",
                     "variants": [{"query": "fixture hall review", "results": [
                         {"position": 1, "url": "https://forum.example.invalid/t/1", "title": "Fixture Hall thoughts?", "publisher": "forum", "result_type": "forum", "dedicated": False,
                          "answer_quality": "partial", "freshness": "stale", "freshness_date": "2023-01-01", "evidence_quality": "unsourced", "missing_contribution": "verified rates and room types"}],
                         "follow_up_questions": ["is fixture hall good for transfers"], "community_occurrences": [{"url": "https://forum.example.invalid/t/1", "title": "Fixture Hall thoughts?", "site": "forum.example.invalid", "date": "2023-01-01"}], "navigational": False}],
                     "seasonality_notes": "peaks in spring housing lottery (fixture)", "demand_evidence": [{"kind": "forum_thread", "query": "fixture hall review", "ref": "https://forum.example.invalid/t/1", "independent": True}],
                     "search_calls_made": 1, "cache_hits": 0},
    "search_strategist": {"scope": {"school_slug": "fixture-state", "topic_key": "housing"},
                          "cluster_map": [{"query_group": "fixture hall review", "queries": ["fixture hall review", "fixture hall rooms"], "page_path": "/schools/fixture-state/housing/fixture-hall/", "format": "entity_guide"}],
                          "win_plans": [{"page_path": "/schools/fixture-state/housing/fixture-hall/", "contribution": "a verified per-person rate and room-type table the forum threads lack",
                                         "target_title": "Fixture Hall: Rooms, Cost and What to Know", "h1": "Fixture Hall: rooms, cost, location", "answer_first_intro": "Fixture Hall is a synthetic residence hall whose double room costs $12,042 per person for 2026-27.",
                                         "snippet_formats": ["table"], "faq_real_questions": [], "secondary_questions": ["is fixture hall good for transfers"], "beats": [{"url": "https://forum.example.invalid/t/1", "how": "verified rates with sources"}]}],
                          "internal_links": [{"from": "/schools/fixture-state/housing/", "to": "/schools/fixture-state/housing/fixture-hall/", "anchor_text": "Fixture Hall rooms and cost"}],
                          "trust_signals": {"sources_section": True, "methods_link": "/about/methods/", "updated_date": True, "corrections_link": "/about/corrections/"},
                          "refresh_cadence": [{"page_path": "/schools/fixture-state/housing/fixture-hall/", "cadence_days": 180, "reason": "rates change yearly"}],
                          "win_criteria": [{"page_path": "/schools/fixture-state/housing/fixture-hall/", "queries": ["fixture hall review"], "check_after_days": 30, "success": "our page appears for the target variant"}]},
}


def cli_stdout(role: str, *, text: str | None = None, is_error: bool = False, turns: int = 3) -> str:
    """Mimic `claude -p --output-format json` stdout whose result carries the envelope text."""
    result = text if text is not None else json.dumps(envelope(role, OUTPUTS[role]))
    return json.dumps({"type": "result", "subtype": "success", "is_error": is_error, "num_turns": turns, "duration_ms": 1000, "total_cost_usd": 0, "session_id": "fixture", "result": result})
