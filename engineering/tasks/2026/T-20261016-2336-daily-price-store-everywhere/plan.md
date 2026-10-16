# Plan

Base: 9801fba (main lacks backend/executor/broker_factory/prices.py). Worktree
`.claude/worktrees/T-20261016-2336-daily-price-store-everywhere`, declared `mode: sandbox`
on an empty root under `alto_sandboxes/` (no production reach).

**Touches:** `backend/api/services/price_chart_service.py` (`_load_daily_bars_from_dhan`,
API chart route), `backend/trading/scripts/rebuild_price_refs.py` (`rebuilt_refs`, CLI),
`backend/trading/harness.py` (`_resolve_price`; callers `_resolve_prices`, line 270, line 434
all forward the caller's `price_store`).

**Money path:** yes (harness prices). Tests pin the DhanPriceStore arguments for a dhan user
at each site; `_resolve_price` with a store is unchanged.

**Change:** each site calls `create_daily_price_store(user, symbols, start, end)`; for dhan
that is `DhanPriceStore(user, symbols, [], start, end)`, identical to before. `_resolve_price`
raises ValueError when `price_store is None` instead of building one (the owner will notice:
any caller relying on the implicit build now raises).

**Known gap:** acceptance 2 as written covers backend/backtest/* and backend/scripts/refresh_price_cache.py,
which also build DhanPriceStore and are outside the goal's three sites. Test written as stated;
reported if it fails.

**Checks:** 1 grep of the three files; 2 `pytest backend/executor/broker_factory/tests/test_no_direct_dhan_price_store.py`;
3 `pytest backend/executor/broker_factory/tests/test_price_store_sites.py`; 4 full suite vs base, boundary test, entry-point imports.

## Round continuation (amendments 2', 5, 6, 7)
- Rebased onto local main 0d07e40 (`rebase --onto main 9801fba`).
- 2': guard test gets an exact-file allowlist (7 named files).
- 5: rebuild_price_refs raises `PaperPriceRefsUnavailable` before building any store when the user's broker is paper.
- 6/7: `paths.DHAN_CACHE_DIR` / `DHAN_CACHE_DAILY_DIR` (same value as the old CACHE_ROOT; dhan_price_store imports it). New read-only `backend/price_feed/cached_daily_series.py` (clamps <= end, raises naming symbol+date when the cache lacks a regular trading day up to end, never writes, no client). New `broker_factory/daily_series.create_symbol_daily_series`: live -> DhanDailyStore (unchanged args), sandbox -> cached series. AsOfLedger._store uses it. `create_daily_price_store`: sandbox + non-paper user -> DailyPriceWindow over the shared cache.
- Not money path beyond price reads; live arguments pinned by tests.
- Checks: pytest on broker_factory/tests, lib/tests asof, price_feed/tests; suite base vs new.

## Round 2 (Amendment 3)
- 9/F1: `backend/price_feed/cached_daily_series.py` gets `read_cached_daily` + `require_current` (one function); `CachedDailySeries` (AsOfLedger) and new `CachedDailyPrices` (fed to `DailyPriceWindow` by `broker_factory/prices._shared_cache_window`) both call it.
- 10/F2: `rebuild_price_refs.require_15min_prices` raises `SandboxPriceRefsUnavailable` for any user when `checkout_mode()=="sandbox"`.
- 11/F3: `DhanInstrumentMapper.load_stored()` reads `WorkspacePaths(user).system_dir/dhan_instruments.json` of any date, never fetches, raises naming the path; `broker_factory/daily_series` injects it as `exchange_of`. 11/F4 (holiday calendar): no stored calendar exists in production; blocked, owner's call.
- 12: `daily_price_service.adjusted_closes` -> `create_symbol_daily_series` (live builds the same `DhanDailyStore(PRICE_USER_ID, SYMBOL, HISTORY_START, end)`).
- Run: targeted tests in executor/broker_factory/tests, api/services/tests; full suite vs a sandbox baseline at 0d07e40.
