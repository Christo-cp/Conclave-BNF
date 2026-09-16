# STATUS — Smart Ambulance

Last updated 2026-09-16. Handoff: `handoffs/AMB_HANDOFF_2026-09-16_6.md`.

## Current State

Overall: implemented backend foundation through S8, realtime core, and selected
S11/S12 services; not a complete S0-S15 release. Full repository audit and
implementation-grounded pitch are documented in
`docs/pitch/PROJECT_PITCH_AND_CODEBASE_ANALYSIS.md`.
Current milestone: S9/S11-S12 continuation; S10 browser exit and later work remain.
Last verified: 2026-09-16.
Backend: FastAPI/PostGIS, migrations through `0018_decision_trace_fields`,
scenario-backed matching/routing, RBAC, acceptance/reservation, crew assignment,
sweeper scheduler, targeted resource-loss controls, and configured CORS.
Frontend: React/Vite build and 11 Vitest tests pass; dispatcher/role screens exist,
but the complete acceptance/reservation browser flow is partial.
Database: PostgreSQL integration available; 58 backend tests pass.
Realtime: authenticated `/api/v1/ws`, explicit subscriptions, post-commit broker,
dedupe/version handling, and reconnect resync client are implemented; browser
integration coverage remains incomplete.
Known blockers: S10-S15 gaps listed below, missing `.env.test`, blind evaluator,
and explicit user live-test sign-off.

## Implemented

- S0-S8 backend foundation is implemented through migration head
  `0018_decision_trace_fields`; S9 realtime client/server contract and S11/S12
  sweeper/resource-targeting pieces are implemented.
- FastAPI/PostGIS backend, deterministic seed/reset, auth/RBAC, CRUD, decision
  persistence, acceptance/reservation lifecycle, selected reassessment/simulation
  services, post-commit events, and authenticated WebSocket subscriptions are
  implemented.
- Existing dispatcher, hospital, ambulance crew, and demo-controller workspaces
  remain present with loading, error, stale, unknown, and simulated states, but
  the complete S10/S11 browser flow is not yet verified.
- S13 ML/voice is intentionally skipped because the approved plan provides no
  training data and forbids fabricated accuracy claims.
- Fabricated frontend fallback recommendations were removed; failed matching is
  now non-confirmable.
- Simulation client paths, seeded demo-controller access, and realtime payload
  consumption were aligned with the backend contract.

## Automated verification

- Backend: `58 passed`; Ruff and Python compilation passed.
- PostgreSQL integration: concurrent reservation, rollback, append-only trigger,
  migration round-trip, seed, RBAC, routing, hospital, acceptance, and sweeper
  tests passed.
- Frontend: build, lint, and `11 passed` Vitest tests.
- Mocked Playwright: `6 passed` accessibility and dispatcher tests.
- Live Playwright: not run in this continuation per user instruction.
- Live demo-controller rehearsal: prior session evidence exists, but no new live
  browser/manual smoke was run in this continuation.
- Migration head: `0018_decision_trace_fields`.
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

## Audit Summary — 2026-09-16

- Reviewed all tracked backend, frontend, migration, script, configuration,
  test, and documentation surfaces.
- Fixed confirmed defects in CORS configuration, backend error-envelope
  propagation, acceptance retry semantics, matching retry behavior, sweeper
  scheduling/logging, and destructive resource deletion routes.
- Audit found no committed secret matches and no untracked environment files.
- Audit found no additional confirmed dead-code deletion safe to make without
  broader product decisions. Remaining gaps below are incomplete capabilities,
  not hidden failures.

## `/ambulances` Authentication Investigation

- Root cause confirmed: the backend authentication path was valid, but the
  frontend retained stale JWTs in `localStorage` indefinitely. A later
  `/ambulances` request reused an expired/invalid token and correctly received
  `401 AUTHENTICATION_ERROR`.
- Direct runtime evidence: login returned HTTP 200 and the same fresh Bearer
  token returned HTTP 200 from `/api/v1/ambulances`.
- Fix: shared API wrapper clears the stale token and broadcasts
  `conclave:auth-expired` on any 401; the app returns to login with an explicit
  session-expired message. Canonical backend hospital roles now map to the
  hospital workspace.
- Regression coverage: malformed-token, expired-token, and valid-token backend
  tests plus frontend stale-session and role-mapping tests.
- Direct runtime verification: login returned `200`; the authenticated
  `/api/v1/ambulances` request returned `200` with 10 records.

## Remaining S1-S15 gaps

- S9 browser subscription delivery needs non-live integration coverage.
- S10 complete acceptance/reservation dispatcher UI and generated API types are
  not complete.
- S11 rejection reranking, crew rejection, hospital screens, map/manual mode,
  and reservation cancellation/consume workflows remain partial.
- S12 reroute/compare, reassessment orchestration, and full failure scenarios
  remain partial.
- S14 CORS and audit-completeness test remain.
- S15 demo assets and reproducible `.env.demo` evidence remain.
- Generated OpenAPI frontend types are still absent; handwritten client types
  remain a contract-drift risk.
- Full acceptance/reservation UI wiring is still absent from the dispatcher
  flow even though backend endpoints and role screens exist.
- Production authentication still uses localStorage for the demo token;
  migrate to secure HTTP-only cookies before production deployment.

## Audit findings — 2026-09-16

- Audited 178 tracked files across backend, frontend, migrations, tests, scripts,
  configuration, demos, pitch/docs, and project memory.
- Verified current pitch boundary: dispatcher browser path reaches route
  calculation; backend acceptance/reservation/mission/realtime paths are broader
  than the fully verified browser flow.
- Confirmed production gaps: insecure defaults, localStorage sessions, no CI/CD,
  no backup/restore evidence, process-local realtime, missing generated API types,
  and missing live browser failure coverage.
- Found stale `docs/dod.md` migration/test evidence: it cites 0015/33 while the
  current repository and STATUS evidence are 0018/58.
- Added `handoffs/AMB_HANDOFF_2026-09-16_6.md`; no application source was changed.

## User sign-off

The blind evaluator and configured code-review subagent were unavailable. The
zero-error gate still requires explicit user live-test sign-off after the
remaining S10-S15 work. Do not call the release complete yet.
