# AMB Handoff — 2026-09-16_3

Supersedes `handoffs/AMB_HANDOFF_2026-09-16_2.md`.

## Audit Result

- Full tracked repository audit completed across backend, frontend, migrations,
  scripts, configuration, tests, assets, and documentation.
- Confirmed and fixed: missing CORS middleware, backend error-envelope message
  loss in the frontend, acceptance retry key coupling, nonfunctional matching
  retry button, unscheduled hold sweeper, silent sweeper exception handling, and
  out-of-plan destructive resource delete endpoints.
- No confirmed unused-file/function/dependency removal was safe without broader
  product decisions.

## Verification

- PostgreSQL backend tests: `55 passed`.
- Ruff: passed.
- Vitest: `9 passed`.
- Web build: passed.
- Mocked Playwright: `6 passed`; live Playwright skipped by instruction.
- Secret scans, tracked-env scan, and `git diff --check`: clean.

## Remaining Risks

- Dispatcher UI does not yet call acceptance/reservation after hospital match.
- Generated OpenAPI types are not present; `apps/web/src/lib/api.ts` remains
  handwritten.
- Browser WebSocket integration is not covered by a real authenticated client
  test; only broker/client tests exist.
- S11 rejection reranking, full hospital UI/map/manual coordination, S12
  reroute/compare and reassessment flows, S14 audit-completeness, and S15 demo
  assets remain partial.
- JWT remains in localStorage for the local demo; production should use secure
  HTTP-only cookie sessions.
- `.env.test` is absent, backup/restore is unverified, blind evaluator was
  unavailable, and user live-test sign-off is pending.

## Memory Files

- `AGENTS.md` updated with the current architecture, commands, invariants, and
  mandatory memory-maintenance workflow.
- `STATUS.md` updated with the audit, exact test counts, fixes, and gaps.
- `CLAUDE.md` updated with current context, domain model, API/realtime rules,
  decisions, and limitations.
