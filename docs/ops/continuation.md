# Continuation and execution mode (SPEC §35, §39)

## What runs where
| Mode | What it is | State |
|------|------------|-------|
| Claude Code session | primary build-and-maintenance interface; reads SPEC/BACKLOG/STATE, edits code, runs checks | used for this build |
| `scripts/continuation_demo.sh N` | bounded loop of scheduler ticks with a `flock`; stops on no work / budget pause / credential block / ceiling; logs every iteration to `build/continuation.log` | **verified locally** (see below) |
| `python -m campus_worker.cli run-once` | one scheduler tick; exit codes 0 completed, 10 waiting, 20 usage-paused, 30 blocked, 11 locked, 1 failed | verified locally |
| External scheduler (cron/systemd/cloud task/Claude Code Routine) | needed for "continuously running"; this container stops when the session ends | **not configured** (owner step) |

A detached process in this container is not continuity: it dies with the container. Continuity requires an external scheduler plus the persistent repository and database.

## Verified run (2026-11-02)
`scripts/continuation_demo.sh 8 --seed-demo` seeded a three-job dependent chain (collect → extract (fails once) → brief) and ran without any manual "continue":
```
iteration 1: exit=0 completed ran=noop:succeeded,fail_once_then_succeed:retry_wait
iteration 2: exit=10 waiting ran=            (retry_wait advanced for the demo)
iteration 3: exit=0 completed ran=fail_once_then_succeed:succeeded,noop:succeeded
iteration 4: exit=10 waiting ran=
STOP: no unblocked work remains (exit 10)
```
Database afterwards: all three jobs `succeeded`; the flaky job shows `attempts=2`; no job ran twice. Stop condition observed from the exit code, not from a self-declared completion phrase.

Interrupt/resume is covered by `tests/test_scheduler.py::test_interrupt_and_resume_without_duplicate_work` (lease expires, next tick reclaims and completes once) and the lock test (`locked` status when another tick holds the advisory lock).

## Claude Code command choice
Check the installed version before relying on `/goal`; in this session `/goal` was not available, and `/loop` is periodic scheduling, not an uninterrupted run. The equivalent bounded milestone instruction for a future session:

> Implement the first unblocked milestone in BACKLOG.md using SPEC.md; run its acceptance checks; fix failures; update STATE.md after each completed task; continue routine authorized work without confirmation; record genuine blockers and complete independent tasks; stop when checks pass, no unblocked work remains, or the configured run limit is reached. Use observed test output as evidence.

Permissions: worker research tasks never get deployment or unrestricted shell access; the scheduler maps job types to a fixed handler registry, so a model proposal cannot schedule arbitrary work.

## Usage-limit and credential failure (fixtures)
- Budget pause: `tests/test_scheduler.py::test_budget_pause_blocks_paid_jobs_but_not_deterministic_ones` → exit 20, paid jobs untouched, deterministic jobs continue.
- Credential missing: `test_model_job_holds_on_missing_credential_and_tick_reports_blocked` → job held `provider_auth`, exit 30.
- Provider auth/usage-limit errors from a connected provider: `ModelRouter.call` converts them to a hold (`provider_auth` / `provider_usage_limit`), never to a retry storm or an account switch.
