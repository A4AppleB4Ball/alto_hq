---
name: dev
description: The procedure for one code change to Alto — start from an approved task in alto_hq, map and design in one page, implement in one worktree, prove the acceptance check, stop after two failed attempts, hand off. Use whenever implementing a feature or fix.
---

# dev

`<task>` is an `alto_hq` task id. Its folder is
`../alto_hq/engineering/tasks/<year>/<task>/` (conventions:
`../alto_hq/README.md`, schema `../alto_hq/org/schemas/task.v1.yaml`).

## Step 0 — Check the task is ready (stop if not)

Read `task.md` and `acceptance.md`.

- `status` must be `ready`, and `approvals` must hold `acceptance.md` with
  the sha256 of the file as it is now (`shasum -a 256 acceptance.md`).
- If there is no task folder, the status is not `ready`, or the hash
  differs: stop and report. Never write or rewrite the acceptance check
  yourself; propose a change to it in your report instead.

Claim it: set `status: in_progress`, `claimed_by: <run id>`,
`lease_until:` (now + 1 day). Read `work/decisions.md` and
`work/dev/notes.md` in `alto` once.

**Round 2.** If `evidence.md` exists, QA failed round 1 and this is your
second and last attempt. Answer every confirmed finding in `handoff.md`:
fixed (commit), or disputed (evidence). Never silently skip one.

## Step 1 — Map and design: one page, before code

Write `plan.md` in the task folder, at most one page:

- **Touches:** files, stores, entry points (intake.runner, stance.runner,
  e2e.run, workflow.cli, execution.runner, raw.master_pipeline,
  backtest.replay, the API). Grep every caller of every function whose
  behaviour changes.
- **Money path?** Target weights, planning, order placement, reconcile,
  fills. If yes, every change gets a test pinning old vs new numbers.
- **Change:** what changes, what explicitly stays the same, and behaviour
  the owner will notice.
- **How each acceptance check will be run**, command by command.

If the map shows the change is a different `kind` than `task.md` declares,
or bigger than about a day: stop, set `status: needs_owner`, say why.

## Step 2 — Implement in one worktree, yourself

- One branch, `eng/<task>`, one worktree under `.claude/worktrees/`. Do the
  work yourself.
- Use a sub-agent only for (a) a read-only search that would flood your
  context, or (b) a genuinely independent piece of more than half a day.
  One level only: sub-agents do not launch sub-agents. Every brief carries
  the rules below.
- Rules: raise, never fall back or silently skip; no brittle rules or
  keyword/regex heuristics; modular code; absolute imports, no shims; data
  paths only through `backend.config.paths` and `backend/stores/`; user
  data only under `workspace/<userid>/`; tests in `<feature>/tests/`.
- **Data safety, until T-20261015-0321-checkout-data-root is merged:**
  worktrees resolve the production data root (the
  `.claude/worktrees/news_server` symlink). Run nothing that writes data
  from a worktree: only `--dry-run`, read-only commands and tests that use
  temp dirs.
- Every bug fix ships with the test that fails before and passes after.

## Step 3 — Prove it

Run, in this order, and keep the outputs:

1. **The acceptance check**, exactly as `acceptance.md` states it. This is
   the proof; tests are not a substitute for it.
2. **Targeted tests** of the touched features (`<feature>/tests/`).
3. **The full suite once, at the end**, against a baseline of the base
   commit. Build the baseline from a committed tree
   (`git worktree add --detach .claude/worktrees/<task>-base <base>`), run
   from `backend/`:

   ```bash
   cd backend && PYTHONPATH=.. SESSION_SECRET=x ALLOWED_EMAILS=a@b.c \
     GOOGLE_CLIENT_ID=x GOOGLE_CLIENT_SECRET=x GOOGLE_REDIRECT_URI=http://x \
     python -m pytest -q -p no:cacheprovider --rootdir=. . \
     | grep -E '^(FAILED|ERROR)' | sed 's/ - .*//' | sort > $TMPDIR/<task>.new
   ```

   Same into `$TMPDIR/<task>.base`; `comm -23 new base` must be empty.
   `stores/tests/test_boundaries.py` passes; every entry point imports.

No separate verifier sub-agents: QA is the independent check.

## Stop rule

A task gets two attempts in all. An **attempt** ends when a check in
Step 3 fails and you cannot see why from its output, or when QA fails a
round. Write `attempts/<n>/diagnosis.md`: what you tried, what failed
(the output), what you now believe the cause is. After the second
attempt, set `status: needs_owner` with `waiting_on:` and stop. Do not
start a third attempt, and do not loosen a check to make it pass.

## Step 4 — Hand off

- One local commit per item on `eng/<task>`, message `<Area>: <what
  changed>`, no Co-Authored-By or Claude attribution. Never push, never
  merge.
- Write `handoff.md` in the task folder: branch, base and commit hashes;
  each acceptance check with its command and output; targeted tests; suite
  base vs new; behaviour changes the owner must know; what was not done,
  with file:line.
- `task.md`: keep `status: in_progress`, clear `claimed_by`, add a
  `friction:` line if the process or a template got in the way.
- Found something outside the task: a one-paragraph note under "Found" in
  `handoff.md`. Do not open or start other work.
- `work/dev/notes.md`: add a fact only if this run proved it (with
  file:line or a commit); fix an entry this run proved wrong. Do not
  reorganise it.

Do not edit this skill or your agent definition. Propose a change in
`handoff.md`; the owner versions roles in `../alto_hq/roles/`.

Next step for the owner: QA on the commit range.
