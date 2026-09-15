# AMB Handoff — 2026-09-15_3

Supersedes `handoffs/AMB_HANDOFF_2026-09-15_2.md`. This session did not write
application code — it was a read-only spec-compliance audit of the repo after
pulling a collaborator's merged PR (`4f893cd`, PR #1 from `febzzz10/main`) that
the previous handoff's author had not seen. `STATUS.md` is rewritten in the
same pass.

## Audit

- `git log`: local `main` was 2 commits behind `origin/main`; fast-forwarded to
  `4f893cd`. That merge added ~4800 lines: full S1-S12 backend (decision
  engines, reservation/mission/acceptance services, realtime, RBAC, migrations
  `0001`-`0015`), a working frontend (RoleScreens, realtime client, e2e specs),
  and the `STATUS.md`/`docs/dod.md`/handoffs this session is now correcting.
- No uncommitted work existed before this session; none was added except this
  handoff, `STATUS.md`, and the bug-catalog entries below.
- Golden path: not run live here (no Docker/Postgres/Chromium in this
  environment). Read the code instead: as written, the golden path would stop
  at the reservation hold — `POST /reservations/{id}/confirm` does not exist,
  so `consume()` (which hard-requires `CONFIRMED`) is unreachable. Separately,
  the dispatcher UI never calls `createAcceptance`, so the hospital-accept step
  is skipped end to end, not just untested.

## Verification run this session (raw, not claimed)

- `pytest apps/api/tests -q`: **18 passed, 7 failed, 9 errors** — every
  failure/error is `psycopg.errors.ConnectionTimeout` against `127.0.0.1:5432`
  (no Postgres available here), not an assertion failure. RBAC, concurrency,
  and audit-trigger tests are therefore **unverified this session**, not
  confirmed passing — re-run with Docker before trusting `STATUS.md`'s "33
  passed".
- `ruff check .`: clean.
- `pnpm build` / `pnpm lint`: clean, but lint has 3 unreported
  `react(set-state-in-effect)` warnings (`App.tsx:122,129,136`).
- `vitest run`: **7 passed**, not the previously-recorded 6 (recount, not a
  regression).
