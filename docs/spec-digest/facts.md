# Smart Ambulance — facts sheet

Condensed from the six specs on 2026-09-13. Each fact cites `file:line`
(`prd`, `plan`, `flow` = appflow, `db` = database, `tech` = techspec, `design`).
`⚠ Cnn` means the specs disagree: read row Cnn in
`.claude/skills/spec-lookup/references/conflicts.md` before implementing. If this
sheet and a spec differ, the spec wins; fix this sheet. This digest is for people.
Agents given it spent 10–12% more tokens than agents that searched and sliced
the specs, so no skill loads it.

## 1. What it is

- Real-time emergency coordination: patient needs → suitable ambulance →
  reliable route → capable hospital → acceptance → transactional reservation →
  readiness → re-coordination when anything changes (prd:5, prd:3130).
- Hackathon prototype with production-shaped architecture. Data is simulated or
  synthetic. Not clinically deployable (prd:21-24).
- Decision support only: deterministic constraints + optimisation + optional
  prediction + human override (prd:24, tech:6616-6630).
- "Nearest is not necessarily fastest. Fastest is not necessarily suitable.
  Suitable is not necessarily accepting. Available now is not necessarily
  available on arrival." (plan:85-88). Final rule: **never optimise an invalid
  option** (plan:5596-5616).
- Roles: DISPATCHER, AMBULANCE_CREW ⚠ C03, HOSPITAL_STAFF, HOSPITAL_ADMIN,
  SYSTEM_ADMIN, DEMO_CONTROLLER ⚠ C04 (prd:501-512, db:519-536).

## 2. Scope

- **P0 / must:** auth, emergency creation, structured patient requirements,
  ambulance matching, routing, hospital matching, acceptance, reservation, live
  tracking, dynamic reassessment, explainability, failure handling, demo
  simulation (prd:2444-2462).
- **Should:** ETA ML, arrival-time readiness prediction, voice (English,
  Malayalam, Hindi), multilingual UI, analytics (prd:2466-2472).
- **Do not build:** blockchain, AR/VR, RL, GNNs, IoT hardware, autonomous
  driving, full ABDM/FHIR, real hospital APIs, Kafka, Kubernetes, microservices
  (prd:200-234, prd:2476-2485, plan:3579-3587, tech:5485-5519, tech:5912-5935).
- OR-Tools only for genuine multi-incident assignment, "not solely for
  appearance" (tech:3810-3826).
- If behind, cut in this order: voice → forecasting → advanced ML → extra
  languages → advanced optimisation. Never cut the core chain (plan:3507-3535).

## 3. Build order

DB → auth → incident CRUD → ambulance CRUD → hospital CRUD → resource CRUD →
ambulance matching → routing → hospital ranking → acceptance → reservation →
mission state → WebSocket → dynamic recalculation → explainability → demo
simulation → tests ⚠ C22 → ML → voice → analytics (plan:4665-4692).

- **First vertical slice before anything else:** Create Incident → Find
  Ambulance → Assign → Calculate Route → Find Hospital → Accept → Reserve ICU
  (plan:4696-4716; longer version tech:6720-6750).
- Milestones: M1 running skeleton · M2 dispatch · M3 hospital · M4 reservation ·
  M5 live coordination · M6 demo complete · M7 hardened · M8 presentation ready
  (plan:5129-5174).
- Hour-by-hour 48-hour plan: plan:3481-3503. Development phases 1–12: plan:3298-3477.

## 4. Stack and layout

No versions are specified anywhere.

- **Web:** React, TypeScript strict, Vite, Tailwind, TanStack Query (server
  state), Zustand (UI state), React Router, React Hook Form + Zod, Lucide,
  Recharts, Mapbox GL or Google Maps; Vitest + RTL and Playwright
  (tech:498-516, tech:2772-2793, tech:2874-2928).
- **API:** FastAPI, Pydantic, SQLAlchemy, Alembic, WebSockets; Black, Ruff,
  Pytest, MyPy. Redis optional (tech:518-527, tech:6363-6411).
- **DB:** PostgreSQL + PostGIS + pgcrypto (db:203-236, db:5415-5427).
- **ML (optional):** XGBoost/LightGBM and scikit-learn with a linear baseline;
  LSTM optional; Transformer/GNN/RL rejected (plan:1029-1040).
