# PROJECT PITCH & CODEBASE ANALYSIS

## Audit Scope And Method

This document is based on the implementation currently present in the repository,
not on the product specification alone. The audit inspected the tracked project
surface: 178 tracked files, 44 backend application files, 20 backend test files,
18 Alembic migration revisions, 17 frontend source files, 3 Playwright specs, 4
scripts, Docker configuration, environment examples, status and handoff records,
demo guides, pitch material, and the project instruction files.

Status labels used below:

- **Implemented:** present in source and supported by automated evidence or a verified runtime path.
- **Partial:** present in code, but incomplete, not wired through the full user flow, or not fully verified.
- **Simulated/demo:** deliberately deterministic, seeded, mocked, or synthetic.
- **Planned:** described in specifications or guides but not demonstrated by current implementation.
- **Broken/risk:** present but currently inconsistent, unsafe for production, or contradicted by evidence.
- **Dead/unused:** present but not shown to be reachable in the current user flow.

## 1. Executive Summary

Conclave is a synthetic emergency-coordination decision-support prototype. It
connects incident intake, patient requirements, ambulance eligibility and ranking,
hospital capability/capacity matching, deterministic route calculation, acceptance
and resource reservation, mission state, realtime updates, and audit history in one
role-aware console.

The strongest implemented idea is not “find the nearest vehicle or hospital.” It
is **constraint-first coordination**: mandatory requirements and data freshness
filter candidates before scoring; unknown or stale capacity is not treated as
available; reservations are server-authoritative and row-locked; and critical
state changes create durable event/audit records. This is implemented on synthetic
data with a mock routing provider, not live hospital feeds and not clinical AI.

The current repository is a credible hackathon MVP foundation, not a production
deployment. The backend foundation through migration `0018_decision_trace_fields`
is substantial. The dispatcher browser flow is verified through ambulance match,
hospital match, and route calculation. Acceptance/reservation, failure
reassessment, and mission progression exist in backend services and role screens,
but the complete browser journey is partial and live failure rehearsals remain
unverified.

## 2. What We Actually Built

The implemented product is a browser-based command console with four practical
workspace types:

- Dispatcher: creates a synthetic incident, adds ICU and ventilator requirements,
  views ranked ambulance candidates, confirms a unit, views ranked hospitals, and
  calculates a route.
- Hospital staff/admin: views scoped resource data and accepts or rejects an
  acceptance request by request ID.
- Ambulance crew: loads a scoped mission, sees the server state version and
  destination/cache state, and submits supported mission transitions.
- Demo controller: triggers controlled simulation actions such as scenario reset,
  traffic change, hospital rejection, resource loss, and stream reconnect.

The API also exposes resource administration, alerts, authentication, mission
state, acceptance, reservation lifecycle, simulation controls, and an authenticated
WebSocket endpoint. The UI and API visibly label operational records as
`SIMULATED` or `DEMO MODE`.

Evidence: `PRODUCT.md:9-19`, `apps/web/src/App.tsx:58-103`,
`apps/web/src/RoleScreens.tsx:30-60`, `apps/api/app/main.py:26-46`.

## 3. Problem Statement

Emergency coordination is a chain of dependent decisions rather than a single
navigation lookup. An operator must determine whether an ambulance is suitable,
whether the destination has the required clinical capability and scarce resource,
whether the hospital will accept the case, and whether the decision remains valid
when information changes.

Manual calls, isolated tracking tools, and static dashboards make it difficult to
answer three questions together:

1. Is this candidate eligible, not merely close?
2. Is the capacity current and confirmed, or unknown/stale?
3. What changed, why did it change, and who approved it?

Conclave addresses that coordination problem as decision support. It does not
claim autonomous clinical decision-making.

## 4. Target Users

The implementation supports these users through roles and scoped endpoints:

| User | Supported workflow |
|---|---|
| Dispatcher | Incident intake, matching, ambulance confirmation, route calculation, operational resource views |
| Hospital staff/admin | Hospital-scoped resource view and acceptance/rejection response |
| Ambulance crew | Ambulance-scoped mission read/update and cached destination view |
| Demo controller | Controlled simulation actions for a synthetic scenario |
| System admin | Broad operational/admin access represented in RBAC |

Evidence: `apps/api/app/core/enums.py:4-10`, `apps/api/app/dependencies.py:51-61`,
`apps/api/app/api/v1/dispatch.py:35-38`, `apps/web/src/RoleScreens.tsx:15-17`.

## 5. Core Solution

Conclave provides a single, auditable coordination loop:

```text
Synthetic incident
  -> mandatory and preferred requirements
  -> hard eligibility filtering
  -> deterministic ambulance ranking
  -> server-confirmed assignment
  -> hospital capability and capacity filtering
  -> deterministic hospital ranking
  -> route estimate from scenario provider
  -> acceptance request and resource hold
  -> hospital acceptance and reservation confirmation
  -> mission/destination state
  -> post-commit realtime event and audit history
```

The current dispatcher UI visibly implements the first part of this loop. The
backend implements additional acceptance, reservation, mission, and event stages.

## 6. Why The Problem Matters

The operational risk is not only delay. A fast but unsuitable match can be worse
than a slower feasible one, and a capacity value that is missing or stale cannot
be treated as a confirmed bed. Conclave's safety-oriented rules make these states
visible and block unsafe confirmation paths.

Defensible benefits supported by the implementation are:

- less manual cross-checking between candidate suitability and destination capacity;
- faster access to a ranked, reason-bearing recommendation;
- explicit handling of stale, unknown, unavailable, and simulated data;
- fewer silent state changes through mission events, notifications, and audit rows;
- server-side protection against double-booking a finite resource;
- a reusable service boundary for later authenticated live providers.

No reduction percentage, clinical outcome, live-feed claim, or accuracy percentage
is supported by this repository.

## 7. How The System Works

### Frontend

The frontend is a React 19/Vite TypeScript app. `App.tsx` owns the dispatcher
shell, login, incident intake, candidate matching, route display, and operational
resource pages. `RoleScreens.tsx` owns hospital, crew, and demo-controller workspaces.
`lib/api.ts` is the shared REST client, and `lib/realtime.ts` owns WebSocket
connection, explicit subscription, exponential reconnect, event dedupe, entity
version checks, and REST resync.

The UI includes loading, error, stale, unknown, empty, and simulated states. It
uses labelled controls, live regions, keyboard-visible controls in the CSS/design
surface, and responsive navigation. The main dispatcher map is a styled mock map,
not a live map tile integration.

Evidence: `apps/web/src/App.tsx:108-188`,
`apps/web/src/components/decision-state.tsx:5-32`,
`apps/web/src/lib/realtime.ts:31-85`, `PRODUCT.md:32-43`.

