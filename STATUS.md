# STATUS — Smart Ambulance

Last updated 2026-09-16. Handoff: `handoffs/AMB_HANDOFF_2026-09-16.md`.

## Implemented

- S0-S15 application surface is present through migration head
  `0015_simulation_integrity`.
- FastAPI/PostGIS backend, deterministic seed/reset, auth/RBAC, CRUD, decision
  persistence, acceptance/reservation lifecycle, reassessment, simulation,
  post-commit events, and authenticated WebSocket subscriptions are implemented.
- Dispatcher, hospital, ambulance crew, and demo-controller workspaces are
  implemented with loading, error, stale, unknown, and simulated states.
- S13 ML/voice is intentionally skipped because the approved plan provides no
  training data and forbids fabricated accuracy claims.
- Fabricated frontend fallback recommendations were removed; failed matching is
  now non-confirmable.
- Simulation client paths, seeded demo-controller access, and realtime payload
  consumption were aligned with the backend contract.

## Automated verification

- Backend: `37 passed`; Ruff and Python compilation passed.
- PostgreSQL integration: concurrent reservation, rollback, append-only trigger,
  and migration round-trip tests passed.
- Frontend: build, lint, and `8 passed` Vitest tests.
- Mocked Playwright: `6 passed` accessibility and dispatcher tests.
- Live Playwright: `1 passed` against the running FastAPI/Postgres stack.
- Live demo-controller rehearsal: 8 mission-targeted controls returned
  `SIMULATED`; dispatcher attempts were rejected with `403`.
- Migration head: `0015_simulation_integrity`.
- Latency: 50 deterministic matcher samples, p50 `0.009 ms`, p95 `0.012 ms`.
- Secret/token/forbidden-claim scans and `git diff --check` passed.

## Live integration

- Docker PostGIS was running during verification.
- The live browser flow passed: login, incident, requirements, ambulance match,
  ambulance confirmation, hospital match, and route calculation.
- The live HTTP golden smoke selected `AMB-002`, selected `H-003`, and returned a
  600-second mock route.
- Frontend realtime URL is aligned with the mounted backend endpoint:
  `/api/v1/ws`.

## Environment limitations

- Backup/restore remains unverified and is marked `none` in `docs/dod.md`.
- The latency measurement is for the deterministic matcher, not production
  HTTP/database/browser latency.
- Browser failure-scenario rehearsal is documented but not all scenarios have a
  live browser recording.
- `.env.test` is absent; live verification used the untracked local `.env`.
- The project is synthetic decision support, not clinical autonomy or a live
  hospital-capacity integration.

## Known warnings

- Starlette/httpx and AnyIO deprecation warnings remain in the test client.
- Playwright mocked tests may log expected Vite proxy connection warnings when
  the API is intentionally not started.
- Browser tokens remain client-side demo tokens in local storage; production
  deployment must move session handling to secure HTTP-only cookies.

## User sign-off

The blind evaluator and configured code-review subagent were unavailable. The
zero-error gate still requires explicit user live-test sign-off. Run the
commands in `docs/demo/golden-scenario.md`, confirm the live workflow and
failure scenarios, then explicitly sign off before calling the release complete.
