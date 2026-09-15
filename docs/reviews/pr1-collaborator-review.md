# What PR #1 actually delivered, step by step

**Code review · Smart Ambulance Routing & Emergency Bed Allocation**

- **Author:** Febin (GitHub `febzzz10`)
- **Commit:** `5f05ebf` "initial", merged as `4f893cd`
- **Reviewed:** 2026-09-15, against `docs/executable-plan.md` S0–S15

> **Bottom line**
>
> **A large, fast and structurally sound scaffold, but not a finished S0–S15.**
> The PR laid down the full shape of the system: the data model, services,
> endpoints, migrations and role screens. Several hard parts are done well,
> notably row-locked reservations, post-commit event publishing and versioned
> mission state.
>
> But the decisions the product exists to make run on placeholder inputs. The
> browser flow stops before hospital acceptance. The UI breaks the
> non-negotiable no-fabrication rule twice: it invents fallback candidates and
> shows a static "Why selected?" explanation. 5 of the plan's 109 named tests
> exist. `STATUS.md` and `docs/dod.md` describe the work as more complete than
> the code is.

| Figure | What it counts |
|---|---|
| **88** | files changed in one commit, +4,775 / −458 lines |
| **15** | Alembic migrations (0001–0015), all with downgrades |
| **5 / 109** | tests named in the plan's S0–S15 Tests blocks that exist under that name |
| **0 of 16** | build steps with an Exit reproduced here; S0 is closest, S13 legitimately skipped |

## How this was checked

Each step's Build, Tests and Exit blocks in `docs/executable-plan.md` were
compared with the merged code. Spec requirements were checked through the
plan's line citations. Four independent read-only audits covered S0–S5, S6–S9,
S10–S12 and S13–S15 plus rules and process. A fifth re-ran the test suites.

The most serious findings were then confirmed by reading the cited lines
directly. They are tagged **[checked in code]** below. Praise below is for code
as written; any test that needs PostgreSQL is marked as not reproduced.

A separate, earlier audit by another session (unmerged branch
`worktree-floofy-meandering-newt`) reached the same conclusions on most points.
Where the two disagree, this report says so.

## What the collaborator got right

### Solid engineering worth keeping

- **Reservations are built to lock correctly.** The code uses
  `SELECT … FOR UPDATE` on resource rows and a capacity CHECK constraint
  (`0008`). A real PostgreSQL test for exactly one winner under concurrency
  exists but was not reproduced here.
- **Events publish only after commit** and are dropped on rollback
  (`realtime/broker.py:97-107`).
- **Mission state is versioned.** A stale `state_version` is rejected, illegal
  transitions return 409, and EN_ROUTE_TO_HOSPITAL requires a confirmed
  destination (`services.py:293-315`).
- **Audit tables are append-only** by database trigger on `audit_logs`,
  `mission_events`, `notifications` and `resource_events`.
- **The pure engine filters are correct:** unknown capacity is excluded, and a
  mandatory requirement is never violated (`decision_engine/hospital.py:34-44`).
  The service layer fails to pass them stale-reading data, though, so stale
  capacity still ranks (defect 4).
- **Health endpoint, request-ID middleware, Argon2 + JWT login, deterministic
  tie-breaking**, and migrations with downgrades plus a round-trip test (not
  reproduced here).

### Good practice in the docs and frontend

- `docs/measurements.md` states plainly that its latency figure covers only the
  pure matcher, not HTTP, database or browser.
- The forbidden-claims grep is clean. The slides make no clinical-autonomy
  claim, and simulated rows carry `data_mode="SIMULATED"`.
- No secrets or `.env` files were committed.
- The web client dedupes events and reconnects with backoff, then resyncs over
  REST (`lib/realtime.ts:56-61`). The Vite proxy is configured and the build
  and lint are clean.
- Loading, error, stale and simulated states exist as components, with
  accessibility-focused Playwright specs.
- Skipping S13 (ML/voice) matches the plan's own recommendation.

## Step-by-step status

