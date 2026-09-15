# AMB Handoff — 2026-09-16

Supersedes `handoffs/AMB_HANDOFF_2026-09-15_2.md`.

## Signed off

- None. User live-test sign-off has not happened.

## Built and verified, awaiting user sign-off

- Removed fabricated selectable ambulance and hospital fallback candidates from
  `apps/web/src/App.tsx`; matching errors remain non-confirmable.
- Reservation release now rejects unknown capacity instead of coercing `NULL` to
  zero. Regression coverage is in the PostgreSQL reservation integration tests.
- Frontend realtime types and consumers now follow the backend envelope:
  `event_id`, `event`, `entity_id`, `entity_version`, `mode`, and `payload`.
  Mission events trigger REST resync by entity id.
- Updated `CLAUDE.md` to describe the implemented S0-S15 repository.
- Demo simulation client paths now call `/api/v1/admin/simulation/{action}`.
- Seed data now includes `demo.controller@demo.invalid` with the
  `DEMO_CONTROLLER` role.
- Full suite: 37 backend tests passed, Ruff passed, web build passed, 8 Vitest
  tests passed, and 6 mocked Playwright tests passed.
- Live golden browser flow passed against FastAPI/PostGIS.
- Live demo-controller rehearsal passed all 8 mission-targeted controls with a
  real mission id. Dispatcher attempts correctly returned 403.

## Open questions and limitations

- `.env.test` is not present. Live verification used the untracked local `.env`
  and did not expose its values.
- Backup/restore remains unverified.
- Not all failure scenarios have live browser recording evidence.
- Browser tokens remain in local storage; production requires HTTP-only cookies.
- Blind evaluator unavailable.
- Configured code-review subagent unavailable because its model was not found.

## Position

- Build order: S15 verification/hardening.
- Milestone: final prototype verification; first vertical slice runs end to end.
- Next: user live-test sign-off, decide whether to add `.env.test`, then address
  production session handling and backup/restore verification.

## Files touched

- `CLAUDE.md`: corrected obsolete no-code repository description.
- `apps/api/app/reservation_service.py`: preserved unknown capacity safely.
- `apps/api/app/simulation/seed.py`: seeded demo-controller user.
- `apps/api/app/tests/*`: added reservation, seed, and realtime regressions.
- `apps/web/src/App.tsx`: removed fabricated recommendation fallbacks.
- `apps/web/src/lib/api.ts`: aligned simulation endpoint mapping.
- `apps/web/src/lib/realtime.ts`, `RoleScreens.tsx`: aligned event contract and
  REST resync behavior.
- `apps/web/e2e/accessibility.spec.ts`: updated simulation endpoint fixture.
- `skills/`: re-mirrored from `.claude/skills/`.