- **Repo ⚠ C16** (tech:5579-5612): `apps/web`, `apps/api`,
  `packages/{shared-types,config,ui}`, `infra/`, `docs/`, `scripts/`, `tests/`,
  `docker-compose.yml`, `.env.example`.
  - API: `app/{main.py, api/routes, core, models, schemas, services,
    decision_engine, ml, integrations, realtime, simulation}` (tech:3452-3516).
  - Web: `src/{app, components, features/<domain>, hooks, lib/api, stores, types,
    schemas}`; every HTTP call goes through `src/lib/api/` (tech:2826-2870,
    tech:5078-5104).
- **Logic placement:** no business logic in React components, SQL, or route
  functions — only in `decision_engine/` and `services/` (tech:6447-6462). The
  decision engine is callable without the frontend and deterministic:
  `evaluate(incident, ambulances, hospitals, routes, configuration) ->
  DecisionResult` (tech:6494-6556).
- **Providers sit behind adapters.** Business logic never imports SDKs
  (tech:5019-5056). `RoutingProvider` has Google/Mapbox/OSRM/GraphHopper/Mock
  implementations (tech:3045-3078). `HospitalIntegration` starts with a Mock
  implementation.
- Commands: `zero-error-gate` skill; spec sources tech:5523-5574, db:3434-3482.

## 5. Environment and config ⚠ C15 (names disagree)

- **Backend env** (tech:4893-4916): APP_ENV, DATABASE_URL, JWT_SECRET,
  CORS_ORIGINS, ROUTING_PROVIDER, GOOGLE_MAPS_API_KEY, MAPBOX_ACCESS_TOKEN,
  REDIS_URL, ML_MODEL_PATH, ML_ENABLED, VOICE_PROVIDER, VOICE_API_KEY,
  SIMULATION_ENABLED.
- **Web env** (tech:4920-4926): VITE_API_BASE_URL, VITE_WS_URL,
  VITE_MAP_PROVIDER, VITE_MAPBOX_TOKEN, VITE_GOOGLE_MAPS_KEY, VITE_ENV.
- **Environments and databases:** dev/test/demo/production use
  `smart_ambulance_{dev,test,demo,prod}` (tech:1670-1681, db:4142-4150).
- **Config, never constants:** weights, freshness thresholds, reservation TTL,
  acceptance timeout, search radii, feature flags (tech:1622-1639,
  tech:5805-5835, plan:3182-3206). Changing config writes an audit record.
- **Secrets:** never in frontend source, logs, or git; `.env.example` is
  committed with empty values (plan:2616-2629, tech:4929-4945).

## 6. Safety rules — constraints, not trade-offs

Sources: tech:6946-6972, flow:3974-3987, prd:1128-1216.

1. Never pick an unsuitable ambulance because it is closer.
2. Never recommend a hospital that violates a mandatory requirement.
3. Unknown ≠ available: `0` means confirmed unavailable, NULL means unknown
   (tech:4405-4433, db:152-168).
4. The server owns reservation truth; stale UI never overwrites newer server state.
5. AI/ML never overrides hard constraints; low confidence falls back to
   deterministic logic (BR-011).
6. Stale and simulated data are always visibly marked.
7. No double booking; critical reservations are transactional (BR-007).
8. No silent destination change; no silently irreversible critical action.
9. No core decision logic in UI components.
10. Never claim clinical autonomy.
11. Every important recommendation carries an explanation.
12. Every critical transition is audited; every override needs a reason (BR-010).

Also:
- Acceptance is recorded before a destination is confirmed (BR-006).
- A rejecting hospital stays excluded unless explicitly re-enabled (BR-009).
- Don't flip between near-equal candidates (BR-013; stability flow:3383-3405).
- Never fabricate a hospital, resource or assignment when none is valid
  (BR-015, prd:1943, flow:3496).

## 7. Decision engine

**Pipeline** (tech:608-637): requirements → hard filter → routing matrix →
optional prediction → scoring → confidence → recommendation → human confirmation.

**Requirements.** Structured categories (TRAUMA, CARDIAC, RESPIRATORY,
NEUROLOGICAL, BURN, MATERNAL, PAEDIATRIC, GENERAL_CRITICAL) map to logistics
needs, not diagnoses. Say "dispatcher selected trauma requirement", never "AI
diagnosed" (plan:408-455). Tri-state REQUIRED/PREFERRED/UNKNOWN ⚠ C06 vs DB
booleans (prd:554-573, db:696-742).

