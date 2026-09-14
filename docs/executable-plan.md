# Smart Ambulance — Executable Build Plan

State on 2026-09-13: six specs, no code, not a git repository. This plan replaces
the specs' prose plan for building. The specs remain the reference.

**How to run it.** Do the steps in order. A step is finished when all three hold:

1. **Exit passes.** Every command in the step's **Exit** block is run and its
   output matches. A test command passes only when every test the step names is
   collected and passes: pytest `-v` prints `PASSED`; Vitest
   (`--reporter=verbose`) and Playwright (`--reporter=list`) print ✓.
   Every Exit ends with the full suite, `.\scripts\full_suite.ps1` (A2), so a
   regression in an earlier step blocks the later one.
2. **Gate complete.** The `/zero-error-gate` checklist
   (`.claude/skills/zero-error-gate/SKILL.md`) is done, ending with a live test
   and explicit sign-off by the user.
3. **Committed.** `git add -A`; then `git ls-files .env .env.demo .env.test` and
   `git diff --cached | Select-String -Pattern "sk-[A-Za-z0-9_-]{20,}","[ps]k\.eyJ[A-Za-z0-9_-]{20,}","AKIA[0-9A-Z]{16}"`
   must print nothing; then `git commit -m "S<n>: <title>"`.

**Citations and marks**

| Mark | Meaning |
|---|---|
| `file:line` | `prd`, `plan`, `flow` (appflow), `db`, `tech` (techspec), `design` |
| `FR-nnn`, `BR-nnn` | Functional requirement prd:485-980; business rule prd:1128-1216 |
| `M1`…`M8` | Milestone, plan:5129-5174 |
| `Cnn` | Row of `.claude/skills/spec-lookup/references/conflicts.md`; decisions are in `docs/spec-conflicts.md` |
| `*` | Chosen by this plan, not by the specs. A citation beside a `*` names the rule the choice serves, not the value |

No number is a clinical or measured claim.

---

## Part A — Before any code

### A1. Machine (checked 2026-09-13)

| Tool | Found | Action |
|---|---|---|
| Node | v22.23.2 | none |
| pnpm | 12.4.1, enabled on 2026-09-13 | Where missing: `corepack enable pnpm` (no elevation needed) |
| Python | 3.14.5 system; 3.12.14 via `uv python install 3.12` (uv 0.12.7) | The API venv uses 3.12 |
| Docker | missing; WSL not installed; the agent's shell is not elevated | The user, in an administrator PowerShell: `wsl --install`, reboot, `winget install -e --id Docker.DockerDesktop`, start Docker Desktop once. Check: `docker version` prints a Server section |
| psql | missing | Not needed: `scripts/db_create.py` uses psycopg |
| git | 2.54.0 | `git init` in S0 |

### A2. Commands and environments

In each new PowerShell window, from the project root: `$py = ".\apps\api\.venv\Scripts\python.exe"`.

