---
name: zero-error-gate
description: Use when a feature, fix, migration, decision-engine change or UI screen in the Smart Ambulance project is about to be called done, when asked "verify it", "run the gate", "is it done?" or "ready for the demo?", and before moving to the next build-order step or milestone. Hard project rule, not optional.
---

# Zero-Error Gate (Smart Ambulance)

Nothing is done until all five steps have literally happened, in order. This
project's failure mode is not a crash. It is a green suite sitting on top of an
unsafe decision: a hospital selected on unknown capacity, one ICU bed reserved
twice, a WebSocket event announcing a reservation that rolled back. The
blind-evaluator gate (CLAUDE.md) runs before this one and never replaces any
step here.

## 1. Tests written and shown

Assert behaviour, not existence. Minimum for whatever the change touches:

| Area | The tests must prove |
|---|---|
| Decision engine | an ineligible candidate is never scored; NULL/unknown ≠ available; same input + config → same output |
| Reservation | two concurrent reserves on one unit → exactly one succeeds; a failed attempt changes no capacity |
| State machines | an invalid transition is rejected (e.g. CREATED → COMPLETED) |
| Realtime | event published only after commit; stale `state_version` write → `MISSION_STATE_CONFLICT` |
| API | wrong role → 403; error envelope shape; idempotent retry returns the original result |
| UI | loading, error, stale and SIMULATED states all render |

Reuse the spec's own cases as test names: Gherkin plan:2817-2879, edge cases
plan:2335-2433, DB-001..006 db:4755-4840, concurrency db:3519-3537.

## 2. Full suite run, real output shown

Until the code scaffold exists (milestone M1) there is no suite. Say so, and
don't claim this step. After that, run everything, not only the new file, from
the project root. Tests use
`smart_ambulance_test`, never the dev or demo database (db:3482). If the repo
defines its own test or lint scripts (`package.json`, `pyproject.toml`), use
those. Until it does, use the commands below: the layout and pnpm come from
tech:5551-5612, and the invocations are the conventional ones.

```powershell
# rtk needs an absolute interpreter path and breaks on the space in "AI conclave".
# The 8.3 short path avoids both (verified 2026-09-13). If $sp still contains a space, 8.3 names are
# disabled on the volume: run the same pytest command without rtk. Read rtk's tee log before diagnosing a failure.
$sp = (New-Object -ComObject Scripting.FileSystemObject).GetFolder($PWD.Path).ShortPath
rtk test "$sp\apps\api\.venv\Scripts\python.exe" -m pytest apps\api\tests -q
& .\apps\api\.venv\Scripts\python.exe -m ruff check apps\api
# Web
pnpm --dir apps/web build                     # runs tsc -b; tsc --noEmit checks nothing on Vite's project-references tsconfig
pnpm --dir apps/web exec vitest run
pnpm --dir apps/web exec playwright test     # golden-path E2E, once it exists
```

Name pre-existing failures as pre-existing. New failures block the gate.

## 3. Safety check — the step that matters here

For each line the change touches, show the evidence (test name or output). For
the rest, write "not affected" explicitly. Silence is not a pass.

- Hard constraints run before scoring on **every** path: match, recalculation, override, voice.
- Unknown or stale capacity is never treated or displayed as confirmed.
- No double booking; no orphaned reservation after rejection, resource loss or cancellation.
- A destination never changes silently: mission event + notification + audit row.
- Recommendations carry reasons, confidence, freshness and algorithm/config versions.
- Overrides require a reason and are audited.
- DEMO MODE / SIMULATED labels are visible wherever the change shows data.
- No business logic in React components or route handlers.

## 4. Definition of Done

Every box from plan:4370 and tech:6754, merged. Tick each or name the gap:
API/backend · database state and migration · validation · authorization ·
backend error handling · UI with loading and error states · realtime (if
applicable) · audit event · tests · demo data and scenario work · failure
scenario works (where applicable) · README/docs updated. Schema or migration
work must also pass the 20-box database DoD (db:6127-6150).

## 5. Live test by the user, then explicit sign-off

Give exact steps: folder, commands, which console and role to log in as, what to
click or trigger in the Demo Console, what they should see if it works, and what
failure looks like. Wait for their report. Then ask:

> "Are you happy with <feature>? Shall I move on to <next build-order step>?"

Only an explicit yes opens the gate. Silence, "probably fine" and your own
confidence do not.

## Milestones

At each milestone M1–M8 (plan:5129) and before any demo rehearsal, also run the
Product Quality Gates (prd:2398-2440): core flow; rejection → reassessment;
traffic or resource event → recalculation; invalid resource → no invalid
recommendation; full scenario with no manual database edits.

## If anything fails

Fix it before asking for sign-off — never ask early. Two failed fixes on the
same bug means the diagnosis is wrong: stop and use `/bug-triage`.
