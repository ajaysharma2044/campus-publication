# Skill evaluations (specs/continuous-local-run.md R12, R30; AT11, AT27)

This file is the authority for what may live under `.claude/skills/`. The guard hook (`.claude/hooks/guard.sh`) blocks any write into `.claude/skills/<name>/` unless `<name>` appears below with status `adopted` and a 40-hex commit SHA, or as the in-repo baseline. Rollback for any adopted skill: delete its folder and revert the adopting commit.

## Installed

| name | status | source | sha | license | eval (baseline → candidate) | installed |
|---|---|---|---|---|---|---|
| `national-college-publishing` | baseline (in-repo) | `skills/national-college-publishing/` (symlink) | in-repo | repo | baseline | 2026-11-06 |

## Candidates (filled by the skill-scout agent, R12)

Top 10 candidates with URL, author, license, last commit, stars, what it does, hooks/scripts shipped; top 5 source-reviewed with accept/reject reasons; benchmark results for every survivor against the baseline on `docs/ops/skill-eval-set.md`.

_No scout run yet (milestone 7)._

## Rejected

_None yet._