### Backend request lifecycle

```text
Browser request
  -> FastAPI router under /api/v1
  -> request context, auth token, role and scope checks
  -> Pydantic request schema
  -> service/orchestration function
  -> SQLAlchemy session and PostgreSQL/PostGIS transaction
  -> audit/event/notification rows
  -> commit
  -> post-commit broker event
  -> browser WebSocket consumer or REST resync
```

FastAPI mounts auth, health, alerts, incidents, dispatch, missions, resources,
simulation, and WebSocket routes. Exceptions are returned in the project's
structured error envelope. Database sessions roll back on exceptions and close
after each request.

Evidence: `apps/api/app/main.py:26-46`, `apps/api/app/dependencies.py:16-45`,
`apps/api/app/core/errors.py`, `apps/api/app/core/middleware.py`.

## 8. End-To-End Workflow

### Verified browser path

1. User opens the login page with prefilled synthetic demo credentials.
2. Login returns a JWT and the UI enters the dispatcher workspace.
3. Dispatcher submits a trauma incident at the seeded Bengaluru demo location.
4. The UI adds required ICU and ventilator requirements.
5. Backend ranks ambulance candidates and returns eligible and ineligible records
   with reasons.
6. Dispatcher confirms the eligible ambulance with an idempotency key.
7. Backend creates assignment/mission records and publishes a post-commit event.
8. UI queries hospital candidates after ambulance confirmation.
9. Dispatcher selects an eligible hospital and calculates a route.
10. UI displays the deterministic mock route, duration, confidence, and simulated label.

This path is covered by mocked Playwright and an opt-in live Playwright spec. The
current live spec stops after route calculation.

Evidence: `apps/web/e2e/golden.spec.ts:3-32`,
`apps/web/e2e/live-golden.spec.ts:3-20`, `STATUS.md:57-65`.

### Backend-supported continuation

The backend can create an acceptance request, hold required resources, accept or
reject the request, confirm reservations, assign a destination only when a
confirmed reservation exists, transition a mission using a state version, expire
holds through the lifespan sweeper, and record mission events/notifications/audit
rows. The complete browser wiring for this continuation is not verified.

Evidence: `apps/api/app/services.py:253-320`,
`apps/api/app/mission_service.py:21-58`, `apps/api/app/sweeper.py:11-24`,
`apps/api/app/api/v1/dispatch.py:97-169`.

## 9. Architecture

```text
React 19 + Vite + TypeScript
  | REST /api/v1 and WebSocket /api/v1/ws
  v
FastAPI application
  | auth/RBAC, schemas, error envelope, request context
  v
Service orchestration
  | matching, routing, acceptance, reservation, mission, sweeper, simulation
  v
Pure decision engines + routing provider interface
  | hard filters before deterministic ranking
  v
SQLAlchemy 2 session
  v
PostgreSQL 16 + PostGIS
  | transactional state, constraints, audit/event history, spatial columns
  v
Post-commit in-process event broker
  v
Authenticated WebSocket consumers + REST resync
```

This is a modular monolith, not a microservice deployment. The broker is
in-process, so it is suitable for the controlled prototype but would need a
shared event transport for multiple API instances.

## 10. Technology Stack

| Layer | Technology | Actual usage |
|---|---|---|
| Frontend | React 19, TypeScript, Vite | Dispatcher and role workspaces |
| UI/state | React hooks, React Router, Zustand/TanStack dependencies, React Hook Form dependencies, Lucide, Recharts dependencies | Current screens primarily use React local state; shared REST/realtime helpers are custom |
| Backend | Python 3.12, FastAPI, Uvicorn | REST API, lifecycle, OpenAPI, WebSocket mounting |
| Persistence | SQLAlchemy 2, Alembic, psycopg | ORM models, transactions, migrations |
| Database | PostgreSQL 16 + PostGIS | Spatial entities, constraints, resource state, event/audit tables |
| Validation/config | Pydantic/Pydantic Settings | Request schemas and environment settings |
| Authentication | PyJWT, Argon2 | Bearer JWT issuance/verification and password hashing |
| Realtime | FastAPI WebSocket + in-process async broker | Authenticated subscriptions, dedupe, version handling, post-commit publication |
| Routing | Internal `RoutingProvider` protocol + `MockRoutingProvider` | Deterministic scenario ETAs/routes labelled simulated |
| Infrastructure | Docker Compose | Local PostGIS only; no deployment manifest |
| Testing | Pytest, Ruff, Vitest, React Testing Library, Playwright | Backend/database, frontend unit, mocked browser/accessibility, opt-in live browser |

Evidence: `apps/api/pyproject.toml:5-27`, `apps/web/package.json:14-39`,
`docker-compose.yml:1-12`.

## 11. Feature Inventory

