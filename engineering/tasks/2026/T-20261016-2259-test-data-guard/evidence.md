---
schema: evidence/v1
task: T-20261016-2259-test-data-guard
round: 4
qa: pass
qa_by: qa@claude
commits: 8cf276e..a121ff3
acceptance_sha256: f761861f811fffc90af7ac7e437365e95aa19e90560b9a7578b8f95c8e65beca
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


## Round 2

Worktrees: head .../.claude/worktrees/tdg-qa (declaration `mode: test`) and tdg-qa2 (sandbox declaration), base tdg-base at 1665a1c (sandbox). Logs and .set files: news_server/verify_data/reports/T-20261016-2259-test-data-guard/r2_tdg-*.{log,set}. Marker /tmp/tdg_marker3 on news_server/data, excluding workspace/*/book/* and scheduler/*.

### Round 1 findings
1. Binary: FIXED. `git log 1665a1c..HEAD -- backend/data` empty; no duckdb in `git diff --stat`. chart_profile_storage.py:32 default is `DASHBOARD_DIR / "chart_profiles.duckdb"` (paths.py:149). Head worktree status clean after suite (no backend/data/dashboard created).
2. Subprocess tests: FIXED. Under `mode: test` (tdg-qa) the 5 round-1 tests pass; `comm -23 head base` empty (see Suite). ALTO_TEST_ROOT is exported by activate_test_mode and read at import (checkout.py:44-57).
3. Session-end assertion (backend/conftest.py, live_root_watch.py): works.
   - My own temp-dir script /tmp/qa_watch.py: created, modified (size change), modified (same size, mtime only), removed, and a file reached through a symlinked dir are all detected; paths named in the message. Exit code with a raising sessionfinish hook is 1 (traceback after results), so it fails the run.
   - Exclusions (workspace/*/book/*, scheduler/*) are justified: round 1 saw snapshots.jsonl change every 4 min with no test running. They do hide a real test write into a book dir or scheduler state; a non-book file under workspace/<u>/ is still detected. fnmatch "*" crosses "/", so the patterns cover nested dirs.
   - False positive: any other live-server write during the 3 min run (dashboard chat duckdb, intake, ledgers) fails the session at the end; none seen in 3 runs here. A file removed between scandir and stat raises FileNotFoundError in snapshot (not tested live). Empty-directory creation is not detected (files only). rmtree of the temp root runs before the assertion, so a failing rmtree skips it. All minor ALERTs, not run past the verifier sub-agent (reproduced by script above).
   - Cost: config/tests+cooldown file 57 tests took 37 s, of which about 28 s is the two walks. Full suite 183 s vs 206 s base: not material for a hand-run suite.

### Acceptance (as written)
1. Mode: PASS. `pytest backend/config/tests backend/api/services/tests/test_rebalance_price_action_cooldown.py -q` with `mode: test`: 57 passed.
2. Guard: PASS (test_store_write_under_live_root_raises_naming_the_path in the 57).
3. ACME class: NOT RUN as written. Base half needs a live-mode checkout; a worktree cannot declare live and base would write production. Head half: after that run and the full suite, `find news_server/data -newer /tmp/tdg_marker3 -not -path '*/workspace/*/book/*' -not -path '*/scheduler/*'` lists nothing. Writer of ACME decisions/trades still unidentified (known gap).
4. Full suite: PASS. Marker find empty after head runs under both declarations; comm -23 below.
5. Repo checks: PASS. test_boundaries in the suite (stores and stage_fleet) pass. Imports config.paths, e2e.run, workflow.cli ok; api.local needs SESSION_SECRET and ALLOWED_EMAILS and fails identically at base.

### Suite
Base sandbox: 95 failed, 11 errors, 1646 passed. Head sandbox (tdg-qa2): 95 failed, 11 errors, 1656 passed. Head mode test (tdg-qa): same counts. `comm -23 head base` empty for both; no failure fixed either. +10 passed are the new tests.

### Findings
- ALERT (owner decision): chart profile database moved from cwd-relative backend/data/dashboard/chart_profiles.duckdb to news_server/data/dashboard/chart_profiles.duckdb, not migrated. A file already exists at the new path (plus chart_profiles_old.duckdb); I did not open it. On the server the old file's profiles will silently not appear unless the owner checks which file holds the real profiles and copies it. Fix is data-side, via the owner.
- ALERT: the watcher minor points above.
- Verdict reason: `fail` only because check 3's base half cannot run in a worktree. No BLOCK. The owner can waive that half; everything else passed.

### Dev claims
Not confirmed: "ACME writer not found" (consistent with mine, not independently solved); the "95 failed 8 errors" count (I get 11 errors on all three trees, same sets). Everything else reproduced.

### Check that would catch the class
The session-end live-root assertion now in place catches any test write outside the book and scheduler exclusions at the end of a hand-run suite. For the ACME class specifically: run the cooldown test file once from the main checkout (live) with the marker after merge, as part of ship's full-suite diff.

## Round 3 (delta e7bfc9d..802a45b; acceptance as re-approved 2026-10-17 03:00, sha be3cff5b)

Worktrees: tdg-qa (head, `mode: test`), tdg-qa3 (head, sandbox declaration), tdg-base (1665a1c, sandbox). Logs/sets: news_server/verify_data/reports/T-20261016-2259-test-data-guard/r3_{base,head_t,head_s}.{log,set}.

### Delta review
- Server path byte-identical: `git diff 1665a1c HEAD -- chart_profile_storage.py` only adds `SERVER_DB_PATH = Path("data/dashboard/chart_profiles.duckdb")` (same relative path as main's default string) and `default_db_path()`. Run outside test mode (sandbox declaration) in a temp cwd: db_path = `data/dashboard/chart_profiles.duckdb`, file created under the temp cwd only. The chart-profile migration ALERT from round 2 is gone (path unchanged).
- Callers: only `backend/api/routes/price_chart.py:27` (module-level `ChartProfileStorage()`, runs at import, now resolves via default_db_path so test mode goes to the temp root) and a type-only use in `ai_levels/service.py:17,47`. No scripts use it. Head worktrees stayed clean after suites (no backend/data/dashboard; base worktree does create it, as expected).
- Smell judgement: acceptable but mildly smelly. One 3-line function, one branch, contained; but production code now knows about test mode (imports TEST_MODE and CHECKOUT). It is the only place a path is cwd-relative, so the branch exists to paper over that. Cleaner: give the path a home in backend.config.paths and keep the server on it (owner's call; not a defect). Callers reading `CHECKOUT.mode` at call time is fine.

### Acceptance
1. Mode: PASS (config tests, 57+ passed in the suites below).
2. Guard: PASS (`test_store_write_under_live_root_raises_naming_the_path`).
3. (a) PASS: `pytest backend/api/services/tests/test_rebalance_price_action_cooldown.py -q` with marker /tmp/tdg_m5, in both `mode: test` and sandbox: 2 passed each; `find news_server/data -newer marker -type f` excluding workspace/*/book/* and scheduler/* empty.
   (b) FAIL (not covered by a committed test). Store write under live root: covered (test_test_mode.py:30, LiveRootAccessError naming the path). Direct file write failing the session through the session-end assertion: NOT covered. `backend/config/tests/test_live_root_watch.py` unit-tests snapshot/assert_unchanged on tmp_path only; nothing runs the conftest `pytest_sessionfinish` (backend/conftest.py:26-27) in a temp copy and sees the session fail. I demonstrated the mechanism myself in round 2 (script, exit code 1) and the sandbox run below shows the real hook raising LiveRootChangedError, but that is not a committed test as written. Finding for dev: add the test (temp copy of the repo with a test that writes a file under the live root, run pytest on it in a subprocess, expect nonzero exit and the path in the output). I wrote no product tests.
4. Full suite: PASS on the comm check. Base 95 failed, 8 errors, 1656 passed. Head `mode: test`: 95 failed, 8 errors, 1666 passed. `comm -23 head base` empty (all three trees, 103 identical failure lines). Marker find after the head runs: empty in `mode: test`. See finding 1 for the sandbox run.
5. Repo checks: PASS (test_boundaries in the suite; entry points as in round 2).

### Findings
1. ALERT (false positive, watcher exclusions): the sandbox-declaration head run ended with `LiveRootChangedError ... modified=['alto_data/workspace/backtest/system/dhan_instruments.json']`. The tests wrote to the sandbox root; the writer was the live uvicorn (cwd main alto, pid 72592) refreshing `workspace/<user>/system/dhan_instruments.json` (backtest at 03:25:10, scienceamit1 at 03:24:23, while my run was going). The exclusions (workspace/*/book/*, scheduler/*) do not cover this live-server write, so a hand-run suite fails at the end whenever the server refreshes instruments (same class as round 2's note). Fix choices belong to dev/owner (exclude that daily refresh path, or compare only paths a test could reach). Confirmed by mtime vs run window and server cwd; not run past the verifier.
2. ALERT: check 3(b) has no committed test for the direct-write session failure (above).
No BLOCK found in the delta itself.

### Verdict
`fail`: check 3(b) as now written has no test to run (the direct-write half), plus the suite-end false positive. Everything in the delta (path revert, default_db_path) is correct and the suite has no new failures. Check 3 base half no longer applies.

### Dev claims
Not read yet before verdict beyond the coordinator brief; nothing to compare.


## Round 4 (8cf276e..a121ff3; acceptance re-approved, sha f761861f)

Base for the suite diff is 8cf276e (not main 9a97ee1). Worktrees tdg4-s (sandbox declaration, root /tmp/qa4r/s), tdg4-t (`mode: test`), tdg4-base (8cf276e, sandbox, root /tmp/qa4r/b); removed after. The live root was never written: all probing used a temp copy of the layout (/tmp/qa4: fake main `alto` with mode live, fake `news_server`, worktree with the head backend). Logs: news_server/verify_data/reports/T-20261016-2259-test-data-guard/r4b_{s,t,base}.{log,set}. No verifier sub-agent was used; every finding below was reproduced by a script I ran.

### Part A: why the dev's store write reached the live root (cause established)

The guard is not a property of the checkout; it is installed only when `backend.config.paths` is first imported while `checkout._test_root` is set, and `_test_root` is set only by `activate_test_mode`, called only from `backend/conftest.py` (or by inheriting ALTO_TEST_ROOT). I reproduced the debris in the temp layout: a probe test calling `CompanyStore(<live>/stances).append_stance("ZZNOSUCH", ...)` and `open(<live>/x.txt,"w")`:
- `pytest backend/qa_probe` (conftest loaded): both refused, LiveRootAccessError, nothing written.
- the same file under a directory outside `backend/` (no conftest.py applies): 3 passed, wrote `stances/ZZNOSUCH/{latest.json,log.jsonl,log.jsonl.lock}` and x.txt into the fake live root. Identical with `--noconftest`.
- a plain script (no pytest): `import backend.config.paths` reports CHECKOUT.mode sandbox, no guard.

So the non-raise happens whenever the process is not a test session of backend/conftest.py: pytest invoked on a file outside backend/, `--noconftest`, `-c`/`--confcutdir`/`--rootdir` settings that skip it, `python -c`/script runs, or a subprocess without ALTO_TEST_ROOT. The debris file set (latest.json, log.jsonl, log.jsonl.lock) is exactly what my unguarded run produced. I cannot know which invocation the dev used; the dev's note "same test raised in other runs" fits (conftest loaded in some, not in others). Treat the cause as: guard absent in that process, not a hole in the hook.

Answers:
1. Under a plain sandbox declaration running pytest on a file under backend/: the guard IS active, because conftest activates test mode unconditionally (not only for `mode: test`). Printed in-run: `MODE test`, CHECKOUT.live_root = main checkout's declared data_root, STANCES_DIR = <tmp>/alto_test_root_*/data/alto_data/stances, guard `_live_root` = the live root. An explicit path under the live root is refused (both probe tests). Under the same declaration without conftest: CHECKOUT.mode is sandbox, STANCES_DIR is the sandbox root, and an explicit live path is writable (above).
3. Install order: safe for tests that run under conftest. conftest imports only `backend.config.checkout`, then `activate_test_mode` (mkdir of the temp root happens before the hook exists, harmless); the hook goes in at the first `import backend.config.paths` (load_checkout), which happens at collection of the first test/conftest that imports it, before any test body runs. No conftest or plugin above backend/ imports paths first (no repo-root conftest.py). Weak point: install is lazy, not in conftest itself, so a process that opens files before paths is imported is unguarded for those (none found). Nested pytest or a shell with ALTO_TEST_ROOT leaked fails loudly: "test mode is already active" in conftest (reproduced), no silent mode.
4. Live root declared differently or missing: the live root is whatever `main_checkout_root(worktree)`'s `.alto_checkout.yaml` says. Missing file: CheckoutDeclarationError at import (loud). Main file not mode live (sandbox or test): CheckoutDeclarationError (loud). Main file declares another root (I set it to /tmp/qa4/other): guard protects only that root; the real production root was writable (ALLOWED). Also nothing in test mode checks the live layout (`_require_live_layout` runs only outside test mode), so a worktree whose gitdir points at a clone or copy with its own mode live file guards that file's root, not production. ALERT: acceptable because the declaration is the owner's source of truth, but it means the guard is only as good as the main checkout file; a test asserting live root == `<workspace>/news_server` in the real main would close it.

