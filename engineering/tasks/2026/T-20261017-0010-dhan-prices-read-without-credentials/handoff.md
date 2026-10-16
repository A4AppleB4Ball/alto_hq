# Handoff T-20261017-0010

Branch eng/T-20261017-0010-dhan-prices-read-without-credentials, base 35e1342.
Commits: b814e9e (paths constants), 4f4e5b3 (store). Worktree .claude/worktrees/T-20261017-0010 (sandbox checkout file, root alto_sandboxes/T-20261017-0010).

Acceptance (tests in backend/price_feed/tests/test_daily_store_without_credentials.py, 5 pass, run from backend/):
1. test_cache_hit_returns_prices_through_the_ledger: client builder and fetch patched to fail; AsOfLedger.daily_price_series returns prices. (Not re-run on base; base builds the client in __init__.)
2. test_cache_ending_before_end_raises_named_error, test_no_cache_raises_named_error: PriceCacheMissError(symbol,start,end).
3. test_not_live_never_writes_the_cache, test_rebuild_is_refused_when_not_live; client/fetch patched to fail. Fake credentials were not needed: the client builder is the failing fake.
4. Existing test_dhan_daily_store.py unchanged; passes except test_cache_past_t_is_still_checked, which fails identically on base.
5. DHAN_CACHE_ROOT/_15MIN/_DAILY/_INDEX_DIR in backend/config/paths.py (same location); `grep Path.home backend/price_feed` empty (prices.py now uses paths.nse_data_root()).
6. Sandbox, DHAN_CLIENT_ID/KEY unset: 20MICRONS read through 2026-10-13 gave 691 rows; end 2030-01-01 raised "20MICRONS: daily price cache miss for 2024-01-01..2030-01-01: cache ends 2026-10-13". Read-only on ~/NSE_BSE_Data.
7. Full suite: 103 failures new and base, comm -23 empty. I did not separately run test_boundaries or entry-point imports beyond the suite.

Design: backend/price_feed/fetch_mode.py fetching_allowed() = CHECKOUT.mode == "live", so any non-live mode (incl. test) never fetches/writes. Client is built lazily only on a fetch. exchange_of() uses DhanInstrumentMapper(user_id) alone (no credentials), unchanged semantics.

Owner should know
- Tests: backend/price_feed/tests/conftest.py autouse forces fetching_allowed True so the existing live-path tests stay unchanged; new tests override it.
- A non-live read requires the cache to reach `end` exactly; an as_of on a weekend/holiday past the last cached day raises PriceCacheMissError (spec-literal). Consider using the last trading day.
- Non-live read does not require the cache start <= start (live covers_window does).
- exchange_of in a sandbox may still load/write the instrument master under the sandbox workspace via the mapper (dhan_instruments.py:54-75, public CSV, no credentials).
- prefetch_daily_prices.py is unchanged and now refuses (via PriceCacheMissError) outside live.

Not done: nothing from acceptance; test-data-guard mode:test untested (only "!= live" logic).
