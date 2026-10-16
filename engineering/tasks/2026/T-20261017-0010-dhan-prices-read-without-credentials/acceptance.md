# Acceptance: dhan-prices-read-without-credentials

1. **Cache hit, no credentials.** A test in `backend/price_feed/tests/` builds a daily price cache for one symbol covering the window, with no credentials present in the temp workspace, and `AsOfLedger.daily_price_series` returns the prices; no Dhan client is constructed (asserted). Fails on base, passes after.
2. **Miss raises a named error.** With a cache ending before `as_of`, or no cache, and no credentials, the read raises `PriceCacheMissError` naming symbol, start and end. No fallback, no fetch.
3. **Sandbox reads never fetch.** In sandbox and test mode the store never fetches or writes the cache, even when credentials exist (test with fake credentials and a fake client that fails if called).
4. **Production still refetches.** In live mode with credentials, the existing refetch of the tail still happens (existing tests unchanged and passing).
5. **Cache path.** The cache root is a constant in `backend/config/paths.py`, with the same location as today for live; no `Path.home()` in `backend/price_feed/`.
6. **Pilot read.** In a sandbox with no workspace credentials, a read of 20MICRONS prices up to the pilot date succeeds, or raises `PriceCacheMissError` naming the date.
7. **Repo checks.** Boundary test, entry-point imports, full suite vs base with `comm -23` (sandbox root with `data/alto_data` created).