**Ambulance**
- Hard filter: AVAILABLE, not on a locked mission, has the mandatory equipment
  and capability, fresh GPS, within operating radius (plan:534-543,
  tech:3141-3148). Vehicle capability is kept separate from equipment
  availability (plan:514).
- Candidates: `WHERE status = 'AVAILABLE' ORDER BY current_location <->
  ST_SetSRID(ST_Point(:lng, :lat), 4326)::geography LIMIT 20`, then routing
  ETA before the final choice (db:2168-2193).
- Score ⚠ C11 direction: `0.45·eta + 0.25·capability + 0.15·equipment + 0.10·crew
  + 0.05·availability_confidence`. The weights are configurable, not clinically
  validated (plan:570-581). techspec variant: tech:3161-3199.

**Routing**
- Choose by emergency travel cost, not distance: `0.55·norm_eta +
  0.20·congestion + 0.10·route_risk + 0.10·eta_uncertainty +
  0.05·route_change_penalty` (tech:3101-3128).
- Reroute only past a configurable threshold (flow:3146-3162); don't recalculate
  continuously (tech:5397-5410).
- Fallback: primary → secondary provider → cached route with LOW confidence →
  human (tech:782-796).

**Hospital**
- Order: clinical hard constraints → resource feasibility → acceptance → ETA →
  readiness → reliability (tech:3205-3215).
- Hard pass: every required capability AND required resource AVAILABLE with
  fresh data AND status ACTIVE (tech:3220-3242).
- Geo pre-filter `ST_DWithin`, then expand the radius → regional → manual
  escalation (db:2197-2238). The geo query is never the sole basis for selection.
- Score ⚠ C11: `0.30·eta + 0.20·capability + 0.20·acceptance + 0.15·resource +
  0.10·readiness + 0.05·route_reliability − uncertainty_penalty`
  (plan:759-772). techspec variant: tech:3246-3257.
- Confirmed destination = feasible AND acceptance ACCEPTED AND resource
  reserved (db:1245-1257) ⚠ C30.
- Capability, availability, acceptance and readiness stay separate fields
  (prd:1461-1506, db:4372-4394).

**Tie-breaks:** none are specified anywhere. Decide one, keep it deterministic,
and record it in `docs/implementation-decisions.md` (tech:2304-2313).

**Reassessment**
- Triggers: TRAFFIC_CHANGED, HOSPITAL_REJECTED, RESOURCE_LOST,
  AMBULANCE_UNAVAILABLE, PATIENT_REQUIREMENTS_CHANGED ⚠ C20, GPS_STALE,
  ROUTE_BLOCKED, confidence drop (prd:869-881, plan:1162-1173).
- Severity: minor → UI only; significant → evaluate; critical → immediate
  (flow:3100-3142).
- Decision lock near the destination: flow:3409-3429.

**Freshness and confidence**
- Example thresholds only — configurable, and not to be presented as clinical
  standards: GPS fresh ≤15 s, aging 15–60 s, stale >60 s (the spec's 15 s
  boundary overlaps; pick one and record it). Hospital state is stale beyond a
  configured threshold (tech:4618-4635).
- Confidence HIGH/MEDIUM/LOW ⚠ C10 vs numeric (tech:6162-6197).
- Recommendation statuses: RECOMMENDED, REQUIRES_CONFIRMATION, LOW_CONFIDENCE,
  UNAVAILABLE, STALE_DATA, MANUAL_REVIEW (plan:4086-4099).

**Explainability**
- `decision_runs` (algorithm/model/config version, trigger, input_snapshot,
  output_snapshot), `decision_candidates` (eligible, exclusion_reason, score,
  rank, feature_values), `decision_reasons` (db:1654-1789).
- Show rejected candidates with their reasons. Never show a bare "AI Score"
  (flow:583-601, tech:1243-1262).

**Override**
- Verify the role → validate feasibility → require a reason → audit (actor,
  before, after, reason) → execute (plan:4907-4936).
- No override of mandatory constraints without an escalation policy — and that
  policy is undefined ⚠ C24.
- Manual coordination mode when the engine fails: flow:1966-1982.

**ML**
- Every prediction stores model_version, confidence, feature_version and
  fallback_used (tech:4000-4022).
