# AMB Handoff — 2026-09-14

Supersedes `AMB_HANDOFF_2026-09-13.md` (kept). `STATUS.md` was rewritten in the
same pass.

## 1. Audit (run this session)

- **Git.** Repository initialised in S0. No commits; every file is untracked.
  `.env` and `.env.test` do not appear in `git status`, so `.gitignore` covers them.
- **API tests.** `pytest apps\api\tests -v`: **1 passed, 1 error**, 261.85 s.
  - `test_health_db_unreachable_503_envelope` PASSED.
  - `test_health_db_up` ERROR at setup: psycopg `ConnectionTimeout`. This is not
    a code fault: PostgreSQL does not exist yet because Docker is not installed.
- **Lint and build.** `ruff check apps\api scripts`: All checks passed.
  `pnpm --dir apps/web build`: exit 0.
- **Vitest and Playwright.** Skipped; no web tests exist yet.
- **Golden path.** Not started. S0 stops at the database.
- **Skills mirror.** Re-mirrored after every skill edit (see §8).

## 2. Signed off

Nothing has passed zero-error-gate step 5. The user did make decisions:
- They took every recommendation in the decision list, then C01(a) and `INTERNAL_ERROR` for the health 503.
- They approved the plan-mode plan, saying "this shall be the last bit of planning, after this start working the project".

## 3. Built, not live-tested

### 3.1 `docs/executable-plan.md` (901 lines)

All user decisions are applied. After gate round 2 fell below round 1, the plan
was rewritten from the round-1 version.

**Quality gate: 7.6/10 — adjudicated best of 5 rounds, below the 8.8 threshold.**
Round scores were 7.2, 6.9, 7.6, 7.6 and 7.6; the adjudicator chose round 5.
Unresolved defects, as the adjudicator named them:
- The browser suite resets once and then runs every Playwright spec on one test
  database, with parallel workers still allowed. Specs can collide on AMB-002
  and H-003's single ICU.
- The A2 env template generates `POSTGRES_PASSWORD` separately in each env file.
  The single container reads only `.env`, so every file needs the same password.
  The real S0 files already share one password.
- A3 lists C36 as a user decision, but the locked brief predates it. The user
  did choose `INTERNAL_ERROR` (2026-09-13); the defect is the brief, not the plan.
- No step names the map library S11 needs.
- Some Exit comments ("exit 0", "All checks passed") describe output rather
  than check it. The S14 check for `\| none \|` depends on the table's format.

Fix these with the user's OK before S10 and S11. Don't hand-edit them in unasked.

### 3.2 S0, partial

**Built**
- `.gitignore`, `.env.example`, `.env` and `.env.test`. Secrets were generated
  locally and never printed; both env files share one password.
- `README.md`, `pnpm-workspace.yaml`, `docker-compose.yml` (bound to
  `127.0.0.1:5432`, named volume `pgdata`).
- `docs/spec-conflicts.md`.
- `apps/web`: Vite react-ts scaffold, all S0 packages, Playwright Chromium.
- `apps/api`:
  - `pyproject.toml` (`requires-python = "==3.12.*"`) and `.venv`;
  - `app/main.py` (`openapi_url` set), `app/core/{config,errors,log,middleware}.py`;
  - `app/db/session.py`, `app/api/v1/health.py`;
  - `alembic.ini`, `migrations/` (no revisions);
  - `tests/conftest.py`, `tests/test_health.py`.
- `scripts/db_create.py`, `scripts/full_suite.ps1` (parse-checked, never run).

**Not done**
- `docker compose up` and `db_create.py`.
- `test_health_db_up`, the live `/health/db` check and a `full_suite.ps1` run.
- The blind-evaluator gate on the S0 code, and the zero-error gate.

**Live test should show**
- `Invoke-RestMethod http://127.0.0.1:8000/api/v1/health/db` returns
  `connectivity: ok`, an empty `migration_version` and `simple_query: 1`.
- `/api/v1/openapi.json` returns the schema.
- With the database stopped, the endpoint returns 503 with `INTERNAL_ERROR` and
  no host, port or password in the body.

**Installed versions**
- Tools: pnpm 12.4.1, Python 3.12.14 (uv).
- API: fastapi 0.141.1, sqlalchemy 2.0.52, alembic 1.20.0, psycopg 3.3.5,
  pydantic 2.13.5, pydantic-settings 2.15.0, pyjwt 2.14.0, argon2-cffi 25.1.0,
  geoalchemy2 0.20.0, uvicorn 0.52.4, pytest 9.1.1, httpx 0.28.1, ruff 0.16.7,
  mypy 2.3.1.
