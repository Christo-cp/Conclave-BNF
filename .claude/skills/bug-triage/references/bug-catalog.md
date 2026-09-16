# Smart Ambulance bug catalog

Compiled 2026-09-13, before any code existed. Part A lists shapes this stack and
these specs make likely. Part B lists shapes that recurred in earlier projects
and transfer here. Part C records bugs actually diagnosed in this project.

## A. Predicted shapes (this stack)

1. **Longitude/latitude swap.** PostGIS is `ST_Point(lng, lat)`, Mapbox arrays
   are `[lng, lat]`, and Google and the API bodies use `{lat, lng}`. Symptoms:
   markers in the sea, thousand-kilometre distances, the wrong "nearest"
   ambulance, `ST_DWithin` returning nothing. Evidence: raw coordinates at every
   boundary. (db:2147-2164)
2. **Geometry vs geography units.** Distances on `geometry(Point,4326)` come
   out in degrees; on `geography` they come out in metres. Symptom: a 5000 radius
   matches everything or nothing. Evidence: the column type plus one known
   distance. (conflict C14)
3. **Unknown collapsed to zero or false.** NULL becomes `0` or `False` via
   `or 0`, a Pydantic default, `bool()`, or JavaScript `?? 0` / `!!`. Symptoms: a
   hospital wrongly excluded, or — worse — UNKNOWN shown as available. Evidence:
   the raw DB value, each transform on the way to the decision input, and
   `exclusion_reason`. (tech:4405-4433)
4. **Double booking under concurrency.** Check-then-update without
   `FOR UPDATE`, a lock on the wrong row, an early commit releasing the lock, or
   an external call made inside the transaction. Sequential tests never catch it.
   Evidence: a two-connection concurrent test (db:3519-3537), the integrity
   checks (db:3906-3939), and `resource_events`.
5. **Orphaned reservation.** A rejection, resource loss, cancellation or
   ambulance-failure path forgets to release. Symptom: capacity drains across
   demo runs and the second rehearsal fails. Evidence: the `active_reservations`
   view vs mission status after each scenario. (db:4886-4908)
6. **Event published before commit.** A WebSocket publish inside the
   transaction makes the UI announce a reservation that later rolled back.
   Evidence: log order of publish vs COMMIT. (db:2895-2907)
7. **Out-of-order or duplicate events.** A late ETA update reopens a completed
   mission in the UI, or a reconnect replays events twice. Evidence: `event_id`
   and `entity_version` in the client log. (db:5230-5298)
8. **Stale client overwrites the server.** Optimistic UI or a second tab
   writes old mission state. Evidence: the `state_version` sent vs the one
   stored; the correct response is `MISSION_STATE_CONFLICT`. (db:1467-1488,
   flow:3771-3810)
9. **Score direction or normalisation inverted.** ETA weighted as a benefit
   instead of a cost, a sort in the wrong direction, or one un-normalised factor
   dominating. Symptom: the slowest suitable unit wins, or the ranking flips on
   trivial data. Evidence: `feature_values` and per-factor contributions for the
   top three. (conflict C11)
10. **Hard constraint skipped on a second code path.** The filter runs in
    `/dispatch/.../match` but not in recalculation, override or voice. Symptom:
    an invalid hospital appears only after an event. Evidence: grep every caller
    of scoring; each must go through the constraints first. (tech:6946-6952)
11. **Enum or name drift between layers.** The DB CHECK says `HANDOVER`, the
    backend emits `HANDOVER_COMPLETE`, the frontend expects `handover.completed`.
    The specs disagree in 34 places, so this is near certain. Symptom: a 422, a
    CHECK violation, or a UI stuck in one state. Evidence: generated OpenAPI
    types vs DB CHECK vs frontend constants. (conflicts C01, C08, C20)
12. **Timezone.** Naive datetimes, or the client clock used for freshness; IST
    display vs UTC storage makes GPS look hours stale or fresh forever. Evidence:
    raw `gps_updated_at` with its timezone vs server `NOW()`. (db:5302-5312)
13. **Silent fallback to a mock.** A missing key or exhausted quota drops to
    straight-line ETA or the mock provider without a label; ML disabled returns a
    baseline without `fallback_used`. Tests pass because tests use mocks.
    Evidence: `provider` and `fallback_used` on the rows; the startup log of
    active providers.
14. **Demo not reproducible.** Seed not fixed at 2026, a reset that leaves
    incidents or reservations behind, wall-clock-dependent timers. Symptom:
    rehearsal differs from the last run. Evidence: run the reset twice and diff
    the key tables. (db:2780-2826)
15. **Swallowed async failure.** An exception in FastAPI `BackgroundTasks` or
    an unreferenced `asyncio.create_task` vanishes, and the reservation-expiry
    worker or the simulation timeline silently stops. Evidence: is the task held
    and its exception logged, and is the worker still ticking?
16. **Tests green, feature broken.** SQLite instead of PostGIS, an in-process
    TestClient WebSocket, mocked routing, or tests hitting the dev database.
    Evidence: list what the test stubs that reality doesn't.
17. **Authorization only in the frontend.** The button is hidden but the
    endpoint is open. Evidence: call the endpoint with a wrong-role token and
    expect 403. (tech:4473-4475)
18. **Simulation leaking unlabelled.** A new screen, export or API response
    omits `data_mode` or the DEMO badge. Evidence: check the affected screen
    against design:3629 and flow:3279.

## B. Carried over from earlier projects

- **Misdiagnosis.** The first plausible cause was repeatedly wrong. Demand a
  confirming trace before fixing.
- **Config/code drift.** A config key exists but nothing reads it — weights
  hardcoded beside a YAML file that says otherwise. Evidence: grep the key's consumers.
- **Declared ≠ installed.** A dependency is added to `requirements.txt` or
  `package.json` but never installed on the user's machine, so it fails deep
  inside a worker. The `/ready` endpoint should import-check dependencies
  (plan:3154-3178).
- **UI caching.** The browser serves a stale bundle after a change. Fix: hard
  reload, versioned assets, `Cache-Control: no-store` on dev HTML.
- **Process mistakes.** Re-proposing an approach the user already rejected,
  advancing a build step before sign-off, or claiming a pass without running the command.

## C. Diagnosed in this project

(one line each: date · symptom · confirmed cause · regression test name)

- 2026-09-14 · `/api/v1/health/db` and pytest setup hang ~130 s when PostgreSQL is down · psycopg 3.3.5 on Windows raises `ConnectionTimeout` against a closed local port only after ~130 s when no `connect_timeout` is set (measured: raw socket refused in 2.02 s, `psycopg.connect` 130.06 s) · `test_health_db_unreachable_503_envelope` (passes slowly; the fix waits for a timeout value from the user)
- 2026-09-16 · Demo controller could not execute simulation controls in the live UI · frontend called `/simulation/control` while backend exposed `/admin/simulation/{action}`, and the seed omitted the DEMO_CONTROLLER user · `operations.test.ts`, `test_seed.py::test_reset_seeds_demo_controller_user`, and mocked demo-controls Playwright test
- 2026-09-16 · `/ambulances` showed `Invalid authentication token` after an earlier login · the shared frontend client kept expired or malformed JWTs in `localStorage` and had no 401 session recovery; fresh login plus Bearer token returned 200 from `/api/v1/ambulances` · `test_expired_token_is_rejected_with_authentication_error`, `test_valid_login_token_can_read_ambulances`, and frontend stale-token regression
