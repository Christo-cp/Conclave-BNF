# What PR #5 and #6 actually delivered, step by step

**Code review · ResQFlow (Smart Ambulance Routing & Emergency Bed Allocation)**

- **Author:** Febin (GitHub `febzzz10`)
- **Commits:** `8f088bb` "S15: harden demo and realtime contracts" (merged as PR #5,
  `869eee0`) and `a5542de` "S8: complete backend coordination foundation"
  (merged as PR #6, `4227853`)
- **Baseline:** `4f893cd`, the state reviewed in
  `docs/reviews/pr1-collaborator-review.md`
- **Reviewed:** 2026-09-16, against `docs/executable-plan.md` S0-S15 and the
  eight defects named in the PR #1 review

> **Bottom line**
>
> **Real, verifiable backend hardening — but the two defects that block the
> demo's golden path are still open.** Authorization is now enforced
> everywhere the last review flagged it, ETAs and routes come from real
> scenario data instead of a formula, and stale/rejected hospitals are
> correctly excluded. But the dispatcher UI still cannot request hospital
> acceptance, the accept endpoint still 409s on every legitimate first
> attempt, and the realtime channel the browser subscribes to never matches
> any event, so live updates still don't reach the screen. `STATUS.md`'s
> claimed backend test count is still not reproducible on a machine without
> Docker/Postgres — not a regression, the same gap the last review found.

| Figure | What it counts |
|---|---|
| **2** | non-merge commits reviewed, `54` files changed, `+1,524 / -212` lines |
| **3** | new Alembic migrations (`0016`-`0018`), head now `0018_decision_trace_fields` |
| **2 / 8** | old defects fully **fixed** (4, 5); **4 / 8** partially fixed (1, 3, 7, 8); **2 / 8** still broken (2, 6) |
| **1** | additional plan-named test now passing exactly under its plan name (`test_sweeper_expires_hold_restores_capacity_once`), out of the ~59 named tests in the re-audited steps |
| **26 / 11 / 17** | backend tests passed/failed/errored when actually re-run (STATUS.md claims `54 passed`) |

## How this was checked

### Sync

The local `main` was behind `origin/main` by 6 commits at session start:

```
$ git status
On branch main
Your branch is behind 'origin/main' by 6 commits, and can be fast-forwarded.
$ git fetch origin
From https://github.com/Christo-cp/Conclave-BNF
   7556733..4227853  main -> origin/main
$ git pull --ff-only
Updating 4f893cd..4227853
Fast-forward
 58 files changed, 2623 insertions(+), 212 deletions(-)
$ git status
On branch main
Your branch is up to date with 'origin/main'.
```

(Two untracked local files under `docs/pitch/` blocked the first pull attempt;
they were byte-identical to the versions already on `origin/main` — confirmed
with `diff`/`cmp` before moving them aside — so the fast-forward was safe.)
`main` is now at `4227853`, matching `origin/main` exactly.

### Audits

Four independent read-only audits then ran in parallel against `HEAD`
(`4227853`): one against defects 1-4, one against defects 5-8, one updating
every row of the PR #1 review's step table, and one re-running the full
test/build/lint suite from `CLAUDE.md`'s Commands section. Each audit re-read
current file content rather than trusting old line numbers or STATUS.md's own
claims, the same discipline the PR #1 review used.

## What got fixed

- **Authorization is enforced everywhere the last review flagged it (defect
  5).** `dispatch.py:35-37` gates match/confirm/route with `require_roles`;
  crew accept/reject is scoped to the crew's own ambulance
  (`dispatch.py:72-84`); mission PATCH is scoped via `can_access_mission`
  (`missions.py:17-22,44-51`); an empty WebSocket subscription now closes the
  connection instead of receiving everything (`websocket.py:34-36`).
  `test_rbac.py` and `test_crew.py` exercise these paths directly.
- **Safety checks now run at the point of action (defect 4).**
  `confirm_ambulance` re-runs equipment/GPS-staleness checks immediately
  before confirming (`services.py:167-170`); `override_reason` is required
  and audited for non-top picks (`services.py:171-172,180-181`); hospitals
  with a prior `REJECTED` request for the incident are excluded (BR-009,
  `services.py:229-231`); stale resources are excluded before scoring
  (`services.py:235`, `decision_engine/hospital.py:41-42`).
- **ETAs and routes are real scenario data, not a formula (defect 3, partial).**
  `routing/providers.py:46-56` looks up per-unit/per-hospital values from the
  `GOLDEN_2026` scenario (`simulation/seed.py:132-143`) instead of
  `420 + unit number`. Score components remain partly hardcoded — see below.
- **Two of the eight database/schema gaps from S1 are closed.** One-active-
  mission and one-active-assignment partial-unique indexes, status `CHECK`s,
  and append-only triggers on `decision_runs/candidates/reasons` all land in
  `migrations/0016_s1_invariants.py:12-37`. The golden seed now includes
  H-007/H-008, `INC-000001`, and `MSN-000001` (`seed.py:91-99`).
- **The fabricated error-path fallback candidates are gone (defect 1,
  partial).** `apps/web/src/components/decision-state.tsx:10` now shows
  honest failure text instead of AMB-002/H-003.
- **The demo simulation route mismatch is fixed (defect 8, partial).** The
  frontend now posts to `/admin/simulation/{action}`, matching a real backend
  route gated to `SYSTEM_ADMIN`/`DEMO_CONTROLLER` (`api.ts:46-55`,
  `simulation.py:12-18`).
- **A working sweeper exists (defect 7, partial).** `sweeper.py:11-24`
  correctly expires held reservations and restores capacity, verified by
  `test_sweeper.py`. Resource-loss simulation now targets a specific resource
  tied to the mission's hospital instead of nulling an arbitrary row
  (`simulation/controls.py:49-64`).

## What's still broken

### 1. The golden path still cannot finish in the browser — defect 2, unchanged

The dispatcher UI (`App.tsx:163-176`) never calls `createAcceptance`; a
hospital operator has no way to obtain the acceptance-request UUID
`RoleScreens.tsx` asks them to type in. Independently, the accept endpoint
still compares the *accept* call's fresh `Idempotency-Key` against the key
recorded at *create* time (`services.py:294`); since the frontend generates a
new UUID per call (`api.ts:40-41`), a correct, fresh accept attempt will
**always** 409. This is the same defect the PR #1 review found, unfixed by
either commit in this range.

### 2. Realtime still doesn't deliver, for a new reason — defect 6, unchanged

The client now sends an explicit subscribe message on connect
(`realtime.ts:47`), which looks like a fix. But it subscribes to the literal
channel `"dispatcher:all"`, and `EventSubscription.accepts()`
(`broker.py:39-46`) only ever matches against real entity/mission/incident/
hospital/ambulance IDs in the event payload — never that literal string — so
the subscription can never intersect a real event. Non-dispatcher roles fare
worse: `can_subscribe` (`realtime/auth.py:27-28`) only allows `dispatcher:*`
for `DISPATCHER`/`SYSTEM_ADMIN`/`DEMO_CONTROLLER`, so hospital and crew
clients are disconnected with code 4403 immediately after connecting. No
test exercises the `dispatcher:all` path or a non-dispatcher subscription, so
this regression-shaped gap is untested.

### 3. Score components are still a quarter to a third hardcoded — defect 3, partial

`decision_engine/ambulance.py:51` still bakes in a fixed `0.25*1.0` term;
`decision_engine/hospital.py:50` still bakes in `0.20*1.0 + 0.20*0.5 +
0.10*0.5` — three constants independent of the actual candidate, ~35% of the
hospital score's weight.

### 4. The sweeper and reassessment engine are built but not wired up — defect 7, partial

`sweeper.py` works when called directly in its own test, but nothing in
`apps/api/app` schedules or calls it — no cron, no admin endpoint. It also
only restores capacity; it does not reassess or rerank after expiring a
hold. `reassessment_service.py`'s four handlers (resource loss, traffic
change, ambulance failure, GPS loss) remain uncalled by `simulation/
controls.py` or any router — confirmed by a repo-wide grep — so a triggered
failure event still cannot flow through to a reassigned candidate.

