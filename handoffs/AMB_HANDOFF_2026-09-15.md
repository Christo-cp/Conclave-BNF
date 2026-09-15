# AMB Handoff — 2026-09-15

Supersedes `handoffs/AMB_HANDOFF_2026-09-14.md`. `STATUS.md` was rewritten in
the same pass.

## Audit

- The worktree already contained broad uncommitted S1-S12 application changes.
  This task did not alter application source, `0001`, or `0002`.
- Added migration revisions `0003` through `0015`, each with a guarded upgrade
  and downgrade. The chain ends at `0015_simulation_integrity`; S13 ML remains
  deferred.
- Added `scripts/measure_decision_latency.py`, `docs/dod.md`,
  `docs/measurements.md`, demo guides, pitch support, README commands, and
  refreshed status.

## Built, not live-tested

- Migration additions cover incident/requirement checks, ambulance assignment
  uniqueness, resource events, acceptance history, reservation invariants,
  mission/route/decision/audit indexes, and simulation scenarios/events.
- The latency utility reads `LATENCY_SAMPLE_RUNS` and prints p50/p95 for the
  pure deterministic matcher. The latest 50-sample run printed `p50_ms=0.019`
  and `p95_ms=0.025`. It does not measure HTTP, database, routing, or browser
  latency.
- Migration verification succeeded: downgrade to `0007_acceptance_history`,
  upgrade to `head`, and `alembic heads` reported
  `0015_simulation_integrity (head)`.
- Demo guide covers the golden path and hospital rejection, ICU failure,
  ambulance failure, traffic, unknown-capacity, and no-feasible-candidate cases.

## Signed off

Nothing. The zero-error-gate live-test and explicit user sign-off have not
occurred.

## Open questions and gaps

- PostgreSQL/PostGIS availability is required to run migration heads and the
  downgrade/upgrade round trip against `smart_ambulance_test`.
- Backup/restore remains unverified and is marked `none` in `docs/dod.md`.
- Existing application worktree changes need their own review and full-suite
  run; they were intentionally outside this task's edit scope.

## Position

- Build order: S14 documentation/hardening support, with S15 demo/pitch support.
- Milestone: M7/M8 preparation; the vertical slice is not independently signed
  off here.
- Next three: verify migrations with PostgreSQL; run full API/web/browser gates;
  conduct the live golden scenario and request user sign-off.

## Files touched

- `apps/api/migrations/versions/0003_*.py` through `0015_*.py`: additive,
  reversible schema/index/constraint/event-history layers.
- `scripts/measure_decision_latency.py`: configured-sample p50/p95 measurement.
- `docs/dod.md`, `docs/measurements.md`: evidence and measurement records.
- `docs/demo/*`, `docs/pitch/slides.md`: rehearsal and judge-support material.
- `README.md`: setup, verification, and scope commands.
- `STATUS.md`: current state and known gaps.

## Skill feed

- No new bug-catalog entry or spec-conflict decision was created.
