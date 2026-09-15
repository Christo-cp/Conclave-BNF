# STATUS — Smart Ambulance

Last updated 2026-09-15 (audit pass). Handoff: `handoffs/AMB_HANDOFF_2026-09-15_3.md`.

## Working

- S0-S3: skeleton, schema/migrations (`0001`-`0015`, clean chain), seed/reset,
  auth/RBAC scaffolding, slice CRUD. Matches spec.
- S8-S9: mission state transitions (versioned, conflict-checked) and realtime
  (`/ws`, JWT+RBAC, client dedupe/backoff/resync). Matches spec.
- Reservation row-locking, idempotency-key handling, unknown-≠-available
  handling (BR-003), simulated-data labelling (BR-012): implemented correctly
  in both backend and frontend.
- `ruff check`: clean. `pnpm build`: clean. `vitest run`: 7 passed.

## In progress / broken

- **Reservation lifecycle cannot complete**: `POST /reservations/{id}/confirm`
  does not exist; `consume()` requires `CONFIRMED`, so it's unreachable.
- **Hospital-accept step is skipped in the dispatcher UI** — `createAcceptance`
  is defined but never called (BR-006).
- **"Why selected?" decision-trace panel is hardcoded static text**
  (`App.tsx:186-188`), not bound to the selected candidate.
- Ambulance/hospital scoring formulas have ~half their weight terms hardcoded
  to constants instead of computed per candidate; no `RoutingProvider`
  abstraction; `/routes/calculate` always returns a fixed 600s.
- No automatic reservation-expiry sweeper (manual `/expire` only).
- BR-009 (exclude rejected hospitals) and BR-013 (reassessment hysteresis)
  unenforced. Missing: `POST /missions`, `POST /missions/{id}/reroute`,
  `POST /routes/matrix`, `POST /routes/compare`, map (no Mapbox/Leaflet).
- 5 migrations (`0006`, `0010`, `0011`, `0013`, `0014`) add tables no
  application code reads or writes.
- S13 ML/voice: intentionally skipped (no training data, per plan).

## Next

1. Implement `/reservations/{id}/confirm`; wire dispatcher UI to call
   `createAcceptance` before route calculation — unblocks the real golden path.
2. Bind the decision-trace panel to the selected candidate's real data.
3. Re-run `pytest`/`pnpm test`/Playwright with Docker+Postgres+Chromium
   available — this session had none, so test-count claims below are
   unverified here, not confirmed.

## Known failures / unverified this session

- `pytest apps/api/tests -q` here: 18 passed, 7 failed, 9 errors — all
  `psycopg.ConnectionTimeout` (no Postgres in this sandbox), not assertion
  failures. Needs re-run with Docker before trusting any backend pass count.
- Playwright (mocked and live): could not launch Chromium in this sandbox.
- Backup/restore: unverified (`docs/dod.md`).
- User live-test sign-off: outstanding, as in every prior status.

## Simulated / mocked

- ETA in both decision engines is derived from the entity's own ID digits, not
  real distance/routing — labelled here as simulated; not yet labelled as such
  in the UI.
- `/routes/calculate` always returns a fixed mock route (`distance_m=6000,
  duration_seconds=600`).
