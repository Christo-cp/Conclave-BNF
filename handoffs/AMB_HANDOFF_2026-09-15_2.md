# AMB Handoff — 2026-09-15_2

## Current position

The final verification and hardening pass is complete. The working tree remains
uncommitted by request. The application is a verified synthetic hackathon
prototype, pending explicit user live-test sign-off.

## Evidence from this session

- `pytest apps\api\tests -v`: 33 passed, 14 dependency warnings.
- `scripts/full_suite.ps1`: passed.
- `alembic heads`: `0015_simulation_integrity (head)`.
- Migration round-trip integration test: passed.
- Concurrent reservation tests: passed; one winner on one unit.
- Append-only trigger tests: passed.
- `pnpm --dir apps/web build`: passed.
- `pnpm --dir apps/web lint`: passed.
- Vitest: 6 passed.
- Mocked Playwright: 6 passed.
- Live Playwright with Docker/PostGIS/API running: 1 passed.
- Latency: p50 0.009 ms, p95 0.012 ms for 50 deterministic matcher samples.
- Live HTTP golden smoke: `ok INC-000001 AMB-002 H-003 600s`.
- Secret, token, forbidden-claim, and diff checks: passed.

## Hardening change

The frontend realtime URL now targets `/api/v1/ws`, matching the FastAPI mounted
WebSocket route. A live Playwright spec is opt-in via `LIVE_E2E=1` and runs
against the real API/database; the existing six browser tests remain isolated UI
tests with route fixtures.

## Remaining limitations

- S13 ML/voice is intentionally skipped by the approved plan.
- Backup/restore is not verified.
- Not all failure scenarios have live browser rehearsal evidence.
- The browser demo stores its token in local storage; secure HTTP-only cookie
  sessions are required before production deployment.
- User live sign-off and the blind evaluator gate are outstanding.
