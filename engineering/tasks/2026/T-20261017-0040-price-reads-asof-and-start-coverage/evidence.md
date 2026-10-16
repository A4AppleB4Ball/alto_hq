---
schema: evidence/v1
task: T-20261017-0040-price-reads-asof-and-start-coverage
round: 2
qa: pass
outputs_changed: unverified
---
# Round 1 (354cbda..b8d3840)

Sandbox checkouts (mode sandbox, data_root /private/tmp/qa0040/sb) for head and base worktrees.

## Acceptance
1. Non-trading as_of: 3 new tests pass (Sat end -> Friday series; holiday end; trading day missing -> raises). PASS, but only with a monkeypatched holiday list. Note: acceptance names `backend/lib/prices`; it does not exist, `backend/lib/market_calendar` was used (reasonable, dev stated it).
2. Start coverage: test passes; listing exemption via CompanyRegistry (NSE-only companies, data/metadata/nse_only_companies_test_results.json, tracked in repo). PASS.
3. Live unchanged: price_feed tests 35 pass, 1 fail (test_cache_past_t_is_still_checked) identically on base and head. PASS.
4. Pilot 20MICRONS (real cache read-only, 2024-01-01..2026-10-13): end 2026-10-17 raises "cache ends 2026-10-13"; end 10-13 ok; end 10-14 raises. Correct per check 1; the live NSE call succeeded. Clamp is NOT exercised on real data.
5. Repo: boundary test passes; entry points import (api.main, lib, asof, workflow.cli, stance/intake runner; I guessed an e2e module name wrong, not run). Full suite head 96F/8E vs base 95F/8E; comm -23 gave one name (test_rebalance_price_action_cooldown::test_cooldown_is_stamped_before_orders_are_queued) that passes on rerun at both head and base (flaky under parallel load, not a regression). PASS.

Verdict is FAIL because of finding 1 (BLOCK per skill: new network/dependency makes a deterministic cache read non-deterministic).

## Findings (reproduced by me; no separate verifier run)
1. BLOCK (answers Q1) dhan_daily_store.py:158-160. Non-live cache read now calls NSE over the network (`nse_trading_holidays` -> `NSE().holiday_list()`, backend/lib/market_calendar/nse_holidays.py:15) whenever cache ends before end. Offline: patched holiday_list to raise -> ConnectionError instead of PriceCacheMissError (reproduced). Year boundary: NSE lists the current year only; `regular_trading_days` raises ValueError when any weekday in the range is in a year with no holiday. Reproduced (/tmp/qa0040/yb.py): cache ends 2026-12-29, end 2027-01-02 with a 2026 list -> ValueError; historical read (cache 2026-12-10, end 2026-12-11) made in 2027 with a 2027 list -> ValueError; cache 2026-12-31, end Sat 2027-01-02 with a 2027 list works. So not a wrong answer, but a loud wrong error type and failure for every prior-year/backtest read with a cache short of end, plus a network dependency in a path meant to be cache-only. A stored list exists: `PAPER_HOLIDAYS_FILE` (backend/config/paths.py:141, read at backend/executor/broker_factory/build.py:44) - JSON of ISO dates, but paper-broker-scoped and presumably current-year too; it is not multi-year. Fix direction: read a stored multi-year holiday list (extend/own one), never the network, raise PriceCacheMissError-compatible error when the list does not cover the range. Owner decision may be needed on which store owns the holidays.
2. ALERT dhan_daily_store.py:~149 starts_after is strict: a start on a weekend/holiday before the first trading day raises. Cache for 20MICRONS starts 2024-01-01; read with start 2023-12-30 raises "cache starts 2024-01-01, after the requested start" (reproduced). A cache built by a fetch from that same start would fail its own re-read. Asymmetric with the end-side clamp. Fix: use the same trading-day logic (no regular trading day in [start, first cached day)).
3. ALERT (Q2) Non-NSE-only symbols have no listing date, so a late-listed BSE-listed/other symbol with a short cache raises. Loud and fail-safe, matches the approved acceptance wording ("recorded by an existing store"); acceptable as-is, but the error message does not say the exemption was unavailable. Judged acceptable.
4. Q3: clamp is proven only by monkeypatched tests; there is no test of the real holiday path, and none of the offline/year-boundary behaviour. Check 4 reading is right. Gap tied to finding 1.
5. Q4: function-level imports with a comment are the simplest option given the cycle (backend.lib init -> asof -> store); acceptable. Removing the network call in finding 1 would likely move the calendar call into a stored-list reader that may not need the cycle.