- Fallback is the provider ETA or the verified state; ML is never a single point
  of failure (plan:4602-4614).
- No fabricated accuracy (plan:1084-1093).

## 8. Acceptance, reservation, concurrency

- **Acceptance:** PENDING → ACCEPTED | REJECTED | EXPIRED ⚠ C08 (db:1233-1241).
  The timeout is configurable, e.g. 60 s, not a medical standard
  (plan:815-823). Rejection → record → exclude → re-rank → request the next →
  notify (prd:765-773). Reasons offered: ICU unavailable, emergency department
  overloaded, required specialty unavailable, surgery unavailable, ventilator
  unavailable, other (flow:924-933).
- **Reservation:** REQUESTED → HELD → CONFIRMED → IN_USE → RELEASED; HELD →
  EXPIRED | CANCELLED; FAILED on error. Resource loss emits a LOST event and
  triggers reassessment ⚠ C08 (db:1306-1323, db:1198-1205, plan:839-863).
- **Capacity:** reserve `available −= n, reserved += n`; expire or release
  reverses it; consume `reserved −= n, occupied += n`. CHECK every value ≥ 0 and
  `occupied + reserved + available <= total` ⚠ C25 (tech:3316-3345, db:1084-1132).
- **Transaction.** The reference SQL (db:1345-1378) is:
  `BEGIN → SELECT … FROM hospital_resources WHERE id=:id FOR UPDATE → validate
  available capacity → UPDATE available −n, reserved +n, version = version + 1
  → INSERT reservations → COMMIT`, or `ROLLBACK` if validation fails.
  - The step list "Transaction C" (db:2868-2877) also writes a
    `resource_events` row inside the same transaction. The SQL example omits
    that step.
  - On any failure the resource is unchanged, no reservation is confirmed, no
    success event fires, and no partial reservation is left (db:2881-2891).
- **Locks:** never hold one across an external API call — fetch → validate →
  short transaction (db:4308-4330).
- **Optimistic locking:** `WHERE version = :expected`; zero rows returns
  `CONCURRENT_UPDATE` (db:2339-2369). A stale `missions.state_version` write
  returns `MISSION_STATE_CONFLICT` (db:1467-1488).
- **Unique partial indexes:** one active assignment per ambulance and one active
  mission per ambulance (db:3035-3065).
- **Idempotency:** an `Idempotency-Key` header on reservation create,
  acceptance, assignment and mission completion (tech:5731-5750).
- **Events:** publish WebSocket events only after commit. Handlers dedupe by
  `event_id` and drop out-of-order events by `entity_version`
  (db:2895-2907, db:5230-5298).
- **Reassignment:** the old record becomes CANCELLED/SUPERSEDED and is never
  overwritten; release the old reservation before confirming the new one
  (db:4479-4531).
- **Incident cancel:** assignment → acceptance → reservation → mission → notify
  → audit (db:4460-4475).

## 9. State machines ⚠ C01 (three competing mission/incident models)

- **Mission** (db:1448-1463): CREATED, ASSIGNED, EN_ROUTE_TO_PATIENT,
  ON_SCENE, PATIENT_ON_BOARD, EN_ROUTE_TO_HOSPITAL, ARRIVED, HANDOVER,
  COMPLETED, CANCELLED, FAILED, REASSESSMENT.
- **Incident** (prd:1090-1124, db:626-676): CREATED → ANALYZING → DISPATCHED →
  PICKUP → HOSPITAL_SELECTION → ACCEPTANCE_PENDING → ACCEPTED →
  RESOURCE_RESERVED → IN_TRANSIT → ARRIVED → HANDOVER → COMPLETED; plus
  CANCELLED, FAILED and ESCALATED.
- **Ambulance** (db:5836-5851): AVAILABLE → RESERVED → DISPATCHED →
  EN_ROUTE_TO_PATIENT → ON_SCENE → PATIENT_ON_BOARD → EN_ROUTE_TO_HOSPITAL →
  ARRIVED → HANDOVER → AVAILABLE.
- **Enforcement:** an explicit `ALLOWED_TRANSITIONS` map; the API never sets an
  arbitrary status (db:5795-5809).

## 10. Data model essentials

- Snake_case plural tables, UUID primary keys via `gen_random_uuid()`, human
  codes INC-/AMB-/H-/RES-/MIS- ⚠ C13 (db:345-470).