Status judges the code against the step's Build and Tests blocks, using five
labels: **Done**, **Partial**, **Stub** (present but fake or non-functional),
**Missing** and **Skipped**. No Exit could be fully reproduced without
PostgreSQL. "Named tests" counts tests that exist under the plan's exact name;
near-equivalents exist for S7–S10.

| Step | Status | Named tests | Main gaps |
|---|---|---|---|
| S0 Skeleton | Partial | 2 / 2 | Build items are present. The health test hard-codes the migration head (`test_health.py:33`). The database health test was not reproduced. |
| S1 Schema & seed | Partial | 0 / 13 | No one-active-mission index, status CHECKs, or append-only triggers on `decision_*`. The seed doesn't match A6: no H-007/H-008 cases, no golden incident or MSN-000001, four of six roles. |
| S2 Auth & RBAC | Partial | 0 / 3 | Dispatch endpoints have no role check. Logout is a no-op. A missing incident returns 200. `test_rbac.py` is missing, and every later Exit depends on it. |
| S3 Slice CRUD | Partial | 0 / 5 | Optimistic `version` unchecked on status and resource PATCH. No `resource_events` or audit rows on those writes. Out-of-plan hard DELETE endpoints added. |
| S4 Ambulance match | Stub | 3 / 13 | ETA invented from the unit's number. Formula deviates from A4. Decisions never persisted. Confirm skips eligibility and the override reason. No heartbeat loop and no crew-accept endpoint. |
| S5 Routing | Stub | 0 / 3 | Every route is a constant 6,000 m / 600 s. No provider interface and no fallback chain. |
| S6 Hospital match | Stub | 0 / 9 | ETA invented from the hospital code. Three score components fixed. No radius search. Stale and inactive resources not excluded. Rejected hospitals not excluded (BR-009). |
| S7 Acceptance & hold | Partial | 0 / 15 | Accept from the UI always returns 409. An expired accept leaks capacity. No automatic request to the rank-1 hospital. Near-equivalent concurrency test targets a different code path. |
| S8 Mission state | Partial | 0 / 5 | Core transitions are good. Any user can PATCH any mission. Accept never sets the destination. No golden-slice e2e test. |
| S9 Realtime | Stub | 0 / 5 | Not working end to end. The server sends one event per subscribe message. The browser never subscribes. Channel names never match. An empty subscription receives everything. |
| S10 Dispatcher UI | Partial | 0 / 3 | Vertical-slice exit not met. The flow stops at route calculation. Fabricated fallback candidates. Static "Why selected?". Hard-coded intake. No real routes, generated types or design tokens. |
| S11 Other flows | Missing | 0 / 11 | No sweeper, crew reject, re-rank on rejection, map or manual coordination. The hospital UI can't be reached with a real hospital login. Crew and hospital screens are ID text boxes. |
| S12 Reassessment & sim | Stub | 0 / 21 | Reassessment only sets a status and has no callers. Resource loss nulls an arbitrary row. No reroute or compare. The demo console calls a route that doesn't exist. |
| S13 ML & voice | Skipped | n/a | Skip is allowed. The README doesn't name FR-023 and FR-032, so the Exit check fails. |
| S14 Hardening | Partial | 0 / 1 | No CORS configuration. No audit-completeness test. `dod.md` cites vague evidence ("RBAC tests in suite"). |
| S15 Demo & pitch | Partial | n/a | Slides and demo guides exist. `.env.demo`, `golden-run.mp4` and the offline map test are missing. |

## The defects that matter most

Ranked by risk to the demo and to the spec's non-negotiable rules.

### 1. The UI invents data when the API fails — [checked in code]

If matching errors, the dispatcher sees hard-coded candidates AMB-002 (score
0.93) and H-003 (0.88). "Why selected?" shows the same static reasons and
"ETA 7 min" for every choice. This breaks the rule "never fabricate an
available resource", on the screen judges will watch.

It also weakens the only live browser test. That test asserts that AMB-002 and
H-003 appear on the page, and the fallback shows exactly those two, so the test
can pass even when matching fails.

`apps/web/src/App.tsx:35-47, :185-188` · `apps/web/e2e/live-golden.spec.ts:13-16`

### 2. The golden path cannot finish in the browser — [checked in code]

