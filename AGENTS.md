# AGENTS.md — Smart Ambulance Routing & Emergency Bed Allocation

Instructions for any AI coding agent working in this folder. Read this file
completely before touching anything.

> **No application code exists yet.** The folder holds six specifications, a
> build plan the user has not signed off, and agent tooling — no git
> repository, package manifest, test suite or runnable app. Everything marked
> **(planned)** comes from the specs or the plan and is not on disk. Check
> reality (`ls`, and `git status` once a repository exists) before acting on it; when reality and this file
> disagree, reality wins — say so and update this file in the same change.

**Authority.** This file states the rules. `CLAUDE.md` (Claude Code) and the
`SKILL.md` files under `.claude/skills/` must agree with it; they add
step-by-step detail, not different rules. If any file contradicts this one,
stop and report the contradiction to the user instead of picking a side.
**Changing state** — current build step, open decisions, test counts, installed
tools — lives in `STATUS.md` and the newest `handoffs/` file, never here.

**Codes used below**

| Code | Meaning | Where |
|---|---|---|
| `prd:123` | A line in a spec. Prefixes: `prd`, `plan`, `flow` (appflow.md), `db` (database.md), `tech` (techspec.md), `design` | Root specs |
| `S0`–`S15` | Build steps | `docs/executable-plan.md` Part B |
| `A1`–`A6` | Plan sections: machine audit, commands, decisions, decision maths, reservation rules, seed | `docs/executable-plan.md` Part A |
| `P1`, `P2` | Pre-build decisions: database runtime, map/routing provider | Plan A3 |
| `C01`… | A row in the spec-conflict register; **DECIDE** rows are the user's call | `.claude/skills/spec-lookup/references/conflicts.md` |
| `M1`–`M8` | Milestones | plan:5129-5174 |
| `FR-nnn`, `BR-nnn` | Functional requirement, business rule | prd:485-980, prd:1128-1216 |

---

## 1. Project Overview

A hackathon prototype for real-time emergency coordination, with a build plan
spanning 48 hours (plan:3485-3503). It must choose a suitable ambulance, route it, rank hospitals against the patient's
clinical requirements, obtain hospital acceptance, and reserve a scarce resource
(for example an ICU bed) transactionally — recalculating when traffic, a
rejection or a resource loss changes the picture.

It is **decision support on synthetic data**, not a clinically autonomous system
(tech:6968). The safety rules in §9 outrank optimisation, speed and polish.

## 2. Repository Structure

Exists today:

| Path | What it is | Agent may edit? |
|---|---|---|
| `prd.md` `plan.md` `appflow.md` `design.md` `database.md` `techspec.md` | The six specs, ~450 KB together | **Never** — read-only |
| `docs/executable-plan.md` | Build plan S0–S15 with per-step tests and exit checks | Only when the user asks |
| `docs/spec-digest/` | Human-facing digest of the specs | No; don't load it for lookups |
| `STATUS.md` | Current state, ≤ 60 lines | Only via the handoff procedure (§10) |
| `handoffs/` | Session handoffs | Add new files only |
| `AGENTS.md` | This file | Yes, without asking, only to match verified reality (new scripts, the generated layout) in the same change. Any change to a rule needs the user's OK |
| `CLAUDE.md` | Claude Code instructions | Only to keep it consistent with this file, with the user's OK |
| `.claude/skills/<name>/SKILL.md` | Detailed procedures: `session-start`, `spec-lookup`, `zero-error-gate`, `bug-triage`, `handoff` | With the user's OK |
| `.claude/skills/spec-lookup/references/conflicts.md` | Spec-conflict register | Add rows; mark rows RESOLVED |
| `.claude/skills/bug-triage/references/bug-catalog.md` | Predicted and diagnosed bug shapes | Append diagnosed bugs to Part C |
| `.claude/agents/blind-evaluator.md`, `prompts/Quality_Gate_Blind_Evaluator.md` | Quality-gate evaluator and protocol | With the user's OK |
| `skills/` | Upload mirror of `.claude/skills/` | **Never directly** — re-mirror (§8) |

Planned layout **(planned)** — tech:5579-5612 as adapted by plan S0; specs stay
at the root (C29):

