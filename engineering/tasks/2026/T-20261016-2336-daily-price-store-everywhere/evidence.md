---
schema: evidence/v1
task: T-20261016-2336-daily-price-store-everywhere
round: 1
qa: fail
qa_by: qa@alto_hq
commits: 0d07e40..6eba391
acceptance_sha256: b99f29aafe882f6ac4f333048f2b550df6668075e4f6fbc6a19dde11e5d19101
outputs_changed: unverified
---

## Round 1

QA ran from its own sandbox worktrees: `.claude/worktrees/T2336-qa` at 6eba391 and `T2336-qabase` at 0d07e40, both created with `new_sandbox_worktree`. Raw logs are in `news_server/verify_data/reports/T-20261016-2336-daily-price-store-everywhere/`. QA made no Dhan calls, no LLM calls, no orders and no production writes.

### Acceptance check results
1. PASS. A grep shows that `price_chart_service.py:117` and `rebuild_price_refs.py:53` build their store only through `create_daily_price_store`. `harness._resolve_price` raises when it is given no store (harness.py:233).
2'. PASS. `grep -rln "DhanPriceStore(" backend` outside tests, broker_factory and price_feed returns exactly the 7 files the owner named. The AST guard test passes in the suite.
3. PASS. The live arguments did not change:
   - The factory still builds `DhanPriceStore(user, symbols, [], start, end)`. That is the same call the chart (`"default"`, `[symbol]`, `[]`) and `rebuild_price_refs` made before.
   - AsOfLedger still builds `DhanDailyStore(user, SYMBOL, start, T)`.
   - Tests pin both: `test_price_store_sites.py` and `test_sandbox_shared_cache.py`.
   - The new `execution_broker` call does not change the chart's `"default"` user, because `DhanPriceStore` already called `active_broker` for it.
   - Paper reads use stored prices, and a missing symbol raises.
4. PASS.
   - Full suite: head has 95 failed / 1611 passed / 8 errors; base has 95 failed / 1590 passed / 8 errors. `comm -23 head base` is empty.
   - `stores/tests/test_boundaries.py`: 2 passed.
   - These entry points import: api.main_cockpit, api.local, api.app_factory, e2e.lanes, harness, rebuild_price_refs, price_chart_service.
5. PASS. A paper user gets `PaperPriceRefsUnavailable` before any store is built.
6. **FAIL.** On the `create_daily_price_store` sandbox path, a stale cache does not raise. See F1.
   - The parts that pass: no client is built and no credentials are read. The real cache `~/NSE_BSE_Data/dhan_cache` (5688 files) hashed the same before and after the whole QA run (`d10ba26e…c1036`, stat of name, size and mtime), and the dev tests snapshot the cache bytes too. The AsOfLedger path raises with the symbol and the date.
7. PASS. Both sandbox paths cut the series at the as-of date (dev tests plus a QA read).
8. N/A. No LLM run.

### Findings (each confirmed by the verifier)
- **F1 BLOCK (acceptance 6), backend/executor/broker_factory/prices.py:18-20, 35-41.**
  - A non-paper user in a sandbox gets a `DailyPriceWindow` over the shared cache with no currency check.
  - Scenario: the cache ends 2026-10-07 and the read needs prices through 2026-10-16. `latest_close("ACME","2026-10-16")` returns the 2026-10-07 close, 105.0, without raising. That is a wrong-but-green stale price reaching proposals, triggers and the harness in a sandbox.
  - `CachedDailySeries._require_current` exists but only the AsOfLedger path uses it.
  - Repro: `/tmp/qa2336/test_qa_adv.py::test_stale_cache_store_raises` → `Failed: stale cache returned 105.0 for 2026-10-16 without raising`.
- **F2 ALERT, backend/trading/scripts/rebuild_price_refs.py:53-56.**
  - For a dhan user in a sandbox the factory now returns a `DailyPriceWindow`, so `store.series_15min` raises `AttributeError`. That is the same unclear failure acceptance 5 removed for paper users.
  - Repro: `test_rebuild_refs_dhan_user_sandbox` → `AttributeError: 'DailyPriceWindow' object has no attribute 'series_15min'`.
- **F3 ALERT (owner judgement), backend/price_feed/cached_daily_series.py:57-62 with backend/lib/asof.py:102-103.**
  - Every NSE-only company raises `NotImplementedError` on the sandbox stance price path. Raising is honest (it is not a silent skip).
  - But acceptance 6 says "every daily price read used by the stance run" reads the cache, and for NSE-only companies it cannot. The likely fix is a read-only copy of the instrument master in the shared cache.
  - Confirmed from the code; dev disclosed it.
- **F4 ALERT (owner judgement), backend/executor/broker_factory/daily_series.py:22 with backend/lib/market_calendar/nse_holidays.py.**
  - A stale-cache read in a sandbox makes a live network call to NSE. It is a public endpoint and needs no credentials, but it makes sandbox runs non-hermetic.
  - NSE lists only the current year, so a stale read in a prior year raises `ValueError` ("holiday list covers no holiday in [2025]") rather than `CachedPriceMissing` naming the date. This breaks backtest-style sandbox reads.
  - The verifier reproduced it without network, using a current-year-only holiday set.
- Observation (out of scope): `backend/api/services/daily_price_service.py:31` still builds `DhanDailyStore` directly, outside the gate.

### Judgement on the three items the caller raised
- **NSE holiday fetch:** acceptable only as a stopgap. The holiday list should come from a stored calendar (see F4).
- **NSE-only companies raising:** correct by the no-fallback rule, but it leaves the sandbox stance run incomplete. This is the owner's call (F3).
- **Dhan users in a sandbox reading the cache:** fine on the money path. No client and no credentials, and the broker gate is unchanged. But the read must check that the cache is current (F1), and the 15-minute path must raise clearly (F2).

### Dev claims not confirmed
- Handoff item 6 says "a missing symbol or missing trading day raises CachedPriceMissing". That holds only on the AsOfLedger path. On the factory path a missing trading day does not raise (F1), and a missing symbol raises `FileNotFoundError`, not `CachedPriceMissing`.

### Check that would catch this class
An invariant test: every price store a sandbox can build either raises or covers the last regular trading day through `end`. Parametrize it over every factory return type.
