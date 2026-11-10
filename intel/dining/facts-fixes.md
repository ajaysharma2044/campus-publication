# Fact-file fixes: dining

Built 2026-11-10 from intel/dining/raw/: every table with a Source column converted by code (lane-prefixed ids dining-A..E<section>-NNNN, 'same' source cells inherit the row above), then one fact-extractor session per lane added the facts those tables miss (ids numbered from 5001): {'analysis': 13, 'competition-part4': 8, 'competition': 10, 'market': 180, 'official': 71, 'voice': 0}.
- 10 converted rows with an empty fact or value (the 'Not found (where looked)' table and three blank rows in section 10 of the official lane) were dropped.
- The student-voice lane added nothing: its sources are opinion columns, forum threads and search snippets, none of which back a fact.
- Known limit: some converted rows bundle several facts in one value cell (the lane wrote them that way); the matcher still finds their numbers, and the checker opens the source page.
- Trailing zeros restored on any money value written as $N.N.
- 51 student-voice rows (lane C) got the URL from the lane's URL column; they stay confidence unsourced with a note: attribute, never a hard-fact source.