```text
apps/web/              React + Vite app; Playwright specs in e2e/ (see §8)
apps/api/              FastAPI: app/, migrations/, tests/, alembic.ini, pyproject.toml
packages/*             pnpm workspace packages (tech:5590-5593: shared-types, config, ui)
scripts/               db_create.py, reset_demo.py, measure_decision_latency.py
docs/spec-conflicts.md Decisions on conflict rows (created in S0)
docker-compose.yml     Only if P1 = Docker
.env.example           Key names with empty values
```

## 3. Tech Stack

Specified in tech:498-560; plan S0 names the packages but pins no library
versions. **Nothing is installed in the project yet.**

| Layer | Specified | Notes |
|---|---|---|
| Frontend **(planned)** | React, TypeScript, Vite, Tailwind CSS, TanStack Query, Zustand, React Router, React Hook Form, Zod, Lucide React, Recharts | pnpm workspace |
| Backend **(planned)** | Python 3.12 (uv), FastAPI, Pydantic + pydantic-settings, SQLAlchemy ≥ 2, Alembic, WebSockets, psycopg, GeoAlchemy2, PyJWT, argon2-cffi | Built with hatchling, package `app` |
| Database **(planned)** | PostgreSQL 16 + PostGIS, `pgcrypto` | Runtime (Docker or native) is decision P1 |
| Optimisation | Google OR-Tools, "only where actually useful" (tech:539-542) | Optional |
| ML | XGBoost / LightGBM, scikit-learn | Optional, S13 only; plan sets `ML_ENABLED=false` |
| Testing **(planned)** | Pytest, httpx, Vitest, React Testing Library, jsdom, Playwright; Ruff (lint), mypy | |
| Maps / routing | Decision P2 (plan recommends a deterministic mock provider plus Mapbox) | |
| Formatter, deployment target, CI | **Unknown** — not specified | Ask before choosing |

Never add a technology, service or provider the specs don't list — including an
LLM API — without the user's explicit decision.

## 4. Architecture & Key Components (planned)

Not implemented. These are binding design rules from the specs.

- **Three separated layers** (tech:570-579): deterministic rules → optimisation
  → prediction. Hard constraints filter candidates **before** scoring on
  **every** path — match, recalculation, override, voice. An ineligible
  candidate is never scored.
- **No business or decision logic in React components or FastAPI route
  handlers** (tech:6966). Planned homes (plan Part D): `ambulance_matcher`,
  `hospital_matcher`, `IncidentService`, `AcceptanceService`,
  `ReservationService`, `MissionService`, `ReassessmentService`,
  `RoutingService` with pluggable providers, `core/security`, `freshness.py`,
  `explanations.py`, and a repository layer for database access inside
  `apps/api`.
- **One definition per name.** All state enums in `app/core/enums.py`; event,
  notification and audit names in one shared constants module.
- **Reservations are server-authoritative** (tech:6956): one transaction with a
  row lock, an optimistic `version = version + 1` bump, and the capacity check
  `occupied + reserved + available <= total`. A destination is confirmed only
  after its reservation commits.
- **Realtime:** publish WebSocket events only **after** COMMIT. A write carrying
  a stale `state_version` is rejected with `MISSION_STATE_CONFLICT`.
- **Explainability and audit:** every recommendation carries reasons,
  confidence, data freshness and algorithm/config versions; every critical
  transition writes an audit row.
- **API:** techspec's endpoint set under `/api/v1`; `Idempotency-Key` header on
  reservations; `X-Request-ID` and JSON logs on every request.

**First vertical slice**, built before anything else (plan:4696-4716, plan
S0–S10): create incident → find ambulance → assign → calculate route → find
hospital → accept → reserve ICU, surfaced through WebSocket to the dispatcher UI.

## 5. Development Setup

**Reading the specs.** Never read a spec end to end. Grep for the keyword, then
read slices of ≤ 80 lines using offset/limit. Cite each spec fact you act on as
`file:line`. `techspec.md` lines 1–2533 are a pasted prompt whose section
numbers repeat the real spec's, so cite lines, never "§N". Details:
`.claude/skills/spec-lookup/SKILL.md`.

**When specs disagree**, precedence is (tech:347-394):
**safety › prd › techspec › database › plan › appflow › design.** Grep the
conflict register first; if the row is marked DECIDE, ask the user.

**Toolchain required (planned)** — verify each with `--version`; never assume
it is installed:

| Tool | Requirement |
|---|---|
| Node + pnpm | Version not specified by the specs; plan installs pnpm with `corepack enable pnpm` |
| uv | Installs and manages Python |
| Python | **3.12** for the API, in `apps/api/.venv`. A newer system Python may be present; always use the venv interpreter |
| PostgreSQL 16 + PostGIS | Docker image `postgis/postgis:16-3.5`, or a native install — per P1 |
| git | Repository created in S0 |

**Setup is gated.** Do not run S0 until P1 is decided and the user has signed
off the plan (check `STATUS.md`).

The S0 commands are only in `docs/executable-plan.md` lines 347-400, and they
are deliberately not copied here: the plan is unsigned, and a second copy would
drift. Two details there matter:
- `pnpm create vite` needs `--no-interactive`, or it stops to prompt.
- If P1 = Docker, use the plan's recommended image, `postgis/postgis:16-3.5`.

## 6. Build, Run & Test Commands

**None of these can run today.** They are plan A2's commands, unverified
against real code. Once `package.json` or `pyproject.toml` defines scripts,
those win; update this table in the same change.

PowerShell, from the project root, after
`$py = ".\apps\api\.venv\Scripts\python.exe"`. In a POSIX shell such as Git
Bash, use forward slashes and call `apps/api/.venv/Scripts/python.exe`
directly.

| Purpose | Command (planned) |
|---|---|
| Migrate | `& $py -m alembic -c apps\api\alembic.ini upgrade head` |
| Reset and seed demo data | `& $py scripts\reset_demo.py` |
| Start API | `& $py -m uvicorn app.main:app --app-dir apps\api --reload` |
| Start web | `pnpm --dir apps/web dev` |
| API tests | `& $py -m pytest apps\api\tests -v` |
| API lint | `& $py -m ruff check apps\api` |
| Web type-check + build | `pnpm --dir apps/web build` (runs `tsc -b`) |
| Web unit tests | `pnpm --dir apps/web exec vitest run` |
| E2E | `pnpm --dir apps/web exec playwright test <spec>` |
| Generate API types | `pnpm --dir apps/web exec openapi-typescript http://127.0.0.1:8000/api/v1/openapi.json -o src/lib/api/schema.d.ts` — the app sets FastAPI's `openapi_url` to this path (tech:5125; user decision 2026-09-13). Open the URL first to confirm |

**Full suite (planned)** — what "run the full suite" means in §13. Run all of it
from the project root, not only the files you changed.

- **No tests yet.** Skip a runner while no test file of its kind exists, and
  name the skip. `vitest run` and `playwright test` exit non-zero when they
  find no tests.
- **Playwright prerequisites.** With `$env:ENV_FILE = ".env.test"`, reset the
  demo data and start the API and the web app first (plan A2).
- **Judging the result.** See §13 step 2.

```powershell
.\scripts\full_suite.ps1   # pytest, ruff, web build, and vitest once web tests exist; refuses to run while port 8000 listens
# From S10, then the browser suite: docs/executable-plan.md A2 "Browser suite"
```

## 7. Coding Standards

Only these are established. Where nothing is established, follow the dominant
pattern in surrounding code; if there is none, ask.

- **Unknown ≠ available.** Never coerce NULL/unknown capacity or requirements
  to `0`, `false` or "available" — watch `or 0`, `bool()`, `?? 0`, `!!` and
  Pydantic defaults. Unknown stays unknown end to end.
- **Coordinates:** PostGIS `ST_Point` and Mapbox take `lng, lat`; API bodies and
  Google use `{lat, lng}`. Convert explicitly at every boundary.
- **Determinism:** same input + config → same output; ties broken by id.
- **Numbers:** every number is a cited spec value, a named configuration key
  (plan A4), or a seed fixture (plan A6). Values the plan chose are marked `*` in
  `docs/executable-plan.md` and are never described as spec values. An unmeasured figure is a **target**.
- **Labelling:** simulated data is always visibly labelled (`DEMO MODE`,
  `SIMULATED`, `data_mode`); stale data is shown as stale.
- **Python:** Ruff clean; SQLAlchemy 2 style; timezone-aware datetimes, UTC in
  storage. mypy strictness is **unknown**.