| Feature | Status | Evidence | Reality |
|---|---|---|---|
| Login, JWT, password verification | Implemented/demo | `apps/api/app/api/v1/auth.py:13-30`, `apps/api/app/services.py:88-97` | Bearer token flow works; demo token is stored in browser localStorage |
| Role-based access | Implemented | `apps/api/app/dependencies.py:30-57`, `apps/api/tests/test_rbac.py` | Server-side role checks and hospital/ambulance scope checks |
| Incident intake | Implemented/demo | `apps/api/app/services.py:100-108`, `apps/web/src/App.tsx:163-170` | Creates simulated incidents with PostGIS point |
| Tri-state requirements | Implemented | `apps/api/app/core/enums.py:43-47`, `apps/api/app/db/models.py:74-81` | Required/preferred/unknown model exists; current UI adds fixed required ICU/ventilator tags |
| Ambulance hard filtering and ranking | Implemented | `apps/api/app/decision_engine/ambulance.py:24-55` | Availability, active mission, GPS freshness, equipment before score |
| Hospital hard filtering and ranking | Implemented | `apps/api/app/decision_engine/hospital.py:23-54` | Capability, unknown/stale/unavailable capacity before score |
| Decision trace persistence | Implemented | `apps/api/app/db/models.py:237-267`, `apps/api/app/services.py:142-143` | Candidates, eligibility, scores, reasons, snapshots, versions |
| Ambulance confirmation | Implemented/verified | `apps/api/app/services.py:159-184`, `apps/web/e2e/live-golden.spec.ts:15-16` | Server validates eligibility and requires reason for non-top eligible override |
| Deterministic routing | Implemented/simulated | `apps/api/app/routing/providers.py:29-56` | Reads `GOLDEN_2026`; missing routes fail rather than fabricate |
| Hospital acceptance request | Implemented backend/partial UI | `apps/api/app/services.py:253-277`, `apps/web/src/RoleScreens.tsx:30-41` | Backend holds required resources; UI requires manually entered request ID |
| Reservation lifecycle | Implemented backend/partial UI | `apps/api/app/reservation_service.py:14-114` | Hold, confirm, release, expire, cancel, consume; complete dispatcher UI absent |
| Concurrent capacity protection | Implemented/tested | `apps/api/tests/test_reservation_postgres_integration.py:112-180` | Exactly one concurrent reservation wins in PostgreSQL integration test |
| Mission transitions | Implemented backend/partial UI | `apps/api/app/services.py:323-356`, `apps/web/src/RoleScreens.tsx:44-52` | State/version checks; crew screen exposes only selected actions |
| Destination change audit | Implemented backend | `apps/api/app/mission_service.py:21-38`, `apps/api/app/services.py:311-318` | Mission event, notification, audit record |
| Realtime WebSocket | Implemented core/partial UI | `apps/api/app/realtime/websocket.py:15-70`, `apps/web/src/lib/realtime.ts:31-85` | Explicit channels, auth, dedupe/version/resync; browser integration incomplete |
| Reservation hold sweeper | Implemented | `apps/api/app/lifespan.py:13-38`, `apps/api/app/sweeper.py:11-24` | Periodic expiration, logging on failure |
| Demo simulation controls | Implemented/simulated | `apps/api/app/api/v1/simulation.py:12-18`, `apps/web/src/RoleScreens.tsx:55-60` | Controlled state changes, not live operational feeds |
| Operational fleet/hospital/alert views | Implemented/partial | `apps/web/src/App.tsx:115-133`, `apps/api/app/api/v1/resources.py:93-227` | REST-backed role-aware views; no live external feed |
| ML arrival prediction | Planned/not built | `README.md:67-71`, `STATUS.md:35` | S13 intentionally skipped; no model or training data |
| Voice control | Planned/not built | `README.md:69-71` | S13 intentionally skipped |
| Live hospital integration | Planned/not built | `README.md:72-73`, `docs/pitch/slides.md:26-32` | Provider/service boundary exists; no live integration |
| Production deployment/CI | Not implemented | No `.github`, Dockerfile, or deployment manifest | Local Docker database only |

## 12. Core Innovation

### Existing problem

Operational teams often coordinate ambulance, destination, acceptance, capacity,
and route decisions across disconnected channels.

### Limitation

Nearest-first or static workflows can ignore mandatory clinical fit, stale
capacity, competing reservations, and the audit trail needed to explain a change.

### Our approach

Conclave treats emergency coordination as a constrained stateful workflow. It
filters unsafe candidates first, ranks only eligible options, reserves scarce
resources transactionally, and exposes state changes to role-specific workspaces.

### Mechanism

- Pure decision engines reject mandatory constraint failures before scoring.
- SQL row locks and capacity checks protect finite resources.
- Idempotency keys prevent duplicate mutation results.
- Mission `state_version` rejects stale writes.
- A post-commit broker emits versioned events; clients resync through REST after
  reconnect or a version gap.
- Decision traces, mission events, notifications, and audit logs preserve reasons
  and transitions.

### Outcome

The prototype enables a dispatcher to see not only a recommendation, but why
other candidates were excluded, whether capacity is trustworthy, and how a
confirmed decision is represented in server state.

## 13. Key Algorithms / Business Logic

### Ambulance matching

`evaluate_ambulances` checks status, active mission, GPS freshness, and required
equipment. Ineligible candidates receive no score or rank. Eligible candidates
receive a deterministic weighted score using ETA, required/preferred equipment,
and freshness; ties use ETA and code ordering.

### Hospital matching

`evaluate_hospitals` checks active status, required capabilities, and required
resource values. Missing capacity is unknown, stale capacity is rejected, and
zero capacity is unavailable. Only eligible hospitals are scored.

### Reservation safety

`ReservationService.reserve` locks the hospital resource, rejects unknown or
insufficient capacity, decrements available capacity, increments reserved
capacity, increments the resource version, and commits the reservation plus
resource event in one transaction.

### Mission safety

Mission transitions are explicit and sequential. A write must carry the current
`state_version`; stale clients receive `MISSION_STATE_CONFLICT`. Travel to a
hospital requires a selected destination, and destination assignment requires a
committed confirmed reservation.

Evidence: `apps/api/app/decision_engine/ambulance.py:34-55`,
`apps/api/app/decision_engine/hospital.py:31-54`,
`apps/api/app/reservation_service.py:18-38`,
`apps/api/app/services.py:334-356`, `apps/api/app/mission_service.py:21-58`.

## 14. Database Architecture

The SQLAlchemy model layer defines users/roles, incidents, patient requirements,
ambulances/equipment, hospitals/capabilities/resources, assignments, missions,
routes, acceptance requests, reservations, decision traces, mission events,
notifications, simulation scenarios, resource events, and audit logs.

Important relationships:

```text
User -> roles, optional hospital, optional ambulance
Incident -> requirements, assignment, mission, routes, events, notifications, audits
Hospital -> capabilities and finite resources
Mission -> ambulance, optional hospital, optional route, state version
AcceptanceRequest -> reservations -> hospital resource
DecisionRun -> candidates -> reasons
SimulationScenario -> deterministic ETAs and route estimates
```

PostGIS geography point columns store incident, ambulance, hospital, route origin,
and route destination. Migration history currently reaches `0018` and includes
resource invariants, assignment guards, audit indexes, simulation state, crew
scope, and decision trace fields.

The seed creates 10 simulated hospitals, 10 ambulances, capability/resource
differences designed to demonstrate exclusion, and a `GOLDEN_2026` scenario. It
also creates synthetic demo users sharing the local-only password
`demo-password-change-me`.

Evidence: `apps/api/app/db/models.py:27-310`,
`apps/api/app/simulation/seed.py:40-158`,
`apps/api/migrations/versions/0001_mvp_schema.py` through
`apps/api/migrations/versions/0018_decision_trace_fields.py`.

## 15. API Architecture

The API prefix is `/api/v1`, with OpenAPI at `/api/v1/openapi.json`.

| Route family | Actual purpose |
|---|---|
| `/auth` | Login, logout, current user, token refresh |
| `/incidents` | Create/read incidents and requirements |
| `/dispatch/ambulances` | Match and confirm ambulance |
| `/dispatch/hospitals` | Match hospitals |
| `/routes/calculate` | Calculate route through provider interface |
| `/acceptance-requests` | Create/get/accept/reject hospital acceptance |
| `/reservations` | Create/get/release/expire/consume/cancel reservations |
| `/missions` | List/read/patch mission and assign destination |
| `/ambulances`, `/hospitals`, `/resources` | Resource and capacity views/admin mutations |
| `/alerts` | Active persisted alerts |
| `/admin/simulation` | Demo-controller/system-admin simulation controls |
| `/ws` | Authenticated explicit-channel WebSocket |