- TIMESTAMPTZ in UTC, server `NOW()` only (db:420-440, db:5302-5312). Enums are
  text + CHECK (db:464).
- `geography(Point,4326)` ⚠ C14; build points with
  `ST_SetSRID(ST_Point(:lng,:lat),4326)` — **longitude first** (db:2127-2164).
- **P0 tables:** users, roles, incidents, patient_requirements, ambulances,
  hospitals, hospital_resources, ambulance_assignments, acceptance_requests,
  reservations, missions, mission_events, routes, decision_runs, audit_logs
  (db:6084-6102). Columns for the core tables: db:474-2011. Minimal schema if
  time runs out: db:5997-6027.
- **Optional tables** — neither appears in the P0/P1/P2 lists:
  - `hospital_readiness`: per-incident `icu_ready`, `ventilator_ready`,
    `trauma_team_ready`, `surgery_ready` booleans plus `overall_status`
    (db:4398-4420); states at db:4422-4432.
  - `handover_records` (db:4434-4459).
- **Append-only:** mission_events, resource_events, decision_*, audit_logs.
  Never hard-delete operational rows (db:1545, db:2398-2431, db:3070-3080).
- **JSONB** only for snapshots, provider metadata, simulation payloads and ML
  features; never for resources (db:2577-2603).
- `data_mode` LIVE/REPLAY/SYNTHETIC/SIMULATED/UNKNOWN ⚠ C09 on every dynamic record
  (db:2674-2682).
- **Migrations:** Alembic; never edit an applied migration (db:3364-3407).
  Order ⚠ C17 db:5390-5410.

## 11. API and realtime

- **Contract:** base `/api/v1`; FastAPI OpenAPI is the contract, with generated
  TS types (tech:3520-3528, tech:5108-5128). Endpoints: tech:3532-3721 (plan
  variant ⚠ C27 plan:1286-1432).
- **Errors:** `{"error":{"code","message","request_id"}}`
  (tech:4501-4533). Codes:
  - VALIDATION_ERROR, AUTHENTICATION_ERROR, AUTHORIZATION_ERROR, NOT_FOUND, CONFLICT
  - RESOURCE_UNAVAILABLE, ROUTING_PROVIDER_ERROR, HOSPITAL_API_ERROR, GPS_STALE
  - ML_FAILURE, VOICE_FAILURE, NETWORK_ERROR, INTERNAL_ERROR
  - from db: MISSION_STATE_CONFLICT, CONCURRENT_UPDATE, DATA_INCONSISTENCY
- **Logging:** `X-Request-ID` on every request; structured JSON logs carrying
  request/incident/mission/decision ids; never `print` (tech:6247-6263,
  tech:5839-5858).
- **WebSocket:** `/ws` with channels `mission:{id}`, `incident:{id}`,
  `hospital:{id}`, `ambulance:{id}`, `dispatcher:{user_id}`
  (tech:4123-4141). Event names ⚠ C20 tech:4145-4163; payloads carry
  `mode:"SIMULATED"` (tech:4167-4183).
- **Client states:** Live / Reconnecting / Data stale / Offline; never show stale
  data as current (tech:4187-4207).
- **Connection loss:** reconnect with exponential backoff, then show
  `RESYNCING MISSION STATE...` (flow:2612-2632).
  - Dispatcher shows `OFFLINE / RECONNECTING`.
  - Ambulance keeps the mission cached and shows the last confirmed destination
    and update age.
  - Hospital keeps state locally and shows `SYNCING...` on return
    (flow:1598-1630, flow:2952-2972).
- **Access control:** RBAC enforced on the backend. Hospital users see only
  their hospital; crew see only their mission (tech:4458-4475, db:3276-3310).
- **Simulation access:** `/admin/simulation/*` needs SYSTEM_ADMIN or
  DEMO_CONTROLLER. Demo reset checks the environment before any destructive
  operation and refuses in production ⚠ C15 (tech:6597-6612, db:5350-5365).
- **Privacy:** synthetic patients only — no Aadhaar, phone numbers or medical
  history. Never log tokens, passwords or patient identifiers (tech:4974-4993).

## 12. Demo and judges

