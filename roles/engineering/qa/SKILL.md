---
name: qa
description: Independent QA of one Alto change from alto_hq — run the task's approved acceptance check yourself, review the diff, confirm findings, write evidence.md with PASS or FAIL. Use after dev hands off, before ship.
---

# qa

Inputs: an `alto_hq` task id and the commit range `<base>..<head>`. The
task folder is `../alto_hq/engineering/tasks/<year>/<task>/`
(conventions: `../alto_hq/README.md`; schema
`../alto_hq/org/schemas/evidence.v1.yaml`). Raw logs and scratch tests go
to `../news_server/verify_data/reports/<task>/`. Never fix code.

## Step 0 — Load, independently

Read `task.md`, `acceptance.md`, `work/qa/notes.md` (in `alto`) and, on
round 2, your own round 1 in `evidence.md`.

- `approvals` must hold `acceptance.md` with the sha256 of the file as it
  is now. If not: stop, report, judge nothing.
- Do **not** read `plan.md` or `handoff.md` until your verdict is written.

## Step 1 — Run the acceptance check yourself

This is the core of QA. Check out `<head>` in your own worktree
(`git worktree add --detach .claude/worktrees/<task>-qa <head>`) and run
every check in `acceptance.md` exactly as written, with your own commands.
Keep each command and its output.

- A check you cannot run as written is a finding, not a pass.
- A check that passes only with a changed command, input or tolerance is a
  failure.
- **Data safety, until T-20261015-0321-checkout-data-root is merged:**
  worktrees resolve the production data root. Run only dry-runs,
  read-only commands and tests that use temp dirs; record any check that
  needs real-data writes as not run, with the reason.

## Step 2 — Review the change

Read `git diff <base>..<head>` and every caller of every changed
function. Do this yourself; use at most two sub-agents, one level deep,
and only for work that would flood your context:

1. **Rules:** fallbacks or silent skips; brittle rules or keyword/regex
   heuristics; complex code; relative imports; shims; data paths outside
   `backend.config.paths` and the stores; user data outside
   `workspace/<userid>/`; tests outside `<feature>/tests/`; attribution
   lines in commits.
2. **Logic:** wrong numbers, off-by-one quarters, lost updates, ordering
   and crash windows (write A then B: what if we die between?).
3. **Scenarios**, only where the diff touches them: two users holding the
   same symbol; concurrent writers on one store; broker timeout, 5xx or a
   duplicate response around an order; a crash between two writes;
   corrupt or missing inputs; on the money path, old vs new weights and
   planned orders on the same input. Write these tests in a temp dir.
4. **Suite:** the full backend suite at `<head>` vs `<base>` (command in
   the `dev` skill, Step 3), built from committed trees; boundary test;
   entry-point imports. Only new failures count.

## Step 3 — Confirm findings

Hand all findings, in one batch, to one verifier sub-agent whose only job
is to disprove each (reproduce it or show why it cannot happen). Keep only
the ones it confirms. Severity: **BLOCK** (can lose money, leak user data,
corrupt stored data, an acceptance check failing or not run, a new test
failure) or **ALERT** (everything else).

## Step 4 — Verdict

Now read `handoff.md` and note anything dev claimed that you could not
confirm. Write `evidence.md` (append `## Round <n>`; update the
frontmatter to this round):

- `qa: pass` only if every acceptance check ran and passed and there is
  no BLOCK; otherwise `fail`.
- `outputs_changed`: `no`/`yes` only if a check compared stored outputs
  before and after; else `unverified`.
- Body: each acceptance check with its command and output; confirmed
  findings (severity, file:line, failure scenario, reproduction); suite
  base vs head; dev claims not confirmed; the check or invariant that
  would catch this class automatically.

Then update `task.md`:

- **PASS:** `status: awaiting_owner`, `waiting_on: "review evidence.md and
  approve the merge"`.
- **FAIL on round 1:** `status: ready` (back to dev; a failed QA round
  counts as one of dev's two attempts).
- **FAIL on round 2:** `status: needs_owner` with `waiting_on:`.

Commit only the task folder in `alto_hq` (`QA: <task> round <n> <verdict>`,
no attribution). Add to `work/qa/notes.md` only a bug class or scenario
this run proved, with file:line. Do not edit this skill or your agent
definition; propose a change in the evidence body.