Errors preserve an envelope with code, message, and request context. Auth and
scope checks happen server-side rather than relying on UI hiding.

Evidence: `apps/api/app/main.py:38-46`, `apps/api/app/api/v1/*.py`,
`apps/api/app/core/errors.py`.

## 16. Realtime Architecture

Writes queue event envelopes in the SQLAlchemy session. The broker publishes them
after the transaction commits. The WebSocket authenticates the user, requires a
non-empty explicit subscription, checks channel scope, supports heartbeat, and
closes unauthorized subscriptions. The browser keeps a bounded dedupe set,
rejects old entity versions, and calls REST resync when it reconnects or sees a
version gap.

This is a meaningful reliability pattern for a prototype. It is not a distributed
message bus: the broker is process-local, so multi-instance deployment would need
shared event infrastructure and connection coordination.

Evidence: `apps/api/app/realtime/broker.py:58-128`,
`apps/api/app/realtime/websocket.py:15-70`,
`apps/web/src/lib/realtime.ts:43-79`, `apps/api/tests/test_realtime.py:12-52`.

## 17. Authentication & Security

### Strengths

- Argon2 password hashing is used for demo user passwords.
- JWTs are signed and checked server-side with user existence/status validation.
- Roles and resource scopes are enforced in API dependencies and route helpers.
- Idempotency keys exist on critical mutation paths.
- Input schemas and structured API errors are present.
- PostgreSQL constraints, append-only event/audit protections, row locks, and
  optimistic version checks protect important state.
- CORS origins are configuration-driven rather than hard-coded to all origins.
- Synthetic data and demo labels are explicit.

### Gaps and risks

- Browser JWTs are stored in `localStorage`; production should use secure
  HTTP-only cookie sessions.
- Settings contain development defaults, including a built-in JWT secret; a
  production deployment must fail closed on missing secrets.
- No rate-limiting middleware or login throttling was found.
- CORS allows all methods and headers and is not cookie-session-ready.
- The demo password is intentionally shared and must remain confined to an
  isolated local synthetic environment.
- No verified backup/restore, deployment hardening, security-header policy, or
  CI security gate is present.

Evidence: `apps/api/app/core/config.py:21-46`,
`apps/api/app/dependencies.py:30-55`, `apps/web/src/lib/api.ts:24-31`,
`STATUS.md:67-85`, `docs/dod.md:62-69`.

## 18. Demo Workflow

### Strongest reproducible current demo

The safest demo is the verified dispatcher golden path:

1. Start local PostGIS with `docker compose up -d postgres`.
2. Reset the synthetic database using the local environment and
   `scripts/reset_demo.py`.
3. Start FastAPI and Vite.
4. Log in with the synthetic dispatcher demo account.
5. Create a critical trauma incident with ICU and ventilator requirements.
6. Show an unsuitable ambulance excluded with a reason such as missing equipment,
   stale GPS, unavailable status, or active mission.
7. Select the eligible ambulance and confirm it.
8. Show the hospital candidate list with capability/capacity reasons.
9. Select the eligible hospital and calculate the mock route.
10. Point out the `SIMULATED` and `MOCK ROUTING` labels.

The seeded live smoke evidence recorded `AMB-002`, `H-003`, and a 600-second mock
route. The deterministic matcher measurement recorded p50 `0.009 ms` and p95
`0.012 ms` across 50 pure matcher samples; this is not HTTP, database, browser,
or production latency.

Evidence: `docs/demo/golden-scenario.md:6-23`,
`docs/measurements.md:15-26`, `STATUS.md:54-65`.

## 19. Current Implementation Reality

| Area | Current reality | Production requirement |
|---|---|---|
| Data | Deterministic seeded PostgreSQL/PostGIS records; all operational demo data is synthetic | Authenticated hospital, ambulance, GPS, and capacity feeds with provenance and freshness contracts |
| Matching | Pure deterministic rule/filter/rank functions | Validated domain policy, operational calibration, monitoring, and broader scenario coverage |
| Routing | Mock provider reads `GOLDEN_2026` and returns simulated estimates | Live provider behind the same interface, failover, quotas, observability, and map integration |
| Authentication | JWT bearer flow; browser stores token locally | HTTP-only secure session strategy, secret enforcement, refresh/revocation policy, throttling |
| Authorization | Server-side RBAC and entity scope checks | Formal role review, tenant/site policy, security testing, and operational identity integration |
| Realtime | Authenticated in-process broker and WebSocket with resync | Shared broker, multi-instance connection strategy, delivery monitoring, backpressure |
| Reservations | Row locks, idempotency, capacity checks, database integration tests | Operational reconciliation, recovery, backup/restore, incident response, concurrency/load testing |
| Notifications | Persisted notification rows and realtime metadata | Verified delivery channel(s), retry/dead-letter policy, human acknowledgement workflow |
| Demo control | Explicit simulation endpoints and seeded scenario | Separate non-production control plane and audited scenario fixtures |
| Deployment | Docker Compose starts only PostGIS | CI/CD, migrations, secrets, health checks, rollback, monitoring, backups |

## 20. Implemented vs Simulated vs Planned

### Implemented

FastAPI routing, SQLAlchemy models, Alembic migration chain, RBAC, incident and
requirement persistence, deterministic matching, route provider boundary,
acceptance/reservation backend, mission state/version checks, sweeper, simulation
controls, audit/event persistence, realtime core, React screens, frontend error
and stale-state components, backend tests, frontend tests, and mocked browser
tests.

### Simulated/demo

All hospitals, ambulances, capacities, GPS, ETAs, routes, alerts, users, and
scenario changes. The routing provider is explicitly mock. The dispatcher map is
visual simulation, not live map tiles. Acceptance/resource changes are only
synthetic local scenarios.

### Planned or intentionally not built

ML arrival-time prediction, voice control, production hospital integrations, live
capacity feeds, live routing/map integration, complete S10-S12 browser workflows,
generated API types, deployment automation, backup/restore evidence, and full
live failure rehearsal.

### Broken/risk/inconsistent

- README setup refers to `.env.test`/`.env.demo`, but the repository only commits
  `.env.example`; clean-checkout setup requires creating those files locally.
- `docs/dod.md` contains stale migration/test counts even though `STATUS.md` and
  the source show migration `0018` and 58 backend tests.
- Production authentication and default secret handling are not safe for release.
- The documented full wow sequence is broader than the live browser spec.

### Dead/unused or not proven reachable

The audit found no safe deletion candidate to claim as dead without a product
decision. Several backend tables and service paths are more complete than the
current browser flow, so they should be described as backend-supported/partial,
not silently treated as unreachable or complete.

## 21. Testing & Verification

