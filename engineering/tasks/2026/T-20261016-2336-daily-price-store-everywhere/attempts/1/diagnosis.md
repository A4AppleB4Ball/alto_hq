# Attempt 1 (QA round 1 FAIL)

Tried: sandbox reads for non-paper users in create_daily_price_store via DailyPriceWindow over the shared cache (6eba391).
Failed: QA F1, a stale cache returned the 2026-10-07 close for a 2026-10-16 read (evidence.md F1).
Cause: the currency check lived only in CachedDailySeries._require_current (AsOfLedger path); the factory path reused the paper window, which never checks the tail. Round 2 moves the check into one function, cached_daily_series.require_current, used by both paths.
