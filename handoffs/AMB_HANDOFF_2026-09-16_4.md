# AMB Handoff — 2026-09-16_4

Supersedes `handoffs/AMB_HANDOFF_2026-09-16_3.md`.

## `/ambulances` Auth Root Cause And Fix

- Confirmed backend auth was valid: fresh login token plus
  `Authorization: Bearer <token>` returned HTTP 200 from `/api/v1/ambulances`.
- The actual failure was stale JWT reuse in `localStorage`; the frontend had no
  401 session recovery and kept sending invalid credentials.
- Fixed shared `api` wrapper to clear the token and emit `conclave:auth-expired`.
- Fixed `App` to return to login with a session-expired message.
- Fixed frontend role aliases for canonical `HOSPITAL_STAFF` and
  `HOSPITAL_ADMIN` claims.

## Verification

- Direct runtime probe: login 200, `/api/v1/ambulances` 200 with fresh token.
- Backend: `57 passed`.
- Ruff: passed.
- Vitest: `11 passed`.
- Web build: passed.
- Mocked Playwright: `6 passed`; live Playwright skipped by instruction.
- Secret scans, tracked-env scan, and diff checks: clean.

## Remaining Limitation

The demo still stores JWTs in localStorage. Production deployment must migrate
to secure HTTP-only cookie sessions. User manual browser sign-off is pending.