- Playwright (mocked and live): could not run in this sandbox (headless
  Chromium won't launch here) — unverified, not confirmed or refuted.
- Full findings, with `file:line` citations both to code and to spec, are in
  this session's conversation transcript; not all fit here (target ≤150 lines).

## Signed off

Nothing. Zero-error-gate step 5 (live test + explicit user sign-off) has not
happened, same as every prior handoff.

## Built, not live-tested

- S0-S3 (skeleton, schema/seed/reset, auth/RBAC, slice CRUD): solid, matches
  spec. Live test should show: login, incident create, requirement add, all
  over real HTTP against Postgres.
- S4-S6 (ambulance/hospital matching, routing): endpoints work, but the
  scoring formulas have ~half their weight terms hardcoded to constants
  (`decision_engine/ambulance.py:51`, `hospital.py:50` — capability/
  acceptance/readiness fixed at 1.0/0.5, never computed) and `/routes/calculate`
  always returns a fixed 600 s regardless of input. No `RoutingProvider`
  abstraction exists despite techspec requiring one. Live test should show two
  different incidents producing two different ETAs/scores — it currently would
  not.
- S7 (acceptance/hold/accept): row-locking and idempotency are real and
  correct, but **`/reservations/{id}/confirm` is missing** — the HELD→
  CONFIRMED→IN_USE chain cannot complete. Live test should show a reservation
  reaching CONFIRMED after hospital accept; it cannot yet.
- S8-S9 (mission state, realtime): solid, matches spec, version-conflict
  handling and WS dedupe/backoff both verified in code.
- S10 (dispatcher UI): screens exist, `DEMO MODE` visible — but the "Why
  selected?" decision-trace panel is **hardcoded static text**
  (`App.tsx:186-188`), not bound to the actually-selected candidate. Live test
  should show the panel's numbers change when a non-default ambulance is
  picked; it currently will not.
- S11 (remaining flows): rejection endpoint real; no automatic sweeper (only a
  manual `/expire`); hospital-accept step never called from the dispatcher UI
  (BR-006); no map (zero Mapbox/Leaflet references anywhere in `apps/web`).
- S12 (reassessment/simulation): `reassessment_service.py` and
  `simulation/controls.py` (all named demo actions) are real, Demo Controller
  screen exists — but no anti-flap/hysteresis (BR-013), and `/missions/{id}/
  reroute` + `/routes/compare` are both missing. Migrations `0006`, `0010`,
  `0011`, `0013`, `0014` add tables (`resource_events`, `route_alternatives`,
  `decision_trace_context`, `simulation_scenarios`, `simulation_events`) that
  **no application code anywhere reads or writes** — orphaned schema.
- S13 (ML/voice): correctly skipped, matches plan's own recommendation.

## Open questions and gaps

- No new spec-vs-spec conflict found this session — gaps found are
  implementation-vs-spec, not spec-vs-spec, so no new row was added to
  `spec-lookup/references/conflicts.md`. Existing resolutions this session
  spot-checked and found correctly followed in code: C01 (`PATIENT_ON_BOARD`),
  C03 (`AMBULANCE_CREW`), C08 (reservation enum spellings), C26 (version bump
  on every reservation write), C32 (idempotency key stored as a column).
- Check `reservation_service.py`/`dispatch.py` before assuming `/confirm`
  exists anywhere — it does not, despite `docs/dod.md` implying the full
  reservation lifecycle is covered.
- Check `App.tsx:186-188` before trusting the decision-trace panel on screen —
  it is demo-only literal text, not live data, until fixed.
- `resources.py` duplicates every route under both `/ambulances/*` and legacy
  `/resources/ambulances/*` — check which one the frontend actually calls
  before removing either.

## Backlog (carried forward — nothing dropped)

From `AMB_HANDOFF_2026-09-15_2.md` / `_1.md`, still open:
- Backup/restore unverified (`docs/dod.md` marks it `none`).
- Not all failure scenarios have live browser rehearsal evidence.
- Browser token in `localStorage`; needs secure HTTP-only cookies before
  production.
- User live-test sign-off and the blind-evaluator gate are outstanding.

New this session, added not substituted:
- `POST /reservations/{id}/confirm` missing — reservation lifecycle broken.
- Hospital-accept step not wired into the dispatcher UI (BR-006).
- Decision-trace panel hardcoded, not data-driven.
- Decision persistence (`decision_runs`/`candidates`/`reasons`) never called.
- BR-009 (rejected-hospital exclusion) and BR-013 (reassessment hysteresis)
  unenforced.
- Missing endpoints: `POST /missions`, `POST /missions/{id}/reroute`,
  `POST /routes/matrix`, `POST /routes/compare`.
- No `RoutingProvider` abstraction; no map; no automatic sweeper (manual
  `/expire` only).
- 5 migrations' tables orphaned from application code (see above).
- Decision-engine scoring formulas partly hardcoded; ETA is derived from
  entity ID digits, not real distance — undisclosed as simulated.
- `docs/dod.md`/`STATUS.md` test-count claims need re-verification with
  Docker/Postgres/Chromium available; this session could not reproduce them.

## Position

- Build order: application code exists through S12; S13 correctly skipped.
  But S7, S10, and S11 have functional gaps that block a genuine end-to-end
  run, so this is **not** a clean vertical-slice pass despite `STATUS.md`
  previously claiming "S0-S15 application surface is present."
- Milestone: pre-M7; hardening claims in the prior handoff are overstated
  relative to what the code does.
- Next three: (1) implement `/reservations/{id}/confirm` and wire the
  dispatcher UI to call `createAcceptance` before route calculation — these
  two together unblock the actual golden path; (2) bind the decision-trace
  panel to real selected-candidate data; (3) re-run the full gate
  (`pytest`, `pnpm test`, Playwright) with Docker/Postgres/Chromium available
  to get real, reproducible pass/fail numbers before any further claim.

## Files touched

- `handoffs/AMB_HANDOFF_2026-09-15_3.md`: this handoff.
- `STATUS.md`: rewritten to match this audit, not the prior self-report.
- `.claude/skills/bug-triage/references/bug-catalog.md`: 4 new Part C entries
  (terminal-transition-endpoint-missing, explanation-UI-bound-to-literal,
  schema-shipped-never-wired, hardcoded-weight-components) — needs
  re-mirroring to `skills/` (not done in this commit; see note in PR).
- No application code changed.

## Skill feed

- Bug catalog: 4 new entries added to Part C (see Files touched). No new Part
  A shape added despite the note in the catalog edit — leaving that judgment
  call to whoever picks up the first real fix, since Part A is meant to be
  predictive, not a running log.
- No new spec-conflict row: gaps found are implementation gaps, not spec
  disagreements.
