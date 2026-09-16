# ResQFlow S1-S15 Gap Closure Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `subagent-driven-development` or `executing-plans` to implement this plan task-by-task. Do not run live browser smoke tests automatically; the owner will perform manual testing.

**Goal:** Complete the verified S1-S15 gaps while preserving the FastAPI/PostGIS, React/Vite, service-layer, migration, audit, reservation, and post-commit realtime architecture.

**Architecture:** Keep business decisions in backend services and pure decision engines. Add a provider seam for deterministic routing/simulation, use migrations for database invariants, and expose one canonical REST/WebSocket contract consumed by the frontend. Build in dependency order: schema/RBAC/CRUD, matching/routing/acceptance/mission, realtime/UI, reassessment/remaining flows, then hardening/docs.

**Tech Stack:** Python 3.12, FastAPI, SQLAlchemy 2, Alembic, PostgreSQL 16/PostGIS, React 19, TypeScript, Vite, Vitest, React Testing Library, Playwright, Ruff.

## Global Constraints

- Hard constraints run before scoring on every matching path; unknown or stale capacity is never available (`docs/executable-plan.md:581-587`, `AGENTS.md` §9).
- Deterministic input plus configuration produces deterministic output; ties sort by score, ETA, then code (`docs/executable-plan.md:180-220`).
- The chosen routing provider is deterministic mock data labelled `SIMULATED`; no live-looking fabricated fallback is allowed (`docs/spec-conflicts.md:27-46`).
- Reservations use row locks, capacity invariants, idempotency, and post-commit event publication (`docs/executable-plan.md:269-309`).
- Events publish only after commit; rollback publishes neither success events nor success audit rows (`apps/api/app/realtime/broker.py:97-107`).
- No live browser smoke test is run automatically in this implementation session; unit, API, database, static, and build checks may run.
- S13 ML/voice remains skipped and documentation must name FR-023 and FR-032 (`docs/executable-plan.md:811-823`).
- No `.env*` secrets are created, printed, or committed.

## Verified Current-State Gaps

- `apps/api/app/services.py:127,173,206` still derives ETA/route values from identifiers/constants instead of the simulation scenario/provider.
- `apps/api/app/decision_service.py` has no callers, so matching decisions are not persisted.
- `apps/api/app/api/v1/dispatch.py` lacks complete role/scoping coverage and `apps/api/app/api/v1/missions.py` does not enforce mission scope.
- `apps/api/app/api/v1/resources.py` still exposes delete endpoints and resource mutation paths do not write `resource_events` or enforce a payload version.
- `apps/api/app/simulation/seed.py` lacks the A6 golden incident, `MSN-000001`, H-007, and H-008 fixtures.
- `apps/api/app/services.py:193-210` does not pass inactive/stale resource state into hospital eligibility and does not exclude rejected hospitals.
- Acceptance requests are not wired into the dispatcher browser flow, and accept/destination/reservation transitions are not one complete service transaction.
- `apps/api/app/realtime/websocket.py` does not maintain a long-lived explicit subscription loop; `apps/web/src/lib/realtime.ts` does not send a subscription message.
- S11/S12 sweeper, crew rejection, reranking, resource-loss accounting, reroute, and reassessment orchestration are incomplete.
- `docs/implementation-decisions.md` is absent; `docs/dod.md` contains vague evidence rows.

## Task 1: S1 Database Invariants And Golden Seed

**Files:**
- Create: `apps/api/migrations/versions/0016_s1_invariants.py`
- Modify: `apps/api/app/db/models.py`, `apps/api/app/simulation/seed.py`, `apps/api/app/core/config.py`
- Create: `apps/api/tests/db/test_constraints.py`, `apps/api/tests/db/test_spec_cases.py`, `apps/api/tests/db/test_migrations.py`
- Modify: `apps/api/tests/test_seed.py`

**Interfaces:**
- Migration adds partial unique indexes for one active ambulance assignment and one active mission per ambulance, status CHECKs, capacity CHECKs, and append-only triggers for decision tables and event/audit tables.
- Seed produces deterministic A6 fixtures including `AMB-001` through `AMB-005`, H-001 through H-008, golden incident, `MSN-000001`, and all six roles; timestamps and scenario ETAs come from the configured simulation fixture, with H-007 unknown ICU and H-008 stale ICU.