The dispatcher UI never calls `createAcceptance`. If a hospital accept is sent
from the client, the server compares its fresh Idempotency-Key with the key used
to *create* the request, and returns 409. The "live Playwright passed" claim
covers a flow that stops at route calculation.

`apps/api/app/services.py:261` · `apps/web/src/lib/api.ts:40-41` · `apps/web/e2e/live-golden.spec.ts`

### 3. Rankings run on placeholder numbers — [checked in code]

Ambulance ETA is `420 + unit number` seconds and hospital ETA is
`600 + code × 60`. Every route is 6,000 m / 600 s with confidence 0.95, and
three hospital score components are constants. AMB-002 and H-003 win the golden
scenario because they have the smallest codes, not because the logic chose
them.

`services.py:127, :173, :206` · `decision_engine/hospital.py:50` · `decision_engine/ambulance.py:46-51`

### 4. Safety rules are not enforced at the point of action — [checked in code]

Confirming an ambulance checks only `status == AVAILABLE`, so an ambulance
missing required equipment or with stale GPS can be dispatched.
`override_reason` is accepted and ignored for non-top picks (BR-010). Hospitals
that rejected an incident can be recommended again (BR-009). Hospital matching
never passes stale readings to the engine, so stale capacity still ranks as
eligible, against the rule never to treat stale data as available.

`services.py:144-163` · `services.py:193-210`

### 5. Authorization gaps — [checked in code]

The dispatch router never uses `require_roles`, so an ambulance crew login can
match, confirm and route. Any logged-in user can PATCH any mission. A WebSocket
subscription with an empty channel list receives every event.

`api/v1/dispatch.py` · `realtime/websocket.py:30-31` · `realtime/broker.py:39-46`

### 6. Realtime doesn't deliver — [checked in code]

After one event or heartbeat, the socket loop goes back to waiting for a new
subscribe message. The browser client never sends one. Live dashboard updates,
a headline feature, don't happen.

`realtime/websocket.py:25-50` · `web/src/lib/realtime.ts`

### 7. Capacity can leak and failure demos are stubs

Accepting an expired hold marks the request EXPIRED but leaves its reservations
HELD, and no background sweeper exists. `resource-lost` nulls the first resource
row in the table. Reassessment is never called. The ICU-failure, rejection and
ambulance-failure demo events therefore can't happen as scripted.

`services.py:265-268` · `simulation/controls.py:49-56` · `reassessment_service.py:11-39`

### 8. Role and route mismatches break two screens — [checked in code]

The frontend expects role `HOSPITAL` but the backend issues
`HOSPITAL_STAFF`/`HOSPITAL_ADMIN`, so hospital users land on the dispatcher
view. The demo console posts to `/simulation/control`, which doesn't exist, and
its test passes only because the call is mocked.

`web/src/lib/auth.ts:1,12` · `web/src/lib/api.ts:46` · `e2e/accessibility.spec.ts:70`

## What the status documents claim vs what the code does

| Claim (source) | Finding |
|---|---|
| "S0-S15 application surface is present" (STATUS.md:7) | Endpoints and screens exist for most steps. Only S0 meets its Exit. |
| "decision persistence … implemented" (STATUS.md:9-11) | `decision_service.persist_decision` has no callers, so decision runs are never stored. |
| "authenticated WebSocket subscriptions" (STATUS.md:11) | Authentication exists, but events don't reach the browser (defect 6). |
| "Backend: 33 passed" (STATUS.md:19) | pytest collects 34 tests. Nine of them are one parametrized test (`test_simulation.py:20`) that only checks action names appear in a set. Without a database, 18 pass (see Test re-run). |
| "Live HTTP golden smoke selected AMB-002, H-003, 600 s" (STATUS.md:34-35) | True, but the outcome is fixed by the placeholder numbers in defect 3. |
| "Full emergency scenario passes" and "ICU/rejection/ambulance failure: backend coverage" (docs/dod.md:57-61) | No golden-slice test exists, and none of the named failure tests exist. The failure simulations are stubs. |
| "The working tree remains uncommitted by request" (handoff 2026-09-15_2:5-6) | The same work was committed and merged as PR #1. |