Current evidence recorded in `STATUS.md`, handoffs, and the audit surfaces:

```text
Backend pytest: 58 passed
Ruff: passed
Frontend build: passed
Vitest: 4 files, 11 tests passed
Mocked/accessibility Playwright: 6 passed
Live Playwright golden spec: opt-in and skipped unless LIVE_E2E=1
Migration head: 0018_decision_trace_fields
PostgreSQL integration: concurrent reservation and migration/resource/audit tests passed
Secret scans and git diff --check: passed
```

Covered behavior includes hard-constraint exclusion, unknown/stale resource
handling, reservation concurrency and rollback, invalid mission transitions,
RBAC, post-commit event behavior, seed protection, routing provider behavior,
authentication/session recovery, and UI loading/error/stale/simulated states.

Critical unverified paths include complete browser acceptance/reservation,
live browser failure scenarios, reroute/compare, full reassessment orchestration,
backup/restore, production deployment, and multi-instance realtime.

Warnings recorded during verification include Starlette/httpx and AnyIO test-client
deprecations and JWT key-length warnings. The project has not received the blind
evaluator quality gate or explicit owner live-test sign-off.

## 22. Known Limitations

- Synthetic data only; no live hospital or ambulance feed.
- Mock routing; no production route provider or map tile integration in the current UI.
- Complete acceptance/reservation flow is not wired through the dispatcher browser path.
- Browser failure scenarios and reassessment are documented more broadly than tested.
- In-process realtime broker does not support independent API instances without redesign.
- Handwritten frontend API interfaces create contract-drift risk; generated OpenAPI types are absent.
- LocalStorage bearer tokens and insecure development defaults block production readiness.
- No CI/CD, deployment manifest, verified rollback, or backup/restore procedure.
- Shared demo password is appropriate only for disposable synthetic local data.
- ML and voice are intentionally absent, not hidden capabilities.

## 23. Production Readiness

### Architecture health: Strong foundation, incomplete operational hardening

The separation between routes, services, pure decision engines, persistence,
realtime, and simulation is clear enough for a prototype. Transactional and
state-version controls are stronger than a dashboard-only implementation.

### Feature completeness: Partial

The backend foundation is broad, but the end-user browser workflow stops before
the most consequential acceptance/reservation/failure sequence.

### Code quality: Adequate with known risks

The code has focused modules, typed request models, and tests. Current risks are
contract drift, stale documentation, development defaults, and limited operational
instrumentation/deployment structure.

### Test coverage: Strong for core invariants, incomplete for the product journey

Database concurrency, safety constraints, RBAC, and core state behavior have
meaningful tests. Browser coverage does not yet prove the full pitch sequence.

### Security: Prototype-grade

Authentication and authorization exist, but production session handling, secret
enforcement, throttling, and deployment controls are incomplete.

### Reliability: Good local-state safeguards, limited distributed resilience

Row locks, idempotency, append-only records, post-commit events, and REST resync
are positive. Backup/restore, multi-instance events, and full live failure
rehearsal are unverified.

### Documentation: Good product honesty, some drift

README, PRODUCT, demo guides, pitch support, status, and handoffs clearly label
simulation and limits. `docs/dod.md` needs migration/test evidence refresh.

### Production readiness: Not ready

The repository is suitable for a controlled synthetic demonstration, not for live
clinical or operational deployment.

## 24. Scalability

### Current architecture

The API is mostly stateless at the request layer, with PostgreSQL as the source of
truth and WebSockets for operator updates. The database has indexes, versioned
resources, transaction boundaries, and spatial columns. The deterministic matcher
is computationally small in the measured local scenario.

### Current limitations

- The broker is process-local.
- There is no queue, shared pub/sub, cache, rate limiter, or deployment topology.
- Full HTTP/database/browser throughput is not measured.
- Resource and mission workflows need operational reconciliation and observability.
- The current seed and UI assume small bounded demo data.

### Scaling path

1. Replace localStorage tokens and development defaults with production identity/session controls.
2. Add CI/CD, migration gates, backups, rollback, health checks, and structured metrics.
3. Move realtime fan-out to a shared broker and define event delivery semantics.
4. Add authenticated provider adapters for routing, GPS, capacity, and hospital acceptance.
5. Load-test reservation contention, matching, API latency, WebSocket fan-out, and failure recovery.
6. Introduce partitioning/archival and operational tenancy only after real workload evidence.

## 25. Future Roadmap

### Phase 1: Current MVP

Complete and live-test the acceptance/reservation browser flow, make failure
scenarios reproducible from the UI, refresh stale DoD evidence, and ship a
reproducible demo environment.

### Phase 2: Production hardening

HTTP-only sessions, secret validation, throttling, security headers, generated
OpenAPI types, CI, backups/restores, migrations/rollback, monitoring, and full
live browser regression paths.

### Phase 3: Real-world integrations

Authenticated hospital capacity/acceptance adapters, ambulance/GPS feeds, live
routing provider, provider freshness/provenance, integration retries, and
reconciliation workflows.

### Phase 4: Advanced intelligence

Only after approved data and evaluation design: arrival-time prediction, route
comparison, learned ranking assistance, and voice input. Hard constraints remain
authoritative over any model output.

### Phase 5: Scale

Shared event transport, multiple API instances, workload isolation, operational
analytics, multi-site policy, and measured capacity planning.

## 26. Differentiation

| Conventional approach | Conclave approach |
|---|---|
| Phone calls and spreadsheets connect decisions manually | One workflow links incident, ambulance, hospital, reservation, route, and mission state |
| Nearest candidate may be selected first | Mandatory capability, equipment, availability, and freshness filter before scoring |
| Unknown capacity may be mistaken for free capacity | Unknown/stale capacity is explicitly excluded or blocked |
| Client/UI may imply a reservation | Server-side row-locked transaction is authoritative |
| State changes are hard to reconstruct | Decision traces, mission events, notifications, resource events, and audits persist the change |
| Static dashboard data can overwrite newer state | Mission state versions reject stale writes; realtime client resyncs after gaps |
| Demo systems hide simulation | `DEMO MODE` and `SIMULATED` labels are part of the UI and data model |

This is workflow and architecture differentiation, not a claim of unique market
position or superiority over named competitors.

## 27. Impact

The implementation supports operational impact language that is specific but not
quantified:

- centralizes the emergency coordination sequence;
- reduces manual suitability and capacity cross-checking;
- makes exclusions and data freshness visible;
- prevents confirmed reservations from exceeding tested resource capacity;
- gives operators a reason-bearing trail for decisions and changes;
- provides a foundation for later live integrations without presenting synthetic
  data as clinical truth.

The repository does not support claims about lives saved, percentage improvement,
clinical accuracy, production response time, or real-world deployment outcomes.

