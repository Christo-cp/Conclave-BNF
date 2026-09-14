# Spec conflicts — decisions

Format: tech:373-392. Precedence where the user has not decided: safety › prd ›
techspec › database › plan › appflow › design (tech:347-394). Row ids match the
register, `.claude/skills/spec-lookup/references/conflicts.md`.

Every decision below was made by the user on 2026-09-13.

## Conflict: P1 — Database runtime

### Document A
tech:5570-5575 runs the database with `docker compose up postgres`.

### Document B
No spec requires a native install; the machine had neither Docker nor PostgreSQL.

### Resolution
Docker Desktop (WSL2) with `postgis/postgis:16-3.5`.

### Reason
Matches techspec and gives the same runtime on every machine.

### Implementation Impact
`docker-compose.yml` with a `postgres` service. The user installs WSL and Docker
Desktop as administrator (plan A1).

## Conflict: P2 — Map and routing provider

### Document A
tech:772-775 lists Google, Mapbox, OSRM and Mock providers; plan:601-607 prefers
Google Routes or Mapbox.

### Document B
tech:2081 resolves the choice as one provider behind a `RoutingProvider` interface.

### Resolution
`MockRoutingProvider` for every scenario route; Mapbox for map tiles and as the
optional live provider.

### Reason
Deterministic, works offline for the demo; one live provider behind the interface.

### Implementation Impact
`ROUTING_PROVIDER=mock`. The user adds `MAPBOX_ACCESS_TOKEN` and
`VITE_MAPBOX_TOKEN` to `.env` at S11; the token is never pasted into chat or
committed.

## Conflict: C01 — State machines

### Document A
Incident states: prd:1094-1124 and flow:1676-1706 (CREATED, ANALYZING, DISPATCHED,
PICKUP, HOSPITAL_SELECTED, ACCEPTED, RESOURCE_RESERVED, IN_TRANSIT, ARRIVED,
HANDOVER, COMPLETED; CANCELLED, FAILED, ESCALATED). Mission states: db:1448-1463
(12 states, `PATIENT_ON_BOARD`).

### Document B
tech:849-868 has 16 different states (`PATIENT_ONBOARD`, `HANDOVER_COMPLETE`);
db:628-644 has `HOSPITAL_SELECTION` and `ACCEPTANCE_PENDING`.

### Resolution
One enum module, `app/core/enums.py`. Mission states from db:1448-1463. Incident
states from prd:1094-1124 **without** `PICKUP`.

### Reason
db's unique index and tests use db's mission names. prd:1101 puts PICKUP before
HOSPITAL_SELECTED, which contradicts C05 (matching before pickup); pickup is
already recorded by the mission state `PATIENT_ON_BOARD`.

### Implementation Impact
Enum CHECKs generated from `app/core/enums.py` (S1).

## Conflict: C05 — When hospital matching runs

### Document A
Before pickup, right after dispatch: prd:1910-1923; tech:2151-2157 reserves before
the mission starts.

### Document B
After pickup: flow:1648-1650, flow:3834-3836, tech:857-862.

### Resolution
Right after the ambulance is confirmed, before pickup.

### Reason
prd has precedence, and the golden scenario depends on it.

### Implementation Impact
Hospital matching runs automatically after route calculation (S6).

## Conflict: C06 — Requirement model

### Document A
Tri-state REQUIRED / PREFERRED / UNKNOWN: prd:567-573.

### Document B
Boolean `*_required` columns: db:708-721.

### Resolution
Tri-state, one row per requirement in `patient_requirement_items` (db:725-742).

### Reason
Booleans cannot express PREFERRED or UNKNOWN, which scoring and safety need.

### Implementation Impact
S1 creates `patient_requirement_items`; the boolean columns are not used.

## Conflict: C08 — Request info

### Document A
tech:3625 lists `POST /acceptance-requests/{id}/request-info`; tech:3007 draws a
REQUEST INFO button.