- **TypeScript:** passes `tsc -b` via `pnpm build`. API types are generated from
  OpenAPI, never hand-written.
- **UI:** token values from `design.md`; every data view renders loading, error,
  stale and simulated states.

## 8. File & Folder Conventions

| Item | Convention | Source |
|---|---|---|
| Specs | Stay at the root with their current names | C29 |
| API package | `apps/api/app/`; `app/core/enums.py`, `app/core/security`; modules snake_case, service classes PascalCase (`ReservationService`) | plan S0, A3, Part D |
| API tests | `apps/api/tests/test_<area>.py`; functions `test_<behaviour>` (e.g. `test_health_db_unreachable_503_envelope`). Reuse spec case names: Gherkin plan:2817-2879, edge cases plan:2335-2433, DB-001..006 db:4755-4840 | plan S0 |
| RBAC tests | One table in `apps/api/tests/test_rbac.py` of (endpoint, role, expected status); every new endpoint adds rows | plan Part B |
| Migrations | `apps/api/migrations/`, db's table order (db:5390-5410), named `0001_…` onward; never edit one that has been applied | C17 |
| E2E tests | `e2e/<name>.spec.ts` (e.g. `e2e/golden.spec.ts`). The plan runs Playwright from `apps/web`, so the folder is `apps/web/e2e/` unless the Playwright config sets another `testDir` — check that config once it exists | plan S15, A2 |
| Generated files | `apps/web/src/lib/api/schema.d.ts` is generated — regenerate, never hand-edit | plan A2 |
| Scripts | `scripts/<snake_case>.py` | plan S0 |
| Env files | `.env` (dev), `.env.test` (browser tests on `smart_ambulance_test`, chosen with `$env:ENV_FILE`), `.env.demo` (demo, chosen with `$env:ENV_FILE`), `.env.example` (committed, empty values) | plan A2 |
| Human-readable IDs | `INC-`, `MSN-`, `RES-` + six digits; `AMB-001`, `H-001` | C13 |
| Names in code | Enum values and domain/audit events UPPER_SNAKE; WebSocket events dotted lowercase | C20 |
| Docs | `docs/spec-conflicts.md`, `docs/dod.md`, `docs/measurements.md`, `docs/demo/`, `docs/pitch/` | plan S0, S14, S15 |
| Handoffs | `handoffs/AMB_HANDOFF_<YYYY-MM-DD>.md`, then `_2`, `_3` the same day | handoff skill |
| Skills | `.claude/skills/<kebab-name>/SKILL.md`, supporting files in `references/`; after any change run `robocopy .claude\skills skills /MIR` (exit codes 0–3 mean success) | CLAUDE.md |
| React components, hooks, stores; web folder layout | **Unknown** — not specified. Follow the Vite scaffold until the user decides | — |

## 9. Non-negotiable Safety Rules

Constraints, not trade-offs (tech:6946-6972, flow:3974-3987, prd:1128-1216). A
change that breaks one is wrong regardless of test results.

1. Never select an unsuitable or unavailable ambulance because it is closer.
2. Never recommend a hospital that violates a mandatory clinical requirement.
3. Never treat unknown or stale capacity as confirmed; never fabricate an
   available resource.
4. Never reserve more than is available; never double-book a finite resource.
5. Never let client code be the source of truth for reservations.
6. Never let AI/ML output override hard constraints.
7. Never change a destination silently: mission event + notification + audit row.
8. Never hide stale or simulated data, or a critical failure.
9. Never override a mandatory constraint. Any other override requires a reason
   and is audited. Do not build a "dispatcher override when nothing is
   feasible" unless the user decides otherwise (C24).
10. Never let stale UI overwrite newer server state.
11. Never claim the prototype is clinically autonomous. Never write "first
    system", "live ICU data", "saves lives" or "% accurate" in UI copy, README or
    pitch (plan:5257-5281).

## 10. AI Agent Workflow

1. **Orient.** Read `STATUS.md` and the newest handoff; verify them against
   reality; report any drift; confirm with the user which item to start.
   (Procedure: `.claude/skills/session-start/SKILL.md`. Agents without a skill
   loader read `SKILL.md` files directly.)
2. **Understand before changing.** Read the relevant spec slices, the conflict
   register and the existing code path end to end, including callers and tests.
3. **Reuse.** Search for an existing service, repository, enum, constant,
   utility or UI component before creating one.
