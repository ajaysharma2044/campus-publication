from campus_worker.editorial import checks as c

GOOD = """The useful comparison is the route to your classrooms and what the quoted room rate includes.

Mews Hall's double room is billed per person for the academic year. The published rate for 2026-27 is $12,042, and the housing office bills it in two semester installments.

The building is air-conditioned. Whether it has a kitchen on every floor is unknown; the housing site does not say.

## What to do next

Compare Mews with Court-Kay-Bauer on the same per-person, academic-year basis before you rank them."""
TABLE = [{"label": "Double (2026-27)", "value": "$12,042 per person, academic year", "claim_id": "c1"}]
ACTIONS = [{"text": "Compare Mews with Court-Kay-Bauer", "target": "/compare"}]


def test_good_draft_has_no_hard_findings():
    f = c.run_all(headline="Mews Hall: what the double-room rate includes", deck="d", body_md=GOOD, byline="Housing desk", fact_table=TABLE,
                  body_claim_ids=["c1"], critical_ids=["c1"], approved_ids={"c1"}, institution_name="Cornell University",
                  other_institution_names=["Columbia University"], academic_year="2026-27", next_actions=ACTIONS, existing_bodies=[])
    assert [x for x in f if x.severity == "hard"] == []


def test_banned_opening_and_filler():
    bad = "Navigating the world of college housing can be daunting.\n\nThis vibrant dorm offers a unique experience for every student with state-of-the-art amenities."
    kinds = [x.kind for x in c.check_openings(bad) + c.check_filler(bad)]
    assert kinds.count("filler") == 2


def test_fabricated_consensus_quote_and_byline_are_hard():
    body = 'Students agree Mews is the best. "The rooms are enormous and the staff are lovely," said one resident. When I lived there it was great.'
    f = c.check_fabrication(body)
    assert {x.kind for x in f} == {"fabricated_consensus", "invented_quote"} and all(x.severity == "hard" for x in f)
    assert c.check_byline("By Sarah Mitchell")[0].severity == "hard"
    assert c.check_byline("Jane Doe")[0].severity == "hard"
    assert c.check_byline("Housing desk") == []


def test_headline_superlatives_and_prose_table_mismatch():
    assert c.check_headline("The Best Dorm at Cornell: Ultimate Guide", None, GOOD)[0].kind == "deceptive_headline"
    stale = GOOD.replace("$12,042", "$11,580")  # prose still shows last year's number
    f = c.check_money_in_prose_matches_table(stale, TABLE)
    assert f and f[0].kind == "prose_table_mismatch"


def test_unsupported_claim_refs_and_arithmetic():
    f = c.check_claim_refs(["c1", "c9"], ["c1"], {"c1"})
    assert f[0].kind == "unsupported_claim" and f[0].severity == "hard"
    assert c.check_arithmetic("Room $12,042 + meal plan $6,500 = $18,542") == []
    assert c.check_arithmetic("Room $12,042 + meal plan $6,500 = $18,000")[0].kind == "incorrect_arithmetic"
    assert c.check_arithmetic("$6,021 × 2 = $12,042") == []


def test_wrong_school_and_year_scope():
    f = c.check_scope("Rates at Columbia University are similar.", "Mews Hall", institution_name="Cornell University",
                      other_institution_names=["Columbia University"], academic_year="2026-27")
    assert f[0].kind == "wrong_school"
    f2 = c.check_scope("The 2025-26 rate was lower.", "h", institution_name="Cornell University", other_institution_names=[], academic_year="2026-27")
    assert f2[0].kind == "wrong_year"


def test_duplicate_audience_rewrite_detected():
    transfer = GOOD.replace("Mews Hall's", "For transfer students, Mews Hall's")
    f = c.check_duplicate_audience(transfer, [("page-1", GOOD)])
    assert f and f[0].kind == "superficial_duplicate" and f[0].severity == "hard"
    assert c.check_duplicate_audience(GOOD, [("page-2", "Completely different text about parking permits and bus routes." * 10)]) == []


def test_missing_next_action():
    assert c.check_next_action([])[0].kind == "missing_next_action"
    assert c.check_next_action([{"text": "You may also like", "target": "/x"}])[0].kind == "weak_link_text"