### Part B: audit-hook gaps (temp layout, run in a test-mode child, script /tmp/qa4/gaps.py)

| operation | result | rating, reachable from repo |
|---|---|---|
| dir_fd open/mkdir/unlink/rename (relative name + dir_fd, resolved against cwd) | ALLOWED | ALERT; `dir_fd` appears nowhere in backend/ |
| os.chmod, os.utime | ALLOWED | ALERT; not used outside tests (grep) |
| mkfifo | ALLOWED | ALERT; unused |
| sqlite3.connect (create table) | ALLOWED | ALERT; only prune_runs.py:39 shells out to `sqlite3` on the dagster home, never a live-root path from a test |
| duckdb ATTACH / COPY TO / duckdb.sql on the default connection | ALLOWED | ALERT; no such SQL in backend/ (grep); path must be a literal live path |
| pyarrow/parquet C++ write | ALLOWED | ALERT; dhan_price_store.py:369,410, dhan_daily_store.py etc. write parquet, but under DHAN_CACHE_ROOT = ~/NSE_BSE_Data/dhan_cache (paths.py:230), outside the live root, so not in scope |
| subprocess `touch`, os.system, python child without importing backend.config.paths, child with env={} | ALLOWED | ALERT; the repo's children (e2e/run.py:209, pipeline_executor.py:50, test_*) pass `{**os.environ}`; a cleared-env child falls to the checkout declaration (sandbox) not live |
| pandas.to_csv, pathlib.touch, r+, O_RDONLY|O_CREAT, truncate, link, symlink, copyfile/copy2/copytree, rename/replace, mkdir, duckdb.connect (positional, kw, Path) | REFUSED | BLOCK class covered |
| cwd-relative write after chdir into live | REFUSED (resolved against cwd) | covered |