## Dev claims
All confirmed, including the dev's own note about the network call and year limit (it was disclosed but treated as acceptable).

## Check that would catch this class
A test that runs the non-live read with the network blocked (socket guard) and with a cache end in December / end in January.

# Round 2 (a6d2315..b008fde)

acceptance.md sha256 c7880926... matches the second approval. Sandbox checkouts (data_root /private/tmp/qa0040/sb2) for head and base worktrees. No verifier run: no BLOCK/ALERT-level code defect found; the one ALERT is data coverage, reproduced myself.

## Acceptance
1. Non-trading as_of, stored list, no network: PASS. New tests in backend/price_feed/tests/test_daily_store_without_credentials.py (socket.socket and create_connection patched to raise) pass: Saturday end -> Friday series; holiday end clamped; missing trading day -> PriceCacheMissError; December cache end 2026-12-31 with end 2027-01-02 works with a temp list covering 2026+2027, end 2027-01-05 raises PriceCacheMissError; list without 2027 -> HolidayYearMissingError (years == [2027]); absent file -> HolidayListMissingError. Round 1 BLOCK is gone: the read path no longer calls NSE (only write_holidays does).
2. Start coverage: PASS (cache starts 2026-01-01, start 2024-01-01 -> "cache starts 2026-01-01"; exemption via CompanyRegistry NSE-only listing_date). The message now adds "no listing date is recorded for X (only NSE-only companies have one)" when unavailable. Confirmed.
3. Live unchanged: PASS. price_feed + lib/market_calendar + boundary: 47 pass, 1 fail (test_dhan_daily_store.py::test_cache_past_t_is_still_checked), same failure on base.
4. Pilot 20MICRONS, real cache read-only, real holiday list, network blocked: end 2026-10-17 -> PriceCacheMissError "cache ends 2026-10-13"; end 10-13 ok; end 10-14 and 10-18 raise the same. PASS. Real-list clamp: real cache copied truncated to 2026-10-01 into a temp dir -> end 10-02 (listed holiday), 10-03 (Sat), 10-04 (Sun) return through 10-01; end 10-05 raises. The clamp works with the real list.
5. Start on non-trading day: PASS. Cache from Mon 2024-01-01, start Sat 2023-12-30 reads clean (also real 20MICRONS, start 2023-12-30, end 10-13 ok); cache from 2024-01-02 with 2024-01-01 missing raises. Round 1 ALERT 2 closed.
6. Repo: boundary test pass; entry points import (backend.lib, asof, workflow.cli, stance.runner, intake.runner, price_feed store, write_holidays, api.app_factory). Full suite head 104 vs base 103 failing lines; comm -23 = only api/services/tests/test_partitioned_storage.py::test_partitioned_storage, which collided because I ran head and base suites in parallel on one sandbox root; it passes alone on head. Not a regression.

write_holidays: tests pass explicit tmp paths and monkeypatch nse_trading_holidays; no test uses the default path (only main() does). The real file mtime (03:09) predates my runs; I only read it. `--help` works.

## Real holiday list
~/NSE_BSE_Data/nse_holidays.json: 20 ISO dates, all 2026 (2026-01-15..2026-12-25). Loads.

## Findings
1. ALERT (data, owner): the list covers 2026 only. A non-live read needing the list for another year raises HolidayYearMissingError (loud, right type), e.g. 20MICRONS start 2023-12-01 raises "no holiday in [2023]"; a January 2027 as_of on a December cache needs a 2027 write_holidays run first. Fully covered caches never touch the list. Not a code defect; extend the list for prior years if backtest reads with gaps are expected.
2. Note: the list has weekend dates (2026-02-15, 03-21, 11-08); harmless.

No BLOCK.

## Dev claims
handoff.md not consulted; nothing here contradicts it.

## Check that catches this class
The no_network socket-guard fixture in the new tests; keep it on every non-live price read test.
