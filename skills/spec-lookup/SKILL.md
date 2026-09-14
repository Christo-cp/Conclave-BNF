---
name: spec-lookup
description: Use when a Smart Ambulance task needs anything from prd.md, plan.md, appflow.md, design.md, database.md or techspec.md — a rule, formula, enum, endpoint, table, state machine, design token, checklist, demo step or judge-facing claim — and before opening any of those files.
---

# Spec Lookup (Smart Ambulance)

The six specs total ~450 KB (~115k tokens). Search-and-slice is what keeps
lookups cheap. Pre-built digests don't: agents given the facts sheet and topic
index in `docs/spec-digest/` spent 10–12% more tokens than agents that only
searched. Don't open that folder for lookups.

## Method

1. **Grep before reading.** Search the one or two specs likely to hold the
   keyword (`output_mode: content`, `-n`). For a feature that spans docs, Grep
   all six at once with a glob to see which ones discuss it.
2. **Read slices, never files.** Use `offset=<hit − 10> limit=60`, and read
   another slice only if the section continues. Never Read a spec without
   `offset` and `limit`.
3. **Stop when answered.** For a build brief, stop once every doc that matched
   has been sliced.
4. **Cite `file:line`** for every spec fact you act on. Prefixes: `prd`, `plan`,
   `flow` (appflow), `db` (database), `tech` (techspec), `design`.

## Where to search first

| Need | Spec |
|---|---|
| Business rules (BR-001..015), user stories, acceptance criteria | prd.md |
| Build order, phases, milestones, demo scenario, judge-facing claims | plan.md |
| Screens, user flows, UI states, error and empty states | appflow.md |
| Colours, typography, layout, components, UI copy | design.md |
| Tables, enums, constraints, transactions, state machines, seed data | database.md |
| Stack, API, algorithms, tests, env vars, non-negotiable rules | techspec.md |

## Conflicts and decisions

`references/conflicts.md` is the register of the 34 places the specs disagree.
Each row gives the precedence default, and **DECIDE** marks the rows that are
the user's call.
- Before implementing any enum, state machine, name, env var, score or ID
  format, Grep the register for it.
- Ask the user before coding across a DECIDE row.
- When a new disagreement turns up, add a row.

Precedence (tech:347-394): safety › prd › techspec › database › plan › appflow ›
design. If a conflict is immaterial, take the least complex compatible reading.
Record each decision in `docs/spec-conflicts.md` and mark the row RESOLVED.

## Trap

techspec.md holds two documents: lines 1–2533 are a pasted master prompt and
2534–7075 are the spec. Section numbers repeat across the two, so cite lines,
never "§49".
