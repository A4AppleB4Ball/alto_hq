# Plan: T-20261017-1200 (dev run 1)

**Touches:** `backend/price_feed/cached_daily_series.py` (the merged reader), `price_feed/dhan_daily_store.py`
(non-live load, index stores), `executor/broker_factory/{daily_series,prices,build}.py`, `price_watchlist/cli.py`,
`price_watchlist/capture/market.py`, `api/services/trading_loop_service.py`, `config/paths.py` (drop
PAPER_HOLIDAYS_FILE only), `lib/market_calendar/write_holidays.py`, `config/pipeline_scheduler.yaml`.
Entry points: the API (trading loop book check, scheduler), backtest.cli, prefetch_daily_prices, price_watchlist.cli,
AsOfLedger sandbox price path (via broker_factory.daily_series). Callers grepped: `nse_trading_holidays`,
`PAPER_HOLIDAYS_FILE`, `CachedPriceMissing`, `require_current`, `PriceCacheMissError`, `_read_cache_only`,
`listed_after`, `CachedDailySeries`, `CachedDailyPrices`.

**Money path?** Indirect: trading_loop_service's book check decides whether a trading day is a trading day
(holiday source changes from NSE live to the stored file; same dates). No target-weight/order arithmetic changes.

**Change:**
1. One reader `read_cache_only(cache_dir, symbol, start, end)` + one error `PriceCacheMissError`, both in
   `cached_daily_series.py`; holidays read from `stored_nse_holidays()` only when the cache does not span the
   window. Current = last bar is the last regular trading day <= end; start rule (with listing date) as T-0040.
   `listing_date`/`listed_after` move with it. `CachedDailySeries`/`CachedDailyPrices` now take `start`.
2. `DhanDailyPriceStore` index stores: no `except Exception`; a failure raises.
3. Readers call `stored_nse_holidays()`; paper broker too; `PAPER_HOLIDAYS_FILE` removed.
4. `write_holidays` raises `NotLiveCheckoutError` before NSE unless checkout mode is live; scheduler job
   `nse_holiday_calendar` daily 15:45 (before refresh_price_cache 16:00), data_pipelines, local machine via
   machine gate, `enabled: false` (first live run is the owner's call).
Stays the same: live DhanDailyStore fetch path; nse_trading_holidays (writer only).
Owner-visible: the server's book check now needs `~/NSE_BSE_Data/nse_holidays.json` on the server.

**Checks:** 1-2,4-5 greps as written; 3,4,5,7 via `lib/market_calendar/tests/test_holiday_readers.py` and
`price_feed/tests/test_cache_only_reader.py`; 6 `PipelineScheduler()._load_config()`; 7 CLI in the sandbox under a
sitecustomize that blocks connect; 8 pytest with a plugin patching `socket.socket.connect` + dead proxy; 9 full
suite vs base worktree, imports; 10 nothing live run.