4. **Respect the order.** Build S0–S15 in sequence; S11 onward waits for the
   S10 exit. Never start a step without the user's sign-off on the previous one.
5. **Ask** when a requirement is ambiguous, a spec is silent, or the work
   crosses a DECIDE row or an item in `STATUS.md` "Waiting on the user". Do not
   guess and do not re-propose an approach the user rejected.
6. **Keep changes focused.** Do what was asked; no drive-by refactors, renames
   or reformatting.
7. **Validate** with §13, then **report**: files changed, commands run with
   their real output, what was not tested, and remaining risks.
8. **Bugs:** gather evidence before proposing a fix
   (`.claude/skills/bug-triage/SKILL.md`). After two failed fixes on the same
   bug, stop and restart the diagnosis from the symptom.
9. **End of session:** write a new handoff and rewrite `STATUS.md` in the same
   pass (`.claude/skills/handoff/SKILL.md`).

## 11. Rules for Modifying Existing Code

- Read the whole function, its callers and its tests before editing.
- Preserve behaviour you were not asked to change; keep public names, enum
  values and endpoint paths stable unless changing them is the task.
- Any change to eligibility, scoring, reservation or state transitions must keep
  hard constraints ahead of scoring on every path — grep every caller.
- Never delete, overwrite or rename a spec, handoff, conflict row, skill, applied
  migration or `.env*` file. If one must change, state why and get the user's
  agreement first.
- Edits to skills, the gate protocol or `CLAUDE.md` need the user's OK; keep them
  consistent with this file.

## 12. Rules for Creating New Files

- Place files per §2 and §8; don't invent new top-level folders.
- If the scaffold generates a layout that differs from §2 or §8, keep the
  generated layout and update this file in the same change.
- Record a decision on a conflict row in `docs/spec-conflicts.md` in techspec's
  format — Document A / Document B / Resolution / Reason / Implementation Impact
  (tech:376-394) — then mark the row RESOLVED in the register. A newly found
  disagreement gets a new `Cnn` row.
- A newly diagnosed bug gets one line in bug-catalog Part C: date · symptom ·
  confirmed cause · regression test name.

## 13. Testing & Validation

Two gates, both mandatory, in this order.

**Gate 1: blind-evaluator quality gate.** It applies to code, scripts, migrations,
schemas, specs, plans, docs, prompts and test suites. It does not apply to
conversation or one-line fixes. Follow `prompts/Quality_Gate_Blind_Evaluator.md`
in full:

- A fresh, context-blind evaluator gets only the locked brief and the artifact.
- End the delivery with the score line.
- Never invent a score, and never simulate the evaluator yourself.
- If you cannot spawn an evaluator, label the delivery `Quality gate: not run — evaluator unavailable`.
- Never copy the pass mark into another file or prompt.

**Gate 2: zero-error gate** (details in `.claude/skills/zero-error-gate/SKILL.md`):

1. **Write the tests and show them.** For each area the change touches, they
   assert behaviour:
   - an ineligible candidate is never scored;
   - NULL/unknown is never treated as available;
   - of two concurrent reserves on one unit, exactly one succeeds;
   - an invalid state transition is rejected;
   - events publish only after commit;
   - a wrong role gets 403;
   - loading, error, stale and SIMULATED UI states render.
2. **Run the full suite from the root and show the real output.**
   - Tests use `smart_ambulance_test`, never the dev or demo database (db:3482).
   - The run passes only if every failure is already recorded as pre-existing
     in `STATUS.md` or the newest handoff. Name each one. Any other failure
     blocks the gate, even one you believe is unrelated.
   - With no suite yet, say so; don't claim this step.
3. **Safety check against §9.** Give evidence for each rule the change touches, and write "not affected" for the rest.
4. **Definition of Done (§17).**
5. **Live test and sign-off.** Give the user exact steps and expected results, then get explicit sign-off.

**Tests that pass while the feature is broken.** Look for these substitutes:

- SQLite instead of PostGIS
- in-process WebSocket clients
- mocked routing
- sequential-only reservation tests
- tests pointed at the dev database

## 14. Security & Privacy

- **Synthetic data only.** Never use real patient health information in code,
  seeds, fixtures, logs, screenshots or demos (tech:1445, prd:1045-1047).