## 28. 60-Second Pitch

Emergency dispatch is not just about finding the closest ambulance. The operator
must find a vehicle with the right equipment, a hospital with the right capability
and current capacity, obtain acceptance, and keep the decision correct as the
situation changes. Conclave is a synthetic emergency-coordination console that
connects those decisions in one auditable workflow. It filters out unsuitable or
stale candidates before ranking, uses server-side transactions to hold scarce
resources without double-booking, and records mission, notification, realtime,
and audit events after committed state changes. Today it runs on clearly labelled
synthetic data with deterministic mock routing, so this is decision support, not
clinical autonomy. The prototype proves the safety-oriented coordination
architecture and the dispatcher path from incident to ambulance, hospital, and
route, while making the production gaps explicit.

## 29. 3-Minute Pitch

Imagine a critical trauma incident arrives. A dispatcher cannot safely solve it by
choosing the nearest ambulance and nearest hospital. The ambulance needs the
right equipment, the destination needs the right clinical capability, and a scarce
ICU or ventilator must still be available when the hospital responds.

Conclave is our emergency coordination decision-support console. The dispatcher
starts a synthetic incident and records mandatory patient requirements. The system
evaluates every ambulance using hard constraints first: availability, active
mission state, GPS freshness, and required equipment. Only eligible candidates are
scored and ranked. The UI shows both the recommendation and the exclusion reasons,
so the operator can see why a closer unit was not suitable.

After the ambulance is confirmed, Conclave evaluates hospitals. It checks required
capabilities and capacity, and it fails closed when a capacity value is missing,
zero, or stale. The dispatcher can then calculate a route through a deterministic
mock provider. Every demo value is visibly labelled simulated.

Behind the UI is a FastAPI and PostgreSQL/PostGIS application. Its service layer
persists decision traces, assignments, routes, acceptance requests, reservations,
mission events, notifications, and audit records. Resource reservations are
server-authoritative: the resource row is locked, capacity is checked, and the
hold is committed transactionally. A PostgreSQL integration test proves that two
concurrent reservations for one unit produce exactly one winner.

The system also has role-scoped hospital and ambulance-crew workspaces, a demo
controller for controlled failure simulations, and an authenticated WebSocket
layer. Events are published after commit, clients deduplicate them, reject older
versions, and resync from REST after reconnect or a version gap.

Our honest boundary is important. This is not live hospital data, not a live
routing deployment, and not autonomous clinical software. The current browser
demo is verified through ambulance match, hospital match, and route calculation;
the backend supports more acceptance, reservation, and mission behavior than the
browser currently wires end to end. Our next step is production hardening and
authenticated real-world adapters, while preserving the rule that hard safety
constraints always outrank optimization or future ML.

## 30. 5-Minute Technical Pitch

Conclave is a modular-monolith emergency coordination prototype. The frontend is
React 19 with Vite and TypeScript. It communicates with a FastAPI Python 3.12
backend under `/api/v1` and an authenticated `/api/v1/ws` WebSocket. PostgreSQL
16 with PostGIS is the system of record, accessed through SQLAlchemy 2 and Alembic.

The request lifecycle begins with a dispatcher login. The API verifies an Argon2
password hash, issues a JWT, and later validates the bearer token against an active
database user. Route dependencies enforce roles and entity scope. Dispatcher
incident creation writes a PostGIS point, synthetic data mode, status, and audit
record. Patient requirements are stored as separate rows with REQUIRED,
PREFERRED, or UNKNOWN levels.

Ambulance matching is a pure function. The service loads required equipment,
active mission IDs, ambulance records, and scenario ETAs. The engine first rejects
non-available units, units with active missions, stale GPS, or missing mandatory
equipment. It then scores only survivors using deterministic factors and breaks
ties by ETA and code. Results, reasons, input snapshots, freshness configuration,
algorithm version, and config version are persisted as decision trace records.

Hospital matching follows the same constraint-first shape. It loads capabilities,
resources, stale thresholds, rejection history, and scenario ETAs. Missing, stale,
zero, or inactive mandatory resources are not scored as viable. The frontend shows
this as candidate cards with eligible states, reasons, age, and simulation labels.

Routing is behind a provider protocol. The current `MockRoutingProvider` reads
`GOLDEN_2026` configuration, returns distance, duration, traffic duration,
confidence, provider, and simulated mode, and raises an error if a route is not
defined. It does not silently invent a constant route. A live provider can later
be added behind the same service boundary, but no live provider is currently
configured.

The reservation path is the strongest reliability feature. It locks a
`HospitalResource` row with `FOR UPDATE`, rejects inactive or unknown capacity,
updates available/reserved counts and the optimistic version, inserts the
reservation and resource event, and commits. The test suite runs concurrent
PostgreSQL attempts and confirms one success and one failure. Acceptance holds
expire through an API lifespan sweeper. Accepting a request confirms associated
reservations, updates the incident and mission destination, and creates a mission
event, notification, and audit record.

Mission writes use a `state_version` supplied by the client. Invalid transitions
and stale writes are rejected. Destination changes require a confirmed reservation.
The realtime broker queues events against the SQLAlchemy session and publishes
only after commit. The WebSocket requires explicit, authorized channels and sends
heartbeat messages. The browser deduplicates event IDs, ignores old entity
versions, and resyncs through REST after reconnect or a version gap.

The current tests cover backend APIs and lifecycle, RBAC, deterministic matching,
hospital matching, routing, reservations, realtime, simulation, seed behavior,
and sweeper behavior. Frontend tests cover API error/session behavior and decision
states. Playwright covers mocked dispatcher/accessibility journeys, while the live
golden test is opt-in and currently ends at route calculation. There is no CI/CD,
verified backup/restore, production session security, shared realtime bus, or
external hospital integration.

The result is a technically credible synthetic prototype: the value is the
constraint-first, auditable, transactional coordination architecture. The honest
next step is not to claim a finished clinical platform; it is to finish the
browser lifecycle, harden deployment and identity, connect authenticated providers,
and evaluate any future predictive intelligence without allowing it to override
hard constraints.

## 31. Slide-By-Slide Presentation

