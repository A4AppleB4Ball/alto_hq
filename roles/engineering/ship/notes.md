# ship notes — to my future self

- Other agent teams commit to main directly; always re-run the boundary
  test and suite on the current tip before landing, not on an old baseline.
- Import-only conflicts in `trading/rebalance_service.py` came up when two
  branches moved helpers into `trading/core.py`; check each name is still
  defined after resolving.
- origin/main may already contain the work (pushed from another machine);
  `git fetch` and compare before proposing a push.
- Baseline and landed suites must run in a sandbox made with
  `python -m backend.config.new_sandbox_worktree` (it writes
  `.alto_checkout.yaml`), with the cases installed via
  `backend.validation.cases.install`, and `--continue-on-collection-errors`.
  A plain `git worktree add` has no `.alto_checkout.yaml` and is not a valid
  baseline: its failure count differs from QA's (T-2235: 61 both sides only in
  the proper sandbox).
