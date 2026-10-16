---
schema: evidence/v1
task: T-20261017-0010-dhan-prices-read-without-credentials
round: 1
qa: pass
qa_by: qa@sonnet-5.5
commits: 35e1342..4f4e5b3
acceptance_sha256: 9ca723ab66cb7fa0e9a595abb0353b1b8c46cf708458f968c7efa11def4f11d8
outputs_changed: unverified
---

## Round 1

### Acceptance check results
Own worktrees (head, base) with a temp sandbox declaration (/tmp/qa0010/sb with data/alto_data); no credentials, none read.
1. PASS. `pytest backend/price_feed/tests` at head: new tests pass. Base: new test file cannot import PriceCacheMissError; and a behavioural script (cache covering window, no active broker) fails on base with BrokerNotConfiguredError, returns OK at head.
2. PASS. Cache ending before end, and no cache, raise PriceCacheMissError naming symbol/start/end (test + real 20MICRONS 2026-10-17: "cache ends 2026-10-13").
3. PASS (with note). Tests make the client builder and fetch fail if called, and assert cache bytes unchanged; fetching_allowed() = CHECKOUT.mode == "live". Fake credentials were not literally supplied, but the gate runs before any credential path, so this is equivalent.
4. PASS. test_dhan_daily_store.py unchanged; 7 pass, test_cache_past_t_is_still_checked fails identically on base (pre-existing). conftest.py forces live for those tests (new file, existing tests untouched).
5. PASS. DHAN_CACHE_* in backend/config/paths.py, same location; no Path.home in backend/price_feed.
6. PASS. Sandbox, no DHAN env: 20MICRONS read through 2026-09-29 ok (cache max 2026-10-13); 2026-10-17 raises PriceCacheMissError naming date. Cache only read.
7. PASS. Full suite 103 failures head vs 104 base, `comm -23 new base` empty. test_boundaries.py 2 passed. Imports ok for prefetch_daily_prices, lib.asof, daily_price_service, dhan_daily_store, stance.runner, intake.runner (backend.executor.runner / e2e.runner do not exist on either).

### Live path (extra asks)
Live is only allowed in the main checkout (checkout.py:118-121 refuses live elsewhere), so fetching_allowed() is true exactly in production main. In live, _load is the old code path (CACHE_DAILY mkdir, covers_window, tail refetch) except the client is built lazily at first fetch; prefetch_daily_prices, API daily_price_service and AsOfLedger therefore still fetch there. The executor does not use DhanDailyStore (only dhan_client; untouched). Risk: it depends on the server's gitignored .alto_checkout.yaml saying mode live; if missing, the base guard already refuses import. Not testable here (I did not run in the main checkout).

### Findings
1. ALERT. dhan_daily_store.py `_read_cache_only` (~line 132-141): non-live read needs cache max >= end exactly. as_of on a Saturday/Sunday/market holiday raises PriceCacheMissError (confirmed: cache through Fri 2026-09-25, end 09-26 raises). Live handles this by tail fetch. Fails loud, not wrong-but-green, so ALERT; but stance with weekend as_of in a sandbox will halt. Needs an owner decision (clamp as_of to last trading day vs. keep strict); worth a follow-up task.
2. ALERT. Same function does not check the cache start (live covers_window does via starts_after). A cache beginning after `start` returns a short series silently (confirmed: cache from 2026-01-01, start 2024-01-01, ok). Loud failure is not guaranteed for truncated caches; legit late-listed symbols look identical. Follow-up.
3. ALERT (minor). exchange_of() in a sandbox may write the instrument master under the sandbox workspace (dhan_instruments.py); no credentials, no production write.

Findings were reproduced directly by me with scripts; I did not spawn a separate verifier.

### Suite
Head 103 failing, base 104, comm -23 empty.

### Dev claims not confirmed
Handoff claims 20MICRONS 691 rows and the 2030 miss; I used different dates (same behaviour). Dev did not run boundary/imports; I did. All else matched.

### Risks / catching this class
Add a test: non-live read for as_of on a weekend after a Friday-ending cache, and a cache with a late start, so the chosen behaviour is pinned.