| # | Title | Main message | Content / visual | Speaker cue | Time |
|---:|---|---|---|---|---:|
| 1 | Conclave | Emergency coordination needs more than a nearest-resource lookup | Product name, simulated-data notice, command-console screenshot | “We coordinate the chain of decisions around an emergency.” | 15s |
| 2 | The problem | Suitability, capacity, acceptance, and route are connected | Four disconnected workflow icons | “The dangerous gap is between a recommendation and a confirmed resource.” | 25s |
| 3 | Why existing workflows fall short | Manual and static tools hide constraints and freshness | Conventional vs connected workflow | “A close resource can still be unsuitable or unknown.” | 20s |
| 4 | Our solution | One constraint-first, auditable coordination loop | Incident → match → reserve → mission diagram | “Conclave keeps the decision and its explanation together.” | 25s |
| 5 | How it works | Hard filters precede scoring | Candidate cards showing eligible/ineligible reasons | “No mandatory failure receives a score.” | 30s |
| 6 | Architecture | React, FastAPI, PostgreSQL/PostGIS, services, realtime | Layered architecture diagram | “The browser is not the source of truth; the transaction is.” | 30s |
| 7 | Core innovation | Safety and traceability are built into state transitions | Filter-before-score and row-lock diagram | “This is coordination logic, not decorative dashboard logic.” | 30s |
| 8 | Key features | Roles, matching, route, acceptance, reservations, audit | Four workspace thumbnails and feature strip | “Each role sees only the operational surface it needs.” | 25s |
| 9 | End-to-end workflow | The current verified path is deterministic and reproducible | Numbered golden path | “The live browser evidence currently reaches route calculation.” | 25s |
| 10 | Live demo | Show the dispatcher path | Login, incident, exclusion, ambulance, hospital, route | Perform the verified path; keep simulated labels visible. | 75s |
| 11 | Technical implementation | Decisions and state are persisted, not faked in the client | Entity relationship / transaction callout | “Decision traces and resource events make the outcome inspectable.” | 35s |
| 12 | Security and reliability | RBAC, locks, idempotency, versions, post-commit events | Shield + transaction + event timeline | “The prototype has meaningful safeguards, with explicit production gaps.” | 35s |
| 13 | MVP vs production | Synthetic demo is not a live clinical platform | Reality matrix | “We will not claim live feeds or clinical autonomy.” | 25s |
| 14 | Impact | Reduce coordination friction and improve traceability | Before/after operator workflow | “The defensible impact is fewer hidden decisions, not an invented percentage.” | 25s |
| 15 | Future scope | Harden first, integrate second, add intelligence with evidence | Roadmap phases | “Any ML remains subordinate to hard constraints.” | 25s |
| 16 | Closing | Make every emergency decision explainable and accountable | One-line close + demo label | “Conclave turns a chain of uncertain handoffs into a visible decision trail.” | 15s |

## 32. Demo Script

### Starting state

PostGIS is running, the database has been reset with `GOLDEN_2026`, the API and
Vite server are running, and the login page shows `DEMO MODE · SYNTHETIC DATA ONLY`.

### Actions and expected evidence

1. Log in as `dispatcher.demo@demo.invalid` with the local synthetic password.
2. Create a critical `TRAUMA` incident at the prefilled Bengaluru demo location.
3. Submit the form. Point out the fixed required `ICU` and `VENTILATOR` tags.
4. On the ambulance list, show an ineligible candidate and read its reason. Explain
   that it has no rank/score because hard constraints run before scoring.
5. Select the eligible candidate, normally `AMB-002` in the seeded live smoke, and
   click `CONFIRM AMBULANCE`.
6. Explain that the API validates eligibility again and creates a mission and
   assignment with an idempotency key.
7. Show hospitals. Point out missing capability, full capacity, unknown capacity,
   or stale data where present.
8. Select the eligible hospital, normally `H-003` in the seeded smoke.
9. Click `CALCULATE ROUTE`. Show `10 min`, `MOCK ROUTING`, confidence, and
   `SIMULATED`.
10. If demonstrating backend/role continuation separately, create an acceptance
    request, show the hospital-scoped acceptance surface, accept it, and explain
    that the backend confirms reservations and records destination/audit events.
11. Do not claim the final continuation was browser-verified unless it has been
    live-tested in the current environment.

### API/database/realtime evidence for the continuation

| Stage | API/service | Database change | Realtime/UI evidence |
|---|---|---|---|
| Incident | `POST /api/v1/incidents` | `incidents`, `audit_logs` | Dispatcher detail view |
| Requirement | `POST /api/v1/incidents/{id}/requirements` | `patient_requirement_items`, audit | Locked UI tags |
| Ambulance match | `POST /api/v1/dispatch/ambulances/match` | `decision_runs`, candidates, reasons | Candidate cards |
| Assignment | `POST /api/v1/dispatch/ambulances/{id}/confirm` | assignment, mission, incident, audit | Post-commit mission event |
| Hospital match | `POST /api/v1/dispatch/hospitals/match` | hospital decision trace | Hospital candidates |
| Route | `POST /api/v1/routes/calculate` | route | Mock route result |
| Acceptance hold | `POST /api/v1/acceptance-requests` | acceptance, reservations, resource event, audit | Realtime metadata/backend role surface |
| Acceptance | `POST /api/v1/acceptance-requests/{id}/accept` | confirmed reservations, mission destination, event, notification, audit | Browser continuation partial |
| Mission write | `PATCH /api/v1/missions/{id}` | mission version/status, event, notification, audit | Crew screen + realtime core |

## 33. Judge Q&A Preparation

### What problem are you solving?

Emergency coordination requires a chain of resource, destination, acceptance,
capacity, route, and mission decisions. Conclave puts that chain into one
constraint-aware, auditable console.

### Why not simply choose the nearest ambulance or hospital?

The implementation filters mandatory equipment, active mission status, GPS
freshness, hospital capabilities, and resource freshness/capacity before scoring.
Proximity is a factor, not a substitute for eligibility.

### Is this real hospital data?

No. The repository uses synthetic seeded records and visibly labels them
`SIMULATED`/`DEMO MODE`. The routing provider is deterministic mock data.

### Is this an AI or ML system?

The current decision engine is deterministic rules plus weighted scoring. ML and
voice are intentionally not built because the approved project has no training
data and does not make fabricated accuracy claims.

### How do you avoid double-booking an ICU?

The server locks the resource row, checks available capacity, updates available
and reserved counts in the same transaction, and has PostgreSQL integration tests
where two concurrent reservations produce one winner.

### What happens when capacity is unknown or stale?

It is not treated as available. Hospital matching adds explicit reasons and the
reservation path rejects unknown/stale/unavailable required resources.

### Can an operator override the algorithm?

The current confirmation path rejects ineligible candidates. An eligible but
non-top choice requires an override reason, which is audited. Mandatory safety
constraints cannot be overridden by this path.

### What happens if a hospital rejects?

The backend rejection path closes the request with a reason and cancels held
reservations. Re-ranking/reassessment exists only partially in the current
browser flow, so the full UI story should be presented as backend-supported but
not fully browser-verified.

### What happens if an ICU disappears after reservation?

The backend has resource-loss/reassessment service paths and simulation controls,
and the documented scenario expects release and re-evaluation. Full live browser
rehearsal is still a gap.

