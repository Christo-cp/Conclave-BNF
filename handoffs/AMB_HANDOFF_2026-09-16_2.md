# AMB Handoff — 2026-09-16_2

Supersedes `handoffs/AMB_HANDOFF_2026-09-16.md`.

## Implemented this continuation

- S1 database invariants: migration `0016_s1_invariants`, crew scope migration
  `0017_crew_scope`, and decision trace migration `0018_decision_trace_fields`.
- A6 deterministic golden seed now includes `INC-000001`, `MSN-000001`, H-007,
  H-008, all six roles, scenario-backed ambulance/hospital ETAs and routes.
- S2 dispatch/mission RBAC, crew ambulance scope, and missing-resource error
  envelopes.
- S3 ambulance/resource version checks, resource events, audit entries, and
  ORM alignment for UUID mission events.
- S4-S5 provider-backed matching/routing and persisted ambulance/hospital
  decision traces.
- S6-S8 hospital hard-pass freshness/rejection handling, acceptance hold checks,
  expiry release, destination assignment, and role-scoped mission mutation.
- S9 explicit non-empty WebSocket subscription, persistent event/heartbeat loop,
  and frontend subscription on connect.
- S11/S12 hold sweeper, crew assignment accept/reject, targeted resource-loss
  simulation, and reservation resource-event writes.
- Acceptance retry contract coverage and deterministic default scenario inputs
  for non-golden incidents.
- Added `docs/implementation-decisions.md` and corrected README/STATUS honesty.

## Verification

- PostgreSQL backend suite: `54 passed`.
- Ruff: passed.
- Frontend Vitest: `8 passed`.
- Frontend build: passed.
- Secret scans, tracked-env scan, and `git diff --check`: clean.
- Live browser smoke and manual browser tests: intentionally not run per user
  instruction.

## Remaining gaps

- S7 acceptance flow is not yet a complete frontend dispatcher/hospital HTTP
  golden slice; acceptance-key semantics still need a dedicated end-to-end API
  contract test.
- S9 browser delivery needs a non-live WebSocket integration test with a real
  authenticated connection; only broker/client unit coverage exists.
- S10 generated OpenAPI types, dynamic explanation drawer, complete dispatcher
  acceptance UI, and route visualization remain partial.
- S11 rejection reranking, hospital screens, map/manual coordination,
  consume/cancel API coverage, and operational sweeper scheduling remain partial.
- S12 reroute/compare, reassessment orchestration, and full failure scenario
  state transitions remain partial.
- S14 CORS and audit-completeness test remain.
- S15 demo assets and reproducible `.env.demo` evidence remain.
- User live-test sign-off and blind evaluator gate remain outstanding.

## Next work

1. Add API-only golden acceptance/missions test and fix idempotency semantics.
2. Add authenticated WebSocket integration test and generated API types.
3. Implement S11/S12 rejection/rerank/reassessment/reroute flows before UI polish.
