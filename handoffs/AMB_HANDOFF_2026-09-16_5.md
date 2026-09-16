# AMB Handoff — 2026-09-16_5

Supersedes `handoffs/AMB_HANDOFF_2026-09-16_4.md`.

## `/ambulances` Authentication Investigation

- Traced `AmbulanceFleetScreen` → `api.ambulances()` → shared `request()` →
  localStorage token → `Authorization: Bearer` → FastAPI `current_user()` →
  JWT decode → database user lookup → `AmbulanceViewer` role check → response.
- Confirmed root cause: stale or malformed JWTs remained in localStorage after a
  prior login, and the frontend had no 401 session recovery. The backend was
  correctly rejecting the invalid token.
- Confirmed runtime behavior: fresh login returned HTTP 200 and the same Bearer
  token returned HTTP 200 from `/api/v1/ambulances` with 10 records.
- Fixed the shared wrapper to clear stale tokens and emit `conclave:auth-expired`;
  `App` returns to login with a session-expired message. Added canonical
  `HOSPITAL_STAFF`/`HOSPITAL_ADMIN` role aliases.

## Verification

- Backend: `58 passed`.
- Ruff: passed.
- Vitest: `11 passed`.
- Web build: passed.
- Mocked Playwright: `6 passed`; live browser test skipped by instruction.
- Malformed-token, expired-token, valid-token, stale-session, role-mapping, and
  direct authenticated ambulance endpoint checks passed.
- Secret scans and `git diff --check`: clean.

## Remaining Limitation

The local demo still stores JWTs in localStorage. Production deployment must use
secure HTTP-only cookie sessions. Explicit user browser sign-off remains pending.
