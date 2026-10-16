---
schema: task/v1
id: T-20261017-1200-nse-holiday-calendar-store
title: "A live job stores NSE's trading holidays per year; every reader reads the stored file and raises when a year is missing"
status: ready
created: 2026-10-17T12:00+05:30
created_by: claude-main
kind: internal
spawned_from: T-20261016-2336-daily-price-store-everywhere
related: [T-20261016-2336-daily-price-store-everywhere, T-20261017-0040-price-reads-asof-and-start-coverage]
approvals:
  - file: acceptance.md
    sha256: 8ddb61d22bf27c9920a421feeb28ee8181db141b97edd183a46fe41b2434cb94
    by: owner
    at: 2026-10-17T13:00+05:30
---

## Goal

NSE's capital-market (CM) trading holidays are stored as one file per calendar year under a new `backend.config.paths` constant, written only by a live job. Every reader of the holiday calendar reads the stored files and raises naming the path and year when the year is missing. No reader calls NSE.

## Why

Owner decision 2026-10-17, option (a) of T-20261016-2336 handoff.md Round 2, F4. That item left check 11 (holiday half) unmet. Today `backend/lib/market_calendar/nse_holidays.py` `nse_trading_holidays()` calls NSE on every use. So the sandbox currency check (`backend/price_feed/cached_daily_series.py` `require_current`, used by `broker_factory/prices._shared_cache_window` and `broker_factory/daily_series.py` on the T-2336 branch) makes a network call. `paths.PAPER_HOLIDAYS_FILE` is a sandbox-only input that nobody fills.

## Proposed design (dev confirms in plan.md)

- **Store.** `paths.NSE_HOLIDAYS_DIR = DATA_ROOT / "market_calendar" / "nse_holidays"`, one `<YYYY>.json` per year: sorted ISO dates plus `fetched_at` and `source`. It is in the data root, so it reaches sandboxes and the server like other live data.
- **Writer.** `backend/lib/market_calendar/` gets separate modules: a fetch (the current `NSE().holiday_list()` call), a store (read/write one year), and a CLI `python -m backend.lib.market_calendar.cli fetch`. The CLI writes the year NSE lists. NSE lists the current year only. It refuses to run in a sandbox checkout (the existing checkout gate). A refetch that differs from the stored year overwrites it and logs the diff.
- **Schedule.** Add a new `nse_holiday_calendar` job to `backend/config/pipeline_scheduler.yaml`. Run it daily, before `refresh_price_cache` (16:00), in collision group `data_pipelines`, with tag `market_calendar`. It is a separate job rather than a step inside `refresh_price_cache`, so a failed NSE call does not block price refresh and each job owns one store.
- **Readers.** `nse_trading_holidays(year)` (or for a span of years) reads only the store. Callers to switch: `cached_daily_series.require_current`, `broker_factory/prices.py`, `broker_factory/daily_series.py`, `broker_factory/build.py`, `price_watchlist/cli.py`, `price_watchlist/capture/market.py` and `api/services/trading_loop_service.py`. In `broker_factory/build.py`, the paper broker's `PAPER_HOLIDAYS_FILE` read is replaced by the store, and the constant is removed.

## Out of scope

BSE-specific holidays, muhurat/special sessions, and backfilling past years NSE no longer lists. The owner seeds those or waives them. Gaps inside a cached series (T-2336 "Not done").

## Notes

- `require_current` and the broker_factory holiday wiring exist only on branch `eng/T-20261016-2336-daily-price-store-everywhere`. This task bases on that branch, or lands after it.
- The first live run is the owner's call. Until a year file exists, every reader raises by design. That includes live `trading_loop_service`.
