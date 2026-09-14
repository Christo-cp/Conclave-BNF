---
name: handoff
description: Use when a Smart Ambulance work session is ending — "write the handoff", "wrap up", "save where we are", "end of session" — or when context is about to run out in the middle of a task.
---

# Handoff (Smart Ambulance)

The next session starts from this document instead of re-reading specs and code,
so a good handoff is the biggest token saving in the project. Audit reality
first; never write state from memory.

## Steps

1. **Audit.**
   - Test counts: if code changed after this session's last gate run, run the
     suite with the zero-error-gate commands; otherwise reuse that run's counts.
     Name each failure as new or pre-existing.
   - Check `git log --oneline` since the last handoff and `git status` for
     uncommitted work.
   - Say whether the golden path runs end to end, or exactly where it stops.

2. **Write four buckets.**
   - **Signed off.** Only items where zero-error-gate step 5 actually happened.
     Tests passing is not sign-off.
   - **Built, not live-tested.** Include what the live test must show on screen.
   - **Open questions.** Conflict IDs touched, decisions made (with where they
     are recorded), and "check X before guessing" warnings.
   - **Backlog.** Carry forward every unresolved item from the previous
     handoff. If an item was deliberately closed, say so; never drop one silently.

3. **Position.** Current build-order step, milestone, and the next three items.

4. **Files touched.** One line each: what changed and why.

5. **Feed the skills.**
   - A new bug shape → add it to `bug-triage/references/bug-catalog.md` Part C.
   - A new spec disagreement → add a row to `spec-lookup/references/conflicts.md`;
     a resolved one → mark it RESOLVED.
   - List these edits here, then re-mirror `skills/` (command in CLAUDE.md).

6. **Save.** Write `handoffs/AMB_HANDOFF_<YYYY-MM-DD>.md`, adding `_2`, `_3`
   for later handoffs the same day. Name the handoff it supersedes, and never
   delete old ones. Rewrite `STATUS.md` in the same pass (≤ 60 lines: working /
   in progress / next / known failures) so the two never disagree.

## Content rules

- Target ≤ 150 lines. Specific beats complete.
- No invented numbers: unmeasured performance is a target, and is labelled as one.
- Say what is simulated or mocked.
- Admit uncertainty out loud rather than sounding finished.