None of the ALLOWED rows is reachable by a repo test, because in test mode every path in backend.config.paths resolves into the temp root; they need a literal live path. Residual non-test risk: any process outside a conftest session is unguarded (Part A), which is outside acceptance 2 ("in test mode").

### Acceptance (as written, sha f761861f)
1. Mode: PASS. `mode: test` declared; `STANCES_DIR` under the temp root (test_roots_are_under_the_temp_root passes; also printed above); temp root removed at session end (conftest sessionfinish, rmtree with ignore_errors=False).
2. One guard: PASS. `pytest backend/stores/tests/test_boundaries.py backend/config/tests/test_live_root_guard.py backend/config/tests/test_test_mode.py` 20 passed. The guard tests cover direct write, append, mkdir, rename, remove, shutil copy, duckdb connect, child process, store write, temp-root write allowed, live read allowed, symlink under temp pointing into live refused. Failing before: copying test_live_root_guard.py into the 8cf276e tree gives 12 errors (no live_root_guard module / no LiveRootAccessError).
3. (a) PASS: marker /tmp/tdg_m9 on news_server/data; `pytest backend/api/services/tests/test_rebalance_price_action_cooldown.py backend/config/tests -q` in both declarations: 65 passed each. `find news_server/data -newer marker -type f` with the stated exclusions (workspace/*/book/*, scheduler/*): empty. (b) PASS: the guard tests run in a temp copy (layout fixture), real live root untouched. (c) PASS: `live_root_watch.py` and LiveRootChangedError no longer exist (grep empty); conftest.py only creates and removes the temp root.
4. Full suite: PASS. Command from the dev skill (run from backend/, PYTHONPATH=.., SESSION_SECRET etc., `pytest -q -p no:cacheprovider --rootdir=. .`), marker /tmp/tdg_m8. Base (8cf276e): 95 failed, 8 errors, 1715 passed. Head sandbox: 95 failed, 8 errors, 1733 passed. Head `mode: test`: same. `comm -23 head base` empty for both (103 identical lines), `comm -13` empty. No LiveRootAccessError in any log, no watcher error. The run is no longer exposed to live-server writes: the guard checks only this process's own calls. Marker find on the live root (excluding workspace/*/book/*, scheduler/*): empty. Without exclusions it listed workspace/scienceamit1/book/default/snapshots.jsonl (live server); after check 3a, scheduler/state.json, history, logs. So the guard needs no exclusion, but the acceptance-3a `find` still does, because the live server writes there during any run (the exclusions are about the find, not the suite).
   Base sandbox received test debris (chat duckdb, u_test, backtest/system, screener raw_reports); head sandbox root received none.
5. Repo checks: PASS. test_boundaries in the suite; imports of backend.config.paths, backend.e2e.run, backend.workflow.cli, backend.api.local ok (with the env vars of the dev skill).

### Findings
1. ALERT (cause of the live-root debris, Part A): the guard exists only inside a pytest session that loads backend/conftest.py. A `pytest` run on a file outside backend/, with `--noconftest`, or a script, writes the live root unguarded when run from a worktree whose gitdir resolves to the live main. Suggested hardening for the owner or dev (not required by acceptance): refuse by default for any process of a non-live checkout, i.e. install the guard in `load_checkout` for sandbox and test modes, not only test mode; this also makes the dev's earlier mistake impossible. Reproduced in /tmp/qa4 as above.
2. ALERT: guard's live root = whatever the main checkout file says; no layout check in test mode (Part A, Q4).
3. ALERT: hook gaps in Part B; none reachable from the repo.
4. ALERT (minor): lazy install point. `activate_test_mode` does not install the guard; `load_checkout` does. If a future conftest/plugin writes files before importing paths it is unguarded.
No BLOCK. The owner can decide whether finding 1's hardening is wanted before merge.

### Dev claims
Confirmed: incident described (debris set matches my unguarded reproduction), dir_fd/chmod/utime gaps (also open-gaps listed above), suite counts (95 failed, 8 errors at base and head; my passed counts 1715/1733). Not confirmed: "cause unproven" is now explained by Part A (guard absent in that process), though which invocation the dev used cannot be recovered.

### Check that would catch the class
A test asserting that `backend.config.paths` import in a sandbox-mode process (no ALTO_TEST_ROOT) cannot write the live root, i.e. guard installed for sandbox as well; or ship's full-suite diff from the main checkout with the marker.