### 5. One role-string mismatch survives — defect 8, partial

The demo route path is fixed, but `auth.ts`'s `ROLE_ALIASES`
(`auth.ts:10-18`) still has no `hospital_staff`/`hospital_admin` entries for
the backend's actual `HOSPITAL_STAFF`/`HOSPITAL_ADMIN` roles. A logged-in
hospital user's role normalizes to `null`, and `rolePath` sends them to
`/dispatch` instead of `/hospital`.

### 6. The "why selected" explanation is still invented — defect 1, partial

`App.tsx:172-173`'s explanation panel and confirmation-bar caption
(`"GPS fresh · 5 seconds old"`, `"ETA 7 min · ALS crew..."`) are static
strings that never read `selectedAmbulance.reasons`, `.age_s`, or `.eta_s` —
the same class of fabrication the last review flagged, just no longer
triggered by an API failure.

## Step-by-step status (all S0-S15)

S0, S3, S4, S6, and S13 were **not independently re-checked this pass** —
neither commit in this range touches their core files (confirmed against the
54-file diff list). Their rows below carry forward the PR #1 verdict
unchanged, marked accordingly, rather than being silently dropped from the
table.

| Step | PR #1 status | Current status | Named tests | What changed |
|---|---|---|---|---|
| S0 Skeleton | Partial (2/2) | Partial (2/2) — *carried forward, not re-audited* | 2/2 | No files in this step's scope changed. |
| S1 Schema & seed | Partial (0/13) | Partial (0/13) | 0/13 | Real invariants (indexes, CHECKs, triggers) and golden seed data added, but no plan-named test file exists and one of six roles (`HOSPITAL_ADMIN`) is still unseeded. |
| S2 Auth & RBAC | Partial (0/3) | Partial (0/3) | 0/3 | Dispatch role gating and `test_rbac.py` close the named gaps in substance; `logout` remains a no-op; no `test_auth.py` exists. |
| S3 Slice CRUD | Partial (0/5) | Partial (0/5) — *carried forward, not re-audited* | 0/5 | No files in this step's scope changed. |
| S4 Ambulance match | Stub (3/13) | Stub (3/13) — *carried forward, not re-audited* | 3/13 | `decision_engine/ambulance.py`'s scoring logic itself is untouched (confirmed by the defect-3 audit, which found the same fixed `0.25*1.0` term still present); only a new extra test file was added. |
| S5 Routing | Stub (0/3) | Partial | 0/3 | Real `RoutingProvider` interface and per-entity scenario ETAs/routes replace the constant formula (defect 3). |
| S6 Hospital match | Stub (0/9) | Stub (0/9) — *carried forward, not re-audited* | 0/9 | `decision_engine/hospital.py`'s scoring logic is untouched apart from the stale-exclusion fix already credited under defect 4; radius search and the other named gaps are unconfirmed this pass. |
| S7 Acceptance & hold | Partial (0/15) | Partial (0/15) | 0/15 | Still blocked end-to-end by the accept idempotency-key bug (defect 2). |
| S8 Mission state | Partial (0/5) | Partial (0/5) | 0/5 | Mission PATCH is now access-scoped and destination assignment writes event/notification/audit; a duplicate, unused `transition_mission` in `mission_service.py` is dead code risking drift with `services.py`. |
| S9 Realtime | Stub (0/5) | Partial (0/5) | 0/5 | Persistent server loop and client auto-subscribe exist, but the channel mismatch means nothing is actually delivered end-to-end (defect 6). |
| S10 Dispatcher UI | Partial (0/3) | Partial (0/3) | 0/3 | Fabricated fallback candidates removed; static "why selected" text remains; flow still stops before acceptance. |
| S11 Other flows | Missing (0/11) | Stub/Partial (1/11) | 1/11 | A working, tested sweeper exists but is unwired; crew reject and targeted resource loss now work; map/manual coordination and hospital-screen reachability not verified this pass. |
| S12 Reassessment & sim | Stub (0/21) | Stub (0/21) | 0/21 | 9 named simulation actions now exist and are role-gated, but `reassessment_service.py` is still never called by anything — no reroute, no compare, no rerank after a failure event. |
| S13 ML & voice | Skipped | Skipped — *carried forward, not re-audited* | n/a | No change; skip remains plan-approved. |
| S14 Hardening | Partial (0/1) | Partial (0/1) | 0/1 | No `CORSMiddleware` anywhere in `main.py`; no audit-completeness test. Unchanged. |
| S15 Demo & pitch | Partial | Partial | n/a | Despite the commit message, S15 deliverables (`.env.demo`, `docs/demo/golden-run.mp4`) are still missing; the commit mostly touched S8/S9 backend files. |

