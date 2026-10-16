---
schema: evidence/v1
task: T-20261016-2259-test-data-guard
round: 1
qa: fail
qa_by: qa@claude
commits: 35e1342..79bdab3
acceptance_sha256: 548696372fb90bf55e97871abdd206456477c4c24552181f3d64a957c06735db
outputs_changed: unverified
---

## Round 1

Worktrees: head /Users/kmrh581/personal/projects/workspace/alto/.claude/worktrees/tdg-qa, base .../tdg-base. Logs: /Users/kmrh581/personal/projects/workspace/news_server/verify_data/reports/T-20261016-2259-test-data-guard/ (base.log, head.log, head2.log). `.alto_checkout.yaml` is gitignored, so each worktree needs its own declaration.

### Acceptance check results
1. Mode: PASS. `pytest backend/config/tests` (with `mode: test` declared) 51 passed incl. test_roots_are_under_the_temp_root.
2. Guard: PASS. test_store_write_under_live_root_raises_naming_the_path passes. Note the guard is only in locking.py's three write primitives (exclusive_lock, atomic_write_text, append_line_durable); a direct open(..., "w") or duckdb write is not guarded (see finding 2).
3. ACME class: NOT RUN as written (FAIL by rule). Base half needs a live-mode worktree; a worktree cannot declare live. Head half: with marker /tmp/tdg_marker, cooldown test file passes (51 incl config), `find news_server -newer marker` empty.
   Extra ask, which test writes ACME: I ran 13 candidate files (every test importing RebalanceService or write_decision_ledger) at base, each under its own empty sandbox root. None created decisions.jsonl or trades.jsonl, and the full base suite in the sandbox created no stances/ dir at all. The writer is NOT identified; it needs data that an empty root lacks (live ACME stance, or an older test version; live ACME decisions.jsonl mtime 16 Oct 22:17, trades.jsonl 9 Oct). Head: also nothing, and a store write to the live root now raises.
4. Full suite: see Suite. Live root: no test-caused writes (no LiveRootAccessError in head logs). `news_server/data/alto_data/workspace/scienceamit1/book/default/snapshots.jsonl` changes every 4 min (:24 marks) with no test running; the live uvicorn (pid 72592) writes it. Not attributable to tests, but it makes "find -newer marker" unusable on a live machine without excluding it.
5. Boundary test: 2 passed. Entry points import: api.local, config.paths, e2e.run, workflow.cli ok (backend.api.main does not exist at base or head).

### Findings
1. BLOCK. backend/data/dashboard/chart_profiles.duckdb (274 KB binary) was committed in 79bdab3 (`git show --stat 79bdab3`). It is a test/app artifact created by backend/api/services/chart_profile_storage.py:31 (default db_path "data/dashboard/chart_profiles.duckdb", relative to cwd backend/). Main already has it untracked (`?? backend/data/dashboard/`), so merging will fail with "untracked file would be overwritten", and it commits a data file. Confirmed with git show. Dev must drop it from the commit.
2. ALERT. Spawned children do not inherit test mode (state is the module global `_test_root`, checkout.py:41; no env var). With a worktree declaring `mode: test`, 5 subprocess tests fail at head with "mode test needs a per-run temp root" (head.log, 20 occurrences): e2e/tests/test_run.py::test_progress_lines_of_a_step_reach_the_console_whole, stores/stance/tests/test_classification_ledger.py::test_concurrent_writers_lose_nothing, stores/stance/tests/test_repository.py::test_concurrent_appends_same_symbol_lose_nothing and ::test_rewrite_history_vs_append_loses_nothing, stores/workflow_cache/tests/test_step_cache.py::test_concurrent_processes_writing_different_steps_lose_nothing. With a sandbox declaration they pass (123 passed). Conversely in the main checkout (mode live) the children resolve the LIVE root unguarded, since the guard is off outside test mode. Whether any child test touches live data was not shown; I did not run in main. Acceptance 1 says `.alto_checkout.yaml` accepts mode: test, and that exact configuration produces 5 new failures.
3. ALERT. The guard covers only locking.py primitives, and relative-path writers (finding 1) bypass both temp root and guard.

LiveRootAccessError cannot fire in a live run: refuse_live_path returns at once unless checkout.mode == "test", and mode test is only reachable when `_test_root` is set, which only backend/conftest.py does (a file declaring mode test outside pytest raises CheckoutDeclarationError, checkout.py _read). Confirmed by reading; locking.py imports paths with no cycle (imports ok).

Tests that relied on live data now see an empty root: head failure set equals base set (sandbox declaration), so none newly failing.

### Suite
Base (sandbox declaration, 35e1342): 95 failed, 8 errors. Head, sandbox declaration (head2.log): `comm -23 head base` empty, nothing fixed either. Head with `mode: test` declaration (head.log): 100 failed; comm -23 lists the 5 tests of finding 2. Tests wrote to the data root at base (backtest/system, u_test, chat duckdb x2, screener raw_reports); at head the sandbox root received nothing.

### Dev claims not confirmed
- "named test file raises _QueueReached before the ledger": consistent with my base runs (no writes). Not independently traced.
- Dev's last-commit suite rerun was not done; I did it (above).

### Risks
Main-checkout run (mode live) not exercised: ship's full-suite diff there should confirm children do not write live.
Check that would catch the class: an end-of-session assertion in backend/conftest.py that nothing under the live root changed, plus an env var carrying the test root to subprocesses.
