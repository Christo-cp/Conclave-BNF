# AMB Handoff — 2026-09-16_6

Supersedes `handoffs/AMB_HANDOFF_2026-09-16_5.md`.

## Session purpose

Completed a read-only full-repository audit and generated
`docs/pitch/PROJECT_PITCH_AND_CODEBASE_ANALYSIS.md`.

## Signed off

- No new product sign-off. This was an analysis/documentation session.
- Repository scope inspected: 178 tracked files; backend app/tests/migrations,
  frontend source/E2E, scripts, Docker/env/configuration, docs, demos, pitch
  artifacts, status, handoffs, and project instructions.
- The strongest verified browser path is incident intake -> requirements ->
  ambulance match/confirm -> hospital match -> deterministic route calculation.

## Built, not live-tested or partial

- Backend acceptance, reservation, mission, destination, sweeper, simulation,
  audit, and realtime paths are implemented and tested in targeted areas.
- Complete browser acceptance/reservation/failure/reassessment journey is not
  verified. Live Playwright is opt-in and current live spec stops at routing.
- The product is synthetic decision support. Routing is `MockRoutingProvider` and
  all seed operational data is `SIMULATED`.

## Important audit findings

- Core safety architecture is a strength: hard constraints precede scoring,
  unknown/stale capacity fails closed, reservations use row locks and idempotency,
  mission writes use versions, and events publish after commit.
- Production blockers: localStorage JWTs, insecure development defaults, no rate
  limiting, no CI/deployment/rollback/backup evidence, process-local realtime,
  missing generated frontend API types, and incomplete live browser coverage.
- Documentation drift: `docs/dod.md` still cites revisions through 0015 and 33
  backend tests; current evidence is migration 0018 and 58 backend tests.
- README setup references `.env.test` and `.env.demo`, which are not committed;
  clean-checkout setup requires local creation.

## Evidence

- `docs/pitch/PROJECT_PITCH_AND_CODEBASE_ANALYSIS.md` contains the full analysis,
  60-second, 3-minute, and 5-minute pitches, slides, demo script, Q&A, and map.
- Verified source anchors include `apps/api/app/services.py`,
  `apps/api/app/reservation_service.py`, `apps/api/app/decision_engine/`,
  `apps/api/app/realtime/`, `apps/web/src/App.tsx`,
  `apps/web/src/RoleScreens.tsx`, and `apps/web/e2e/`.

## Next three items

1. Owner reviews and live-tests the generated pitch against the current demo.
2. Refresh `docs/dod.md` evidence counts/migration range before presenting it as
   current verification.
3. If continuing implementation, finish the S10 acceptance/reservation browser
   flow before claiming the documented wow sequence is demonstrable end to end.

## Quality gate status

Blind evaluator unavailable; no score is claimed. Explicit owner live-test
sign-off remains pending.