### How does realtime remain correct?

Events publish after commit, include IDs and entity versions, and are deduplicated
by the browser. Version gaps or reconnects trigger REST resync. The current broker
is process-local, so distributed scaling needs a shared transport.

### How is access controlled?

JWT authentication, role dependencies, hospital scope, and ambulance scope are
enforced server-side. Hiding a frontend control is not the security boundary.

### Is it production-ready?

No. It is a controlled synthetic prototype with a strong safety-oriented backend
foundation. Production still requires secure sessions, secret enforcement,
throttling, live integrations, CI/CD, backups/rollback, distributed realtime,
and full live failure verification.

### What is the measurable performance result?

The repository records 50 pure deterministic matcher samples at p50 `0.009 ms`
and p95 `0.012 ms`. That excludes database, HTTP, routing, browser, and network
latency and must not be presented as an end-to-end SLA.

### What would it cost to run?

The repository does not contain a cloud cost model. The current local runtime is
Docker PostGIS plus a Python API and Vite frontend. A real estimate requires chosen
hosting, database, routing, identity, messaging, observability, and integration
providers.

## 34. Difficult Questions & Honest Answers

| Difficult question | Honest answer |
|---|---|
| Does it save lives? | The repository does not measure clinical outcomes, so we make no such claim. It demonstrates a coordination architecture intended to reduce hidden decision friction. |
| Does it use live ICU availability? | No. Capacity is seeded synthetic data. The code supports explicit unknown/stale states and a future integration boundary. |
| Is the route live? | No. `MockRoutingProvider` reads deterministic scenario values. |
| Is the hospital automatically notified? | Notification rows and realtime metadata are persisted; a verified external notification channel is not implemented. |
| Is the full demo automated? | The mocked dispatcher path and selected backend invariants are tested. The complete acceptance/reservation/failure browser journey is not. |
| Can two API servers share realtime events? | Not with the current in-process broker. A shared broker is part of the scaling path. |
| Are frontend contracts generated from OpenAPI? | Not yet. The client uses handwritten interfaces, which is a known drift risk. |
| Is authentication production secure? | Not yet. The demo uses localStorage JWT storage and development defaults; secure cookies and fail-closed secrets are required. |
| Does it predict ETA with ML? | No. Current ETA is deterministic scenario input. ML/voice are intentionally skipped. |
| What is the competitive moat? | The defensible current distinction is the integrated constraint-first, transactional, auditable workflow. No exclusivity or market-first claim is made. |

## 35. Evidence Map

| Pitch claim | Supporting file/module | Evidence |
|---|---|---|
| Synthetic non-clinical prototype | `README.md:1-4`, `CLAUDE.md:3-7` | Explicit project positioning |
| Dispatcher workflow | `apps/web/src/App.tsx:163-188` | Incident, matching, confirmation, hospital, route screens |
| Role workspaces | `apps/web/src/RoleScreens.tsx:30-60` | Hospital, crew, demo controller |
| Constraint-first ambulance matching | `apps/api/app/decision_engine/ambulance.py:34-55` | Ineligible candidates receive no score/rank |
| Constraint-first hospital matching | `apps/api/app/decision_engine/hospital.py:31-54` | Capability/capacity/stale filtering before score |
| Decision trace | `apps/api/app/db/models.py:237-267`, `apps/api/app/decision_service.py` | Runs, candidates, reasons, versions, snapshots |
| Server-authoritative reservation | `apps/api/app/reservation_service.py:18-38` | Locked resource and atomic capacity update |
| Concurrent reservation proof | `apps/api/tests/test_reservation_postgres_integration.py:112-180` | One winner, one failure, correct counts |
| Acceptance and reservation backend | `apps/api/app/services.py:253-320` | Hold, expiry, accept, reservation confirmation |
| Mission state/version protection | `apps/api/app/services.py:323-356` | Explicit transition map and stale version conflict |
| Destination audit trail | `apps/api/app/mission_service.py:21-38` | Event, notification, audit record |
| Post-commit realtime | `apps/api/app/realtime/broker.py:73-128`, `apps/api/tests/test_realtime.py:12-35` | Rollback publishes nothing; event metadata/dedupe |
| WebSocket authorization/subscription | `apps/api/app/realtime/websocket.py:15-70` | Token, explicit channels, scope checks, heartbeat |
| Deterministic mock routing | `apps/api/app/routing/providers.py:29-56`, `docs/implementation-decisions.md:5-10` | Scenario route, simulated mode, missing route error |
| Synthetic seed | `apps/api/app/simulation/seed.py:40-158` | Ten hospitals/ambulances, capability/capacity cases, GOLDEN_2026 |
| UI state honesty | `apps/web/src/components/decision-state.tsx:5-32`, `apps/web/src/App.tsx:151-160` | Loading/error/stale/unknown/simulated states |
| Current verification | `STATUS.md:42-65`, `handoffs/AMB_HANDOFF_2026-09-16_5.md:19-27` | Test counts and live path boundary |
| Production gaps | `STATUS.md:67-137`, `docs/dod.md:62-69` | LocalStorage, missing backup/restore and full browser rehearsal |

## 36. Final Project Summary

Conclave is a transparent synthetic emergency-coordination prototype. Its value
is the combination of constraint-first matching, explicit freshness semantics,
transactional reservation safety, role-scoped workflows, versioned mission state,
post-commit realtime events, and durable decision/audit traces.

The current implementation proves a compelling dispatcher path from incident
intake to ambulance selection, hospital matching, and deterministic routing. It
also contains a broader backend foundation for acceptance, resource holds,
reservation confirmation, mission progression, simulation, and reassessment.

The accurate pitch is therefore:

> **Conclave turns emergency resource coordination from a chain of opaque,
> manual handoffs into a visible, constraint-aware, auditable decision workflow.**

The accurate qualification is equally important:

> **It is a synthetic decision-support prototype, not a live hospital-capacity
> integration and not a clinically autonomous system.**

### Audit completion checklist

- [x] Repository structure, history, instructions, and status inspected
- [x] Frontend inspected
- [x] Backend and API routes inspected
- [x] Database models and migration surface inspected
- [x] Realtime implementation inspected
- [x] Authentication and authorization inspected
- [x] Tests and Playwright coverage inspected
- [x] Configuration, Docker, environment, and deployment surface inspected
- [x] Demo, simulation, pitch, and documentation inspected
- [x] Mock/demo/planned/partial/risk classifications made
- [x] Main workflow and strongest reproducible demo identified
- [x] Unsupported metrics, live integrations, and clinical claims excluded
- [x] Limitations and production gaps included
- [x] Evidence map included
- [ ] Blind evaluator quality gate: unavailable in this environment
- [ ] Explicit user live-test sign-off: pending