- **Demo mode is mandatory** (plan:2665). Required text is `DEMO MODE` on every
  screen where synthetic data is used (flow:3281-3287).
  - The UI must also state what is simulated: hospital capacity, ambulance GPS,
    acceptance, resource reservation (plan:2669-2677).
  - `SIMULATED HOSPITAL DATA` is added where needed (design:753-763).
    `DEMO MODE · SIMULATED HOSPITAL DATA` is appflow's example, not a mandated
    string (flow:3289-3292).
  - Never hidden, and never behind a settings page (flow:3295, design:765).
  - Real vs simulated per component: plan:2679-2691.
- **Seed:** deterministic `seed = 2026`; ≥10 ambulances and ≥10 hospitals ⚠ C18;
  deliberately messy (near-but-unsuitable, far-but-suitable, rejecting
  hospitals, scarce ICU); fictitious names. Reset restores the seed and clears
  incidents and missions (db:2031-2126, db:2780-2826, plan:3906-3924).
- **Golden scenario:** road-traffic trauma needing Trauma + ICU + Ventilator +
  Surgery (tech:2120-2178, plan:3591-3664, prd:3015-3092) ⚠ C19 letters and ETAs differ.
  1. Nearest ambulance lacks a ventilator → second is chosen.
  2. H-001 has no ICU and H-002 no trauma → H-003 matches fully and accepts.
  3. ICU reserved → traffic change → reroute → ready → arrive → handover → full audit trail.
- **Stress events:** traffic +50%, ICU failure (the primary judge test),
  hospital rejection, ambulance failure, GPS lost, route blocked
  (plan:3668-3757, tech:6057-6124).
- **Success test:** a judge changes a condition ("Hospital C lost its ICU") and
  the system visibly releases → re-ranks → requests acceptance → reserves →
  updates the ambulance → explains (plan:5178-5199).
- **Judges must see:** not every ambulance or hospital is suitable; the choice
  uses more than distance; the system responds to change; it explains itself
  (plan:4329-4351).
- **Never say:** "first system to…", "we provide live ICU data", "our AI saves
  lives", "95% accurate", "no existing system does this". Unmeasured numbers
  are targets (plan:4355-4366, plan:5257-5281, prd:2685-2693).
- 20 judge questions with answers: plan:3761-3804.

## 13. Tests and performance

- **Layers:**
  - Unit: constraints, scoring, ranking, reservation, transitions, permissions, ML fallback.
  - Integration: API, DB, WebSocket, transactions, adapters.
  - E2E: Playwright golden path.
  - Plus scenario replay, failure injection, security
    (plan:2759-2813, tech:5238-5338).
- **Required failure tests** (tech:1521-1540): rejection, no ambulance, no
  hospital, resource unavailable, GPS failure, routing failure, hospital API
  down, duplicate reservation, invalid transition, unauthorised action,
  WebSocket disconnect, ML failure.
- **Ready-made cases:**
  - Gherkin plan:2817-2879; edge cases 1–10 plan:2335-2433
  - DB-001..006 db:4755-4840; concurrency db:3519-3537; negative tests db:5778-5794
  - Critical E2E ids tech:5315-5338
- **Targets** (engineering, not medical): API < 500 ms, decision < 2 s ⚠ C23,
  event propagation < 1 s, 0 duplicate reservations (tech:4829-4853,
  plan:2437-2453). Report measured numbers only.
- **CI minimum:** web lint + typecheck, API lint + typecheck, unit tests,
  migration validation, build (plan:3126-3150).

## 14. Checklists — where they live

| Checklist | Lines |
|---|---|
| Product Quality Gates 1–5 | prd:2398-2440 |
| Engineering DoD (10 boxes) | plan:4370-4387 |
| Technical DoD (12 boxes) | tech:6754-6771 |
| Database DoD (20 boxes) | db:6127-6150 |
| Build quality rule — no fake buttons | tech:1904-1930 |
| Final architectural check | tech:2095-2116 |
| Golden-path test (25 steps) and failure test | tech:2120-2206 |
| MVP acceptance criteria | tech:6775-6837 |
| Final acceptance (20 items) | plan:5537-5560 |
| Final implementation checklist | plan:5404-5533 |
| Product checklist / DoD chain | prd:2856-2920 / prd:2924-3011 |
| Design validation / acceptance | design:3675-3729 |
| Agent MUST / MUST NOT | tech:2268-2300 |
