---
schema: task/v1
id: T-20261017-1200-nse-holiday-calendar-store
title: "Every holiday reader uses the stored NSE list from T-0040; one sandbox cache-only daily reader; a live job refreshes the list"
status: ready
created: 2026-10-17T12:00+05:30
created_by: claude-main
kind: internal
spawned_from: T-20261016-2336-daily-price-store-everywhere
related: [T-20261016-2336-daily-price-store-everywhere, T-20261017-0040-price-reads-asof-and-start-coverage]
approvals:
  - file: acceptance.md
    sha256: dc1036de7905826fd82b6c4bb392d8a811864e00230d5d9c7f1d2c9d1a51f451
    by: owner
    at: 2026-10-17T15:30+05:30
---

## Goal

Build on the stored holiday list that T-20261017-0040 adds; do not create a second store. After this task, every reader of the NSE holiday calendar reads `stored_nse_holidays()` and never calls NSE; the sandbox has one holiday-aware cache-only daily reader with one error type; index-store errors raise; and a live-only scheduler job keeps the stored list current.

## Why

Owner decision 2026-10-17 (revised the same day). T-2336 check 11 (holiday half) is unmet because `nse_trading_holidays()` calls NSE on every use. T-0040 already provides:

- `paths.NSE_HOLIDAYS_FILE = ~/NSE_BSE_Data/nse_holidays.json`, a single multi-year JSON list of ISO dates, already populated;
- `backend/lib/market_calendar/stored_holidays.py`: `stored_nse_holidays()` and `HolidayListMissingError` (raised naming the path when the file is absent);
- the writer `python -m backend.lib.market_calendar.write_holidays`, which merges NSE's listed year into the file.

QA of T-2336 (evidence.md round 3, A4) also found two sandbox cache-only daily readers with different rules and error types, and a silent `except Exception` around index stores.

## Depends on

Lands after both T-20261017-0040 (commits 38337b9, b008fde) and T-20261016-2336 (branch `eng/T-20261016-2336-daily-price-store-everywhere`). Base the worktree on main once both have merged.

## Proposed design (dev confirms in plan.md)

1. **Readers use the store.** Switch every holiday read to `stored_nse_holidays()`: `require_current` in `backend/price_feed/cached_daily_series.py`, `broker_factory/prices._shared_cache_window`, `broker_factory/daily_series.py`, the paper broker in `broker_factory/build.py`, `price_watchlist/cli.py`, `price_watchlist/capture/market.py`, `api/services/trading_loop_service.py`, and any other caller of `nse_trading_holidays()` that reads (found by grep). `nse_trading_holidays()` remains only as the writer's fetch. Remove `paths.PAPER_HOLIDAYS_FILE`.
2. **One cache-only daily reader (A4).** Merge `cached_daily_series.require_current` / `CachedPriceMissing` and `dhan_daily_store._read_cache_only` / `PriceCacheMissError` into one holiday-aware reader in the price-feed package with one error type. Callers (`prefetch_daily_prices.py`, `DhanDailyPriceStore`, `backtest/cli.py`, broker_factory) use it. A cache is current when its last bar is the last trading day on or before `end`, per the stored list.
3. **No swallowed index errors.** `dhan_daily_store.py` (~211-214) stops catching `Exception` around index stores; a failure raises.
4. **Scheduled refresh.** A `nse_holiday_calendar` job in `backend/config/pipeline_scheduler.yaml` runs `python -m backend.lib.market_calendar.write_holidays`, daily, before `refresh_price_cache`, collision group `data_pipelines`, live machine only (machine gate). The writer refuses to run in a sandbox checkout before any network call (add the gate if T-0040 has not).

## Out of scope

Re-creating or relocating the holiday store; BSE-specific holidays, muhurat/special sessions; backfilling past years NSE no longer lists; gaps inside a cached series.

## Notes

- The first live run of the scheduled job is the owner's call.
- If the stored list lacks a year a reader needs, the reader raises; no weekends-only fallback.
