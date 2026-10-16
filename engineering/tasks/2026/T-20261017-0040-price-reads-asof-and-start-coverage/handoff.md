# Handoff
Branch eng/T-20261017-0040-price-reads-asof-and-start-coverage, base 354cbda, commit b8d3840. Worktree: alto/.claude/worktrees/<task>.
1. Non-trading end: tests test_saturday_end..., test_end_after_a_trading_day..., test_holiday_end... pass (price_feed/tests/test_daily_store_without_credentials.py). Uses backend.lib.market_calendar (regular_trading_days + nse_trading_holidays); backend/lib/prices does not exist and market_day.py is announcement-file based, so market_calendar was used.
2. Start coverage: test_cache_starting_after_start_raises_naming_first_day; listing exemption via CompanyRegistry (backend/raw/utils/company_registry.py, NSE-only companies only; other symbols have no listing date recorded, so they raise).
3. Existing tests unedited; test_cache_past_t_is_still_checked fails on base too.
4. Pilot 20MICRONS (real cache read-only, cache ends Tue 2026-10-13): end 2026-10-17 (Sat) raises PriceCacheMissError "cache ends 2026-10-13", correct since Wed-Fri 14-16 are trading days. No Saturday after 10-13 can clamp until the cache is refreshed; clamp shown by tests only.
5. Suite: 95 failed/8 errors both; comm -23 empty (/tmp lists). Boundary test 2 passed; entry points import.
Notes: function-level imports of market_calendar in _read_cache_only to avoid cycle (backend.lib __init__ -> asof -> store). nse_trading_holidays is a network call to NSE and lists the current year only; reads whose end is beyond the cache by a year boundary raise ValueError. Called only when cache ends before end.