## Test re-run

Re-run on this machine on 2026-09-15. PostgreSQL was not running and Docker was
not on the PATH. Every check that needs the database therefore reads **not
reproduced**, which is different from failed.

| Check | Claimed | Observed |
|---|---|---|
| Backend `pytest apps/api/tests` | 33 passed | **Not reproduced.** 34 collected: 18 passed, 7 failed, 9 errors. Every failure is `psycopg ConnectionTimeout` on 127.0.0.1:5432. An earlier session without a database got the same 18 / 7 / 9. |
| PostgreSQL integration (concurrency, append-only triggers, migration round-trip) | passed | **Not reproduced.** These need the database. They have no skip marker, so they fail loudly rather than skipping silently. |
| Ruff | clean | **Confirmed.** All checks passed. |
| Web build | passed | **Confirmed.** Built in 749 ms; 310 kB JS. |
| Web lint | passed | **Passes with warnings.** 0 errors, 3 unreported `react(set-state-in-effect)` warnings (`App.tsx:122, 129, 136`). |
| Vitest | 6 passed | **Confirmed.** 7 passed in 4 files. The claim undercounted by one. |
| Mocked / live Playwright | 6 / 1 passed | **Not run.** The live spec skips unless `LIVE_E2E=1` is set with the API and database running. `scripts/full_suite.ps1` runs neither Playwright suite nor lint. |

The 16 failing or erroring backend tests all need PostgreSQL. They cover
lifecycle, hospital scoping, reservations, triggers and the migration round-trip.
Once Docker Desktop is running, re-run them before any claim about them is
trusted either way.

## Process and hygiene

### Needs to change

- **One 88-file commit named "initial"** covering fifteen build steps. No step
  can be reviewed, bisected or reverted on its own.
- **Neither mandatory gate ran.** STATUS records the blind evaluator as
  "unavailable", and there was no user live-test sign-off.
- **Open items were silently dropped.** STATUS.md was rewritten wholesale,
  removing two items waiting on the user: the psycopg connect-timeout value and
  the `openapi-typescript` peer mismatch.
- **Decisions went unrecorded.** Placeholder ETAs, constant score weights and
  token storage in localStorage appear nowhere in `docs/spec-conflicts.md`, and
  `docs/implementation-decisions.md` was never created.
- **Unused schema.** Migrations 0010, 0011, 0013 and 0014 create tables that no
  application code uses.

### Handled well

- Every migration has a downgrade, and the chain round-trips.
- No credentials, tokens or env files in the repository; `.gitignore` respected.
- Project skills, agent instructions and the `skills/` mirror left untouched.
- Handoffs were written. The first honestly states that application code had
  not been reviewed in that pass, and that nothing was signed off.

*Authorship note:* the 2026-09-15 handoff says the S1–S12 application code
already existed uncommitted in the working tree when that session began. All of
it landed under this one commit, so this report reviews the PR as delivered and
does not attribute individual lines.

## Agreement with the earlier independent audit

The unmerged audit on `worktree-floofy-meandering-newt` (handoff 2026-09-15_3)
found the same placeholder ETAs, fixed route, constant score parts, static "Why
selected?", missing sweeper, missing reroute and compare, and unused tables.
This review differs on two points:

- **It rated S8–S9 "solid".** Mission transitions are, but realtime delivery is
  broken (defect 6).
- **It named a missing `POST /reservations/{id}/confirm` as the golden-path
  blocker.** Accept already sets reservations to CONFIRMED
  (`services.py:271-272`). The real blockers are the accept idempotency-key bug
  and the UI never requesting acceptance.

## What happens next

A ready-to-paste implementation prompt, `prompts/S01-S15_Gap_Closure.md`, turns
every gap above into a step-by-step backlog in build order. It cites the
evidence for each gap, the plan's named tests to write, the rules and gates, and
the six questions only the project owner can answer.

Priority is the vertical slice: S1 seed, S2 RBAC, S4–S7 real inputs and working
accept, S9 realtime, then the S10 browser exit. S11–S15 come after.

---

*Prepared 2026-09-15 from repository state `4f893cd`. File and line references
point at that commit.*
