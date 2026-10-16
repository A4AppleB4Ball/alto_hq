# Handoff: T-20261016-2336-daily-price-store-everywhere (continuation after amendments 2', 5, 6, 7, 8)

Branch `eng/T-20261016-2336-daily-price-store-everywhere`, worktree `alto/.claude/worktrees/T-20261016-2336-daily-price-store-everywhere`.
Base is local main **0d07e40**. I rebased with `git rebase --onto main 9801fba`: a plain rebase replayed the pre-squash paper-broker commits and conflicted, so I aborted it.
Commits, oldest first: 87984e5 (chart), e61ada7 (rebuild via factory), 501ea2d (harness raises), 826b0d8 (site tests), d8eecc5 (AST guard), 400c845 (paths constants), b01157f (guard named exceptions), c697cea (rebuild paper error), 6eba391 (sandbox shared-cache reads).
The worktree has an untracked `.alto_checkout.yaml` (mode sandbox). I wrote no production data and no cache data, made no Dhan or LLM calls and read no credentials.

## Acceptance
1. PASS. A grep of the three files finds only `create_daily_price_store(` (price_chart_service.py:117, rebuild_price_refs.py:53). `_resolve_price` raises when no store is passed (`test_resolve_price_raises_without_a_store`).
2'. PASS. `executor/broker_factory/tests/test_no_direct_dhan_price_store.py` lists the 7 named files under `NAMED_EXCEPTIONS`, matched by exact path. A second test fails if any named file stops existing.
3. PASS. `test_price_store_sites.py` and `test_daily_price_store.py` pin the live Dhan arguments and cover paper reads of stored prices. A missing symbol raises.
5. PASS. `rebuilt_refs` raises `PaperPriceRefsUnavailable("...15-minute price refs are not available for the paper broker...")` before it builds any store (`test_paper_rebuild_refs_raises_a_clear_error_and_builds_no_store`). The old AttributeError path is gone.
6. PASS (tests in `executor/broker_factory/tests/test_sandbox_shared_cache.py`). New constants `paths.DHAN_CACHE_DIR` and `DHAN_CACHE_DAILY_DIR` hold the same value as the old `CACHE_ROOT`; `dhan_price_store` now imports them. The new `broker_factory/daily_series.create_symbol_daily_series` returns `DhanDailyStore` in a live checkout. In a sandbox it returns `price_feed/cached_daily_series.CachedDailySeries`, which reads parquet only and builds no client. `AsOfLedger._store` uses it. `create_daily_price_store` gives a non-paper user in a sandbox a `DailyPriceWindow` over the shared cache. The tests check that the cache bytes are unchanged, that `load_credentials` and both Dhan store classes are never called, and that a missing symbol or missing trading day raises `CachedPriceMissing` naming the symbol and the date. Live is pinned by tests: AsOfLedger gets `DhanDailyStore(user, SYMBOL, "2024-01-01", T)` and the factory gets `DhanPriceStore(user, syms, [], start, end)`.
7. PASS. Both sandbox paths cut the series at T (`test_*never_returns_a_price_after*`).
8. N/A. No LLM run.
4. PASS.
   - Suite run from backend/ with --continue-on-collection-errors. Base 0d07e40: 95 failed / 1590 passed / 8 errors. New: 95 failed / 1611 passed / 8 errors.
   - `comm -23 new base` is empty, and so is `comm -13`.
   - `test_boundaries.py` passes.
   - These import: intake.runner, stance.runner, e2e.run, workflow.cli, execution.runner, raw.master_pipeline, backtest.replay, api.app_factory, rebuild_price_refs.
   - Targeted: broker_factory/tests, lib/tests, price_feed/tests, trading/tests. The only failure is `price_feed/tests/test_dhan_daily_store.py::test_cache_past_t_is_still_checked`, which also fails on base.

## Behaviour changes the owner must know
- **Sandbox, NSE-only companies:** `CachedDailySeries.exchange_of()` raises NotImplementedError (cached_daily_series.py, end of file). The NSE_EQ check in AsOfLedger needs the Dhan instrument master, which a sandbox does not fetch, so a sandbox stance run raises for NSE-only companies. Fixing it needs an owner call, for example a read-only copy of the instrument master in the shared cache. I did not skip the check.
- **Sandbox, stale cache:** if the cache ends before the last regular trading day through T, the read raises. Only in that case is `nse_trading_holidays()` called, which is a network call to NSE (not Dhan). NSE lists only the current year, so if the stale span crosses into a prior year the read raises "holiday list covers no holiday".
- A sandbox read at T = today, before today's bar is cached, raises. A live read would fetch.
- A dhan user in a sandbox no longer gets BrokerNotAllowedInCheckout from `create_daily_price_store`; they read the shared cache. The broker client gate itself is unchanged.
- Carried over from the earlier attempt: callers of `_resolve_price` / `process_trigger` with no store now raise.

