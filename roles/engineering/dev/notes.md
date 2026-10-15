# dev notes — to my future self and other devs

Read this at Step 0. Product facts go in the product's docs (`backend/docs/40_contracts.md` covers the boundary test; `backend/stance/docs/architecture.md` covers shared stances vs per-user triggers), not here. Keep it curated: fix or delete entries that go stale.

## Running things
- Run the suite from `backend/` (command in the `dev` skill, Step 3). The
  sandbox blocks reading `.env` at the repo root, hence the dummy env vars.
- A worktree outside the repo cannot resolve the data root; keep worktrees
  under `.claude/worktrees/`. For the main baseline, a checkout of `main`
  in place also works.
- main has a set of pre-existing failures (≈46–72 depending on the branch,
  2026-10-11). Always compare against main; never read the raw count.
- **Build the baseline from a committed tree, not the working tree.** Round 2
  of the stance/TWAP work first diffed against a clean `main` worktree while
  the tree under test carried *other people's* uncommitted work
  (`config/machine.py`, `paths.py`, `work/*`), so `comm -23` reported their
  edits as mine. Commit your own work first, then
  `git worktree add --detach .claude/worktrees/<name> HEAD~<n>`. If the
  worktree errors with "dubious ownership", add it to
  `git config --global --add safe.directory`.
- The sandbox runs as **root**. Any test that makes a file unreadable with
  `chmod` silently tests nothing (root ignores permission bits). Inject the
  failure into the reader instead. Caught in `config/tests/test_machine.py`.

- Live Dhan data: `python -m backend.executor.dhan_client_cli funds`
  (repo CLAUDE.md, "Live broker data"). It works inside the sandbox: an
  unreadable `.env` resolves to the local machine (2026-10-11). Don't
  hunt for tokens or read `.env`.

## Codebase traps
- **Never assert on `mock.call_args` when a collaborator is built more than
  once.** `process_work_item` builds `TriggerQueue` twice (production, then
  custom-trigger), so `call_args` is the *last* call and the test passed
  while checking the wrong object. Assert on the built object's own state.
- A predicate used as a **guard** and as a **question** is two predicates.
  `has_unresolved_placement` was widened for finding 4 of the TWAP task,
  which made it block the cancel it exists to permit; split into it and
  `has_uncancellable_placement`.
- **Separate "derived artifact" from "delivery mechanism" before making
  anything per-user.** Round 2 made the stance *ledger* per user because the
  stance *trigger queue* had to be: QA's finding was about the queue, and
  generalising it to the ledger was wrong. A derived artifact is a function of
  shared inputs and carries no user state, so per-user means N identical
  computations and N copies. A delivery mechanism (a queue folder, a
  credential, a mailbox) has an addressee and must be where that addressee
  reads. Ask which one you are looking at.
- Moving a module breaks importers silently until import time; import
  every changed module before handing off.
- Executor tests build a Dhan client by hand; when the client gains a
  required map (e.g. `set_lot_map`), test setup must add it.
