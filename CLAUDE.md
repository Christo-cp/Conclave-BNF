# ResQFlow Project Context

ResQFlow is a synthetic emergency-coordination prototype for ambulance
selection, deterministic routing, hospital capability/capacity matching,
acceptance, resource reservation, mission state, realtime updates, and failure
reassessment. It is decision support, not a clinically autonomous system and
does not integrate live hospital capacity.

## Current Context

Current milestone: S1-S8 backend foundation, S9 realtime core, and selected S11-
S12 backend services. S10-S15 remain partial.

Current architecture: React 19/Vite frontend in `apps/web`; FastAPI/Python 3.12
backend in `apps/api`; PostgreSQL 16/PostGIS with Alembic migrations; pure
decision engines; service-layer orchestration; deterministic routing provider;
post-commit in-process WebSocket broker; synthetic reset/seed data.

Current golden path: incident → patient requirements → ambulance match →
ambulance confirmation → route → hospital match → acceptance hold → hospital
acceptance → reservation confirmation → mission destination/state → realtime
updates → arrival/handover. The backend portions through acceptance,
reservation, and destination are implemented; the complete browser path is not
yet verified.

Current roles: `DISPATCHER`, `AMBULANCE_CREW`, `HOSPITAL_STAFF`,
`HOSPITAL_ADMIN`, `SYSTEM_ADMIN`, and `DEMO_CONTROLLER`. Hospital staff/admin
are scoped to their hospital. Crew users are scoped through `users.ambulance_id`.
Authorization is enforced server-side.

Current major constraints: backend state is authoritative; the frontend never
fabricates operational candidates, ETAs, scores, capacity, routes, or reasons;
simulated data is visibly `SIMULATED`; unknown/stale capacity is not available;
reservations use row locks and capacity checks; mission writes use
`state_version`; events publish only after commit; audit/event history is
append-only.

Current known limitations: S10 dispatcher acceptance/reservation UI, generated
OpenAPI types, full S11 hospital/crew/map/manual flows, S12 reroute/compare and
reassessment orchestration, S14 CORS/audit-completeness, and S15 demo assets
remain partial. S13 FR-023 and FR-032 are intentionally skipped. Live browser
smoke and explicit user sign-off are pending.

## Read Before Coding

1. Read `AGENTS.md`, `STATUS.md`, and the newest `handoffs/` file.
2. Grep the relevant specification first, then read slices of no more than 80
   lines. Use `file:line` citations for specification facts.
3. Read the current service, callers, models/migrations, and tests before editing.
4. Check `.claude/skills/spec-lookup/references/conflicts.md` before naming or
   changing enums, states, endpoints, scoring values, or environment keys.

The six root specs are read-only: `prd.md`, `plan.md`, `appflow.md`, `design.md`,
`database.md`, and `techspec.md`. The executable build plan is
`docs/executable-plan.md`.

## Backend Map

- `apps/api/app/main.py`: FastAPI app, `/api/v1` mounting, middleware, routers.
- `apps/api/app/api/v1/`: auth, incidents, dispatch, missions, resources,
  simulation, alerts, and health routes.
- `apps/api/app/services.py`: current incident, matching, route, acceptance,
  and mission orchestration; extract new domain services only when needed.
- `apps/api/app/decision_engine/`: pure ambulance and hospital hard-pass/rank
  functions. No database, HTTP, or FastAPI imports.
- `apps/api/app/routing/`: `MockRoutingProvider` and `RoutingService`; inputs
  come from the `GOLDEN_2026` simulation scenario and return `SIMULATED` data.
- `apps/api/app/reservation_service.py`: row-locked reservation lifecycle and
  resource accounting.
- `apps/api/app/sweeper.py`: idempotent expiration of held reservations.
- `apps/api/app/assignment_service.py`: crew assignment accept/reject events.
- `apps/api/app/realtime/`: authenticated WebSocket, explicit subscriptions,
  dedupe/version filtering, and post-commit broker.
- `apps/api/app/simulation/`: deterministic seed and target-aware controls.
- `apps/api/app/db/models.py`: SQLAlchemy models matching the migration schema.
- `apps/api/migrations/versions/`: applied history through `0018_decision_trace_fields`.

## Frontend Map

- `apps/web/src/App.tsx`: dispatcher shell, incident intake, matching, route UI.
- `apps/web/src/RoleScreens.tsx`: hospital, crew, and demo-controller workspaces.
- `apps/web/src/components/`: loading/error/stale/simulated decision states.
- `apps/web/src/lib/api.ts`: shared REST client. Do not add endpoint calls in
  components.
- `apps/web/src/lib/realtime.ts`: WebSocket URL, explicit subscription,
  reconnect/backoff, event dedupe, version checks, and REST resync.
- `apps/web/e2e/`: mocked browser specs and opt-in live spec. Do not run live
  smoke automatically for this project unless the user explicitly requests it.

## API And Data Conventions

- REST prefix: `/api/v1`; OpenAPI: `/api/v1/openapi.json`; WebSocket:
  `/api/v1/ws?token=...`.
- State/enums use uppercase strings; WebSocket event names use dotted lowercase.
- `Idempotency-Key` is required for ambulance confirmation, acceptance holds,
  acceptance responses, and reservations where the endpoint schema requires it.
- API errors use `{ "error": { "code", "message", "request_id" } }`.
- Coordinates are `{lat, longitude}` at API boundaries and `POINT(lng lat)` in
  PostGIS. Resource distance queries use `geography(Point,4326)`.
- Data modes are explicit: operational demo values are `SIMULATED`; unknown and
  stale values remain unknown/stale end to end.
- Decision runs persist candidates, eligibility, reasons, input snapshots,
  freshness, algorithm version, and config version in the same transaction.

## Commands

PowerShell from the repository root:

```powershell
$py = ".\apps\api\.venv\Scripts\python.exe"
docker compose up -d postgres
& $py -m alembic -c apps\api\alembic.ini upgrade head
& $py scripts\reset_demo.py
& $py -m uvicorn app.main:app --app-dir apps\api --reload
pnpm --dir apps/web dev
& $py -m pytest apps\api\tests -v
& $py -m ruff check apps\api scripts
pnpm --dir apps/web build
pnpm --dir apps/web exec vitest run
pnpm --dir apps/web exec playwright test <spec>
```

Tests use `smart_ambulance_test`, not dev/demo. Do not run Playwright live smoke
automatically in this project; the owner performs manual browser verification.

## Durable Decisions

- P1: Docker PostGIS `postgis/postgis:16-3.5`.
- P2: deterministic `MockRoutingProvider` for scenarios; Mapbox is optional for
  tiles/live integration and secrets never enter source control.
- Requirements are tri-state `REQUIRED`, `PREFERRED`, `UNKNOWN`.
- Hard constraints filter before scoring. No mandatory constraint can be
  overridden; non-top eligible overrides require a reason and audit row.
- Hospital matching excludes unknown/stale/inactive/unavailable required
  resources and rejected hospitals in the current acceptance chain.
- Reservations are server-authoritative, row-locked, idempotent, and publish
  success events only after commit.
- S13 ML/voice is skipped because FR-023 and FR-032 lack approved data and no
  fabricated accuracy claim is allowed.

## Agent Routing

Use `/session-start` first, `/spec-lookup` for root-spec questions,
`/bug-triage` before debugging, `/zero-error-gate` before claiming completion,
and `/handoff` at session end. Use `AGENTS.md` for the complete operational
rules and project-memory maintenance protocol.