- Web: create-vite 9.2.1, react 19.3.0, vite 8.3.0, typescript 6.0.3,
  tailwindcss 4.3.3, vitest 5.0.0, @playwright/test 1.63.0,
  openapi-typescript 7.13.0; Chromium 153.0.8010.12.

## 4. Open questions

### 4.1 Blocking S0

1. **Docker Desktop (P1).** WSL is not installed and the agent's shell is not
   elevated. The user runs, in an administrator PowerShell: `wsl --install`,
   reboot, `winget install -e --id Docker.DockerDesktop`, then starts Docker
   Desktop once.
2. **Database connect timeout.** With PostgreSQL down, psycopg takes about 130 s
   to fail (bug catalog Part C), so `/health/db` and pytest hang that long. No
   spec gives a value. Ask the user for a `connect_timeout` (an engine
   `connect_args` value, marked `*`) or whether to accept the hang.

### 4.2 Decisions recorded

- `docs/spec-conflicts.md` (tech:373-392 format): P1, P2, C01, C05, C06, C08,
  C10, C11, C14, C24, C27, C31 and the new C36.
- The register marks C01, C05, C06, C08, C10, C11, C14, C24, C27 and C31
  RESOLVED, and has a new row C36.
- In the plan text only:
  - D1: `openapi_url`;
  - D2: a refused hold is not sticky;
  - D3: resource-loss rule d returns 409 when nothing can be decremented;
  - D4: browser tests use `.env.test`.

### 4.3 Check before guessing

- `openapi-typescript` 7.13.0 declares a peer of TypeScript `^5`, and the
  scaffold installed 6.0.3. Verify type generation when S10 first needs it.
- Starlette warns that `TestClient` with httpx is deprecated (it suggests httpx2).
  This is a warning only; the plan names httpx.
- The create-vite 9 scaffold ships oxlint, not ESLint.
- `conftest.py` does not yet force `SIMULATION_ENABLED=false` (plan A2). That is
  needed from S4, not S0.
- The rtk and 8.3 short path from the zero-error-gate skill were not used this
  session; plain pytest output was read directly.
- `AGENTS.md` §6 now points at `full_suite.ps1`. Its header still says the plan
  is unsigned and no code exists; update that at S0 sign-off.

## 5. Backlog (carried from 2026-09-13)

| Item | State |
|---|---|
| Plan defect: openapi path | Closed: D1 applied |
| Plan defect: A5.3 rule d | Closed: D3 applied |
| Plan defect: refused-hold persistence | Closed: D2 applied |
| Plan defect: browser tests on the dev database | Closed: D4 applied |
| Schedule is tight (slice at hour 29) | Open |
| Plan sign-off and DECIDE answers | Closed: answered and approved |
| Gemini for S13 | Deferred until the S12 exit (user took the recommendation) |
| Skill fix `tsc --noEmit` → `pnpm build` | Closed: done and mirrored |
| Spec critique: coordination-time baseline, prior-art framing, privacy note | Open, after S10 |
| The five adjudicator defects (§3.1) | New, before S10/S11 |
| Database connect timeout (§4.1) | New, blocks finishing S0 |

## 6. Position

- **Build-order step:** S0 (M1, plan:5131), in progress.
- **Vertical slice:** not started.
- **Next three**
  1. The user installs Docker and answers the connect-timeout question.
  2. Finish the S0 exit (compose, `db_create`, both health tests, live checks,
     `full_suite.ps1`), then the blind-evaluator gate on the S0 code and
     `/zero-error-gate`.
  3. User sign-off, then the secret checks, commit `S0: Repository, database,
     skeleton` and a `STATUS.md` update; then S1.

## 7. Files touched

| File | Change |
|---|---|
| `docs/executable-plan.md` | Decisions applied; five gate rounds; the adjudicated version is on disk |
| `AGENTS.md` | OpenAPI path; `.env.test`; §6 full suite points at `full_suite.ps1` |
| `.claude/skills/zero-error-gate/SKILL.md` | Web type check is `pnpm --dir apps/web build` |
| `.claude/skills/spec-lookup/references/conflicts.md` | 10 rows RESOLVED; C36 added |
| `.claude/skills/bug-triage/references/bug-catalog.md` | First Part C entry (psycopg hang) |
| `docs/spec-conflicts.md` | Created; 13 decisions |
| S0 files | See §3.2 |
| `STATUS.md` | Rewritten to match this handoff |

## 8. Skill feed

- **bug-catalog Part C:** psycopg's ~130 s connect timeout on Windows.
- **conflicts register:** C01, C05, C06, C08, C10, C11, C14, C24, C27 and C31
  RESOLVED; C36 added.
- **zero-error-gate:** web type-check command.
- **Re-mirror:** robocopy after each edit; the final mirror runs with this handoff.