- [ ] Write failing database tests named `test_db_001` through `test_db_006`, `test_capacity_check_rejects_negative`, `test_second_active_assignment_rejected`, `test_mission_events_update_raises`, and `test_seed_is_deterministic`.
- [ ] Run the focused database tests and confirm failures are caused by absent constraints/fixtures, not unavailable PostgreSQL.
- [ ] Add migration `0016_s1_invariants.py` without editing applied migrations; make `downgrade()` remove only objects created by this migration.
- [ ] Update seed/reset to preserve append-only rows during reset, refuse production, and create the exact golden records.
- [ ] Run focused database tests and migration round-trip tests.
- [ ] Run Ruff and Python compilation for touched backend files.

## Task 2: S2 Authentication, RBAC, And Scope

**Files:**
- Modify: `apps/api/app/dependencies.py`, `apps/api/app/api/v1/auth.py`, `apps/api/app/api/v1/dispatch.py`, `apps/api/app/api/v1/missions.py`, `apps/api/app/api/v1/incidents.py`, `apps/api/app/api/v1/resources.py`, `apps/api/app/realtime/auth.py`, `apps/web/src/lib/auth.ts`, `apps/web/src/App.tsx`, `apps/web/src/RoleScreens.tsx`
- Create: `apps/api/tests/test_auth.py`, `apps/api/tests/test_rbac.py`

**Interfaces:**
- Canonical frontend role mapping accepts backend `HOSPITAL_STAFF` and `HOSPITAL_ADMIN` as hospital workspace roles while preserving backend role codes for authorization.
- Dependencies expose role and scope checks for dispatcher, hospital staff/admin, crew, system admin, and demo controller.

- [ ] Add failing tests for unauthenticated access, invalid login, dispatcher-only incident creation, hospital scope, crew mission scope, dispatch roles, simulation roles, and WebSocket channel scope.
- [ ] Implement server-side role dependencies on every dispatch and mission mutation endpoint.
- [ ] Implement JWT logout using the existing architecture by adding a server-side revoked-token identifier store only if the current specification requires invalidation; otherwise document stateless logout as client token removal and test the chosen behavior.
- [ ] Make missing incident/mission/resource responses return the standard 404 error envelope.
- [ ] Align frontend role mapping and route guards with backend role codes without weakening backend checks.
- [ ] Run `pytest apps/api/tests/test_auth.py apps/api/tests/test_rbac.py -v` and frontend auth tests.

## Task 3: S3 CRUD, Versioning, Resource Events, And Audit

**Files:**
- Modify: `apps/api/app/schemas.py`, `apps/api/app/api/v1/resources.py`, `apps/api/app/services.py`
- Create: `apps/api/app/resource_service.py`
- Create: `apps/api/tests/test_slice_crud.py`, `apps/api/tests/test_audit_completeness.py`

**Interfaces:**
- Resource and ambulance mutations require the current `version`; stale writes raise HTTP 409 `CONFLICT` without changing state.
- Resource mutation service writes `resource_events`, audit rows, and post-commit events in one transaction.

- [ ] Add failing tests for stale resource/ambulance updates, lng/lat roundtrip, required incident requirement behavior, hospital scope, and audit/resource-event writes.
- [ ] Move resource mutation logic from route handlers into the service layer and add version predicates/row locks.
- [ ] Remove out-of-plan hard DELETE routes; use status/lifecycle operations instead.
- [ ] Run focused CRUD, RBAC, and audit tests.

## Task 4: Routing Provider And Ambulance Matching

**Files:**
- Create: `apps/api/app/routing/__init__.py`, `apps/api/app/routing/providers.py`, `apps/api/app/routing/service.py`
- Create: `apps/api/app/simulation/heartbeat.py`
- Modify: `apps/api/app/decision_engine/ambulance.py`, `apps/api/app/services.py`, `apps/api/app/decision_service.py`, `apps/api/app/api/v1/dispatch.py`, `apps/api/app/schemas.py`, `apps/api/app/core/config.py`
- Create: `apps/api/tests/test_dispatch_ambulances.py`, `apps/api/tests/test_heartbeat.py`, `apps/api/tests/test_routes.py`

**Interfaces:**
- `RoutingProvider.calculate(origin: Point, destination: Point, context: RouteContext) -> RouteEstimate` returns deterministic distance, duration, congestion, provider, data mode, and confidence metadata.
- `RoutingService.calculate()` executes primary → secondary → cached → manual-review behavior and records `fallback_used` honestly.
- Ambulance matching asks the provider for each ETA, applies hard eligibility first, persists `DecisionRun`/candidate/reason rows, and returns explanations backed by persisted factors.

