# Handoff, attempt 2

Branch eng/T-20261016-2259-test-data-guard, rebased onto main 1665a1c (local main moved past 354cbda). Commits 1665a1c..e7bfc9d:
63b62a6 test mode + guard (rewritten, unchanged content), be8fda9 test reads stances via CompanyStore (duckdb file dropped), cb2f413 chart profile path, 2abede5 ALTO_TEST_ROOT, e7bfc9d session-end live-root assertion.

## QA findings
1. BLOCK duckdb committed: fixed. chart_profiles.duckdb is in no commit of the branch (history rewritten; `git log 1665a1c..HEAD -- backend/data` empty). ChartProfileStorage default is now `DASHBOARD_DIR / "chart_profiles.duckdb"` (backend/api/services/chart_profile_storage.py:31), so tests write under the temp root. Test: test_chart_profile_storage_default_path_is_under_the_temp_root.
   Behaviour change: production now reads news_server/data/dashboard/chart_profiles.duckdb (a file already exists there) instead of backend/data/dashboard/ (cwd-relative). Server profiles in the old cwd file are not migrated; owner should check which one the server uses.
2. ALERT children: fixed. activate_test_mode exports ALTO_TEST_ROOT; checkout.py reads it at import (_inherited_test_root, raises on a bad value). Test: test_child_process_inherits_test_mode_and_root. test_checkout.py's import-in-sandbox helper now strips the variable (it simulates a non-test process).
3. ALERT unguarded writes: backend/config/live_root_watch.py snapshots (mtime,size) of <live>/data before the session and backend/conftest.py compares at session end, raising LiveRootChangedError naming created/modified/removed files. Excluded (a live server writes them, not tests): alto_data/workspace/*/book/* (snapshots.jsonl every 4 min) and alto_data/scheduler/*. Walk costs about 14 s twice. Unit tests: config/tests/test_live_root_watch.py. Caveat: any other live-server write during a run (e.g. dashboard chat, intake) would raise a false positive; none seen in 3 runs.

## Acceptance
1. Mode / STANCES_DIR under temp root: config/tests 55 passed (declaration `mode: test` in the worktree).
2. Guard test: passes (test_store_write_under_live_root_raises_naming_the_path).
3. ACME class: BASE HALF NOT RUN: a worktree cannot declare live, so the base cannot write the live root from here. Head half: marker /tmp/tdg2_marker; after three full suite runs `find news_server -newer marker` lists only my report logs under verify_data and workspace/scienceamit1/book/default/snapshots.jsonl (live server). The ACME writer was NOT identified (QA found 13 candidate files wrote nothing in an empty root); I did not find it either.
4. Full suite from backend/, vs base 1665a1c in a sandbox declaration (logs and .set files in news_server/verify_data/reports/T-20261016-2259-test-data-guard/r2*):
   base 95 failed 8 errors; head sandbox declaration 95 failed 8 errors; head `mode: test` 95 failed 8 errors. `comm -23 head base` empty for both; head sets identical to each other. The 5 subprocess tests QA listed pass under mode: test. The session-end assertion passed on the live root in both head runs.
5. test_boundaries + cooldown file: 4 passed. Imports ok: config.paths, e2e.run, workflow.cli, api.local (needs the env vars the suite sets).

## Not done / notes
- Base half of check 3 (above). The 95 base failures are unchanged, not investigated.
- A nested pytest subprocess would inherit ALTO_TEST_ROOT and its conftest would raise "already active"; none exists in the suite.
- Scripts with cwd-relative data/dashboard paths (scripts/migrate_*.py, api/services/migrate_to_partitioned.py) are untouched.

## Follow-up (owner decision): server chart-profile path unchanged
Reverted cb2f413 (9b5f007). ChartProfileStorage keeps the cwd-relative data/dashboard/chart_profiles.duckdb for the server; `default_db_path()` returns the temp-root DASHBOARD_DIR path only in test mode (802a45b, backend/api/services/chart_profile_storage.py). The "behaviour change" note above no longer applies. Suite vs base (r2base.set): sandbox declaration and mode test both 95 failed 8 errors, comm -23 empty, no LiveRoot error; no backend/data/dashboard created; only the live server's snapshots.jsonl changed under the live root. Head 802a45b.

## Redesign (owner decision): one guard, no watcher
Rebased onto main 8cf276e. Commits: 0ce3bcf (guard), a121ff3 (executor gate).
- backend/config/live_root_guard.py: sys.addaudithook for open with write flags, os.mkdir/rename/remove/rmdir/truncate/link/symlink, shutil copyfile/copymode/copystat/copytree/move/rmtree, plus a duckdb.connect wrapper (not read_only, not :memory:). Paths resolved through symlinks. Raises LiveRootAccessError naming operation and path. Installed by load_checkout in test mode (checkout.py), so children with ALTO_TEST_ROOT get it. Removed: live_root_watch.py (+ its test and conftest assertion, so no exclusions or walks) and the three-primitive check in stores/locking.py and paths.refuse_live_write.
- Tests: backend/config/tests/test_live_root_guard.py, each in a child process against a temp copy of the layout (temp "live" root): direct write, append, mkdir, rename, remove, shutil copy, duckdb connect, child-process write, store write (append_stance), allowed temp write, allowed live read, symlink under temp into live. With install disabled, the 10 refusal tests fail and the 2 allowed ones pass (run once).
- a121ff3: main's new daily_series/prices gates raise NotImplementedError for mode test; gate.checkout_mode() now maps test to sandbox (otherwise one new failure under mode test).
- Suite (base = main 8cf276e, own sandbox root; head sandbox declaration; head mode test; each own root): 95 failed 8 errors on all; comm -23 head base empty for both; no LiveRoot/INTERNALERROR in logs. Logs r4*/r5* in verify_data/reports/T-20261016-2259-test-data-guard/. Marker find after the final runs: only workspace/scienceamit1/book/default/snapshots.jsonl (live server). Boundary test, cooldown file (4 passed), imports ok.
- INCIDENT: during development an in-process store test (since removed; the store write now runs only in a temp copy) wrote debris to the live root: news_server/data/alto_data/stances/ZZNOSUCH/{latest.json,log.jsonl,log.jsonl.lock}, mtime 17 Oct 03:39-03:40. Created by my own test when the guard did not raise in two runs; I could not reproduce the non-raise afterwards (the same test raised in other runs, and probes of the hook behaved correctly). Cause unproven. I did not delete it (owner's call). Owner should remove that directory. Note the guard's reliability under every ordering is therefore not proven beyond the temp-copy tests and two full suite runs with a clean marker.
- Not done: dir_fd-relative paths are not resolved; os.chmod/utime and os.open of directories are not guarded.

## Follow-up 3: guard for every non-live checkout, independent of conftest
Rebased onto main 9a97ee1; head 319e42c (one commit).
- load_checkout installs live_root_guard for sandbox declarations as well as test mode, never live (checkout.py). install() is idempotent and keeps a set of live roots (a process that loads several checkouts, as the checkout tests do, guards each). conftest does not install anything. Known gaps (dir_fd, chmod/utime/chown, ATTACH, sqlite, ctypes) are in the module docstring.
- Tests backend/config/tests/test_live_root_guard_outside_pytest.py (temp copy of the layout): script from a directory outside backend/ under a sandbox declaration refuses a live write; pytest --noconftest refuses; live mode installs nothing (write to the temp "live" succeeds); sandbox write under its own root allowed; sandbox read of live allowed. With the sandbox install removed the first two fail (run once).
- Sandbox tooling: new_sandbox_worktree seed_index and validation/cases freeze --live only read the live root; no tooling found that writes it.
- Suite (base main 9a97ee1 / head sandbox declaration / head mode test, separate roots): 95 failed 8 errors each; comm -23 empty both; no LiveRoot/INTERNALERROR; marker find only workspace/scienceamit1/book/default/snapshots.jsonl; boundary test inside the suite; entry points import. Logs r6* in verify_data/reports/T-20261016-2259-test-data-guard/.
- ZZNOSUCH debris (see above) still in the live root; its cause is QA's Round 4 explanation (unguarded run outside conftest), now closed by this change.
