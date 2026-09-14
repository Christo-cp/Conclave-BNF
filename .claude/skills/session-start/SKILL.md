---
name: session-start
description: Use when starting any Smart Ambulance work session — when asked to "resume", "continue", "pick up where we left off", or when the project is opened without context — before reading specs or writing code.
---

# Session Start (Smart Ambulance)

Get ready to build without opening the six specs. In a 48-hour build, status
notes go stale within hours, so verify them before trusting them.

## Steps

1. **Read only what exists, in this order:**
   - `STATUS.md`
   - the newest file in `handoffs/`
   - the headings of `docs/implementation-decisions.md` and `docs/spec-conflicts.md`

   If none exist, say "no status yet — first session" and go to step 4.

2. **Verify against reality, reading summaries rather than full output:**
   - `rtk git status` and `git log --oneline -10`, if it is a repo.
   - `robocopy .claude\skills skills /MIR /L /NJH /NJS /NDL /NP` is a dry run.
     Any file it lists means the `skills/` mirror has drifted, so re-mirror
     (command in CLAUDE.md).
   - Run the test suite only if there are commits or uncommitted changes since
     the newest handoff; otherwise trust its recorded counts. When you do run it,
     use the zero-error-gate commands — `rtk` returns only the pass/fail summary.
   - Grep only for the files and functions of the item you are about to resume.

3. **Report drift in plain words.** Write "STATUS says X, repo shows Y" for each
   mismatch, or "status verified, no drift". Include test counts and name any
   known failures.

4. **Place the work.** Name the current build-order step and milestone
   (plan:4665-4692; milestones plan:5129-5174), and say whether the first vertical slice runs end
   to end yet.

5. **Confirm direction.** Offer the next three items and ask which to start.
   Don't assume the top item is still what the user wants today. If an item
   crosses a conflict marked DECIDE in `spec-lookup/references/conflicts.md`,
   put that decision to the user in the same message.