- **Secrets.** Never commit `.env` or `.env.demo`.
  - Before the first commit, `.gitignore` must list `.env`, `.env.demo`, `.env.test`, `.venv` and `node_modules`.
  - Commit only `.env.example`, with empty values. Key names follow tech:4893-4926.
  - Generate `JWT_SECRET` locally.
  - Never paste real tokens (Mapbox, Google) into files, prompts, issues or chat.
- **Never log** passwords, tokens, API secrets or unnecessary patient
  identifiers (tech:4965-4970). Health endpoints never expose connection details.
- **Authorisation is server-side** on every endpoint (RBAC with data scoping).
  Hiding a button is not authorisation.
- **Required controls** (tech:4949-4963): HTTPS, input validation,
  parameterised SQL, CORS restricted to `CORS_ORIGINS`, rate limiting, audit
  logging.
- **Before any commit**, run both checks below across the whole repository. Each
  must print nothing. The second is plan S14's check, widened to root files and
  to Mapbox secret tokens (`sk.eyJ…`) and hyphenated keys (`sk-proj-…`). A pattern search catches only the
  formats it knows, so also read the staged diff for anything that looks like a
  key or password.
  - `git ls-files .env .env.demo .env.test`
  - `git grep -nIE "sk-[A-Za-z0-9_-]{20,}|[ps]k\.eyJ[A-Za-z0-9_-]{20,}|AKIA[0-9A-Z]{16}"`

## 15. Git & Commit Guidelines

- There is no repository until S0 runs `git init`. Branching, remotes, PRs and
  CI are **unknown / not defined**; ask before creating any of them.
- Planned convention (`docs/executable-plan.md` lines 6-16): one commit per completed build
  step, made after its exit passes and the user signs off, with the message
  `S<n>: <title>`.
- Stage deliberately and read `git status` before committing; confirm no
  secret or `.env*` file is staged.
- Never force-push, rewrite shared history, or commit outside the agreed
  convention without asking.

## 16. Common Pitfalls

- **The plan has open defects.** `STATUS.md` lists them. Check it before
  implementing any plan step verbatim.
- **Type-check.** `tsc --noEmit` checks nothing on a Vite project-references
  tsconfig. Use `pnpm --dir apps/web build`, even where another project file
  shows `tsc --noEmit`.
- **Distance units.** With SRID 4326, `geometry` distances come out in degrees
  and `geography` distances in metres. Metre-radius queries need `geography`
  (C14).
- **The space in `AI conclave`** breaks unquoted paths and tools that shell
  out through cmd.exe. Quote every path.
- **Unspecified values.** The specs give no reservation TTL, stability margin,
  reroute gain, decision lock or search radii. Plan A4 defaults are
  configuration, not spec values.
- **Pre-ticked `[x]` boxes** in plan.md (plan:3543-3558) are not evidence of
  completion.
- **Name drift.** The specs disagree on many enums and names, so expect
  mismatches between database CHECKs, backend enums and frontend constants.
  Grep the conflict register before naming anything.
- **More bug shapes.** Predicted shapes: lng/lat swap, event published before
  commit, orphaned reservations, silent mock fallback and others, listed in
  `.claude/skills/bug-triage/references/bug-catalog.md`.

## 17. Definition of Done

A task is done only when **all** of these are true, each shown with evidence
from the current session:

- [ ] Every applicable Definition of Done box (plan:4370-4387, tech:6754) is
      ticked, or its gap is named. The boxes: API, database state and
      migration, validation, authorisation, error handling, UI with loading and
      error states, realtime (if applicable), audit event, tests, demo scenario,
      failure scenario (where applicable), README/docs updated.
- [ ] Schema or migration work also passes the database DoD (db:6127-6150).
- [ ] The build step's **Exit** block in `docs/executable-plan.md` passes, with
      each named test shown as `PASSED`.
- [ ] No §9 safety rule is broken, with evidence for each rule touched.
- [ ] The quality gate has run and its score line is reported honestly.
- [ ] The user has live-tested the change and explicitly signed off. Neither a
      green suite nor silence counts as sign-off.
- [ ] At session end, the handoff and `STATUS.md` are updated, and `skills/` is
      re-mirrored if any skill changed.

Never say "done", "fixed" or "passing" without running the command and reading
its output in the same session.