## What the status documents claim vs what the code does

| Claim (source) | Finding |
|---|---|
| "Backend: `54 passed`" (`STATUS.md`) | **Not reproducible** on a machine without Docker/Postgres. Observed: 26 passed / 11 failed / 17 errored, every failure a `psycopg.errors.ConnectionTimeout`. The prior review found the identical pattern (18/7/9 then); this is not a new regression, it's an environment dependency that STATUS.md still doesn't caveat for a Docker-less run. |
| "S15: harden demo and realtime contracts" (commit message) | Realtime is not end-to-end functional (defect 6); no S15 demo artifacts were added. The commit's actual content is mostly S7-S9 backend work. |
| "S8: complete backend coordination foundation" (commit message) | Mission-state scoping and destination writes are genuinely more complete, but "complete" overstates it: acceptance still can't be created from the UI, and reassessment/reroute (also S8-adjacent) remain uncalled. |
| Lint "passed" (`STATUS.md`) | **Confirmed but incomplete disclosure.** 0 errors, but 3 undisclosed `react(set-state-in-effect)` warnings in `App.tsx:108,115,122`. |

## Test re-run

Re-run on 2026-09-16. Docker was **not installed** on this machine (not just
not running), so every check needing PostgreSQL reads **not reproduced**,
consistent with the prior review's finding under the same constraint.

