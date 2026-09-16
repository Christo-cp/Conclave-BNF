# Definition of Done Evidence

Last reviewed: 2026-09-15. Evidence is limited to commands and files actually
run or inspected in this repository. `none` means the requirement is not
verified; it is deliberately not a claim of completion.

## Engineering DoD

| Requirement | Evidence |
|---|---|
| API exists | `apps/api/app/api/v1/` and `pytest apps/api/tests` |
| Database state exists | Alembic revisions `0001` through `0015`; `alembic heads` |
| Validation exists | Pydantic schemas in `apps/api/app/schemas.py`; API tests |
| Authorization exists | `apps/api/app/dependencies.py`; RBAC tests in suite |
| Error handling exists | `apps/api/app/core/errors.py`; health error test |
| UI exists | `pnpm --dir apps/web build` |
| Test exists | `apps/api/tests/` and `apps/web/e2e/` |
| Audit/event exists | `audit_logs`, `mission_events`, `resource_events`; append-only triggers |
| Demo scenario works | Live Playwright `e2e/live-golden.spec.ts`; HTTP smoke selected AMB-002/H-003 |
| Failure scenario works where applicable | Backend simulation/lifecycle tests; browser rehearsal pending |

## Technical DoD

| Requirement | Evidence |
|---|---|
| Backend implemented | `apps/api/app/`; API test command |
| Database migration implemented | `apps/api/migrations/versions/0003_*.py` through `0015_*.py` |
| Validation implemented | `apps/api/app/schemas.py`; API tests |
| Authorization implemented | `apps/api/app/dependencies.py`; RBAC tests |
| Frontend implemented | `pnpm --dir apps/web build` |
| Error state implemented | API error envelope and UI components; targeted tests |
| Loading state implemented | UI component tests and screen source |
| Realtime state implemented if applicable | `apps/api/app/realtime/`; realtime tests |
| Audit event implemented where relevant | audit/event tables and service tests |
| Tests written | `apps/api/tests/`, `apps/web/src/**/*.test.*`, `apps/web/e2e/` |
| Demo data added | `apps/api/app/simulation/seed.py`; `scripts/reset_demo.py` |
| README/documentation updated | `README.md`, `docs/demo/`, `docs/pitch/` |

## Database DoD

| Requirement | Evidence |
|---|---|
| PostgreSQL/PostGIS is running | Docker-backed test run in final verification |
| All P0 tables exist | `alembic upgrade head`; migration head `0018_decision_trace_fields` |
| Migrations are reproducible | PostgreSQL migration round-trip test passed |
| Foreign keys are enforced | PostgreSQL integration tests passed |
| Core indexes exist | `0003`-`0012` index revisions |
| Spatial indexes exist | `0001_mvp_schema.py` GiST indexes |
| Resource constraints work | `0008_reservation_invariants.py`; PostgreSQL tests passed |
| Reservations are transactional | concurrent DB test passed: exactly one winner |
| Duplicate active ambulance assignments are prevented | `0004_ambulance_assignment_guard.py` |
| Mission events are append-only | `0002_s7_s12_backend.py` trigger |
| Decision traces are stored | `decision_runs`, `decision_candidates`, `decision_reasons` |
| Audit logs are stored | `audit_logs` and `0012_audit_indexes.py` |
| Demo seed data can be generated | `scripts/reset_demo.py`; database-dependent |
| Demo reset is protected from production | `app/simulation/seed.py`; seed test |
| Full emergency scenario passes | 33 backend tests plus live HTTP/Playwright golden path passed |
| Reservation concurrency test passes | PostgreSQL concurrent test passed |
| ICU failure scenario passes | Backend simulation/lifecycle coverage; live browser rehearsal pending |
| Hospital rejection scenario passes | Backend simulation/lifecycle coverage; live browser rehearsal pending |
| Ambulance failure scenario passes | Backend simulation/lifecycle coverage; live browser rehearsal pending |
| Backup/restore has been tested for deployed environment | none |

## Gate status

The automated database, migration, backend, frontend, and live golden browser
evidence passed in the final verification session. The remaining gate is user
live-test and explicit sign-off; backup/restore and full live browser failure
rehearsal remain unverified.
