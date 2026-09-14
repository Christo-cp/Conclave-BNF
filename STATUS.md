# STATUS — Smart Ambulance

Last updated 2026-09-14. Handoff: `handoffs/AMB_HANDOFF_2026-09-14.md`.

## Working

- **Web app.** `pnpm --dir apps/web build` exits 0 on the Vite react-ts scaffold,
  with every S0 package installed.
- **API skeleton.** `app/main.py` serves `/api/v1/health/db` and
  `/api/v1/openapi.json`.
- **Tests.** `test_health_db_unreachable_503_envelope` PASSED.
- **Lint.** `ruff check apps\api scripts` is clean.
- **Git.** The repository is initialised with no commits. `.env` and `.env.test`
  are ignored.

## In progress

**S0 · Repository, database, skeleton (M1).** Every file is written. Still to do:
- start the database and run `db_create.py`;
- `test_health_db_up` and the live health checks;
- a `scripts/full_suite.ps1` run;
- both gates, then the user's sign-off and commit.

**Plan.** `docs/executable-plan.md` reflects every user decision and the user
approved building from it. Quality gate: 7.6/10, adjudicated best of 5 rounds,
below the threshold. Five defects remain (handoff §3.1): Playwright specs share
one database, the per-file password template, C36's attribution, no map
library, loose Exit comments. Fix them with the user's OK before S10/S11.

## Waiting on the user

1. **Docker Desktop.** In an administrator PowerShell: `wsl --install`, reboot,
   `winget install -e --id Docker.DockerDesktop`, then start it once.
2. **Database connect timeout.** A down database makes psycopg hang about 130 s
   before failing. No spec gives a value. Ask for a `connect_timeout`, or whether
   to accept the hang.

## Next

1. Finish the S0 exit once Docker is running.
2. Run the blind-evaluator gate on the S0 code, then `/zero-error-gate`, then the
   user's live test and sign-off.
3. Run the secret checks, commit `S0: Repository, database, skeleton`, then start S1.

## Known failures

- **`test_health_db_up`** errors at setup: psycopg `ConnectionTimeout`, because
  no database exists yet (Docker missing). Environmental; pre-existing until
  Docker is installed.
- **Slow unreachable test.** `test_health_db_unreachable_503_envelope` passes but
  takes about 130 s (bug catalog Part C).
- **Warnings.** Starlette deprecates `TestClient` with httpx; anyio deprecates
  `BlockingPortal`. Warnings only.
- **Peer mismatch.** `openapi-typescript` 7.13.0 declares a TypeScript `^5` peer,
  and 6.0.3 is installed. Check this at S10.