| Purpose | Command |
|---|---|
| Migrate | `& $py -m alembic -c apps\api\alembic.ini upgrade head` |
| Reset and seed | `& $py scripts\reset_demo.py` (migrates to head first, A6) |
| Start the API | `& $py -m uvicorn app.main:app --app-dir apps\api --reload` |
| Start the web app | `pnpm --dir apps/web dev` |
| Generate API types | `pnpm --dir apps/web exec openapi-typescript http://127.0.0.1:8000/api/v1/openapi.json -o src/lib/api/schema.d.ts` |
| API tests | `& $py -m pytest <files> -v` |
| Lint | `& $py -m ruff check apps\api` |
| Web type-check and build | `pnpm --dir apps/web build` (the scaffold's script runs `tsc -b`) |
| Web unit tests | `pnpm --dir apps/web exec vitest run <files> --reporter=verbose` |
| Browser tests | `pnpm --dir apps/web exec playwright test <spec> --reporter=list` |

**Full suite.** `scripts/full_suite.ps1`* (S0) runs, stopping at the first
failure: `pytest apps\api\tests -v`, `ruff check apps\api`,
`pnpm --dir apps/web build`, and `vitest run --reporter=verbose` once web unit
tests exist. It refuses to start while anything listens on port 8000, because
pytest and a running API would share `smart_ambulance_test`.

**Browser suite** (from S10, after the full suite). Window 1:
`$env:ENV_FILE = ".env.test"`, Reset, start the API. Window 2: start the web
app (Vite reads no `ENV_FILE`). Window 3: `pnpm --dir apps/web exec playwright
test --reporter=list`. Then stop windows 1 and 2.

**Libraries.** Cited: React, TypeScript, Vite, Tailwind CSS, TanStack Query,
Zustand, React Router, React Hook Form, Zod, Lucide React, Recharts
(tech:504-515); Python, FastAPI, Pydantic, SQLAlchemy, Alembic, WebSockets
(tech:520-527); Pytest, Vitest, React Testing Library, Playwright
(tech:555-559). Chosen here*: uvicorn, psycopg, GeoAlchemy2, pydantic-settings,
PyJWT, argon2-cffi, hatchling, httpx, Ruff, mypy, jsdom, openapi-typescript,
@tailwindcss/vite. Versions are not pinned*: S0 installs the newest releases,
`pnpm-lock.yaml` locks the web ones and the S0 hand-over records
`uv pip freeze`. Database access is synchronous SQLAlchemy 2 over psycopg;
FastAPI runs sync endpoints in its threadpool*.

**Environment files** (key names tech:4893-4926; never committed). Settings,
Migrate and Reset read the file named by `$env:ENV_FILE`* (it selects a file, so it is not in
tech's list), default `.env`.

| File | Database | Used for | Created |
|---|---|---|---|
| `.env` | `smart_ambulance_dev` | development | S0 |
| `.env.test` | `smart_ambulance_test` | pytest and browser tests | S0 |
| `.env.demo` | `smart_ambulance_demo` | the recorded live demo only | S15 |

```text
APP_ENV=development            # .env.demo: APP_ENV=demo
POSTGRES_PASSWORD=<python -c "import secrets; print(secrets.token_urlsafe(24))">
DATABASE_URL=postgresql+psycopg://postgres:<password>@127.0.0.1:5432/<database>
JWT_SECRET=<python -c "import secrets; print(secrets.token_urlsafe(32))">
CORS_ORIGINS=http://localhost:5173
ROUTING_PROVIDER=mock
MAPBOX_ACCESS_TOKEN=
VITE_MAPBOX_TOKEN=
SIMULATION_ENABLED=true
ML_ENABLED=false
```

**Test databases** (db:3477-3485). pytest never touches dev or demo:
`conftest.py` swaps `smart_ambulance_test` into `DATABASE_URL` and migrates it
once, with `SIMULATION_ENABLED=false` so no heartbeat runs (heartbeat tests call
one tick directly). The function-scoped `golden_db` fixture calls
`app.simulation.seed.reset_and_seed()` before each test, so seeded `NOW()`
timestamps are seconds old when the test starts. Browser tests use the windows
above.

### A3. Decisions

**Decided by the user on 2026-09-13.** S0 records each in `docs/spec-conflicts.md`
(format tech:373-392) and marks the register row RESOLVED.

| ID | Decision | Blocks |
|---|---|---|
| P1 | PostgreSQL + PostGIS on Docker Desktop (WSL2), image `postgis/postgis:16-3.5` (tech:5570-5575). Install: A1 | S0 |
| P2 | `MockRoutingProvider` for every scenario route; Mapbox for map tiles and as the optional live provider (tech:2081). The user adds the token to `.env` at S11, never in chat or a commit | S11, S12 |
| C01 | One module, `app/core/enums.py`. Mission states: db:1448-1463. Incident states: prd:1094-1124 without `PICKUP`; pickup is the mission state `PATIENT_ON_BOARD`. Transitions: A5.0 | S1 |
| C05 | Hospital matching runs right after the ambulance is confirmed, before pickup (prd:1910-1923) | S6 |
| C06 | Requirements are tri-state REQUIRED / PREFERRED / UNKNOWN (prd:567-573), one row each in `patient_requirement_items` (db:725-742). Semantics: A4 | S1 |
| C08 | No `/request-info` endpoint (tech:3625) and no button for it | S7 |
| C10 | Confidence is stored as a number 0–1; the band is derived (A4) | S4 |
| C11 | Weighted factors lie in 0–1 with higher better; sort descending; deterministic tie-break (A4) | S4 |
| C14 | `geography(Point,4326)` (db:581, db:2142; metre radius db:2197-2216) | S1 |
| C24 | No override of a mandatory constraint; the incident becomes `ESCALATED` (prd:1120-1124) and the UI enters manual coordination mode (flow:1966-1982) | S4, S6 |
| C27 | OpenAPI at `/api/v1/openapi.json` via FastAPI `openapi_url` (tech:5125) | S0 |
| C31 | The backend holds on acceptance request and confirms on accept (A5). `POST /reservations` is limited to HOSPITAL_STAFF, HOSPITAL_ADMIN and SYSTEM_ADMIN (S11) | S7, S11 |
| C36 | An unreachable database returns 503 with `INTERNAL_ERROR` (tech:4519-4533 has no outage code) | S0 |

**Pinned without asking** — each is the register's default.

| Row | Pinned answer | Source |
|---|---|---|
| C02 | Severity CRITICAL / HIGH / MEDIUM / LOW | prd:543-550 |
| C03 | Crew role `AMBULANCE_CREW` | prd:505-512 |
| C04 | `DEMO_CONTROLLER` role kept | prd:511 |
| C07 | Notes optional; at least one requirement required | prd:532-535 |
| C09 | `data_mode` and data-source values from db | db:2646-2653, db:2676-2682 |
| C12 | `acceptance_score` only ranks; only ACCEPTED confirms a destination | db:1245-1257 |
| C13 | `INC-`, `MSN-`, `RES-` + six digits; `AMB-001`, `H-001` | tech:2923, db:458 |
| C15 | Environment variable names from tech's list | tech:4893-4926 |
| C16 | Monorepo `apps/web`, `apps/api` | tech:5579-5612 |
| C17 | Migrations in db's order, named `0001_` onward | db:5390-5410 |
| C18 | 10 ambulances, 10 hospitals; prd's 3 scenarios plus plan's 4 demo events | db:2038, plan:3668-3757 |
| C19 | Golden scenario from prd; tech's golden path is the test script | prd:3015-3092, tech:2120-2178 |
| C20 | Domain and audit events UPPER_SNAKE; WebSocket events dotted | tech:4149-4163 |
| C21 | Explainability, demo and failure handling are P0 | prd:474-476 |
| C22 | Tests written with each step | plan:4383 |
| C23 | Decision latency target under 2 s | plan:2446, tech:4829-4853 |
| C25 | `occupied + reserved + available <= total` | db:1114-1132 |
| C26 | Reservation SQL bumps `version` | db:1366 |
| C29 | Specs stay at the root | tech:5599 |
| C30 | A destination is confirmed only after its reservation commits | db:1247-1257 |
| C32 | `Idempotency-Key` header | tech:5731-5750 |
| C33 | The capacity transaction is the guard; indexes are for lookup | db:2559-2573 |
| C34 | HELD → EXPIRED on TTL; CONFIRMED → RELEASED with `release_reason` | db:1306-1323 |
| C35 | GPS FRESH ≤15 s, AGING >15–60 s, STALE >60 s | tech:4618-4635 |

### A4. Decision maths (C06, C10, C11)

**Requirement semantics.** REQUIRED items filter (hard pass). PREFERRED items
score. UNKNOWN items neither filter nor score; the recommendation lists them as
unconfirmed needs*. Unknown candidate data is never treated as available.

**Order.** Hard constraints run first; an ineligible candidate gets no score and
no rank (tech:642-670). The engine takes `now` as an input.

**Scores.** Weights from plan:572-581 and plan:764-774. The six weighted factors
lie in 0–1, higher better. `uncertainty_penalty` is the spec's separate deduction
(plan:774), not a weighted factor.

```text
ambulance_score = 0.45·eta_score + 0.25·capability_score + 0.15·equipment_score
                + 0.10·crew_score + 0.05·freshness_factor                  range 0 … 1
hospital_score  = 0.30·eta_score + 0.20·capability_score + 0.20·acceptance_score
                + 0.15·resource_score + 0.10·predicted_readiness
                + 0.05·route_reliability − uncertainty_penalty              range −FALLBACK_PENALTY … 1
```

| Factor | Definition |
|---|---|
| `eta_score` | `1 − min(eta_s, ETA_CAP_S)/ETA_CAP_S`; ambulance → incident, or incident → hospital |
| `capability_score`, `equipment_score`, `crew_score` | Share of PREFERRED items met; 1.0 if none |
| `freshness_factor` | plan:572-581's `availability_confidence`. GPS FRESH 1.0, AGING `AGING_FACTOR`; STALE is excluded |
| `acceptance_score` | ACCEPTED 1.0; not asked or PENDING `PENDING_ACCEPTANCE_SCORE`; REJECTED is excluded |
| `resource_score` | `min(available of the scarcest REQUIRED resource, RESOURCE_SAT)/RESOURCE_SAT`; 1.0* when no REQUIRED item is a capacity resource |
| `predicted_readiness` | `READINESS_FALLBACK` while `ML_ENABLED=false`, recording `fallback_used = true` |
| `route_reliability` | `1 − congestion` (0–1, from the routing provider) |
| `uncertainty_penalty` | `FALLBACK_PENALTY` when the hospital's ETA came from a fallback or cached route, else 0 |

**Sort.** Score descending, then `eta_s` ascending, then code ascending.

**Confidence.** Start from the selected candidate's `freshness_factor`
(hospitals 1.0*, stale hospital data being excluded). Cap at
`FALLBACK_CONFIDENCE_CAP` for a fallback or cached ETA. Band: HIGH ≥
`CONFIDENCE_HIGH_MIN`, MEDIUM ≥ `CONFIDENCE_MEDIUM_MIN`, else LOW. LOW makes the
recommendation `REQUIRES_CONFIRMATION` (plan:4086-4099).

**Configuration** in `app/core/config.py`; `CONFIG_VERSION`* is written to every
`decision_runs` row.

| Key | Default | Source | Rule |
|---|---|---|---|
| `GPS_FRESH_MAX_S`, `GPS_STALE_AFTER_S` | 15, 60 | tech:4618-4635 | C35 |
| `RESOURCE_STALE_AFTER_S` | 300 | * | A reading is current up to this age, else STALE (tech:4618-4635 names no threshold) |
| `AGING_FACTOR` | 0.6 | * | `freshness_factor` for AGING GPS |
| `PENDING_ACCEPTANCE_SCORE`, `READINESS_FALLBACK` | 0.5, 0.5 | * | Neutral while unknown |
| `ETA_CAP_S`, `RESOURCE_SAT` | 3600, 3 | * | Normalisation caps |
| `FALLBACK_PENALTY`, `FALLBACK_CONFIDENCE_CAP` | 0.10, 0.40 | * | A fallback route gets LOW confidence (tech:782-796) |
| `CONFIDENCE_HIGH_MIN`, `CONFIDENCE_MEDIUM_MIN` | 0.80, 0.50 | * | Band cut points |
| `HOSPITAL_SEARCH_RADII_M` | 10000, 25000, 50000 | * | Each radius in turn, then escalate (db:2222-2238) |
| `ACCEPTANCE_TIMEOUT_S` = `RESERVATION_HOLD_TTL_S` | 60 | plan:815-823 | A request and its hold expire together |
| `SWEEPER_INTERVAL_S` | 5 | * | Expiry sweep period (S11) |
| `STABILITY_MARGIN` | 0.05 | * | Keep the current pick unless beaten by more, or it becomes ineligible (BR-013 prd:1202) |
| `REROUTE_MIN_GAIN_S` | 120 | * | Offer a new route only above this saving (flow:3146-3162) |
| `DECISION_LOCK_ETA_S` | 120 | * | At or below this ETA with a CONFIRMED reservation, only critical triggers reassess (flow:3409-3429) |
| `HEARTBEAT_S` | 10 | * | Simulation heartbeat period (S4) |
| `LATENCY_SAMPLE_RUNS` | 50 | * | Matches timed by `measure_decision_latency.py` (S14) |

### A5. State and transactions

Each numbered transaction is one database transaction. Events publish only after
commit (db:2895-2907). Times use the database clock (db:5302-5312): transactions use `NOW()`, and
each engine run takes its `now` from `SELECT NOW()`, so the hard pass and the
hold judge freshness by the same clock. Every transition writes an audit row. Services own
`ALLOWED_TRANSITIONS` (pattern db:5795-5809).

**0. Transitions**

| Entity | From → to | Trigger | Step |
|---|---|---|---|
| Incident | → CREATED | incident created | S3 |
| Incident | CREATED → ANALYZING | ambulance matching starts | S4 |
| Incident | ANALYZING → DISPATCHED | the dispatcher confirms an ambulance | S4 |
| Incident | DISPATCHED → HOSPITAL_SELECTED | hospital matching selects a hospital | S6 |
| Incident | HOSPITAL_SELECTED → HOSPITAL_SELECTED | rejection or expiry re-ranks to a new hospital | S11 |
| Incident | HOSPITAL_SELECTED → ACCEPTED → RESOURCE_RESERVED | accept commits (A5.2) | S7 |
| Incident | RESOURCE_RESERVED, IN_TRANSIT → HOSPITAL_SELECTED | reservation lost and a new hospital selected (flow:1636-1670 REASSESSMENT → HOSPITAL_SELECTION) | S12 |
| Incident | DISPATCHED … IN_TRANSIT → ANALYZING → DISPATCHED | ambulance failure and reassignment (db:4479-4531) | S12 |
| Incident | RESOURCE_RESERVED → IN_TRANSIT | mission reaches `EN_ROUTE_TO_HOSPITAL` | S8 |
| Incident | IN_TRANSIT → ARRIVED → HANDOVER → COMPLETED | mission reaches the same state | S11 |
| Incident | any non-terminal → ESCALATED | nothing feasible (C24) | S4, S6 |
| Incident | ESCALATED → DISPATCHED or HOSPITAL_SELECTED | manual coordination: the dispatcher confirms an eligible ambulance or hospital through the normal endpoints (flow:1966-1982) | S11 |
| Incident | any non-terminal → CANCELLED | the dispatcher cancels (db:4460-4475) | S11 |
| Incident | FAILED | no spec trigger; no step writes it | — |
| Mission | CREATED → ASSIGNED | ambulance confirmed | S4 |
| Mission | ASSIGNED → EN_ROUTE_TO_PATIENT → ON_SCENE → PATIENT_ON_BOARD → EN_ROUTE_TO_HOSPITAL | crew `PATCH /missions/{id}` (tech:3648); → EN_ROUTE_TO_HOSPITAL needs a CONFIRMED destination (C30), else 409 `CONFLICT` | S8 |
| Mission | EN_ROUTE_TO_HOSPITAL → ARRIVED → HANDOVER → COMPLETED | crew `PATCH /missions/{id}` | S11 |
| Mission | EN_ROUTE_TO_HOSPITAL ⇄ REASSESSMENT | critical reassessment starts / a destination is confirmed | S12 |
| Mission | non-terminal → FAILED | ambulance failure; the replacement gets a new mission | S12 |
| Mission | non-terminal → CANCELLED | incident cancelled | S11 |
| Reservation | → HELD → CONFIRMED → IN_USE → RELEASED | A5.1, A5.2, consume, release (db:5802-5806) | S7, S11 |
| Reservation | HELD → EXPIRED | the TTL passes (C34) | S11 |
| Reservation | HELD → CANCELLED | A5.3 rule b, or the incident is cancelled | S11, S12 |
| Reservation | CONFIRMED → RELEASED | A5.3 rule c, release, reassignment or cancellation (C34) | S11, S12 |

Crew accept (`POST /ambulance-assignments/{id}/accept`) changes the assignment,
not the mission.

**1. Request acceptance and hold** (db:1345-1378, db:2868-2877)

1. Lock every REQUIRED resource row of the hospital with `SELECT … FOR UPDATE`,
   in `id` order.
2. If any row meets a condition below, roll back everything (db:2881-2891).
   Then, in a separate transaction, write one audit row (db:3867 monitors
   reservation failures) and re-run hospital matching (db:4344-4345). S6's hard
   pass applies the same conditions to every REQUIRED resource, so the hospital
   drops out on live data. A refusal is not stored as ineligibility. The re-run
   also skips hospitals already refused in this chain of re-runs, so the chain
   ends when none remain (then ESCALATED, C24); a later trigger starts a new
   chain.

   | Condition | Response |
   |---|---|
   | no row for a REQUIRED resource | `MISSING_CAPABILITY`* |
   | `status` is not ACTIVE | `RESOURCE_UNAVAILABLE` (tech:4525) |
   | `available_capacity IS NULL` | `CAPACITY_UNKNOWN`* |
   | `last_updated_at < NOW() − RESOURCE_STALE_AFTER_S` | `STALE_DATA` (plan:4095) |
   | `available_capacity < 1` | `RESOURCE_UNAVAILABLE` (tech:4525) |

3. Otherwise, for each row: `available −= 1`, `reserved += 1`, `version += 1`;
   insert a HELD reservation with `expires_at = NOW() + RESERVATION_HOLD_TTL_S`
   and a `resource_events` HELD row. Then insert one PENDING acceptance request
   with the same expiry.

**2. Accept.** `Idempotency-Key` is required and stored on the request.

1. Lock the request and its reservations.
2. ACCEPTED under the same key: return the stored result, change nothing.
   ACCEPTED under another key, or REJECTED or EXPIRED: 409 `CONFLICT`, change
   nothing.
3. All reservations HELD and `expires_at > NOW()`: request → ACCEPTED,
   reservations → CONFIRMED, incident → ACCEPTED → RESOURCE_RESERVED; write the
   mission destination, a `mission_events` row and a notification.
4. Any reservation HELD past `expires_at`: expire every HELD reservation of the
   request, restoring each unit once (`reserved −= 1`, `available += 1`); set the
   request EXPIRED with `closed_reason`* = `HOLD_LOST`*; return
   `RESOURCE_UNAVAILABLE`; start reassessment.
Every path that ends a hold (sweeper, A5.3 b, cancellation) closes its request
in the same transaction, so a PENDING request never has a non-HELD reservation.

**3. Resource lost** (S12)

1. If `total = 0`, or no rule below applies, return 409 `CONFLICT` and change
   nothing. A NULL count never satisfies `> 0`.
2. Otherwise decrement `total` and exactly one other count, by the first rule
   that applies:

   | Rule | When | Decrement | Also |
   |---|---|---|---|
   | a | `available > 0` | `available` | — |
   | b | a HELD reservation exists | `reserved` | newest HELD → CANCELLED; its request's other HELD reservations → CANCELLED, each restoring its unit once; the request → EXPIRED, `closed_reason`* = `HOLD_LOST`* |
   | c | a CONFIRMED reservation exists | `reserved` | newest CONFIRMED → RELEASED, `release_reason = RESOURCE_LOST` (db:1284, db:1202); its request's other CONFIRMED reservations → RELEASED with the same reason, each restoring its unit once |
   | d | `occupied > 0` | `occupied` | — |

3. Write a `resource_events` LOST row. After b or c, run critical reassessment
   after commit (BR-008 prd:1172).

**Two incidents, one resource.** The first hold to commit wins; the other is
refused and moves to its next candidate. Greedy allocation is acceptable for the
MVP (flow:3195-3221); pre-emption is out of scope and the pitch says so.

### A6. Golden seed and reset

`app.simulation.seed.reset_and_seed()` backs both `scripts/reset_demo.py` and the
`golden_db` fixture:

1. Refuse when `APP_ENV=production` (db:5350-5365).
2. Migrate to head.
3. `TRUNCATE … RESTART IDENTITY CASCADE` every domain table (full reset is
   acceptable for an isolated demo, db:2804). The append-only triggers are
   row-level `UPDATE`/`DELETE` triggers, which `TRUNCATE` does not fire.
4. Seed deterministically with seed 2026 (db:2808-2826). Every row is
   `data_mode = SIMULATED` with fictitious names; timestamps are `NOW()` except
   AMB-005 and H-008; every golden hospital lies inside the first search radius;
   scenario ETAs live in `simulation_scenarios.payload`, served by
   `MockRoutingProvider`.

**Golden incident** (prd:3015-3023, tech:2125-2131): severity CRITICAL; REQUIRED
ICU, TRAUMA, VENTILATOR and EMERGENCY_SURGERY. ICU and VENTILATOR are capacity
resources (tech:2155) and count as capabilities of any hospital with a row for
them, so a hospital without an ICU row is `MISSING_CAPABILITY:ICU`*; TRAUMA and
EMERGENCY_SURGERY are capabilities only. "All four"
below means all four requirements. Role is the candidate's letter in
prd:3029-3043; the exclusion codes are chosen here*.

| Code | Role | Setup | Expected |
|---|---|---|---|
| AMB-001 | A | ETA 4 min, no ventilator | Excluded: `MISSING_EQUIPMENT:VENTILATOR` |
| AMB-002 | B | ETA 7 min, ventilator + trauma kit | **Selected** |
| AMB-003 | C | ETA 6 min, ventilator, on seeded mission MSN-000001 | Excluded: `ACTIVE_MISSION` |
| AMB-004 | D | ETA 9* min, ventilator + trauma kit | Replacement in the ambulance-failure event |
| AMB-005 | — | Ventilator, GPS 120* s old | Excluded: `GPS_STALE` |
| H-001 | A | ETA 5 min, no ICU | Excluded: `MISSING_CAPABILITY:ICU` |
| H-002 | B | ETA 8 min, no trauma | Excluded: `MISSING_CAPABILITY:TRAUMA` |
| H-003 | C | ETA 10 min (15 after traffic, alternative 11); all four; ICU 1/1, ventilator 1*/1* | **Selected**; loses its ICU in the failure event |
| H-004 | D | ETA 13* min; all four; ICU 1, ventilator 1* | Selected after the ICU failure |
| H-005 | E | ETA 16* min; all four; ICU 1, ventilator 1* | Selected after H-004 rejects |
| H-006 | — | All four; ICU available 0 | Excluded: `RESOURCE_UNAVAILABLE:ICU` |
| H-007 | — | All four; ICU available `NULL` | Excluded: `CAPACITY_UNKNOWN:ICU` |
| H-008 | — | All four; ICU reading 900* s old | Excluded: `STALE_DATA:ICU` |

The scenario follows prd:3015-3092 and plan:3591-3760. Fillers AMB-006..010 and
H-009..010 are generated from the seed, farther away, each lacking at least one golden requirement*, so the golden hard
pass excludes them.

---

## Part B — Build steps

**Order.** The spec build order (plan:4665-4692) with two declared changes:
WebSocket and the dispatcher UI come before the other screens, because the
spec's slice ends "WebSocket ↓ Dispatcher UI" (tech:1874-1900); tests are written
in each step, not at plan:4686 (C22). **Nothing outside S0–S10 starts before the
S10 exit passes.** Hours derive from plan:3485-3503.

**Slice chain** (all server-side): dispatcher confirms an ambulance → route (S5)
→ hospital matching (S6, C05) → acceptance request and hold (S7) → hospital
accepts → mission destination (S8) → live update (S9). Held back to S11–S12:
rejection, sweeper, crew reject, consume, cancel, reassignment, resource loss.

**Paths.** API tests are under `apps/api/tests/`; web tests under `apps/web/`.
React file names under `src/` are marked * (the specs name none).
`apps/api/tests/test_rbac.py` is a table of (endpoint, role, expected status);
each step adds rows for its endpoints, and every Exit that lists it runs it.

### S0 · Repository, database, skeleton — 0–2 h · M1

**Build**
1. `git init`. `.gitignore`: `.env`, `.env.demo`, `.env.test`, `.venv`,
   `node_modules`, `dist/`, `__pycache__/`, `.pytest_cache/`, `.ruff_cache/`,
   `.mypy_cache/`, `*.egg-info/`, `test-results/`, `playwright-report/`.
   `.env.example` (A2 keys, empty values), `.env`, `.env.test`, `README.md` with
   an empty "Not built" section, `docs/spec-conflicts.md`, `pnpm-workspace.yaml`
   (`apps/web`, `packages/*`).
2. Web scaffold first, while `apps/web` does not exist (command block).
3. `docker-compose.yml`: service `postgres`, image from P1, `POSTGRES_PASSWORD`
   from `.env`, port `127.0.0.1:5432:5432`, a named data volume*.
4. `apps/api/pyproject.toml`: `requires-python = "==3.12.*"`*, hatchling, `packages = ["app"]`; runtime fastapi,
   uvicorn[standard], sqlalchemy>=2, alembic, psycopg[binary], geoalchemy2,
   pydantic-settings, pyjwt, argon2-cffi; dev extra pytest, httpx, ruff, mypy;
   ruff isort `known-first-party = ["app", "tests"]`.
5. `scripts/db_create.py`: creates `smart_ambulance_{dev,test,demo}` and enables
   `postgis` and `pgcrypto` in each, skipping what exists (db:4142-4150,
   db:5415-5427).
6. `apps/api/alembic.ini` with `script_location = %(here)s/migrations`;
   `migrations/env.py` takes the URL from the caller or settings.
7. `app/main.py`: `FastAPI(openapi_url="/api/v1/openapi.json")` (C27).
   `GET /api/v1/health/db` returns `connectivity`*, `migration_version`* (null
   before S1) and `simple_query`* (the checks of db:4692-4696); a database failure
   returns 503 with the error envelope (tech:4503-4513) and `INTERNAL_ERROR`
   (C36); no connection details (db:4684-4698).
8. Middleware: `X-Request-ID` echoed or generated with the `req_` prefix
   (tech:4510, tech:6247-6263); one JSON log line per request with `request_id`,
   `user_id`, `route`, `duration` (ms), `status` (tech:4776-4784) plus
   `timestamp` and `level` (plan:2579-2588).
9. `scripts/full_suite.ps1`* (A2).

```powershell
pnpm create vite apps/web --template react-ts --no-interactive
pnpm --dir apps/web add @tanstack/react-query zustand react-router react-hook-form zod lucide-react recharts
pnpm --dir apps/web add -D tailwindcss @tailwindcss/vite vitest @testing-library/react jsdom @playwright/test openapi-typescript
pnpm --dir apps/web exec playwright install chromium
uv venv --python 3.12 apps\api\.venv
uv pip install --python $py -e "apps/api[dev]"
docker compose up -d postgres
docker compose exec postgres pg_isready -h 127.0.0.1 -U postgres   # repeat until "accepting connections"; the init server listens on no TCP port
& $py scripts\db_create.py
```

**Tests** — `tests/test_health.py`: `test_health_db_up`,
`test_health_db_unreachable_503_envelope`.

**Exit**
```powershell
& $py -m pytest apps\api\tests\test_health.py -v
& $py -m uvicorn app.main:app --app-dir apps\api          # second window
Invoke-RestMethod http://127.0.0.1:8000/api/v1/health/db   # connectivity ok, migration_version empty
Invoke-RestMethod http://127.0.0.1:8000/api/v1/openapi.json | Select-Object openapi
pnpm --dir apps/web build                                  # exit 0
& $py -m ruff check apps\api                               # All checks passed
.\scripts\full_suite.ps1                                   # after stopping the API
```

### S1 · Schema, seed, reset — 2–5 h

**Build**
- Migrations `0001_extensions` … `0015_simulation` in db:5390-5410 order
  (`0016_ml` waits for S13): the P0 tables (db:6084-6102) plus
  `patient_requirement_items`, `resource_events`, `decision_candidates`,
  `decision_reasons`, `notifications`, `simulation_scenarios`.
- Enums as text + CHECK generated from `app/core/enums.py`; capacity CHECKs
  (db:1114-1132); partial unique indexes for one active assignment and one
  active mission per ambulance (db:3035-3065); GiST on every `geography` column.
- Append-only row-level triggers raising on UPDATE or DELETE of
  `mission_events`, `resource_events`, `decision_*`, `audit_logs` (db:1545,
  db:3070-3080).
- `app/simulation/seed.py` and `scripts/reset_demo.py` (A6).

**Tests** — `tests/db/`
- `test_spec_cases.py`: `test_db_001`, `test_db_002`, `test_db_003`, `test_db_004`, `test_db_005`, `test_db_006` (DB-001..006, db:4755-4840)
- `test_migrations.py`: `test_migrations_roundtrip_twice` (downgrade `base`,
  upgrade `head`, twice)
- `test_constraints.py`: `test_capacity_check_rejects_negative`,
  `test_second_active_assignment_rejected`, `test_mission_events_update_raises`
- `test_seed.py`: `test_seed_is_deterministic`, `test_reset_refuses_in_production`,
  `test_reset_succeeds_with_append_only_rows_present`

**Exit**
```powershell
& $py -m pytest apps\api\tests\db -v
& $py scripts\reset_demo.py
& $py -m alembic -c apps\api\alembic.ini heads             # note the head revision
& $py -m uvicorn app.main:app --app-dir apps\api          # second window
Invoke-RestMethod http://127.0.0.1:8000/api/v1/health/db   # migration_version equals it
.\scripts\full_suite.ps1                                   # after stopping the API
```

### S2 · Authentication and RBAC — 5–6 h

**Build**
- `/auth/login`, `/auth/logout`, `/auth/me`, `/auth/refresh` (tech:3532-3539).
- Argon2 hashing, JWT, a `require_roles(...)` dependency; one seeded user per
  role (prd:501-512); error codes from tech:4519-4533.
- Data scoping in every service query: hospital users see only their hospital,
  crew only their mission (db:3276-3310).

**Tests** — `tests/test_auth.py`: `test_login_invalid_401`,
`test_me_without_token_401_envelope` (asserts `AUTHENTICATION_ERROR`),
`test_me_as_dispatcher_returns_role`. `tests/test_rbac.py`: rows for `/auth/*`.

**Exit** — `& $py -m pytest apps\api\tests\test_auth.py apps\api\tests\test_rbac.py -v`, then `.\scripts\full_suite.ps1`

### S3 · Slice CRUD — 6–8 h

**Build.** Only these, from tech:3543-3605: incidents `POST`, `GET /{id}`,
`POST /{id}/requirements`; ambulances `GET`, `POST /{id}/location`,
`POST /{id}/status`; hospitals `GET`, `GET /{id}/resources`, resource `PATCH`.
Optimistic `version`; an audit row on every create and status change; points
built longitude first (db:2127-2164); a resource `PATCH` writes `resource_events`.

**Tests** — `tests/test_slice_crud.py`:
`test_invalid_transition_created_to_completed_rejected` (calls IncidentService
directly; S3 has no incident status endpoint),
`test_incident_requires_one_requirement_notes_optional`,
`test_point_roundtrip_lng_lat`, `test_stale_version_returns_concurrent_update`,
`test_hospital_user_cannot_read_other_hospital`. `tests/test_rbac.py`: rows for
these endpoints, including (`POST /api/v1/incidents`, HOSPITAL_STAFF, 403,
`AUTHORIZATION_ERROR`).

**Exit** — `& $py -m pytest apps\api\tests\test_slice_crud.py apps\api\tests\test_rbac.py -v`, then `.\scripts\full_suite.ps1`

### S4 · Ambulance matching and heartbeat — 8–11 h · M2

**Build**
- `app/decision_engine/`, a pure package (tech:586-604):
  `evaluate_ambulances(incident, candidates, etas, config, now)` implements A4.
  The `RoutingProvider` interface and `MockRoutingProvider` start here.
- Candidates from db:2168-2193. Each run persists `decision_runs`,
  `decision_candidates` (excluded ones with reasons) and `decision_reasons`.
- No eligible ambulance: incident → ESCALATED, no recommendation (BR-015
  prd:1214, C24).
- `POST /dispatch/ambulances/match` (tech:3570).
- `POST /dispatch/ambulances/{id}/confirm` (tech:3571): `{id}` is the ambulance
  id and the body carries `incident_id`*. Requires `Idempotency-Key`; creates
  the assignment and the mission; rank ≠ 1 requires `override_reason` (BR-010
  prd:1184); an ineligible ambulance returns 409.
- `POST /ambulance-assignments/{id}/accept`*: FR-011 (prd:652) needs it and
  tech's list lacks it.
- `app/simulation/heartbeat.py` while `SIMULATION_ENABLED=true`: every
  `HEARTBEAT_S`, refresh GPS and resource timestamps on SIMULATED rows except
  AMB-005, H-008 and ambulances in its skip set (S12 `gps-lost`).

**Tests**
- `tests/decision_engine/test_ambulance_engine.py`:
  `test_ineligible_candidate_has_no_score_or_rank`,
  `test_unknown_equipment_is_not_available`,
  `test_unknown_requirement_neither_filters_nor_scores`,
  `test_same_input_same_output`, `test_tie_break_eta_then_code`,
  `test_engine_imports_no_io` (parses `decision_engine/*.py` with `ast`; fails on
  `sqlalchemy`, `fastapi` or `httpx`)
- `tests/test_dispatch_ambulances.py`:
  `test_golden_amb_002_selected_001_003_005_excluded_with_reasons`,
  `test_no_eligible_ambulance_escalates_without_fabrication`,
  `test_override_without_reason_422`, `test_confirm_ineligible_409`,
  `test_confirm_retry_same_key_returns_stored_result`,
  `test_crew_accept_assignment`
- `tests/test_heartbeat.py`: `test_heartbeat_skips_amb_005_h_008_and_skip_set`
- `tests/test_rbac.py`: rows for these endpoints

**Exit** — `& $py -m pytest apps\api\tests\decision_engine apps\api\tests\test_dispatch_ambulances.py apps\api\tests\test_heartbeat.py apps\api\tests\test_rbac.py -v`, then `.\scripts\full_suite.ps1`

### S5 · Route calculation — 11–13 h

**Build.** `POST /routes/calculate`, persisting to `routes` (tech:3655-3661);
confirming an ambulance calls it. Fallback chain primary → secondary → last
cached route → `MANUAL_REVIEW` (tech:782-796). Every route records `provider`,
`fallback_used`, `computed_at`. Comparison, reroute and the live provider wait
for S12.

**Tests** — `tests/test_routes.py`:
`test_primary_failure_uses_fallback_confidence_low` (a test primary that always
fails; confidence `FALLBACK_CONFIDENCE_CAP`, band LOW),
`test_all_providers_fail_returns_manual_review`,
`test_mock_incident_to_h003_is_600_s_not_fallback`. `tests/test_rbac.py` rows.

**Exit** — `& $py -m pytest apps\api\tests\test_routes.py apps\api\tests\test_rbac.py -v`, then `.\scripts\full_suite.ps1`

### S6 · Hospital matching — 13–17 h · M3

**Build**
- `evaluate_hospitals(...)`. Hard pass (tech:3220-3242): every REQUIRED
  capability present; every REQUIRED resource present as a row with `status` ACTIVE, non-NULL
  `available >= 1` and a current reading (A5.1's conditions); hospital ACTIVE.
  `ST_DWithin` over each radius in `HOSPITAL_SEARCH_RADII_M`, then escalate
  (db:2197-2238). Hospitals that rejected this incident stay excluded (BR-009
  prd:1178). Ranking per A4 with `STABILITY_MARGIN`.
- Nothing feasible: incident → ESCALATED, no recommendation (C24).
- Runs automatically after route calculation (C05);
  `POST /dispatch/hospitals/match` (tech:3612) runs it on demand.

**Tests** — `tests/test_hospital_matching.py`:
`test_golden_h003_selected_h001_h002_excluded`,
`test_null_capacity_excluded_capacity_unknown` (H-007),
`test_stale_reading_excluded` (H-008), `test_zero_capacity_excluded` (H-006),
`test_inactive_resource_excluded`, `test_missing_resource_row_excluded_missing_capability`, `test_rejected_hospital_stays_excluded_on_rerun`,
`test_radius_expands_then_escalates_without_fabrication`,
`test_stability_margin_keeps_current`. `tests/test_rbac.py` rows.

**Exit** — `& $py -m pytest apps\api\tests\test_hospital_matching.py apps\api\tests\test_rbac.py -v`, then `.\scripts\full_suite.ps1`
(Product Quality Gate 4, prd:2429-2436.)

### S7 · Acceptance request, hold, accept — 17–19 h

**Build**
- `POST /acceptance-requests` (A5.1), called automatically for the rank-1
  hospital unless the recommendation is `REQUIRES_CONFIRMATION`; then nothing is
  sent until the dispatcher calls it. `GET /acceptance-requests/{id}`.
  `POST /acceptance-requests/{id}/accept` (A5.2) (tech:3621-3623).
- Only staff of the target hospital may accept.

**Tests** — `tests/test_acceptance.py`:
- `test_hold_refuses_null_capacity`, `test_hold_refuses_stale_reading`,
  `test_hold_refuses_zero_available`, `test_hold_refuses_inactive_resource`
- `test_hold_covers_every_required_resource_or_none`
- `test_two_concurrent_holds_on_last_icu_exactly_one_succeeds` (two threads,
  separate connections; `available = 0`, exactly one HELD row; db:3519-3537)
- `test_failed_hold_changes_no_capacity_and_writes_no_reservation`
- `test_refused_hold_writes_audit_and_reruns_matching`
- `test_accept_expired_hold_restores_capacity_once`,
  `test_every_hold_end_closes_its_request`,
  `test_accept_retry_same_key_returns_stored_result`,
  `test_accept_other_key_or_closed_request_409`
- `test_low_confidence_hospital_waits_for_dispatcher`
- `test_refusal_chain_ends_escalated_when_all_refused`
- `test_other_hospital_staff_cannot_accept_403`
- `tests/test_rbac.py` rows

**Exit** — `& $py -m pytest apps\api\tests\test_acceptance.py apps\api\tests\test_rbac.py -v`, then `.\scripts\full_suite.ps1`

### S8 · Mission state — 19–22 h · M4 · API checkpoint

**Build.** MissionService: transitions per A5.0 carry `state_version`, and a
stale write returns `MISSION_STATE_CONFLICT` (db:1467-1488); every destination
change writes a mission event, a notification and an audit row; crew status
changes through `PATCH /missions/{id}` (tech:3648).

**Tests**
- `tests/test_missions.py`: `test_stale_state_version_conflict`,
  `test_destination_change_writes_event_notification_audit`,
  `test_invalid_mission_transition_409`, `test_en_route_to_hospital_sets_incident_in_transit`
- `tests/e2e/test_golden_slice.py`: `test_golden_slice` — on `golden_db`, over
  HTTP as each role: incident created; AMB-002 selected; dispatcher confirms and
  crew accepts; route calculated; H-003 selected with ICU and ventilator HELD;
  H-003 accepts and both reservations are CONFIRMED; mission destination H-003;
  `reserved_capacity` 1 on each; an audit row for every step (Product Quality
  Gate 1, prd:2400-2409)
- `tests/test_rbac.py` rows

**Exit** — `& $py -m pytest apps\api\tests\test_missions.py apps\api\tests\e2e\test_golden_slice.py apps\api\tests\test_rbac.py -v`, then `.\scripts\full_suite.ps1`

### S9 · Realtime — 22–25 h

**Build**
- `/ws` with JWT auth and an RBAC check on every channel subscription
  (tech:4123-4141). Envelope `{event_id, event, entity_version, timestamp, mode,
  payload}`, names from tech:4149-4163; services publish after commit.
- `apps/web/src/lib/realtime/`: dedupe by `event_id`; drop older
  `entity_version`; reconnect with backoff, then resync over REST
  (flow:2612-2632).
- `apps/web/vitest.config.ts` (from `vitest/config`, with `@vitejs/plugin-react`):
  `environment: "jsdom"`, `include: ["src/**/*.test.{ts,tsx}"]`. It is outside
  the scaffold's tsconfig projects, so `tsc -b` does not check it, and
  Playwright's `e2e/` specs are never collected.

**Tests**
- `tests/test_realtime.py`: `test_rolled_back_hold_publishes_nothing`,
  `test_hospital_cannot_subscribe_other_hospital`,
  `test_slice_client_receives_resource_reserved`
- `src/lib/realtime/realtime.test.ts`*: `drops_out_of_order_event`,
  `shows_reconnecting_then_resyncs`

**Exit**
```powershell
& $py -m pytest apps\api\tests\test_realtime.py -v
pnpm --dir apps/web exec vitest run src/lib/realtime --reporter=verbose
.\scripts\full_suite.ps1
```

### S10 · Dispatcher UI — 25–29 h · vertical-slice exit

**Build**
- Pages `/login`, `/dispatcher/emergencies/new`, `/dispatcher/emergencies/:id`
  (flow:3656-3700); every call through `src/lib/api/` with generated types
  (tech:5108-5128).
- Candidate lists show excluded candidates with reasons (flow:583-601); a "Why
  selected?" drawer; freshness badges; live updates via `src/lib/realtime/`;
  `DEMO MODE` on every screen (flow:3281-3295); Tailwind tokens from
  design:214-322 and design:417-500 (C28). No decision logic in components; no
  map yet.
- `vite.config.ts` dev server proxies `/api` and `/ws` to `127.0.0.1:8000`*, so
  the browser uses one origin.
- `apps/web/playwright.config.ts`: `testDir: "e2e"`, `baseURL:
  "http://localhost:5173"` (the `CORS_ORIGINS` origin, A2), Chromium, no
  `webServer` (servers are started by hand, A2).

**Tests**
- `src/components/candidate-list.test.tsx`*:
  `candidate_list_renders_loading_error_stale_simulated`
- `src/components/resource-card.test.tsx`*:
  `resource_card_renders_loading_error_stale_simulated`
- `e2e/slice.spec.ts`: `slice` — the dispatcher logs in and creates the golden
  incident; AMB-002 recommended, AMB-001/003/005 excluded with reasons; the
  dispatcher confirms; the test's API client performs the crew accept and the
  H-003 accept; without a reload the page shows H-003 with ICU and ventilator
  reservations CONFIRMED; `DEMO MODE` visible throughout (tech:1874-1900)

**Exit**
```powershell
pnpm --dir apps/web exec vitest run src/components --reporter=verbose
.\scripts\full_suite.ps1                                    # no servers running
$env:ENV_FILE = ".env.test"; & $py scripts\reset_demo.py   # window 1
& $py -m uvicorn app.main:app --app-dir apps\api            # window 1
pnpm --dir apps/web dev                                     # window 2
pnpm --dir apps/web exec playwright test --reporter=list     # window 3; includes e2e/slice.spec.ts
```

### S11 · Remaining flows and screens — 29–34 h

**Build**
- Rejection: `POST /acceptance-requests/{id}/reject` (tech:3624) with reasons from
  flow:924-933; exclude, re-rank, request the next candidate, notify.
- Sweeper every `SWEEPER_INTERVAL_S`: expire HELD reservations and PENDING
  requests past `expires_at`, restoring each unit once, then reassess.
- Crew rejection: `POST /ambulance-assignments/{id}/reject`* re-runs matching
  without that ambulance.
- Reservations (tech:3633-3637): `POST /reservations` limited to HOSPITAL_STAFF,
  HOSPITAL_ADMIN and SYSTEM_ADMIN (C31), holding a unit of the caller's own
  hospital by A5.1's lock and checks without an acceptance request (prd:1655);
  `consume` at handover (reserved → occupied, reservation IN_USE); `release`.
  Incident cancellation cascades (db:4460-4475).
- Crew screen `/ambulance/mission` (flow:3676): accept or reject, status buttons, the last
  confirmed destination with its age while offline (flow:1598-1630).
- Hospital screens (flow:3683-3685) `/hospital/incoming/:id` (accept, or reject with reason) and
  `/hospital/resources` (edits write `resource_events`).
- `/dispatcher` overview (flow:3663) and the P2 map, with an "offline" panel when tiles fail.
  `vite.config.ts` sets `envDir: "../.."` so `VITE_MAPBOX_TOKEN` comes from the
  root env file.
- Manual coordination on `ESCALATED` (flow:1966-1982): the incident screen lets
  the dispatcher pick an eligible ambulance, route and hospital and request
  acceptance through the S4–S7 endpoints; nothing bypasses the hard pass (C24).
- `e2e/golden.spec.ts`: three browser contexts (dispatcher, crew, hospital)
  through tech:2120-2178 steps 1–16 and 21–25.

**Tests**
- `tests/test_rejection.py`: `test_rejection_reranks_and_requests_next`
  (Gherkin plan:2817-2879)
- `tests/test_sweeper.py`: `test_sweeper_expires_hold_restores_capacity_once`
- `tests/test_crew.py`: `test_crew_reject_reruns_match`
- `tests/test_manual_coordination.py`: `test_manual_coordination_still_enforces_hard_constraints`
- `tests/test_reservations.py`: `test_consume_moves_reserved_to_occupied`,
  `test_cancel_leaves_no_active_reservation`,
  `test_post_reservation_limited_to_hospital_roles`
- `src/pages/crew-mission.test.tsx`*: `crew_offline_shows_cached_destination_and_age`
- `src/pages/hospital-incoming.test.tsx`*: `hospital_sees_only_own_incoming`
- `e2e/golden.spec.ts`: `golden_steps_1_16_21_25`, `map_offline_panel_when_tiles_fail`
- `tests/test_rbac.py` rows

**Exit** — Product Quality Gate 2 (prd:2411-2418).
```powershell
& $py -m pytest apps\api\tests\test_rejection.py apps\api\tests\test_sweeper.py apps\api\tests\test_crew.py apps\api\tests\test_reservations.py apps\api\tests\test_manual_coordination.py apps\api\tests\test_rbac.py -v
pnpm --dir apps/web exec vitest run src/pages --reporter=verbose
.\scripts\full_suite.ps1
# then the browser suite (A2); it includes e2e/golden.spec.ts
```

### S12 · Reassessment, simulation, deferred routing — 34–40 h · M5–M6

**Build**
- ReassessmentService: triggers from plan:1162-1173, classed minor, significant
  or critical (flow:3100-3142), applying `STABILITY_MARGIN` and
  `DECISION_LOCK_ETA_S`.
- Resource loss (A5.3). Reassignment: the old assignment becomes SUPERSEDED and
  its reservations are released before the new ones confirm (db:4479-4531).
- Routing: emergency travel cost (tech:3101-3128); `POST /routes/compare`,
  `POST /missions/{id}/reroute`; a traffic multiplier in `MockRoutingProvider`;
  the live provider (P2).
- `/api/v1/admin/simulation/*`, SYSTEM_ADMIN or DEMO_CONTROLLER only
  (tech:6597-6612): `reset`, `scenario/start`, `traffic-change`, `resource-lost`,
  `hospital-reject`, `ambulance-failure`, `gps-lost` (adds the ambulance to the
  heartbeat skip set until reset), `route-blocked`.
- A movement ticker and the Demo Console at `/demo/control` (flow:3698); `e2e/golden.spec.ts`
  extended to all 25 steps plus the failure test at tech:2182-2206.

**Tests**
- `tests/failures/test_failures.py`, one per case at tech:1521-1540:
  `test_hospital_rejection`, `test_no_suitable_ambulance`,
  `test_no_suitable_hospital`, `test_resource_unavailable`, `test_gps_failure`,
  `test_routing_provider_failure`, `test_hospital_api_unavailable_marks_unknown`,
  `test_duplicate_reservation`, `test_invalid_state_transition`,
  `test_unauthorized_action`, `test_websocket_disconnect_resyncs`,
  `test_ml_failure_uses_fallback`
- `tests/test_resource_loss.py`: `test_loss_rules_a_b_c_d_keep_invariant`,
  `test_loss_with_nothing_to_decrement_409_no_change`,
  `test_loss_releases_sibling_reservations`
- `tests/test_demo_events.py`:
  `test_icu_failure_releases_reranks_h004_accepts_destination_updated`
  (plan:3689-3716), `test_traffic_spike_offers_alternative_route`
  (plan:3668-3686), `test_h004_rejects_h005_selected` (plan:3718-3738),
  `test_ambulance_failure_supersedes_assigns_amb_004` (plan:3740-3757)
- `e2e/golden.spec.ts`: `golden_all_25_steps`, `golden_failure_path`
- `tests/test_rbac.py` rows

**Exit** — Product Quality Gates 3 and 5 (prd:2420-2440); no manual database
edits.
```powershell
& $py -m pytest apps\api\tests\failures apps\api\tests\test_resource_loss.py apps\api\tests\test_demo_events.py apps\api\tests\test_rbac.py -v
.\scripts\full_suite.ps1
# then the browser suite (A2); it includes e2e/golden.spec.ts
```

### S13 · Optional ML and voice — 40–42 h, only after the S12 exit

**Recommendation: skip.** There is no training data, and "No Fabricated
Accuracy" (plan:1084-1093) rules out a demo model. Cut order: plan:3507-3535.

**Exit — one of:**
- Skipped: `Select-String -Path .env,.env.test -Pattern "^ML_ENABLED=false$"` finds
  both, and `(Get-Content README.md -Raw) -match '(?s)## Not built.*FR-023.*FR-032'`
  prints `True` (prd:824, prd:962).
- Built: `& $py -m pytest apps\api\tests\test_ml.py -v` shows
  `test_ml_timeout_uses_provider_eta PASSED`, and with `ML_ENABLED=true` in
  `.env.test` the browser suite (A2) passes.
- Either way, `.\scripts\full_suite.ps1`.

### S14 · Hardening — 42–45 h · M7

**Build**
- CORS limited to `CORS_ORIGINS`.
- `scripts/measure_decision_latency.py`: with `ENV_FILE=.env.test`, runs
  `LATENCY_SAMPLE_RUNS` matches and prints p50 and p95; `docs/measurements.md`
  records the dated output against the <2 s target only (tech:4829-4853).
- `docs/dod.md`: every Definition of Done box (plan:4370-4387, tech:6754-6771,
  db:6127-6150), one row per box with an Evidence column naming the test or
  command that proves it, or `none`. Backup/restore is
  proposed as waived for a local demo*; the user confirms or rejects it at this
  step's sign-off.

**Tests** — `tests/test_audit_completeness.py`: `test_audit_completeness` (after
the full scenario on `golden_db`, every critical transition in A5.0 has an audit
row).

**Exit**
```powershell
& $py -m pytest apps\api\tests\test_audit_completeness.py -v
git grep -nIE "sk-[A-Za-z0-9_-]{20,}|[ps]k\.eyJ[A-Za-z0-9_-]{20,}|AKIA[0-9A-Z]{16}"   # prints nothing
git ls-files .env .env.demo .env.test                                                 # prints nothing
$env:ENV_FILE = ".env.test"; & $py scripts\measure_decision_latency.py              # prints p50 and p95
Select-String -Path docs\measurements.md -Pattern "p95"                               # the recorded line
Select-String -Path docs\dod.md -Pattern "\| none \|"                                  # only the backup/restore row
.\scripts\full_suite.ps1
```

### S15 · Demo and pitch — 45–48 h · M8

**Build**
- `.env.demo` (A2). The recorded live run uses the demo database: `$env:ENV_FILE
  = ".env.demo"`, Reset, start the API and web app, perform the golden scenario
  by hand, and save `docs/demo/golden-run.mp4`.
- `docs/pitch/slides.md`: the story at flow:3949-3970, judge answers from
  plan:3761-3804.

**Exit** — the offline check runs on the test database (A2), with Wi-Fi off,
`ROUTING_PROVIDER=mock` and the S10 windows after a fresh reset:
```powershell
pnpm --dir apps/web exec playwright test e2e/golden.spec.ts --reporter=list   # all pass, including map_offline_panel_when_tiles_fail
Test-Path docs\demo\golden-run.mp4                                            # True
Get-ChildItem docs\pitch, README.md, apps\web\src -Recurse -File -Include *.md,*.ts,*.tsx | Select-String -Pattern "first system","live ICU data","saves lives","% accurate"   # prints nothing
.\scripts\full_suite.ps1
```
The patterns are the claims forbidden at plan:5257-5281 and plan:1084-1093.

---

## Part C — If behind

| Checkpoint | If missed, cut | Exit change |
|---|---|---|
| Hour 22: S8 exit green | Drop S13. S11 builds `/hospital/incoming/:id` only | None |
| Hour 29: S10 exit green | S11's crew screen is status buttons only; the map shows markers without routes | Remove `crew_offline_shows_cached_destination_and_age` from S11 |
| Hour 40: S12 exit green | Keep ICU failure, hospital rejection and traffic (prd gates 2–3); drop `gps-lost` and `route-blocked` | Remove `test_gps_failure` and `golden_failure_path` from S12 |

The core chain is never cut: incident → ambulance → route → hospital →
acceptance → reservation (plan:3511-3525).

## Part D — Traceability

| Feature | FR / BR | Tables | API | Logic* | Screen (flow:3661-3698) | Proof |
|---|---|---|---|---|---|---|
| Auth / RBAC | FR-001-002 | users, roles, user_roles | `/auth/*` | `core/security` | `/login` | S2 |
| Emergency | FR-003-005 | incidents, patient_requirement_items | `/incidents` | IncidentService | `/dispatcher/emergencies/new` | S3 |
| Ambulance match + override | FR-008-011, FR-028, BR-004-005, BR-010 | ambulances, ambulance_assignments, decision_* | `/dispatch/ambulances/*`, `/ambulance-assignments/*` | `ambulance_matcher` | Emergency detail | S4, S11 |
| Routing | FR-012-014 | routes | `/routes/*`, `/missions/{id}/reroute` | RoutingService + providers | Map | S5, S12 |
| Hospital match | FR-016-017, BR-001-003, BR-015 | hospitals, hospital_resources, decision_* | `/dispatch/hospitals/match` | `hospital_matcher` | Ranking panel | S6 |
| Acceptance | FR-018-019, BR-006, BR-009 | acceptance_requests | `/acceptance-requests/*` | AcceptanceService | `/hospital/incoming/:id` | S7, S11 |
| Reservation | FR-020-022, BR-007-008 | hospital_resources, reservations, resource_events | `/reservations/*` | ReservationService | Reservation card | S7, S11, S12 |
| Mission + realtime | FR-024-025 | missions, mission_events | `/missions/*`, `/ws` | MissionService, broker | Live mission | S8, S9, S10 |
| Reassessment + failures | FR-026, FR-031, BR-013-014 | decision_runs | `/admin/simulation/*` | ReassessmentService | Alerts, `/demo/control` | S12 |
| Explainability | FR-027 | decision_candidates, decision_reasons | Match responses | `explanations.py` | "Why selected?" drawer | S4, S6, S10 |
| Freshness / data mode | FR-029-030, BR-012 | `last_updated_at`, `data_mode` | All reads | `freshness.py` | Badges, `DEMO MODE` | S4, S6, S7, S10 |

Not built: FR-023 (arrival-time readiness, needs ML) and FR-032 (voice). See S13.