- [ ] Add failing pure-engine tests for unknown requirements, deterministic output, no score/rank for ineligible candidates, and A4 formula components.
- [ ] Add failing API tests for no-eligible escalation, ineligible confirmation 409, override reason 422, idempotent confirmation, crew accept, and decision persistence.
- [ ] Implement the provider seam and move all ETA/route constants into deterministic simulation scenario data, not identifier arithmetic.
- [ ] Revalidate eligibility at confirmation time, require `override_reason` for non-rank-1 eligible selection, and audit the override.
- [ ] Add heartbeat service that updates only simulated rows not in the skip set and preserves H-008/AMB-005 fixtures.
- [ ] Run matching, route, heartbeat, and RBAC tests.

## Task 5: Hospital Matching And Acceptance/Reservation Vertical Slice

**Files:**
- Modify: `apps/api/app/decision_engine/hospital.py`, `apps/api/app/services.py`, `apps/api/app/acceptance_service.py`, `apps/api/app/reservation_service.py`, `apps/api/app/mission_service.py`, `apps/api/app/api/v1/dispatch.py`, `apps/api/app/api/v1/missions.py`
- Create: `apps/api/app/freshness.py`, `apps/api/app/explanations.py`
- Create: `apps/api/tests/test_hospital_matching.py`, `apps/api/tests/test_acceptance.py`, `apps/api/tests/test_missions.py`, `apps/api/tests/e2e/test_golden_slice.py`

**Interfaces:**
- Hospital matcher performs PostGIS radius expansion using configured radii, passes current/stale/inactive resource state to the pure engine, excludes rejected hospitals for the current chain, persists decision traces, and escalates without recommendations when no candidate passes.
- Acceptance hold locks required resources in ID order, creates HELD reservations/resource events, and creates a PENDING request with the same expiry/key semantics.
- Accept locks request/reservations, confirms all holds atomically, assigns mission destination, writes mission event/notification/audit, and releases all holds exactly once on expiry/rejection.

- [ ] Add failing tests for H-007 unknown capacity, H-008 stale capacity, inactive/zero/missing resources, radius expansion, rejection exclusion, hold atomicity, concurrency, expiry release, retry keys, and cross-hospital acceptance 403.
- [ ] Implement hospital scoring from the executable-plan factors, including pending acceptance/readiness fallback values as named configuration, not ad hoc constants.
- [ ] Fix acceptance idempotency semantics so create and accept use distinct operation keys and retries return stored results.
- [ ] Automatically request rank-1 hospital when confidence allows; keep low-confidence recommendations pending for dispatcher confirmation.
- [ ] Connect acceptance to mission destination and reservation confirmation.
- [ ] Add the complete HTTP golden-slice integration test through mission completion prerequisites, without browser execution.
- [ ] Run hospital, acceptance, reservation, mission, and RBAC tests.

## Task 6: Realtime Contract And Dispatcher Slice

**Files:**
- Modify: `apps/api/app/realtime/websocket.py`, `apps/api/app/realtime/broker.py`, `apps/api/app/realtime/auth.py`, `apps/web/src/lib/realtime.ts`, `apps/web/src/RoleScreens.tsx`, `apps/web/src/App.tsx`, `apps/web/src/lib/api.ts`
- Create: `apps/web/src/lib/api/schema.d.ts` through the pinned OpenAPI generator
- Create: `apps/web/src/components/candidate-list.test.tsx`, `apps/web/src/components/resource-card.test.tsx`, `apps/web/e2e/slice.spec.ts`
- Modify: `apps/web/vite.config.ts`, `apps/web/playwright.config.ts`

**Interfaces:**
- WebSocket accepts one authenticated subscription command with canonical channels, rejects empty/unauthorized channels, then concurrently reads commands and event queue until disconnect.
- Frontend sends the subscription command after connect, filters/deduplicates/version-checks events, and REST-resyncs after reconnect or version gaps.
- Dispatcher UI renders only API candidates and API explanations; matching/routing errors show non-confirmable error/empty states.

