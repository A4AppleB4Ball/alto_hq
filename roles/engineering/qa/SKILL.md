---
name: qa
description: Independent end-to-end QA of an Alto change given a task statement and a commit range. Launches reviewer, tester and adversarial-verifier sub-agents, and returns PASS or confirmed findings. Use after dev hands off, before ship.
---

# qa

Inputs: the task id and a commit range `<base>..<head>`. The written
record goes to `work/tasks/<task>/` (see `work/README.md`); raw logs and
scratch tests to `../news_server/verify_data/reports/<task>/`. Do not fix code.

## Step 0 — Load memory

Read `work/decisions.md`, `work/qa/notes.md` and `work/tasks/<task>/task.md`.
On a re-round, also read your own earlier sections of `qa.md`. Do **not**
read `impact.md`, `handoff.md` or `thread.md` yet.

## Step 1 — Understand the change yourself

Read `git diff <base>..<head>` and the task. Write your own impact list:
touched stores, money path yes/no, user isolation yes/no, entry points.
Do not read the dev hand-off yet.

## Step 2 — Launch independent sub-agents (in parallel)

You are the lead: launch sub-agents for the real work, and add ad-hoc ones
whenever something needs a closer look. Any sub-agent may launch its own
sub-agents (for example the scenario tester, one per scenario), passing the
rules and independence on. Each gets the task, the commit range, the
relevant bug classes from `work/qa/`, and only its own brief. The five
below are the minimum, not the limit:

1. **Rules reviewer** — checks the diff against repo CLAUDE.md and the
   global rules: fallbacks or silent skips, brittle rules or keyword/regex
   heuristics, overly complex code, relative imports, shims, data
   paths outside `backend.config.paths`/stores, user data outside
   `workspace/<userid>/`, missing tests in `<feature>/tests/`.
2. **Logic reviewer** — reads the changed code and every caller; looks for
   wrong numbers, off-by-one quarters, lost updates, ordering and crash
   windows (write A then B: what if we die between?).
3. **Suite runner** — full backend suite at `<head>` vs `<base>` (command
   in the `dev` skill, Gate 4); boundary test; entry-point imports.
   Reports new-only failures.
4. **Scenario tester** — writes and runs its own tests in a temp dir,
   outside the repo's test folders, acting like a user and an adversary:
   - two users with the same symbol never see each other's data
   - concurrent processes on the same store (no lost updates)
   - broker timeout / 5xx / duplicate response around order placement
   - crash between two writes; corrupt or missing input files
   - money path: old vs new target weights / planned orders on the same input
5. **Replay runner** (only once `50_verification.md` Phase 1 exists) —
   real entry points against the verify data root with the fake broker;
   run the rules in `backend/invariants/`; compare with production.

## Step 3 — Adversarial verification

For each finding, launch a separate verifier whose only job is to
disprove it (reproduce or show why it cannot happen). Keep only findings
it confirms. Severity: **BLOCK** (can lose money, leak user data, corrupt
stored data, new test failure) or **ALERT** (everything else).

## Step 4 — Verdict

Now read `handoff.md` and `thread.md` and note anything dev claimed that
you could not confirm. On a re-round, judge each dev reply in `thread.md`
(fixed → re-test it; disputed → accept or reopen with evidence). Append a
`## Round N` section to `work/tasks/<task>/qa.md`:

- verdict: **PASS** (no BLOCK) or **FAIL**
- confirmed findings: severity, file:line, failure scenario, reproduction
- suite: base vs head counts, new-only failures
- dev claims not confirmed
- suggested rule/journey to add so this class is caught automatically

Then write the memory (commit only files under `work/`, message
`QA: <task> round N <verdict>`, no attribution):
- `thread.md` — one entry per open finding, for dev to answer.
- `task.md` — `status: ready-to-ship` or `qa-failed`, a log line.
- Real bugs outside this change → new `work/tasks/<id>/task.md`.
- `work/qa/` — tend your space (`work/README.md`, "Role spaces"): new bug
  classes, scenarios that found something (keep them reusable), checks
  worth automating; drop what never pays off; improve this skill.

On FAIL the findings go back to dev (max 2 rounds), then to the user.
On PASS the next step is `/ship`.
