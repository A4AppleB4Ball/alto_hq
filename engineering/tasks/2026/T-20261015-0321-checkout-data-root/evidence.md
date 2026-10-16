---
schema: evidence/v1
task: T-20261015-0321-checkout-data-root
round: 1
qa: fail
qa_by: qa@claude
commits: 9950df7..20e6afe
acceptance_sha256: 0d5e9c9923dfbb324bdcd5428c1b9b9724493636b1386191fea565feecaa6a95
outputs_changed: unverified
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
