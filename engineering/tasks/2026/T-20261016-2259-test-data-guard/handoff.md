# Handoff: test-data-guard (attempt 1)

Branch `eng/T-20261016-2259-test-data-guard` (worktree
/Users/kmrh581/personal/projects/workspace/alto/.claude/worktrees/test-data-guard), base 35e1342.
Commits: e5b664d (test mode, guard, backend/conftest.py, tests), 79bdab3 (test reads stances root via CompanyStore; fixes boundary test).

## Change
- `backend/config/checkout.py`: mode `test` (no data_root needed); `activate_test_mode(root)`, `active_test_root()`, `LiveRootAccessError`, `refuse_live_path`. While active, `load_checkout` returns mode test with the temp root; the declared live root is kept for the guard.
- `backend/config/paths.py`: test mode treated like sandbox for WORKSPACE_ROOT; `refuse_live_write(path)`.
- `backend/stores/locking.py`: exclusive_lock, atomic_write_text, append_line_durable call `refuse_live_write` (every store write goes through these).
- `backend/conftest.py` (new): makes a temp root, activates test mode before any test imports paths, removes the root at session end.
- Tests: `backend/config/tests/test_test_mode.py`; `conftest.py` there with fixture `outside_test_mode`, used by test_checkout.py and test_new_sandbox_worktree.py (they test declarations as live/sandbox).

## Acceptance
1. Mode: `test_roots_are_under_the_temp_root`, `test_declaring_test_mode_in_the_file_is_accepted` pass.
2. Guard: `test_store_write_under_live_root_raises_naming_the_path` (CompanyStore(live/...).append_stance raises LiveRootAccessError naming the path) passes.
3. ACME class: NOT shown as written. I may not write production, and the check needs base to run on the live root. Substitute: base run in a sandbox worktree. The named test file (2 tests) raises `_QueueReached` before `write_decision_ledger` and wrote nothing even on base-in-sandbox, so it does not itself reproduce the ACME files (the live ACME decisions.jsonl mtime 16 Oct 22:17 predates my runs). At head, same file: nothing created in the sandbox or live (`find -newer marker`). Owner/QA should run the base half on a quiet main if wanted.
4. Full suite with markers: base-in-sandbox wrote 5 files into its sandbox root (workspace/backtest/system/dhan_instruments.json, workspace/u_test/strategy/config.json, dashboard/chat/*.duckdb x2, screener_data/raw_reports/.../HDFCBANK_page_*.html), i.e. tests do write the data root. Head: nothing in its sandbox, nothing in the live root (`find news_server -newer marker`: empty), temp root removed. Failures: base 100 failed + 8 errors; head 101 failed (after fixing, the only extra was test_boundaries on my own test, fixed in 79bdab3; rerun of config/tests + stores/tests: 66 passed). I did not rerun the whole suite after 79bdab3; `comm -23` before the fix listed only that one line.
5. Boundary test passes (in the 66). Imports OK: intake.runner, stance.runner, e2e.run, workflow.cli, execution.runner, raw.master_pipeline, backtest.replay, api.main_cockpit, api.app_factory.

## Notes for the owner
- Tests that hardcoded live/sandbox expectations of the checkout now need the `outside_test_mode` fixture.
- Tests that wrote to the data root (list above) now write to the temp root; any test that relied on real live data being present (e.g. screener_data, index files) now sees an empty root, possibly causing different failures than base; the failure sets matched except the one fixed line.
- Run needs no `<data_root>/data/alto_data` any more under pytest (conftest creates it).

## Not done
- Acceptance 3 base half on live root (above); final full-suite rerun after 79bdab3.

## Found
`api/services/tests/test_rebalance_price_action_cooldown.py` cannot be the writer of ACME decisions in its current form (raises before the ledger). Writer is another test reaching `rebalance_service.py:1012`; head makes that harmless.