- [ ] Add failing backend/frontend realtime tests for subscription, channel isolation, event delivery, heartbeat, reconnect, resync, deduplication, and rollback suppression.
- [ ] Generate API types from `/api/v1/openapi.json` and replace handwritten response interfaces where the generator covers them.
- [ ] Remove all operational fallback candidates and static explanations; render decision reasons from response data only.
- [ ] Complete dispatcher acceptance/reservation controls and live state updates through the REST/WebSocket contract.
- [ ] Add dynamic ETA, score, freshness, data-mode, and route metadata rendering.
- [ ] Run Vitest, TypeScript build, and focused Playwright component/mock tests only; do not run live browser smoke.

## Task 7: S11 Operational Flows And S12 Reassessment

**Files:**
- Create: `apps/api/app/sweeper.py`, `apps/api/app/reassessment_service.py` tests, and failure test modules under `apps/api/tests/failures/`
- Modify: `apps/api/app/simulation/controls.py`, `apps/api/app/api/v1/simulation.py`, `apps/api/app/api/v1/dispatch.py`, `apps/api/app/api/v1/missions.py`, `apps/api/app/acceptance_service.py`, `apps/api/app/mission_service.py`
- Modify: `apps/web/src/RoleScreens.tsx`, `apps/web/src/App.tsx`, `apps/web/src/lib/api.ts`
- Create: `apps/api/tests/test_rejection.py`, `apps/api/tests/test_sweeper.py`, `apps/api/tests/test_crew.py`, `apps/api/tests/test_reservations.py`, `apps/api/tests/test_manual_coordination.py`, `apps/api/tests/test_resource_loss.py`, `apps/api/tests/test_demo_events.py`

**Interfaces:**
- Sweeper is idempotent and expires HELD reservations/requests, restores capacity once, closes requests, audits, and triggers reassessment.
- Simulation actions target the actual mission/resource/route associated with the scenario and call the same domain services as production operations.
- Reassessment releases/supersedes old assignments and reservations before selecting replacements; reroute uses provider comparison and configured minimum gain.

- [ ] Add failing tests for rejection reranking, sweeper, crew rejection, consume/cancel, manual coordination hard constraints, resource-loss rules, reroute, and all named failure cases.
- [ ] Implement domain services and API endpoints without direct arbitrary-row mutation.
- [ ] Add crew accept/reject and hospital incoming/resource screens backed by scoped API responses.
- [ ] Add dispatcher overview/manual coordination and map/offline panels without inventing route data.
- [ ] Run all S11/S12 backend tests and frontend unit tests; do not run browser smoke.

## Task 8: S13-S15 Hardening, Documentation, And Demo Assets

**Files:**
- Create: `docs/implementation-decisions.md`, `.env.demo.example` only if the existing env policy permits it
- Modify: `apps/api/app/main.py`, `apps/api/app/core/config.py`, `README.md`, `docs/dod.md`, `docs/measurements.md`, `STATUS.md`, latest handoff, `docs/demo/golden-scenario.md`, `docs/demo/failure-scenarios.md`
- Create: `apps/api/tests/test_audit_completeness.py`, offline map/unit tests, and deterministic demo configuration tests

**Interfaces:**
- CORS reads configured origins; no secret is committed.
- S13 documentation explicitly names skipped FR-023 and FR-032.
- DoD evidence names exact tests/commands or `none`; no vague “covered by suite” claims.

- [ ] Add failing CORS/audit-completeness/documentation checks.
- [ ] Implement configured CORS and audit coverage for critical transitions.
- [ ] Record routing, simulation, idempotency, expiration, role mapping, stale-data, decision-persistence, and reassessment decisions.
- [ ] Add reproducible demo reset/config instructions without claiming an unrecorded video exists.
- [ ] Run secret scans, Ruff, full backend tests, web build/lint/Vitest, and non-live Playwright tests.
- [ ] Update status/handoff with exact passed, failed, and not-run checks; keep user live sign-off outstanding.

## Verification Matrix

- Database available: run all PostgreSQL migrations, constraint, concurrency, append-only, acceptance, and golden HTTP tests against `smart_ambulance_test`; never use the demo database.
- Database unavailable: run pure engines, static checks, frontend tests/build, and report PostgreSQL tests as `Not run — PostgreSQL unavailable`.
- Always run `git diff --check`, secret scans, Ruff, frontend build, Vitest, and non-live Playwright tests where configured.
- Do not run `LIVE_E2E`, a manual browser rehearsal, or any live smoke test automatically; provide manual instructions to the user after implementation.
