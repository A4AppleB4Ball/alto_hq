# Handoff (round 2)
Branch eng/T-20261017-0040-price-reads-asof-and-start-coverage, base a6d2315 (current local main), commits 25ae2de (clamp + start coverage), 38337b9 (stored holiday list), b008fde (price feed uses it). Worktree: alto/.claude/worktrees/T-20261017-0040-price-reads-asof-and-start-coverage (clean; only pre-existing untracked backend/data/dashboard).

## QA findings
1. BLOCK network call: fixed (b008fde, 38337b9). NSE_HOLIDAYS_FILE = ~/NSE_BSE_Data/nse_holidays.json in backend/config/paths.py; backend/lib/market_calendar/stored_holidays.py reads it (HolidayListMissingError if absent); write command `python -m backend.lib.market_calendar.write_holidays [--path F]` merges NSE's listing into the stored years (NSE lists the current year only, so run it each year). trading_days.HolidayYearMissingError (ValueError) names the missing year(s). dhan_daily_store._read_cache_only no longer touches the network; the list is only read when the cache does not already cover start..end.
2. ALERT start on weekend/holiday: fixed; start raises only if a regular trading day lies in [start, first cached day).
3. ALERT listing message: fixed; the error says no listing date is recorded for the symbol (only NSE-only companies have one).
4. Tests: offline/year-boundary tests with a socket guard (Dec cache end -> Jan end works with a covering list; names missing year otherwise; missing file raises), weekend-start, start-before-missing-trading-day, write command tests (price_feed/tests/test_daily_store_without_credentials.py, lib/market_calendar/tests/test_stored_holidays.py).

## Acceptance (acceptance.md sha c788...2814, unchanged)
1,2,3,5: targeted run price_feed/tests + market_calendar + test_boundaries: 46 pass, 1 fail (test_cache_past_t_is_still_checked, fails on base too).
4. Pilot 20MICRONS, real cache read-only, temp holiday list in /tmp (the real file is not written; it does not exist yet): end 2026-10-13 ok; 10-14 and Sat 10-17 raise PriceCacheMissError "cache ends 2026-10-13". Clamp on real data still not exercisable until the cache is refreshed.
6. Full suite (sandbox roots) base a6d2315 103 fail/err, new 103; comm -23 empty. Boundary test passes. Entry points import (api.main etc. imported by suite).

## Owner action
Populate the real file: `python -m backend.lib.market_calendar.write_holidays` from a machine with network (writes ~/NSE_BSE_Data/nse_holidays.json), and add past years. Until then non-live reads that need the list raise HolidayListMissingError. Not done: no history of past-year holidays exists to backfill (NSE lists only the current year).
