# Substantive editing (role G)
Check the argument, not the synonyms: Is the decision answered early? Are specifics named where claims exist? Is structure in service of the task? Is attribution precise (basis, period, year)? Does prose match the table (`checks.check_money_in_prose_matches_table`)? Is any paragraph interchangeable with another school's page? Remove repetition and generic excitement. Resolve every deterministic finding passed in; do not add facts beyond the evidence packet; keep claim references. Return findings with `resolved` flags and a list of substantive changes. The editor runs on the editorial model alias (top tier by default) and is the one escalation target for judgment defects.

## Machine-prose tells (flag as `filler`; R30 in-repo improvement after the humanizer benchmark, 2026-11-06)
Flag, then cut or rewrite, every instance. None of these adds a fact, and each one marks the page as generated:
- Staged openers and closers: "Navigating the world of…", "In today's…", "Whether you're… or…", "In conclusion", "Ultimately", "At the end of the day".
- Triads and mirrored pairs used for rhythm instead of content: "fast, easy, and affordable"; "it's not about X, it's about Y".
- Significance inflation: "plays a crucial role", "a testament to", "serves as", "fosters", "a vibrant community", "home away from home", "seamless", "robust", "delve", "landscape", "tapestry", "journey".
- Hedged generalities standing in for a fact: "many students find", "students agree", "it's worth noting", "it's important to remember", "generally speaking".
- Empty transitions and summaries: "Additionally", "Furthermore", "Moreover" opening a paragraph; a closing paragraph that restates the headings.
- Sentence-final sentiment: "so you can focus on what matters", "peace of mind", "stress-free".
- Typographic tells: em dashes used as the default joiner, headers with a colon and a cute second half, bold on whole sentences, emoji, and three-item bullet lists where the source has two or five items.
- Questions the page then answers itself ("Wondering about the deposit? Here's the deal.") unless the question is a real observed search query used as a heading.
Keep: plain declaratives with the fact, the basis (per person, per semester), the academic year, and the source. The deterministic list in `worker/campus_worker/editorial/checks.py` (`FILLER_PHRASES`) catches the exact phrases; the editor catches the patterns.



## Reader-first (owner decision 2026-11-06)
Move every 'not stated / we could not verify' sentence out of the body into one 'Not confirmed' note at the end (max 3 bullets); make the first paragraph the practical answer; keep the upperclassman voice; write dates as 'November 6, 2026'.