| Check | Claimed | Observed |
|---|---|---|
| `alembic heads` | `0018_decision_trace_fields` | **Confirmed** (migration-file check, no DB needed). |
| Backend `pytest apps/api/tests -v` | 54 passed | **Not reproduced.** 26 passed / 11 failed / 17 errored, 100% `ConnectionTimeout` on Postgres. All DB-free tests (decision engine, mock routing, realtime unit, simulation controls) passed. |
| Ruff | passed | **Confirmed.** Clean. |
| Web build | passed | **Confirmed.** Clean, no warnings. |
| Web lint (`oxlint`) | passed | **Passes with 3 undisclosed warnings** (`react(set-state-in-effect)`, `App.tsx:108,115,122`). |
| Vitest | 8 passed | **Confirmed exactly.** |
| Mocked Playwright | 6 passed | **Confirmed exactly.** |
| `git diff --check` / secret scan | clean | **Confirmed.** One labeled synthetic demo credential (`seed.py:30`, `"demo-password-change-me"`), not a real secret. |

Raw evidence (as reported by the re-run, not paraphrased from STATUS.md):

```
$ docker --version
'docker' is not recognized as an internal or external command   # not installed, not just "not running"

$ apps\api\.venv\Scripts\python.exe -m alembic -c apps\api\alembic.ini heads
0018_decision_trace_fields (head)

$ apps\api\.venv\Scripts\python.exe -m pytest apps\api\tests -v
...
54 collected: 26 passed, 11 failed, 17 errors in 484.42s
FAILED/ERROR (representative, all identical root cause):
  sqlalchemy.exc.OperationalError: (psycopg.errors.ConnectionTimeout) connect() ...
Failing/erroring files: test_acceptance.py, test_acceptance_contract.py,
  test_api_resources_and_lifecycle.py, test_backend_lifecycle.py, test_crew.py,
  test_health.py (2 of 3 — test_health_db_unreachable_503_envelope PASSED, it
  expects the DB-down case), test_rbac.py (5), test_reservation_postgres_
  integration.py (7), test_seed.py (3), test_sweeper.py.
Passing without a database: decision_engine unit tests, routing provider
  (mock), realtime unit tests, simulation controls, hospital_matching
  (service-input based).

$ apps\api\.venv\Scripts\python.exe -m ruff check apps\api scripts
All checks passed!

$ pnpm --dir apps/web build
tsc -b && vite build
✓ 1930 modules transformed. Built with no warnings.

$ pnpm --dir apps/web lint   # runs oxlint
Found 0 errors, 3 warnings:
  react(set-state-in-effect)  apps/web/src/App.tsx:108
  react(set-state-in-effect)  apps/web/src/App.tsx:115
  react(set-state-in-effect)  apps/web/src/App.tsx:122

$ pnpm --dir apps/web exec vitest run
Test Files  4 passed (4)
     Tests  8 passed (8)

$ pnpm --dir apps/web exec playwright test golden.spec.ts accessibility.spec.ts
6 passed (30.8s)

$ git diff --check
(no output, exit 0)

$ grep -riE "password|secret|api[_-]?key|token\s*=" $(git diff --name-only 4f893cd..HEAD)
apps/api/app/simulation/seed.py:30: PASSWORD = "demo-password-change-me"
(no other hits)
```

