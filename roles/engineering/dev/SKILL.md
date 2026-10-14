---
name: dev
description: The gated procedure for any code change to Alto — impact map, design, implement in worktrees with sub-agents, self-check against main, hand-off. Use whenever implementing a feature or fix.
---

# dev

Do the gates in order. Do not start a gate before the previous one is done.
`<task>` below is the task id; its folder is `work/tasks/<task>/` (see
`work/README.md`). Raw logs go to `../news_server/verify_data/runs/<task>/`.

## Gate 0 — Load memory

Read `work/decisions.md`, `work/dev/notes.md`, and `work/tasks/<task>/`
(`task.md`, plus `qa.md` and `thread.md` if this is a re-round). If the
task has no folder, create `task.md` from the user's request. Set
`status: in-dev` and `owner:`, and add a log line.

On a re-round, answer every open QA finding in `thread.md`: fixed (commit),
disputed (evidence), or deferred (new task id). Never silently skip one.

## Gate 1 — Impact map (before any code)

Write `work/tasks/<task>/impact.md`:

- **Touches:** files, stores (`backend/stores/<feature>/`), pipelines,
  entry points (intake.runner, stance.runner, e2e.run, workflow.cli,
  execution.runner, raw.master_pipeline, backtest.replay, the API).
- **Callers:** grep every caller of every function whose behaviour changes.
  A change to a shared function is a change to all its callers.
- **Who is affected:** which users/accounts, live orders, positions,
  on-disk formats. Does any user data leave `workspace/<userid>/`?
- **Money path?** Does it touch target weights (`backend/trading/core.py`),
  planning, order placement, reconcile, fills? If yes, every change needs
  a test that pins old vs new numbers.
- **Ownership:** which sub-agent owns which files. One owner per file.

## Gate 2 — Design

Append to `impact.md`: what changes, what explicitly stays the same, and
**behaviour changes the user will notice** (new errors, stopped jobs,
changed numbers). Prefer the smallest change. No fallbacks — anything
that would "default" must raise instead.

## Gate 3 — Implement

- You are the lead: you plan, split, integrate and judge. Hand the actual
  work to sub-agents, including ad-hoc work that comes up mid-task
  (investigating a caller, a data scan, a flaky test, a design spike) —
  spawn one for it rather than doing it yourself.
- Independent pieces → one sub-agent each, in its own worktree
  (`isolation: "worktree"`). Dependent pieces → sequential.
- A sub-agent may split its piece further and launch its own sub-agents,
  as deep as the work needs. Each level passes the full rules on and
  reports up. If a sub-agent cannot launch agents, it does the work itself
  or reports back the split for you to launch.
- Every sub-agent brief contains: the task, its owned files, the rules
  (raise don't fallback, no brittle rules or keyword/regex heuristics,
  modular code, absolute imports, paths via `backend.config.paths`
  and stores, per-user data only, no real-data writes, tests in
  `<feature>/tests/`, no attribution lines), and "report what you did not do".
- Every bug fix ships with the test that fails before and passes after.
  Where a rule in `backend/invariants/` fits, add the rule too.

## Gate 4 — Self-check

Run from `backend/` (the sandbox blocks pytest from scanning the repo root):

```bash
cd backend && PYTHONPATH=.. SESSION_SECRET=x ALLOWED_EMAILS=a@b.c \
  GOOGLE_CLIENT_ID=x GOOGLE_CLIENT_SECRET=x GOOGLE_REDIRECT_URI=http://x \
  python -m pytest -q -p no:cacheprovider --rootdir=. . \
  | grep -E '^(FAILED|ERROR)' | sed 's/ - .*//' | sort > $TMPDIR/<task>.new
```

Run the same on `main` (a fresh worktree under `.claude/worktrees/`) into
`$TMPDIR/<task>.base`, then `comm -23 new base`. Required:

- No failure that is new versus main. A test that moved files counts as
  the same test.
- `stores/tests/test_boundaries.py` passes; KNOWN_VIOLATIONS only shrank.
- Every entry point above imports (`python -c "import backend.x.y"`).
- Rebased onto current `main` with conflicts resolved.

Then launch at least one **independent verifier** sub-agent per piece:
it gets the diff and the task only, and tries to break the change.
Fix what it confirms; re-verify.

## Gate 5 — Hand-off

One local commit per item, message `<Area>: <what changed>`, no
Co-Authored-By or Claude attribution. Never push.

Write the memory before reporting (commit it with the work):
- `work/tasks/<task>/handoff.md` — the report below.
- `task.md` — `status: in-qa`, a log line with the commit range.
- Anything found outside the task → a new `work/tasks/<id>/task.md`
  (`status: open`); product ideas → `backend/docs/25_future_ideas.md`.
- `work/dev/` — tend your space (`work/README.md`, "Role spaces"): what a
  future dev must know that the code does not say; fix what proved wrong;
  improve this skill if a step proved wrong or missing.

Report:

- branch, commit hashes, base commit
- per item: what changed, its test(s), verifier result
- suite: base vs new counts, new-only failures (must be none)
- behaviour changes the user must know before deploy
- deferred / not done, with file:line

Next step for the user: `/qa` on the commit range.
