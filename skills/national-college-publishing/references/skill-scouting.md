# Skill scouting (new role: skill-scout · contract `skill_eval.json`)
Spec: continuous-local-run R12, R30, R32 (usage tools). Weekly, plus once at the start of the first run.

## Search
Skill marketplaces, GitHub, and official Anthropic skill/plugin sources for SEO, editorial writing, SERP research, content-strategy skills, plugins, and MCP servers. Record the top 10 candidates: url, author, license, last_commit, stars, what_it_does, ships_hooks, ships_scripts, kind, and which R30 capabilities it would cover.

## Source review (top 5)
Read SKILL.md, every script, every hook. Reject when it: makes network calls not disclosed in its docs; writes outside its own scope; has an unclear license; requires a paid account. Record `files_read`.

## Benchmark survivors
Fixed eval set `docs/ops/skill-eval-set.md` (3 cluster briefs, 1 draft edit, 1 title/snippet task, 1 SERP gap analysis). Compare against the baseline (the repo's own references in this folder). Record quality score (0–10), errors, turns, seconds, and `hard_rule_regression` (any violation of the hard rules in SPEC §7 / continuous-local-run §7 is an automatic fail).

## Adoption rule
Adopt only if the candidate beats baseline on quality with no hard-rule regression. Adopted skills are vendored into `.claude/skills/<name>/` pinned to a 40-hex commit SHA; the coordinator records url, sha, license and eval results in `docs/ops/skill-evaluations.md` **before** any file is written there (the guard hook enforces it). Never install anything globally; never add hooks without a review note; rollback = delete the folder and revert the commit.

## Usage tools (docs/ops/usage-optimization.md, SPEC §38)
Evaluate in this order, each alone, on the fixed eval set already defined there: Session Report, token-optimizer, context-mode, rtk. Read source, license, hooks; pin; record rollback. Bytes saved ≠ tokens ≠ dollars; never adopt a compression tool that can hide footnotes, conflicts, or failure details.

## Coverage matrix (R30)
`docs/ops/skill-coverage.md`: for each required capability, the covering skill (adopted external or in-repo reference), pinned version, eval score. A capability with no cover becomes a scout job; if nothing external beats baseline, write or improve the in-repo reference and benchmark it.
