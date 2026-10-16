---
schema: evidence/v1
task: T-20261015-0321-checkout-data-root
round: 2
qa: pass
qa_by: qa@claude
commits: 9950df7..dce991f
acceptance_sha256: a8ad8dd82d7f8e48ee50bb48f9faa45fde490e35d9b00193a179abf4264dff9a
outputs_changed: no
---

## Round 1

Method: throwaway clones in /tmp/qa1 (head at /tmp/qa1/alto with a live `.alto_checkout.yaml` naming /Users/kmrh581/personal/projects/workspace/news_server; base at /tmp/qa1/base). Hash of acceptance.md matches the second approval in task.md (0d5e9c99...). Production was only read. Live change seen in a full before/after mtime walk (401880 files): one file, /Users/kmrh581/personal/projects/workspace/news_server/data/alto_data/workspace/scienceamit1/book/default/snapshots.jsonl, written by the running API; nothing under any 544332 path.

### Acceptance check results
1. PASS. `python -m backend.config.dump_paths` at base (old code, clone prefix and ALTO_ROOT normalised) vs head live: 69 lines, `diff` identical. Normalisation needed because ALTO_ROOT-derived paths follow checkout location.
2. PASS. No file; missing field; unknown field; mode dev; sandbox == live; sandbox inside live; sandbox via `..` and via symlinked path; live in a worktree: each raises CheckoutDeclarationError naming the file and problem.
3. FAIL (two parts).
   - 3a. "every path in the dump resolves under the sandbox root": in /tmp/qa1/alto/.claude/worktrees/chk4 (made by `new_sandbox_worktree chk4 --seed-index 544332`), 14 of 69 lines do not: nse_data_root(), nse_eq_dir(), nse_index_dir() = /Users/kmrh581/NSE_BSE_Data/... (production market data, outside any checkout root), plus ALTO_ROOT-derived paths (ALTO_ROOT, ALTO_WORKSPACE_REPO_ROOT, data/metadata/*, data/custom_triggers.jsonl, data/macro_events) which sit in the worktree, not the sandbox root. Dev's handoff concedes these 14.
   - 3b. The command as written, `python -m backend.e2e.run --symbols 544332 --steps documents`, in the seeded sandbox exits with traceback `NoClosedDay: No day in [2026-07-01, 2026-10-16] has both exchange day files in /private/tmp/qa1/alto_sandboxes/chk4/news_server/data/1/daily_announcements`. It passes only with an added `--end 2026-10-15`, which is a changed command. With `--end`, an open() audit hook logged exactly one open under news_server/NSE paths: the sandbox 544332_index.json.
   - Write part PASSES: `CompanyStore().append_stance('544332', make_record(...))` (synthetic record from backend/stores/stance/tests/test_repository.py) in chk4 landed under /tmp/qa1/alto_sandboxes/chk4/news_server/data/alto_data/stances/544332/; live walk shows the one API file above only.
4. PASS. Live clone: `--llm-config backend/config/llm_benchmark_deepseek.yaml` raises NonProductionLLMConfigOnLiveError for backend.e2e.run and backend.stance.runner; `LLM_CONFIG_PATH=<benchmark>` raises for e2e.run, stance.runner and workflow.cli. Sandbox chk4: same `--llm-config` on e2e.run completes (with the --end caveat). `new_sandbox_worktree` run from a sandbox worktree raises "must be the live main checkout". No other code builds LLMSettings with a path (grep).
5. PASS with caveat. Full suite, `backend/` command from the dev skill: head 83 failed/1531 passed/8 errors; base 83 failed/1519 passed/8 errors; `comm -23 head base` empty (91 identical entries). Caveat: to avoid touching production, both ran against EMPTY data roots (base clone with an empty sibling news_server; head in sandbox worktree chk3), in parallel not sequentially, so the 91 failures are mostly missing data and the comparison is weaker than on the live root. Entry-point imports: all 144 `__main__` modules under backend/ imported at head (sandbox) vs base: no new failures (5 vs 6 pre-existing). outputs_changed: unverified, because the golden-company stores were not compared before/after the change itself on the live root.

### Findings
1. BLOCK (acceptance check 3 fails as written): see 3a and 3b. Either the check wording or the product must change: seeding only the index leaves e2e documents unable to run in a sandbox, and 3a cannot hold while NSE paths are outside the root.
2. ALERT: price caches live outside the declared root and are written from any checkout. /Users/kmrh581/personal/projects/workspace/alto/backend/price_feed/dhan_price_store.py:27 and backend/price_feed/dhan_candle_cache.py:18 set `CACHE_ROOT = Path.home() / "NSE_BSE_Data" / "dhan_cache"`; dhan_price_store.py:369 and :410 `to_parquet` there. A sandbox running backtest, price_watchlist or refresh_price_cache writes the real cache. Same for backend/price_feed/prices.py:26 and backend/lib/price_context/price_loader.py:31 (read). Cause: paths computed outside backend.config.paths. Goal "sandbox can never resolve to production" is not met for these.
3. ALERT: hardcoded or location-relative production paths, unchanged by this task but defeating a sandbox: /Users/kmrh581/personal/projects/workspace/alto/scripts/rename_gujgasltd_to_gujenergy.py:32 (absolute production data path); scripts/search_cli.py:16 and scripts/backfill_exchange_feed.py:15 (`sys.path.insert` of the main alto checkout, so they run main's live paths from a sandbox); start.sh:6-7 and stop.sh:6 (`../news_server/...` pid and log); cwd-relative `Path("data/dashboard/chat")` in backend/api/services/hybrid_conversation_storage.py:166, migrate_to_partitioned.py:138,165, backend/scripts/migrate_chat_add_status_columns.py:74, migrate_macro_to_trade_groups.py:18. Grep command: `grep -rnE '/Users/|Path\.home\(\)|"\.\./|Path\("data' backend scripts`.
4. ALERT: sandbox check compares only textual data_root against the main checkout's file; a sandbox root containing a symlink into production (the exact shape of the old .claude/worktrees/news_server link) is not detected. Not reproduced as a write; noted as a gap.
5. Verified clean: bse_collector.py edits resolve through paths (DAILY_ANNOUNCEMENTS_DIR; SHARED_DATA_ROOT/"1"/"companies_announcements" equals the old literal); the two LLM tests are patched only to sandbox mode plus a new live-refusal test, which does not weaken the guard; stance.runner and e2e.run both go through select_llm_config; get_llm_settings guards the env var path at first use and at import of llm_settings.

Verifier step: findings 1-3 were reproduced by me directly (commands above) rather than by a separate verifier sub-agent.

### Dev claims not confirmed
- "e2e documents ... passed" is true only with `--end 2026-10-15`, which is not in acceptance.md.
- "Suite 66 failed" differs from my 83 only because of the empty data root; no new failures in either.
- "The evidence that it read sandbox only is that the empty sandbox failed on sandbox paths": consistent with my audit-hook log (one open, sandbox index).

### Check that would catch this class
An invariant test that scans backend/ and scripts/ for `Path.home()`, `/Users/`, `"../` and cwd-relative `data/` outside backend/config/paths.py, plus making the NSE_BSE_Data and dhan_cache roots a declared field (or derived from data_root) in `.alto_checkout.yaml`.


## Round 2

Method: throwaway clones in /tmp/qa2 (head at /tmp/qa2/head, live file naming /Users/kmrh581/personal/projects/workspace/news_server; base 9950df7 at /tmp/qa2b/base). acceptance.md sha256 a8ad8dd8... matches the third approval. Production only read.

1. PASS. 69-line dumps. Base clone with a news_server symlink, normalising only the clone prefix and that symlink (ALTO_ROOT and ALTO_WORKSPACE_REPO_ROOT derive from checkout location): identical. Stronger: the unmodified main checkout (HEAD 9950df7, no normalisation, no symlink) vs head: the only differing line is ALTO_WORKSPACE_REPO_ROOT, which is the checkout prefix. The normalisation is a legitimate equivalence.
2. PASS. No file, missing field, unknown field, unknown mode, sandbox == live, sandbox inside live, live in worktree: each raises CheckoutDeclarationError naming the file. backend/config/tests: 40 passed.
3. PASS. Worktree via new_sandbox_worktree w1 --seed-index 544332: 56 of 69 lines under the sandbox root; the 13 others are ALTO_ROOT-derived (10) and nse_data_root/nse_eq_dir/nse_index_dir (3); known_user_ids() is []. `python -m backend.e2e.run --symbols 544332 --steps documents --end 2026-10-16` passed; an open() audit hook inside child processes saw one open under any news_server/NSE/sandbox path: the sandbox screener_announcements index. CompanyStore().append_stance landed under the sandbox stances/544332. Full live mtime walk before/after (456665 entries): zero modified or new under any path, only the news_server/.git directory entry (not data, not 544332); nothing removed.
4. PASS. Live: --llm-config benchmark raises NonProductionLLMConfigOnLiveError for e2e.run and stance.runner; LLM_CONFIG_PATH=benchmark raises for e2e.run, workflow.cli, stance.runner. Sandbox: same flag on e2e.run completes; env var builds LLMSettings.
5. PASS. Sequential full suite (dev-skill command, committed trees, empty data roots to avoid production writes): base 83 failed/1519 passed/8 errors; head 83 failed/1532 passed/8 errors; comm -23 head base empty (91 entries each), so no failure needed rerunning. Entry-point imports (every non-test __main__ module under backend/): 3 failures at both base and head, none new.
Ruling items: PASS. Symlink directly into live, nested, a chain, a link to the live root, and a ../ link are refused. grep for rename_gujgasltd over the head tree (all file types, .sh and docs included): no references; only alto_hq task docs name it.

### Mishap check
A find over the live root for files newer than 21:25 today: nothing under any 544332 path. Changed files are other writers: data/screener_data/raw_reports/stocks (scraper, 29), data/alto_data/scheduler/logs, workspace/scienceamit1 (API), data/dashboard/chat/partition_index.duckdb, stances/ACME/decisions.jsonl (22:17, not golden), verify_data reports of other tasks. Side effect in the diff: commit 8152dde carries a progress.jsonl line from the mishap run (logs/e2e/progress.jsonl, run 20261016_213331, symbol 544332): production log noise, not data.

### Findings (reproduced by me; no separate verifier sub-agent)
1. ALERT: symlink guard gaps, backend/config/checkout.py:_refuse_symlinks_into (about lines 83-92). It resolves only each link's own target and does not descend links. (a) sandbox/data -> /tmp/el2, and /tmp/el2/alto_data -> live alto_data: accepted, and paths.DATA_ROOT realpath is the live alto_data. (b) a link to a parent of the live root (sandbox/data -> .../workspace) is accepted (the target is not inside live), and SHARED_DATA_ROOT then resolves into workspace/, so DATA_ROOT becomes workspace/alto_data. Direct, nested and chain cases are refused. The guard also runs only at import, and walks the whole sandbox root on every import (a seeded full root of about 450k files took about 30 s to walk).
2. ALERT: mode live is accepted in any clone with a .git directory, not only the main checkout on this machine (checkout.py is_main_checkout). My /tmp/qa2/head clone with a live file pointing at production was accepted. Needs a human-written file, so low likelihood.
3. ALERT: commit 8152dde includes an unrelated logs/e2e/progress.jsonl line from the mishap; drop it before merge.

### Dev claims not confirmed
- Dev's suite run on the live root (66 failures): not reproduced; mine used empty roots (83 identical on both sides). Dev's find-based no-change claim is confirmed independently.

### Check that would catch this class
A test that builds a two-hop link and a link to a parent of the live root in a temp dir; make the guard compare realpath of each data_root child, or check realpath(path under data_root) for every PATH constant in paths.py against the live root.
