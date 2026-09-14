# AMB Handoff — 2026-09-13

This is the first handoff, so it replaces nothing. `STATUS.md` was rewritten in
the same pass.

## 1. Audit (run this session, not from memory)

- **Code, git and tests.** No code exists. `git status` returns "fatal: not a
  git repository". There is no test suite yet (M1 not reached), so step 2 of the
  zero-error gate cannot run.
- **Golden path.** Not started; nothing has been built before S0.
- **Skills mirror.** A dry run before edits exited 0. After this session's
  register edits, robocopy exited 1 (one file copied), and a dry run afterwards
  exited 0.

## 2. Signed off

Nothing. Zero-error-gate step 5 (live test plus explicit user sign-off) has not
happened for anything.

## 3. Built, not live-tested

### `docs/executable-plan.md` (865 lines)

The S0–S15 build plan. It is a document, not code, and the user has not signed
it off.

**What it contains**
- **Setup:** machine audit and commands.
- **Decisions:**
  - 11 DECIDE questions for the user, each with a recommendation;
  - 23 pinned conflicts, with citations.
- **Engine rules:** scoring formulas and demo configuration defaults;
  hold/accept/resource-loss transactions; golden seed.
- **Build:** steps S0–S15, each with named tests and exits, with the
  vertical-slice exit at S10 (hour 29); cuts if behind; traceability.

**Quality gate: 7.9/10.** It was adjudicated best of 5 rounds and is below the
threshold. Defects still open:
- **Type generation.** The command fetches `/api/v1/openapi.json`, but FastAPI
  serves `/openapi.json` unless `openapi_url` is set.
- **A5.3 rule d.** It can push `occupied` below zero when `available` is NULL
  and no reservation exists.
- **A5.1.** A refused hold rolls back, but nothing persists the "ineligible for
  this incident" result.
- **Schedule.** It is optimistic: 15 migrations, triggers and RBAC scoping come
  before the slice at hour 29, and every step needs sign-off.
- **Databases.** Browser tests use the dev database; the demo database is used
  only in S15.

**What the live test looks like for a plan:**
1. The user reads A3 and answers the decisions.
2. The user confirms the S0 commands fit their machine.
3. The user says yes or no to the plan.

## 4. Open questions

### 4.1 DECIDE rows awaiting the user

P1 database runtime (blocks S0); P2 map/routing provider and Mapbox token
(S11–S12); C01, C05, C06, C08, C10, C11, C14, C24, C31 (block S1–S7). Plan A3
has a recommendation for each. None is recorded yet: `docs/spec-conflicts.md` is
created in S0.

### 4.2 Gemini API

The user raised this at the end of the session and has not answered yet.

My advice:
- **Not for predictions.** Don't use Gemini to produce ETA or readiness numbers:
  they would be fabricated (plan:1084-1093), and the specs reject an "LLM
  wrapper" (tech:6004).
- **Maybe for intake or voice.** Consider it as optional intake/voice assist in
  the S13 slot, with a schema-validated output, dispatcher confirmation, a
  manual form as fallback, and synthetic data only.

Still open: whether to rewrite S13. If adopted, record the stack change, because
tech:544-551 lists XGBoost/LightGBM.

### 4.3 Check before guessing

- **Type check.** `tsc --noEmit` checks nothing on a Vite react-ts scaffold,
  whose tsconfig uses project references with `files: []`. Use `pnpm build`
  (`tsc -b`). `.claude/skills/zero-error-gate/SKILL.md` still uses
  `tsc --noEmit`; it has not been edited and needs the user's OK.
- **Vite prompts.** `pnpm create vite` prompts in a terminal unless given
  `--no-interactive` (verified against the create-vite source and docs).
- **PostGIS image.** `postgis/postgis:16-3.4` is no longer in the maintained tag
  list; use `16-3.5`.
- **Machine.**
  - Docker, pnpm and psql are not installed.
  - Python is 3.14.5; the plan pins 3.12 via uv 0.12.7.
  - Node 22.23.2, git 2.54.0.
  - The path contains a space, so rtk needs the 8.3 path
    `C:\Users\chris\Claude\Projects\HACKAT~1\AICONC~1`.
- **Unspecified values.** The specs give no values for reservation TTL,
  stability margin, reroute gain, decision lock or search radii. Plan A4 sets
  demo configuration defaults; never cite those as spec values.
- **techspec.md.** Lines 1–2533 are a pasted master prompt, and its section
  numbers repeat. Cite lines, not sections.
- **Gate agent.** The `blind-evaluator` agent type was not loaded during this
  session's gate rounds. Those rounds used fresh general-purpose agents given the
  text of `.claude/agents/blind-evaluator.md` verbatim. It has loaded since.

## 5. Backlog

There is no previous handoff to carry forward. Current items:

- **Plan fixes.** Fix the three plan defects (openapi_url, A5.3 rule d, persisting
  hold refusals), then re-gate.
- **Sign-off.** Get the user's sign-off on the plan and answers to the DECIDE
  rows.
- **Gemini.** Get a decision, then rewrite S13 or leave it.
- **Skill fix.** Propose the `zero-error-gate` change from `tsc --noEmit` to
  `pnpm build`.
- **Spec critique leftovers.** Points from this session's spec review that no
  document covers yet:
  - a measured coordination-time baseline for the pitch;
  - prior-art framing (existing 108 ambulance services, bed portals);
  - a privacy/regulatory note for patient data.

## 6. Position

- **Build-order step:** before step 1 of plan:4665-4692, i.e. plan step S0.
- **Milestone:** none; M1 not reached.
- **Vertical slice:** not started.
- **Next three:**
  1. The user answers P1 (ideally every DECIDE row) and signs off the plan.
  2. Fix the three plan defects and re-gate.
  3. S0: repository, database, skeleton.

## 7. Files touched

| File | Change |
|---|---|
| `docs/executable-plan.md` | Created: the build plan (adjudicated version, 7.9/10) |
| `.claude/skills/spec-lookup/references/conflicts.md` | C13 notes tech:2923's five-digit `MSN-00012`; C35 added for the GPS freshness boundary overlap (tech:4618-4635) |
| `skills/spec-lookup/references/conflicts.md` | Re-mirrored copy of the above |
| `STATUS.md` | Created; matches this handoff |
| `handoffs/AMB_HANDOFF_2026-09-13.md` | This file |

## 8. Skill feed

- **`spec-lookup/references/conflicts.md`:** C13 updated and C35 added, both as
  defaults rather than DECIDE rows.
- **`bug-triage/references/bug-catalog.md` Part C:** no entries. No code has
  run, so nothing has been diagnosed; the design defects from plan review are in
  sections 3 and 4.
- **Re-mirror:** done, exit 1; the dry run afterwards exited 0.
