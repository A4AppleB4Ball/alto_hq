---
schema: evidence/v1
task: T-20261016-2336-daily-price-store-everywhere
round: 2
qa: pass
qa_by: qa@alto_hq
commits: 0d07e40..3becf29
acceptance_sha256: 38c4da22fb594140d8ec136e04062d6108e2f92ae84a03b32a27d964561046a5
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

## Round 2

The approval sha256 38c4da22... matches acceptance.md as it is now (amendments 1-3). QA ran at 3becf29 in its sandbox worktree `.claude/worktrees/T2336-qa`, with `.alto_checkout.yaml` set to mode sandbox and the data root `alto_sandboxes/T2336-qa`. The base was the sandbox worktree `T2336-qabase` at 0d07e40. HTTP(S)_PROXY pointed at a dead port (127.0.0.1:9), and `requests.Session.request` was patched to raise in the repros. QA made no Dhan or NSE calls, no LLM calls, no credential reads, no orders and no production writes. `~/NSE_BSE_Data/dhan_cache` (5688 files) has the same name+size+mtime hash as in round 1, `d10ba26e...c1036`. Logs and the repro file are in `news_server/verify_data/reports/T-20261016-2336-daily-price-store-everywhere/` (`r2_suite_*.log`, `test_qa_r2.py`).

**Owner decision (relayed by the caller):** the NSE holiday half of check 11 (F4) moves to a separate follow-up task, a live job that stores NSE's holiday list per year under a `backend.config.paths` constant. That half is **PENDING on the follow-up task**, not judged here. Every other check was run and judged.

### Acceptance checks
1. PASS. Unchanged since round 1 (grep).
2'. PASS. `grep -rln "DhanPriceStore(" backend | grep -v /tests/ | grep -v broker_factory | grep -v price_feed` returns exactly the 7 named files. `DhanDailyStore(` is built only in `broker_factory/daily_series.py:17` and in `price_feed`.
3. PASS. The live pins pass in `broker_factory/tests` (test_sandbox_shared_cache, test_price_store_sites).
4. PASS.
   - Full suite: head has 98 failed / 1615 passed / 8 errors; base has 98 failed / 1587 passed / 8 errors. `comm -23 new base` is empty (107 lines on each side).
   - `test_boundaries.py` passes.
   - These entry points import: main_cockpit, local, app_factory, e2e.lanes, harness, rebuild_price_refs, price_chart_service, daily_price_service.
5. PASS (round 1).
6. PASS. F1 is fixed:
   - With a stale cache, `create_daily_price_store` for a dhan user in the sandbox raises `CachedPriceMissing: No cached daily price for ACME on 2026-10-08 (cache ends 2026-10-07, read needs through 2026-10-16)` (`test_qa_r2.py::test_F1_stale_store_raises`).
   - A missing symbol raises `CachedPriceMissing` naming NOPE.
   - No client is built and no credentials are read (`load_credentials` was patched to raise).
7. PASS. `series()` ends at or before `end` (`test_F1_current_store_ok_no_lookahead` and the dev tests).
8. N/A. No LLM run.
9. PASS. Both paths call the one `require_current` (cached_daily_series.py:37). The AsOfLedger path and the factory path raise naming the symbol and the date, in QA repros and dev tests.
10. PASS. A dhan user in a sandbox gets `SandboxPriceRefsUnavailable` (`test_F2_rebuild_refs_dhan_sandbox`).
11. Instrument master half: PASS.
    - `load_stored` reads `WorkspacePaths(user).system_dir/dhan_instruments.json` and never fetches.
    - A missing copy raises `FileNotFoundError` naming the path. A copy missing keys raises `ValueError ... lacks [...]`. A stored copy maps ACME to NSE_EQ (`test_F3_stored_master`).
    - Holiday half: **PENDING** on the follow-up task. Both sandbox paths still call `nse_trading_holidays`, a live NSE request, whenever the cache ends before `end`.
12. PASS.
    - `adjusted_closes` goes through `create_symbol_daily_series`. The live arguments `("scienceamit1", SYMBOL, HISTORY_START, end)` are pinned by test.
    - In a sandbox it reads the cache and raises `CachedPriceMissing` when the cache is stale (`test_12_daily_price_service_sandbox`).

`test_qa_r2.py`: 6 passed.

### Findings (each confirmed by the verifier; all ALERT, no BLOCK)
- **A1 ALERT, backend/executor/broker_factory/daily_series.py:36.** It reads the private attribute `mapper._loaded` of DhanInstrumentMapper from another module. Style only.
- **A2 ALERT (operational), daily_series.py:30-39 with dhan_instruments.py:75-77.** No sandbox has a stored instrument master, and nothing installs one. `alto_sandboxes/T2336-qa/.../workspace/scienceamit1/system` does not exist. So every NSE-only check on the sandbox AsOfLedger path raises `FileNotFoundError` until a copy is seeded. Raising is honest, but the sandbox stance run stays incomplete for those companies. Dev disclosed this.
- **A3 ALERT, dhan_instruments.py:69-80.** `load_stored` accepts a master of any date. An unknown symbol raises (`get_exchange` :109-128). A symbol whose exchange listing changed after the stored copy's date returns the old segment without raising.
- Carried over, disclosed by dev: `require_current` checks only the tail of the series, not gaps inside it.

### Dev claims not confirmed
- The suite counts differ: QA saw 98 failed / 1615 passed at head and 98 failed / 1587 passed at base; dev reported 95 / 1618 at head and 95 / 1590 at base. The new-failure diff is empty either way.
- Every other claim was confirmed.

### Check that would catch this class
- A sandbox-hermeticity test that runs each sandbox factory return type with sockets disabled.
- A seeding step (or check) that `new_sandbox_worktree` installs the stored instrument master and the holiday file.
