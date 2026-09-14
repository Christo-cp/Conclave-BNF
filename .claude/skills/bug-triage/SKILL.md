---
name: bug-triage
description: Use when anything in the Smart Ambulance project breaks or looks wrong — a failing test, an empty or odd ranking, the wrong ambulance or hospital chosen, markers in the wrong place, a reservation that double-books or never releases, a dashboard that stops updating, or "it's not working" — BEFORE proposing a fix, and before any second fix attempt on the same bug.
---

# Bug Triage (Smart Ambulance)

Coordination bugs rarely crash. The ranking renders, the reservation row exists,
the event fires — and the decision is wrong or unsafe. Never guess. Gather
evidence first, and never attempt a third blind fix.

## Protocol

**1. Capture the exact symptom.** The request or scenario, what appeared, what
should have appeared (cite the golden-path step, tech:2120-2178, when one
applies). From the user's machine, get the verbatim error and its `request_id`.

**2. Match the known shapes first.** Read `references/bug-catalog.md`. The
matching shape tells you which evidence to collect.

**3. Gather evidence before hypothesising.**
- Wrong decision → the stored `decision_runs.input_snapshot` and
  `decision_candidates` rows (eligible, exclusion_reason, feature_values, rank)
  for that run. Never re-run against today's data and call it the same decision.
- Capacity or reservation → the `hospital_resources`, `reservations` and
  `resource_events` rows, plus the integrity checks: negative capacity, invalid
  active reservations, orphans (db:3906-3939).
- Realtime → log order of COMMIT vs publish; `event_id`, `entity_version` and
  `state_version` as seen by the client.
- Map or distance → raw coordinates at every boundary (request, `ST_AsText`,
  map layer) and the column type (geometry vs geography).
- Routing or prediction → `provider`, `fallback_used` and `model_version` on the row.
- Green tests, broken app → what does the test stub that reality doesn't?
  Mock routing, synthetic hospital provider, in-process TestClient WebSocket,
  a non-PostGIS database?

For anything non-trivial, spawn an investigation agent to read the real code
path end to end rather than skimming.

**4. Isolate and confirm.** Find the value, row or line that flips with the
hypothesis. Only then propose the fix, stated as cause → fix → the regression
test that proves it.

**5. Fix, add the regression test, then run `/zero-error-gate`.**

**6. Two-strike rule.** Two failed fixes on the same bug means the diagnosis is
wrong. Restart from step 1 as if the bug were new, and say so plainly.

## Honesty rules

- Say "confirmed cause" or "most likely candidate" — never blur them.
- If the evidence needs the user's machine, state exactly what to run and what
  its output will settle. Do not fix ahead of the evidence.
- If the bug comes from two specs disagreeing, stop and surface the conflict ID
  from `spec-lookup/references/conflicts.md` — do not pick a side silently.
- A genuinely new shape goes into the bug catalog (Part C) and into the handoff.
