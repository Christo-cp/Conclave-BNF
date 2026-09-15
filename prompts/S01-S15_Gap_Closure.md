# Prompt — Close every S01–S15 gap (Smart Ambulance)

Paste everything below the line into a fresh Claude Code session opened at the
project root.

---

## 1. Your job

You are the implementer on the Smart Ambulance Routing & Emergency Bed
Allocation hackathon prototype. `docs/executable-plan.md` Part B defines build
steps S0–S15. Each step has **Build**, **Tests** and **Exit** blocks. PR #1
(commit `5f05ebf`, merged as `4f893cd`) delivered code for most steps, and
`STATUS.md` claims "S0-S15 application surface is present". An audit on
2026-09-15 found that claim does not hold. Many steps are partial, stubbed or
wrong, and most named tests do not exist.

Bring every step S1–S15 to its Exit, as written in the plan. Do it in build
order, and get the vertical slice (S0–S10) passing through the browser before
touching S11+ (plan Part B preamble: "Nothing outside S0–S10 starts before the
S10 exit passes").

**Done** means all of the following hold for every step:
- every Build item is implemented;
- every test named in its Tests block exists and passes;
- its Exit commands produce the stated output;
- the gates in §4 have run.

## 2. Read first, in this order

1. `CLAUDE.md` and `AGENTS.md`. They hold the project rules and two mandatory
   gates.
2. Run `/session-start`. Then read `STATUS.md` and the newest `handoffs/`
   file, but **treat both as unverified claims**. Also read
   `handoffs/AMB_HANDOFF_2026-09-15_3.md` on branch
   `origin/worktree-floofy-meandering-newt`, which is an independent audit.
3. `docs/executable-plan.md`:
   - A2 commands and environments (lines 48–117)
   - A3 decisions (118–167)
   - A4 decision maths, A5 state and transactions, A6 golden seed (168–377)
   - the step you are working on (S0 starts at line 396)
4. For anything the plan cites (`db:`, `tech:`, `prd:`, `flow:`, `design:`),
   use `/spec-lookup`: grep, then read ≤80-line slices. Never read a spec end to
   end.

## 3. What the audit found — your starting backlog

The evidence below points at `4f893cd`. Line numbers drift, so re-grep before
editing. For each item:
- **Already fixed:** prove it with a test and record it as closed in your step
  report (§6).
- **Audit wrong:** write down why in your report. Do not skip it silently.

Across all steps, the plan names about 109 tests. Only these exist today under
the plan's names or as close equivalents:
- `test_health_db_up`, `test_health_db_unreachable_503_envelope`
- `test_ineligible_candidate_has_no_score_or_rank`,
  `test_unknown_equipment_is_not_available`, `test_tie_break_eta_then_code`
- near-equivalents in `test_backend_lifecycle.py`,
  `test_api_resources_and_lifecycle.py`,
  `test_reservation_postgres_integration.py`, `test_realtime.py`,
  `src/components/decision-state.test.tsx` and `src/lib/realtime.test.ts`

Rename or extend these rather than duplicating them. Everything else in each
Tests block must be written. `tests/test_rbac.py` does not exist, yet every
Exit from S2 on runs it.

### S0 · Skeleton
- `tests/test_health.py:33` hard-codes `0015_simulation_integrity`. Compare
  against `alembic heads` instead.

### S1 · Schema, seed, reset
- Add a partial unique index allowing only one active mission per ambulance
  (db:3054-3065). Today only the assignment guard exists (`0004`).
- Add GiST indexes on `routes.origin` and `routes.destination`.
- Enums must be text + CHECK generated from `app/core/enums.py`. Add the
  missing CHECKs for incident, mission, ambulance, reservation and acceptance
  statuses (only requirement level has one, `0003:17`).
- Append-only triggers are missing on `decision_runs`, `decision_candidates`
  and `decision_reasons` (db:1545, db:3070-3080).
- The seed does not follow A6. Fix `app/simulation/seed.py` so it has:
  - seed value 2026
  - H-007 with ICU `NULL`
  - H-008 with an ICU reading 900 s old
  - MSN-000001 and the golden incident
  - `simulation_scenarios.payload`
  - fillers AMB-006..010 each lacking at least one golden item
  - one user for **each** of the six roles (today there are four)
- Missing tests: `tests/db/test_spec_cases.py`, `test_migrations.py`,
  `test_constraints.py`, plus `test_seed_is_deterministic` and
  `test_reset_refuses_in_production` (`test_seed.py` only checks that reset
  runs twice).

### S2 · Authentication and RBAC
- `/auth/logout` is a no-op (`api/v1/auth.py:18-20`), and refresh just reissues
  a token. Implement both per tech:3532-3539.
- The dispatch router never uses `require_roles` (`api/v1/dispatch.py`). Any
  logged-in role, including AMBULANCE_CREW, can match, confirm and route.
  `POST /incidents/{id}/requirements` is also unguarded (`incidents.py:34`).
- `GET /incidents/{id}` has no data scoping (`incidents.py:26`). It also
  returns 200 with `{"error":"not found"}` instead of a 404 error envelope
  (`incidents.py:29`).
- Missing tests:
  - `tests/test_auth.py`: `test_login_invalid_401`,
    `test_me_without_token_401_envelope` and
    `test_me_as_dispatcher_returns_role`;
  - `tests/test_rbac.py`: a table of endpoint, role and expected status that
    every later step adds rows to.

### S3 · Slice CRUD
- Optimistic `version`:
  - it is optional on ambulance location (`resources.py:138`);
  - it is unchecked on ambulance status and resource PATCH (`resources.py:150,
    247, 294`);
  - a stale write must return the concurrent-update code from tech:4519-4533.
- A resource PATCH writes no `resource_events` row, and no ORM model exists for
  that table (created in `0006`).
- Ambulance status, location and resource changes write no audit row.
- The incident-transition guard and the "at least one requirement" rule are
  missing.
- Missing test: `tests/test_slice_crud.py`.

### S4 · Ambulance matching and heartbeat
- `decision_engine/ambulance.py:46-51` deviates from A4:
  - `capability_score` is fixed at 1.0;
  - `equipment_score` counts REQUIRED items instead of PREFERRED ones;
  - there is no `crew_score`;
  - the 15 s and 0.6 freshness values are literals, not config;
  - there is no confidence, band or `REQUIRES_CONFIRMATION`.
- ETA is invented as `420 + ambulance number` (`services.py:127`). Build the
  `RoutingProvider` interface and a `MockRoutingProvider` computed from
  coordinates, plus the PostGIS candidate query (db:2168-2193).
- `active_mission` is always `False`, so AMB-003 is excluded as UNAVAILABLE
  instead of ACTIVE_MISSION.
- Decision runs are never persisted: `decision_service.persist_decision` has
  no callers.
- `confirm_ambulance` (`services.py:144-163`) has four gaps:
  - it only checks `status == AVAILABLE`; re-check full eligibility and return
    409;
  - `override_reason` is accepted but never enforced for rank ≠ 1 (return 422,
    BR-010);
  - it doesn't trigger route calculation;
  - it has no role check.
- `queue_event` is called before `flush`, so events carry entity id `"None"`
  (`services.py:161, 175`; `realtime/broker.py:124`).
- Missing: `POST /ambulance-assignments/{id}/accept`; `app/simulation/heartbeat.py`
  with its skip set; the `{incident_id, recommendations}` response shape
  (tech:3576).
- Missing tests:
  - the engine tests `test_same_input_same_output`,
    `test_unknown_requirement_neither_filters_nor_scores` and
    `test_engine_imports_no_io`;
  - all six tests in `test_dispatch_ambulances.py`;
  - `test_heartbeat_skips_amb_005_h_008_and_skip_set`.

### S5 · Route calculation
- Every route is hard-coded to 6000 m / 600 s / confidence 0.95 /
  `fallback_used=False` (`services.py:173`).
- The origin must be the ambulance, not the incident. `mission_id` and
  `computed_at` are never set.
- Implement the primary → secondary → cached → `MANUAL_REVIEW` fallback chain
  (tech:782-796) and `FALLBACK_CONFIDENCE_CAP`.
- The golden 600 s must come out of the mock provider's calculation, not a
  constant.
- Missing test: `tests/test_routes.py`.

### S6 · Hospital matching
- ETA is invented as `600 + code*60` (`services.py:206`). There is no
  `ST_DWithin` search over `HOSPITAL_SEARCH_RADII_M` and no escalation step.
- `hospital.py:50` fixes capability at 1.0, acceptance at 0.5 and readiness at
  0.5. Route reliability, the uncertainty penalty and `STABILITY_MARGIN` are
  missing, along with their config keys.
- The hard pass is incomplete:
  - it doesn't check that the resource is ACTIVE;
  - `stale_resources` is never filled, so stale capacity still ranks;
  - a missing resource row must give `MISSING_CAPABILITY`.
- Hospitals that already rejected the incident are not excluded (BR-009). The
  incident is never set to `HOSPITAL_SELECTED`. Matching does not run
  automatically after the route (C05). Results are not persisted.
- Missing test: `tests/test_hospital_matching.py`.

### S7 · Acceptance request, hold, accept
- **Accept always fails from the UI.** `services.py:261` requires the accept
  `Idempotency-Key` to equal the key used to *create* the request, but
  `web/src/lib/api.ts:41` sends a new key. The accept operation needs its own
  stored key.
- Accepting an expired hold sets the request to EXPIRED but leaves the
  reservations HELD, so the capacity is never returned (`services.py:265-268`).
  Release it exactly once.
- A successful accept must also:
  - set the incident to ACCEPTED;
  - set the mission destination, but only after the reservations commit (C30);
  - write a mission event, a notification and an audit row.
- `hold_acceptance` (`services.py:222-240`) has these gaps:
  - locks are not taken in id order;
  - a missing resource row is skipped silently, so a hold can succeed with zero
    reservations;
  - freshness uses the app clock instead of DB `NOW()`;
  - it writes no `resource_events` HELD row;
  - a refused hold writes no audit row and doesn't re-run matching;
  - any role can call it.
- The automatic request to the rank-1 hospital, and the dispatcher wait when
  `REQUIRES_CONFIRMATION` applies, are missing.
- `acceptance_service.cancel` commits once per reservation
  (`acceptance_service.py:27`). Make it one transaction.
- `reservation_service.py:54` lets `/expire` expire a CONFIRMED reservation.
- The "one winner" test runs `ReservationService.reserve`, not the hold path.
  Write the plan's `test_two_concurrent_holds_on_last_icu_exactly_one_succeeds`
  against `hold_acceptance`.
- Missing test: `tests/test_acceptance.py` (all 15 named tests).
- Before adding `POST /reservations/{id}/confirm`, check tech:3633-3637 and
  C31. Accept already confirms reservations (`services.py:271-272`).

### S8 · Mission state
- Transition logic exists twice (`services.py:293-315` and
  `mission_service.transition_mission`). Keep one copy.
- `PATCH /missions/{id}` lets any logged-in user update any mission. Limit it
  to the crew of that mission, plus the roles tech allows.
- Accept never sets the destination, so the golden path can't reach
  EN_ROUTE_TO_HOSPITAL.
- Missing tests: `tests/test_missions.py` and
  `tests/e2e/test_golden_slice.py` (Product Quality Gate 1).

### S9 · Realtime
- `realtime/websocket.py:25-50` sends one event or heartbeat, then waits for
  another subscribe message. A client message arriving during the wait is
  thrown away. Rewrite it as concurrent receive and send loops.
- The browser client (`web/src/lib/realtime.ts`) never sends a subscribe
  message.
- Channel matching never succeeds: subscriptions are `hospital:<id>` but events
  are matched on bare ids (`broker.py:39-46`).
- RBAC holes:
  - an empty channel list passes `all([])` and receives every event;
  - `dispatcher:{user_id}` isn't checked against the caller (`realtime/auth.py:25`).
- Envelope problems:
  - no `entity_type`, so the client's version check never runs
    (`realtime.ts:69`);
  - acceptance events always carry version 1;
  - `mode` is hard-coded;
  - `hospital.acceptance.requested`, `resource.released` and
    `hospital.rejected` are never emitted (names from tech:4149-4163).
- Move the client to `src/lib/realtime/`.
- Tests:
  - replace the SQLite rollback test with a real rolled-back hold;
  - add a socket-level subscription test;
  - add `test_slice_client_receives_resource_reserved` and
    `shows_reconnecting_then_resyncs`.

### S10 · Dispatcher UI — vertical-slice exit
- Routing: add `/login`, `/dispatcher/emergencies/new` and
  `/dispatcher/emergencies/:id` as real routes (flow:3656-3700). Screens
  currently switch on React state under `/dispatch`.
- API types: generate them with `openapi-typescript` into
  `src/lib/api/schema.d.ts`, replacing the hand-typed `lib/api.ts`.
- **Delete the fabricated fallback candidates** (`App.tsx:35-47`, used at
  :185 and :188). An API error must show the error state (non-negotiable:
  never fabricate a resource).
- **Bind "Why selected?" to the persisted decision trace.** It is static text
  today (`App.tsx:186-188`).
- Intake: coordinates, requirements and patient count are hard-coded
  (`App.tsx:170,174`). Freshness is faked: `decision-state.tsx:18` falls back
  to "8s old" and `App.tsx:183` always says "UPDATED JUST NOW".
- The dispatcher screen never uses the realtime client. After the dispatcher
  confirms, it must request acceptance and then show H-003 with ICU and
  ventilator CONFIRMED **without a reload**. `api.createAcceptance` is never
  called today.
- Show `DEMO MODE` on every screen.
- Styling: Tailwind is installed but not wired. Apply the tokens from
  design:214-322 and design:417-500, and the fonts in
  `docs/spec-digest/design-tokens.md`.
- Tests: `candidate-list.test.tsx`, `resource-card.test.tsx` and
  `e2e/slice.spec.ts` against the real API. `e2e/golden.spec.ts` is fully
  mocked with a role-less token, and `live-golden.spec.ts` stops at route
  calculation. Neither satisfies the Exit.

### S11 · Remaining flows and screens
- Rejection (`acceptance_service.py:19-31`) only cancels holds. It must also
  exclude the hospital, re-rank, request the next candidate and notify, using
  the reasons at flow:924-933.
- Build the sweeper (`SWEEPER_INTERVAL_S`, `ACCEPTANCE_TIMEOUT_S`). Today
  there is only a manual `/expire`.
- Add `POST /ambulance-assignments/{id}/reject`, which re-runs matching without
  that ambulance.
- `POST /reservations` needs the C31 role limit (`dispatch.py:101-148`).
  Verify consume and release, and build the incident-cancel cascade
  (db:4460-4475).
- Frontend role bug: the frontend uses role `HOSPITAL` (`web/src/lib/auth.ts:1,
  12`) but the backend issues `HOSPITAL_STAFF`/`HOSPITAL_ADMIN`. Real hospital
  users land on the dispatcher view.
- The crew screen must move to `/ambulance/mission`, with:
  - accept and reject;
  - all mission statuses (only EN_ROUTE and ARRIVED exist);
  - a cached last-confirmed destination with its age that survives going
    offline.
  Today the mission ID is pasted by hand (`RoleScreens.tsx:44-53`).
- Hospital screens:
  - `/hospital/incoming/:id` needs an incoming list, countdown and reason
    codes;
  - `/hospital/resources` must be editable and write `resource_events`.
  Today both are UUID text boxes (`RoleScreens.tsx:30-42`).
- The map is CSS boxes. Build the `/dispatcher` overview and a real map (P2
  Mapbox, `envDir: "../.."`), with the offline panel when tiles fail.
- Add manual coordination on ESCALATED (flow:1966-1982), without bypassing the
  hard pass.
- Tests: every test in the S11 Tests block, including the three-context
  `e2e/golden.spec.ts`.

### S12 · Reassessment, simulation, deferred routing
- `reassessment_service.py:11-39` only sets a status and logs, and nothing
  calls it. Implement:
  - triggers (plan:1162-1173) and classes (flow:3100-3142);
  - `STABILITY_MARGIN`, `DECISION_LOCK_ETA_S` and anti-flapping (BR-013);
  - re-ranking;
  - SUPERSEDED assignments with reservations released before new ones confirm
    (db:4479-4531).
- Resource loss per A5.3. Today `resource-lost` nulls the first resource row in
  the table (`simulation/controls.py:49-54`).
- Simulation controls:
  - `hospital-reject` and `route-blocked` only emit events (`controls.py:55-56,
    69-70`);
  - `gps-lost` doesn't add the ambulance to the heartbeat skip set;
  - `traffic-change` offers no alternative route.
- Routing: emergency travel cost (tech:3101-3128), `POST /routes/compare`,
  `POST /missions/{id}/reroute`, a traffic multiplier in the mock provider,
  and the optional live provider.
- The Demo Console calls `/simulation/control` with uppercase action names
  (`web/src/lib/api.ts:46`). That route doesn't exist; the real one is
  `/admin/simulation/{action}`. It only passes because
  `accessibility.spec.ts:70` mocks it. Move the page to `/demo/control` and add
  the movement ticker.
- Tables created by migrations but unused by any code: `0010`
  route_alternatives, `0011` decision-trace context, `0013`/`0014` simulation
  scenarios and events. Wire them in where S1/S12 need them. Otherwise raise
  them under §5.
- Tests: `tests/failures/test_failures.py` (12), `test_resource_loss.py`,
  `test_demo_events.py`, and `golden_all_25_steps` plus `golden_failure_path`.
  `test_simulation.py` only checks that action names are in a set.

### S13 · ML and voice — skipped (allowed)
- Keep `ML_ENABLED=false`. The README "Not built" section must name FR-023 and
  FR-032, or the Exit regex prints `False`.

### S14 · Hardening
- `CORSMiddleware` is not configured anywhere in `apps/api`. Limit it to
  `CORS_ORIGINS`.
- Missing test: `tests/test_audit_completeness.py`.
- Rewrite `docs/dod.md` as one row per box from plan:4370-4387, tech:6754-6771
  and db:6127-6150. Each Evidence cell must name a test or command, or say
  `none`. Replace "RBAC tests in suite" and "backend simulation/lifecycle
  coverage" with real test names.
- Re-run the latency script. Keep the "matcher only" label, and never quote
  the figure as system latency.

### S15 · Demo and pitch
- Create `.env.demo`: `docs/demo/failure-scenarios.md:3` already points to it.
- Record `docs/demo/golden-run.mp4`. This needs a human (§5).
- Run the offline check, including `map_offline_panel_when_tiles_fail`.
- Re-run the forbidden-claims grep after the UI copy changes.

## 4. Rules — non-negotiable

- **Tests first.** For each gap, write the plan-named failing test, watch it
  fail for the right reason, then fix. A step is not done on a green suite that
  lacks its named tests.
- **Specs win over the current code.** When code and spec disagree, the spec
  wins. When specs disagree with each other, follow
  `.claude/skills/spec-lookup/references/conflicts.md` and the A3 decisions
  (C05, C06, C10, C14, C24, C30, C31). Never re-open a RESOLVED decision.
- **Non-negotiables:** tech:6946-6972, flow:3974-3987, prd:1128-1216. None of
  these may be broken:
  - never select an ineligible unit;
  - never treat unknown or stale data as available;
  - never fabricate candidates, capacity, ETAs or scores;
  - no core decision logic in the UI;
  - label simulated data as simulated.
- **No invented numbers** in code, UI copy, README or pitch. A mock provider's
  output must be derived and labelled simulated; an unmeasured value is a
  target.
- **Migrations are forward-only.** `0001`–`0015` are merged: never edit them.
  Add `0016_*` onward. Record in `docs/implementation-decisions.md` that
  `0016_ml` is not used because S13 is skipped.
- **Record decisions.** Create `docs/implementation-decisions.md` and log every
  choice the plan doesn't dictate. Add new spec-vs-spec disagreements to
  `docs/spec-conflicts.md`.
- **Two failed fixes on the same bug:** stop and run `/bug-triage`.
- **Evidence before assertion.** Quote the command and its real output for
  every claim. Docker/PostGIS must be up: tests that time out on
  `127.0.0.1:5432` count as not run, not as passed.
  - Baseline on 2026-09-15, with Docker not on PATH: `pytest` collected 34
    tests: 18 passed, and 16 failed or errored, all on DB timeouts.
  - Ruff clean; web build clean; Vitest 7 passed.
  - `oxlint`: 3 `set-state-in-effect` warnings (`App.tsx:122,129,136`).
  - `scripts/full_suite.ps1` doesn't run lint or Playwright, so run those
    separately.
  - If Docker can't be started, stop and ask (§5).
- **Git:**
  - work on a branch, never on `main`;
  - one commit per step (conventional messages, e.g. `feat(api): S7 accept
    idempotency and expiry release`);
  - no force-push, no `--no-verify`;
  - never commit `.env*` files other than `.env.example`.
- **After each step:**
  - run its Exit commands;
  - run `/zero-error-gate`;
  - update `STATUS.md` with real counts;
  - write a handoff with `/handoff`.
  Before calling the whole task done, run the blind-evaluator gate in
  `prompts/Quality_Gate_Blind_Evaluator.md` on the delivered work.

## 5. Stop and ask the user — do not guess

Ask questions 2–5 once, together, at the start, and carry on with work that
doesn't depend on the answers. Question 1 is asked the moment it happens.

1. **Docker won't start:** PostgreSQL isn't reachable and Docker Desktop can't
   be started. Ask the user to start it. Don't write DB-dependent code you
   can't test.
2. **Backup/restore:** waive it for a local demo, or not (S14)?
3. **Out-of-plan code:** keep or remove the hard `DELETE` endpoints for
   hospitals and ambulances (`resources.py:119, 209`) and the duplicate legacy
   `/resources/ambulances/*` routes? Check which ones the frontend calls before
   asking.
4. **Unused tables** from `0010`/`0011`/`0013`/`0014` that no plan step needs:
   drop them in a new migration, or keep them?
5. **Values waiting on the user since 2026-09-14:** the psycopg
   `connect_timeout` value, and the `openapi-typescript` versus TypeScript 6
   peer mismatch.

Only the user can do these. Tell them when you reach the step, then carry on
without them:
- **S11:** add `VITE_MAPBOX_TOKEN` and `MAPBOX_ACCESS_TOKEN` to `.env` (P2).
  Never ask for the token in chat.
- **S15:** record `docs/demo/golden-run.mp4` after the S12 exit.

## 6. Report back

After each step, keep it to 15 lines or fewer:
- the step;
- gaps closed, with commit SHAs;
- named tests added, and the pass/fail/skip counts from the Exit commands;
- anything the audit got wrong;
- new decisions;
- blockers.

At the end:
- a table of S1–S15 × Build / Tests / Exit, each marked pass, fail or waived,
  with evidence;
- `git log --oneline` for the branch;
- the open questions from §5 that are still unanswered;
- the blind-evaluator score line.

Nothing is signed off until the user has run `docs/demo/golden-scenario.md`
live and said so.
