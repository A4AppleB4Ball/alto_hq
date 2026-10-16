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
