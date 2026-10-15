# ship notes — to my future self

- Other agent teams commit to main directly; always re-run the boundary
  test and suite on the current tip before landing, not on an old baseline.
- Import-only conflicts in `trading/rebalance_service.py` came up when two
  branches moved helpers into `trading/core.py`; check each name is still
  defined after resolving.
- origin/main may already contain the work (pushed from another machine);
  `git fetch` and compare before proposing a push.