## Process and hygiene

### Needs to change

- **Two large commits, "S8" and "S15", each touching many unrelated steps.**
  `a5542de` alone spans S1, S2, S5, S8, S9, S11, and S12 files; a step name in
  a commit message no longer indicates its actual scope.
- **Dead code introduced.** `mission_service.py` duplicates
  `services.py`'s mission-transition logic; only one of them is wired to the
  route. Left as-is, the two will drift.
- **A built-but-unwired sweeper and a built-but-uncalled reassessment
  service** both look, from `STATUS.md`, like delivered capability. Neither
  does anything in the running application yet.
- **Commit-message claims ("complete", "harden") outrun what the diff
  contains,** the same pattern the PR #1 review flagged for STATUS.md.

### Handled well

- Every new migration (`0016`-`0018`) is additive and matches the existing
  downgrade convention.
- The RBAC and safety-check fixes are real, tested, and match the exact
  file:line locations the prior review cited as broken.
- No new secrets, and the one demo credential is clearly synthetic and
  labeled.
- Frontend build/lint/vitest/Playwright claims all reproduced exactly as
  stated — the frontend side of `STATUS.md` is currently trustworthy.

## What happens next

Priority order to actually unblock the demo:

1. **Fix the accept idempotency-key comparison** (`services.py:294`) and wire
   the dispatcher UI to call `createAcceptance` — this is the single blocker
   keeping the golden path from finishing in the browser.
2. **Fix the realtime channel mismatch** — either have the client subscribe
   to real entity IDs instead of `"dispatcher:all"`, or make `accepts()`
   understand role-scoped wildcard channels — and open subscriptions to
   hospital/crew roles.
3. **Wire the sweeper and reassessment service into something that runs**
   (a scheduled task or an explicit admin trigger, plus calling
   `reassessment_service` from the simulation-failure handlers), or the S11/
   S12 failure-scenario demo steps still cannot happen as scripted.
4. Fix the `HOSPITAL_STAFF`/`HOSPITAL_ADMIN` role-alias gap in `auth.ts` and
   replace the two remaining hardcoded score/explanation constants once the
   above are unblocked.

---

*Prepared 2026-09-16 from repository state `4227853`, reviewing commits
`8f088bb` and `a5542de` against baseline `4f893cd`. File and line references
point at `4227853`.*