### Document B
No spec defines a status for it, and tech:1904-1930 forbids buttons without backend
behaviour.

### Resolution
Not built: no endpoint, no button.

### Reason
It would need an invented state.

### Implementation Impact
None in S7 or S11.

## Conflict: C10 — Confidence type

### Document A
Numeric: tech:3094, tech:3713, tech:6217; db:1809 `NUMERIC(8,5)`.

### Document B
Text HIGH / MEDIUM / LOW / UNKNOWN: db:1076, db:1677, db:2661-2665, tech:6162-6170.

### Resolution
Store a number from 0 to 1; derive the band for display (plan A4).

### Reason
One stored value, no drift between two representations; design:1138-1148 shows both.

### Implementation Impact
Numeric confidence columns; band cut points are plan A4 configuration.

## Conflict: C11 — Score direction and tie-break

### Document A
"Lower is better for cost-based components" (tech:3174); sort ASC (tech:5720);
minimise objective (tech:3835-3840).

### Document B
Weights read higher-is-better: plan:572-581, plan:764-774.

### Resolution
Every factor normalised to 0–1 with higher better; sort by score descending, then
`eta_s` ascending, then code ascending (plan A4).

### Reason
Matches the spec weights and makes the ordering deterministic.

### Implementation Impact
`app/decision_engine/` implements plan A4 (S4, S6).

## Conflict: C14 — Spatial column type

### Document A
`geometry(Point,4326)`: tech:3406.

### Document B
`geography(Point,4326)`: db:581, db:2142; metre-radius `ST_DWithin` at db:2197-2216.

### Resolution
`geography(Point,4326)`.

### Reason
With SRID 4326, geometry distances are in degrees; the metre-radius queries need
geography.

### Implementation Impact
All location columns are geography with GiST indexes (S1).

## Conflict: C24 — Override when nothing is feasible

### Document A
flow:1465 offers `[ DISPATCHER OVERRIDE ]`.

### Document B
plan:4936 forbids overriding mandatory constraints without an escalation policy;
none is defined.

### Resolution
No override of a mandatory constraint. The incident becomes `ESCALATED`
(prd:1120-1124) and the UI enters manual coordination mode (flow:1966-1982).

### Reason
Safety rule.

### Implementation Impact
S4 and S6 escalate without a recommendation.

## Conflict: C27 — OpenAPI path

### Document A
`/api/v1/openapi.json`: tech:5125.

### Document B
`/openapi.json`: tech:6341.

### Resolution
`/api/v1/openapi.json`, by setting FastAPI's `openapi_url`.

### Reason
Keeps every API path under `/api/v1`, as the api-client section (tech:5108-5128)
expects.

### Implementation Impact
`app/main.py` sets `openapi_url`; type generation uses that URL (plan A2).

## Conflict: C31 — Who reserves

### Document A
Hospital staff reserve: prd:1655. Dispatcher only requests: plan:2139.

### Document B
Dispatcher may reserve: tech:4469. Backend reserves after acceptance:
flow:2556-2560, db:4339-4346.

### Resolution
The backend holds when it requests acceptance and confirms on accept (plan A5).
`POST /reservations` is limited to HOSPITAL_STAFF, HOSPITAL_ADMIN and SYSTEM_ADMIN.

### Reason
The hold stops a hospital accepting capacity that has already gone.

### Implementation Impact
AcceptanceService and ReservationService (S7).

## Conflict: C36 — Error code for an unreachable database

### Document A
The error categories (tech:4519-4533) have no database-outage code.

### Document B
db:4684-4698 requires a database health endpoint that exposes no connection details.

### Resolution
`GET /api/v1/health/db` returns HTTP 503 with the error envelope (tech:4503-4513)
and code `INTERNAL_ERROR`.

### Reason
The catch-all code; the frontend won't mistake it for the user's own network.

### Implementation Impact
`app/api/v1/health.py`; test `test_health_db_unreachable_503_envelope`.
