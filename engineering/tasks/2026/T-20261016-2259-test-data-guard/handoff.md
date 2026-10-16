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