## Found
- `PriceSource` (harness.py:52) does not name `DailyPriceWindow` or `CachedDailySeries`. This is a type annotation only.
- `price_feed/tests/test_dhan_daily_store.py::test_cache_past_t_is_still_checked` already fails on main.

## Round 2 (after QA round 1 FAIL; Amendment 3)

Branch `eng/T-20261016-2336-daily-price-store-everywhere`, base 0d07e40 (main has not moved), round-1 head 6eba391, round-2 commits 6a28349, 3becf29.

### Findings
- **F1 fixed (6a28349).** `cached_daily_series.require_current(symbol, series, end, holidays)` is the one currency check. `CachedDailySeries` (AsOfLedger path) and the new `CachedDailyPrices` (fed to `DailyPriceWindow` by `broker_factory/prices._shared_cache_window`) both call it. A stale cache raises `CachedPriceMissing` naming the symbol and the first missing day. A missing symbol on the factory path now raises `CachedPriceMissing` (it used to be `FileNotFoundError`). Tests: `test_dhan_user_in_a_sandbox_raises_for_a_stale_cache_naming_symbol_and_date`, `..._for_a_missing_trading_day`, `test_both_sandbox_paths_share_one_currency_check`. All three fail before the fix.
- **F2 fixed (3becf29).** `require_15min_prices` raises `SandboxPriceRefsUnavailable` for any user in a sandbox, before any store is built. Test: `test_dhan_rebuild_refs_in_a_sandbox_raises_a_clear_error_and_builds_no_store`.
- **F3 fixed (6a28349).** In a sandbox, the NSE-only exchange check reads the user's stored instrument master, `WorkspacePaths(user).system_dir/dhan_instruments.json` (this is where live already caches it), through `DhanInstrumentMapper.load_stored()`. That read accepts a copy of any date, never fetches, and raises naming the path when the copy is missing or incomplete. Tests cover the missing copy, a correct mapping read from the stored master with the fetch patched to fail, and a BSE_EQ mismatch. They also check the file bytes are unchanged.
  - A sandbox only has this file if it is seeded into its workspace. Today it is not seeded, so NSE-only reads raise naming the path.
- **F4 NOT fixed, BLOCKED: owner decision.** No stored NSE holiday calendar exists anywhere in production.
  - Searched: `news_server/data` (to depth 4), `~/NSE_BSE_Data` and `backend/config`. Live calls NSE on every use (`backend/lib/market_calendar/nse_holidays.py:13`).
  - `paths.PAPER_HOLIDAYS_FILE` (`paper_broker/nse_holidays.json`) is a sandbox-only input. It does not exist in the production root or in this sandbox.
  - As instructed, I did not invent one. Both sandbox paths still call `nse_trading_holidays` (a network call to NSE) when, and only when, the cache ends before `end`. A year NSE does not list raises `ValueError`.
  - Owner's choice: (a) a live job that stores NSE's list per year under a `backend.config.paths` constant, with sandboxes reading it, or (b) reuse `PAPER_HOLIDAYS_FILE` and define who fills it.
- **Check 12 fixed (3becf29).** `daily_price_service.adjusted_closes` uses `create_symbol_daily_series`. A test pins that live builds the same `DhanDailyStore("scienceamit1", SYMBOL, HISTORY_START, end)`, and a sandbox reads the cache without building one. The existing tests in `api/services/tests/test_daily_price_service.py` now patch `create_symbol_daily_series` instead of `DhanDailyStore`. The assertions are unchanged.

