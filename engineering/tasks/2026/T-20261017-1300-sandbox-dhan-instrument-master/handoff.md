# Handoff — T-20261017-1300 (attempt 1)

Branch `eng/T-20261017-1300-sandbox-dhan-instrument-master`, worktree `alto/.claude/worktrees/T-20261017-1300-sandbox-dhan-instrument-master`. Base 909272f. Commits 909272f..4ad96b4:
- cac0e31 Executor: `load_stored(as_of: date)` (no default); raises on missing `date` or `date < as_of` (message: path, stored date, as_of). Shared contract `backend/executor/instrument_master/contract.py` (file path under a data root, six keys + date).
- aa285b1 Executor: `daily_series._stored_exchange_of(user_id, end)` passes `as_of=date(end)`; the closure keeps its own loaded flag (fixes T-2336 A1, no `mapper._loaded`). Existing test fixture `_store_master` in test_sandbox_shared_cache.py re-dated 2026-01-01 -> 2026-10-16 (it read through 2026-10-06; the old date only passed because any date was accepted).
- 4ad96b4 Config: `seed_instrument_master`, `check_live_instrument_master` pre-check before the worktree, `create(..., seed_masters=())`, `--seed-instrument-master` (repeatable), `main_checkout_root()` split out so a test can drive `main()`.

All runs with HTTP(S)_PROXY=http://127.0.0.1:9.

| Check | How | Result |
|---|---|---|
| 1 | config/tests/test_new_sandbox_worktree.py::test_seed_instrument_master_copies_bytes_and_leaves_live_untouched (requests.get, _fetch_and_cache patched to raise) | pass |
| 2 | ::test_create_raises_before_the_worktree_when_the_live_master_is_missing, ::test_create_raises_naming_path_and_missing_key[date + 6 keys] | pass |
| 3 | `python -m backend.config.new_sandbox_worktree --help` lists `--seed-instrument-master USER_ID`; ::test_cli_lists_the_flag, ::test_cli_seeds_the_master | pass |
| 4 | executor/tests/test_dhan_instruments_load_stored.py (5 tests) | pass |
| 5 | executor/broker_factory/tests/test_sandbox_instrument_master.py (3 tests); `git grep -n "load_stored()" -- backend/executor` empty (rc 1) | pass |
| 6 | same tests with socket.socket.connect patched to raise | pass |
| 7 | see below | pass, with deviation |
| 8 | full suite new vs detached sandbox base at 909272f: both 98 failed / 8 errors (107 lines each), `comm -23` empty; new 1717 passed vs base 1698. test_boundaries and test_new_sandbox_worktree not in failures. Imports ok: main_cockpit, app_factory, e2e.lanes, trading.harness, new_sandbox_worktree | pass |
| 9 | no Dhan/NSE/LLM call; dead proxy throughout | held |

Check 7: the CLI resolves its main root from its own file and must run from the live main, which does not have this code yet. So I ran, from the branch worktree, `create(Path(<main>), 'T1300-qa', <branch>, 'eng/T1300-qa', ('SHILPAMED',), ('scienceamit1',))`. It succeeded. The sandbox held only SHILPAMED_index.json and workspace/scienceamit1/system/dhan_instruments.json. The live master is dated **2026-10-17** (a live checkout refreshed it today, not 2026-10-16). In T1300-qa: `create_symbol_daily_series('scienceamit1','SHILPAMED','2024-01-01','2026-10-13').exchange_of()` gave `CachedDailySeries NSE_EQ`. `load_stored(as_of=2026-10-18)` raised the dated error. Worktree, branch and sandbox root removed. After merge, QA can run the CLI form as written.

Behaviour the owner should know about:
- Every sandbox that reads NSE-only exchanges now needs `--seed-instrument-master <uid>`.
- A read with an end after the master date raises.
- Re-seed to refresh.

