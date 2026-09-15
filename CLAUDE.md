# Smart Ambulance Routing & Emergency Bed Allocation — project instructions

Hackathon prototype: real-time coordination of ambulance selection, routing,
hospital acceptance and transactional resource reservation. The implemented
surface is S0-S15 with a FastAPI/PostGIS backend and React/Vite frontend.

## The specs — never read one end to end

`prd.md` `plan.md` `appflow.md` `design.md` `database.md` `techspec.md` total
~450 KB (~115k tokens). Grep for the keyword, then Read slices of ≤80 lines
with `offset` and `limit`. On identical questions that cut an agent's cost from
170k to 73k tokens. `/spec-lookup` has the method, where to
search first, and the conflicts register.

## Two mandatory gates — both, in this order

### 1. Blind-evaluator quality gate — runs first

Before showing any substantial deliverable, run the protocol in
`prompts/Quality_Gate_Blind_Evaluator.md` **in full**. Read that file — do not
work from this paragraph.

Scope: code, scripts, migrations, schemas, specs, plans, docs, prompts, test
suites, refactors, or any multi-part answer meant to be used as-is. Not
conversation, quick answers, status updates or one-line fixes. If it is unclear
which side something falls on, gate it.

**The pass mark is deliberately not repeated here** — subagents inherit this
file, and an evaluator that knows the target is no longer blind. Never write it
into this file, a memory, a skill, or the prompt you hand the evaluator.

Every evaluation needs a genuinely fresh reader: spawn a new subagent with
`subagent_type: blind-evaluator` (`.claude/agents/blind-evaluator.md`) and pass
it the locked brief and the complete artifact — nothing else. The isolation
rules are in the protocol file.

End every gated delivery with the score line. **Never fabricate a score. Never
simulate the evaluator in your own head and call it independent.** "gate this"
forces the gate on; "skip the gate" opts out.

### 2. Zero-error gate — runs second

Use `/zero-error-gate`. Nothing is done until the user has live-tested it and
explicitly signed off. A green suite is not sign-off.

## Standing rules

- Follow the spec build order (plan:4665-4692) and get the first vertical slice
  working end to end before anything else (plan:4696-4716).
- Two failed fixes on the same bug → stop guessing, use `/bug-triage`.
- Evidence before assertion: never claim a test passes, a file exists or a
  feature works without running the command and reading the output this session.
- The specs' non-negotiable rules (tech:6946-6972, flow:3974-3987,
  prd:1128-1216) are constraints, not trade-offs.
- No invented numbers in code, UI copy, README or pitch — unmeasured means
  target. Simulated data is always labelled as simulated.

## Skills (`.claude/skills/`)

| Skill | Use when |
|---|---|
| `/session-start` | First thing every session, before reading specs or writing code |
| `/spec-lookup` | Any question the specs answer — before opening a spec |
| `/zero-error-gate` | About to call anything done, or to move to the next step |
| `/bug-triage` | Anything breaks or looks wrong; before a second fix attempt |
| `/handoff` | End of session, or context running out mid-task |

`docs/spec-digest/` holds a cited digest of the specs for people: a facts sheet,
a topic index and design tokens. Agents given it spent 10–12% more tokens than
agents that just searched and sliced, so no skill loads it.

`skills/` in the project root is an upload mirror; Claude Code loads only
`.claude/skills/`. Edit `.claude/skills/`, then re-mirror (robocopy exit codes
0–3 mean success):

```powershell
robocopy .claude\skills skills /MIR
```