### Acceptance
- 1, 2': the grep for `DhanPriceStore(` outside tests, broker_factory and price_feed returns only the 7 named files. There is no `DhanDailyStore(` outside the factory or price_feed.
- 3, 6, 7, 9, 10, 12: pinned by tests in `backend/executor/broker_factory/tests/` (39 passed).
- 11: instrument master half done; holiday calendar **not met** (F4).
- 4: entry points import (main_cockpit, local, app_factory, e2e.lanes, harness, rebuild_price_refs, price_chart_service, daily_price_service, asof, intake.runner, stance.runner, workflow.cli). `stores/tests/test_boundaries.py`: 2 passed.
- Suite: head 95 failed / 1618 passed / 8 errors. Base is the sandbox worktree T2336-qabase at 0d07e40: 95 failed / 1590 passed / 8 errors. `comm -23 new base` is empty.
  - A base resolving the production root showed about 40 extra data-root failures, so it is not comparable.
- QA's `/tmp/qa2336/test_qa_adv.py::test_stale_cache_store_raises` now raises instead of returning 105.0.
- 8: no LLM run.

### Not done
- F4 / check 11 holiday half: `backend/executor/broker_factory/prices.py` (`_shared_cache_window`) and `backend/executor/broker_factory/daily_series.py` still pass `nse_trading_holidays`.
- `require_current` checks only the tail of the cache. A gap inside the series (for example ACME has no bar on 10-06 in the fixture) is not checked on either path, the same as round 1.

### Found
`price_feed/tests/test_dhan_daily_store.py::test_cache_past_t_is_still_checked` also fails at base 0d07e40. It is outside this task.

## Round 3 (rebase onto local main; owner decision, no code change)

- Rebased `eng/T-20261016-2336-daily-price-store-everywhere` onto local main **1665a1c** (main as of the start and the end of this round; no T-2235 ship landed in between). Old range 0d07e40..3becf29. **New range 1665a1c..58e69ed**, 10 commits: 6668565, 3b76a1d, 6195c30, d2af601, cdf574c, 3e143d4, fc0f20c, 0339c05, 727b697, 58e69ed.
- The only conflicts came from 400c845 (`DHAN_CACHE_DIR` in paths.py and dhan_price_store.py). I kept main's versions of both hunks (`DHAN_CACHE_ROOT`/`_15MIN_DIR`/`_DAILY_DIR`/`_INDEX_DIR` from 4a75794). The commit became empty, so git dropped it. `DHAN_CACHE_DIR` and `CACHE_ROOT` no longer appear anywhere under backend/. The branch's later code uses only `paths.DHAN_CACHE_DAILY_DIR`, which has the same name and value on main. No other conflicts.
- Main's 354cbda (DhanDailyStore reads the cache without credentials and raises PriceCacheMissError) sits beside this task's sandbox path, and neither replaces the other. In a sandbox, `create_symbol_daily_series` still returns `CachedDailySeries`, and in a live checkout it still returns `DhanDailyStore`. I made no design change here. The owner or a follow-up may want to merge the two cache-read paths.

### Checks (sandbox worktrees from new_sandbox_worktree: head `.claude/worktrees/T2336-r3` at 58e69ed, base `.claude/worktrees/T2336-r3base` at 1665a1c)
- 1, 2': a grep for `DhanPriceStore(` outside tests/broker_factory/price_feed returns only the 7 named files. There is no `DhanDailyStore(` outside them. The AST guard test passes.
- 3, 5, 6, 7, 9, 10, 12: broker_factory/tests, price_feed/tests, lib/tests/test_asof_prices.py, api/services/tests/test_daily_price_service.py, trading/tests and stores/tests/test_boundaries.py gave 183 passed and 1 failed. The failure is `price_feed/tests/test_dhan_daily_store.py::test_cache_past_t_is_still_checked`, which also fails on base 1665a1c.
- 11: the instrument master half passes (tests). The holiday half is still not met and waits on T-20261017-1200 (F4 above).
- 8: no LLM run. I made no Dhan, NSE or LLM calls, read no credentials, and wrote nothing to production or ~/NSE_BSE_Data.
- 4: the full suite with --continue-on-collection-errors gives head 95 failed / 1684 passed / 8 errors and base 95 failed / 1656 passed / 8 errors. `comm -23 new base` is empty, and so is `comm -13`. Boundary test passes. These import: intake.runner, stance.runner, e2e.run, workflow.cli, execution.runner, raw.master_pipeline, backtest.replay, api.app_factory (with the env vars), rebuild_price_refs, price_chart_service, daily_price_service, lib.asof, trading.harness.
- Found: the suite leaves an untracked `backend/data/dashboard/chart_profiles.duckdb` in the worktree it runs in. Main's checkout has the same file. It is outside this task.