## Found
- With end 2026-10-16, building the SHILPAMED sandbox series tried to fetch the NSE holiday calendar from www.nseindia.com (blocked by the proxy, curl_cffi ConnectionError). The cache ends 2026-10-13, so `require_current` calls `nse_trading_holidays`. That is T-20261017-1200's area. The pilot needs it before any read past the cache's last bar.
- Residual leftover: the dev sandbox root `alto_sandboxes/T1300-dev` backs this worktree's `.alto_checkout.yaml` (untracked). Remove it together with the worktree.

## Round 2 (2026-10-17)

Branch `eng/T-20261017-1300-sandbox-dhan-instrument-master`, rebased onto local main 8cf276e. Range **8cf276e..060f850** (ed74dd3, 2121d8e, 4e92ebf are the round-1 commits rebased; 060f850 is new).

### Findings
- **F2, fixed (060f850).** `contract.py` no longer holds a path. `backend.config.paths.workspace_root_for(checkout, local_machine)` is now the one rule, and `WORKSPACE_ROOT` is computed by it. The seeder resolves each side from that checkout's own file and its own `.env`: `instrument_master_path(checkout_root, user)` = `load_checkout(root)` + `machine.is_local_machine_at(root)` (new, reads `<root>/.env`) + `workspace_root_for`. A live server checkout gives `<workspace>/alto_workspace/workspace/<u>/system/dhan_instruments.json`. Tests: `test_server_style_live_checkout_reads_the_alto_workspace_repo`, `test_workspace_root_for_server_and_local_checkouts`.
  - **Signature change QA must know:** `seed_instrument_master(live_root, sandbox_root, user_id)` now takes **checkout roots** (live main, sandbox worktree), not data roots. A data root alone cannot resolve the server workspace. The check-1 test now builds a fake live checkout. The assertions are unchanged: byte-identical, live bytes and mtime unchanged, Dhan patched to raise.
- **F1, fixed (060f850).** `contract.stored_date(cached, path)` takes only a `str` that is an exact `YYYY-MM-DD` (`date.fromisoformat` and an isoformat round-trip) and raises ValueError naming the file. Both the seeder (before the worktree exists) and `load_stored` use it. Tests are parametrized over garbage, None, `2026-10-16T09:00` and `20261016`.
- **Fail before:** with the source changes stashed, the 11 new or changed tests failed and 17 passed. With them in place, all pass.

### Checks (dead proxy 127.0.0.1:9 throughout; sandboxes T1300-r2head at 060f850 and T1300-r2base at 8cf276e, made by main's new_sandbox_worktree)
1-6. A targeted run in the head sandbox gave 115 passed: config/tests, test_dhan_instruments_load_stored, broker_factory/tests, stores/tests/test_boundaries.
   - `--help` lists `--seed-instrument-master USER_ID`.
   - `git grep -n "load_stored()" -- backend/executor` is empty (rc=1).
7. create() form, from the head sandbox: `create(Path(main),'T1300-qa','060f850','qa/T1300-qa',('SHILPAMED',),('scienceamit1',))` succeeded.
   - The sandbox master `cmp`-matches live. Live is dated 2026-10-17 (sha1 af04e3705e98, mtime 1792187663 unchanged).
   - `create_symbol_daily_series('scienceamit1','SHILPAMED','2026-01-01','2026-10-13').exchange_of()` gave NSE_EQ.
   - `_stored_exchange_of(...,'2026-10-17')('SHILPAMED')` gave NSE_EQ.
   - The '2026-10-18' read raised the check-4 message.
   - Removed afterwards. The exact CLI run is a release-checklist item post-merge, per the owner.
8. Suite: head 98 failed/8 errors/1761 passed; base 98/8/1712. `comm -23 new base` is empty (107 lines each). Imports OK: main_cockpit, app_factory, e2e.lanes, harness, new_sandbox_worktree.
9. No Dhan, LLM or network calls and no credentials. On live, only the scienceamit1 master and the SHILPAMED index were read.

### Cleanup
Removed the T1300-qa, r2head and r2base worktrees, their branches and sandboxes, and `alto_sandboxes/T1300-dev`.

### Notes
- One commit covers both findings: they share contract.py and the seeder.
- `new_sandbox_worktree` now imports `backend.config.paths`, so it carries paths' import-time checks. On the live main these hold.
