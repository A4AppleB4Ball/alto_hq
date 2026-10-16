---
schema: evidence/v1
task: T-20261017-1200-nse-holiday-calendar-store
round: 1
qa: fail
qa_by: qa@claude
commits: 9a97ee1..4677511
acceptance_sha256: dc1036de7905826fd82b6c4bb392d8a811864e00230d5d9c7f1d2c9d1a51f451
outputs_changed: unverified
---

## Round 1

QA worktree `.claude/worktrees/T-1200-qa` at 4677511 (sandbox, own data root `alto_sandboxes/T-1200-qa`), base `.claude/worktrees/T-1200-base` at 9a97ee1. All runs had `socket.socket.connect` / `create_connection` patched to raise (wrapper `scripts/nonet.py`) and proxy pointed at 127.0.0.1:9. Raw logs: `news_server/verify_data/reports/T-20261017-1200-nse-holiday-calendar-store/`. The approval sha matches acceptance.md.

### Acceptance check results

1. PASS. The `nse_trading_holidays` grep (excluding tests) lists only `nse_holidays.py:11` and `write_holidays.py:14,32`. Both AST tests pass. The NSE connector importers are all non-holiday users, the fetcher and `market_constants`.
2. PASS. `grep -rn PAPER_HOLIDAYS_FILE backend` is empty. The paths.py diff adds only a comment line.
3. PASS. All 19 `test_holiday_readers.py` tests pass with sockets blocked: each reader with a seeded list, and each reader with the file absent raising `HolidayListMissingError` naming the path.
4. **FAIL as written.** The grep shows one class (`cached_daily_series.py:28 class PriceCacheMissError`). It shows no reader function at all, because the merged reader is public `read_cache_only` (`cached_daily_series.py:51`), which the pattern `_read_cache_only` does not match. With the pattern changed to `read_cache_only` the check passes, and `test_cache_only_reader.py` passes (6 tests).
   - On dev's open point: the intent is met (one reader, one error type). But this check passes only with a changed command, so under the rules it fails.
   - Owner action: amend the pattern in acceptance.md (`_read_cache_only` -> `read_cache_only`) and re-approve. No code change is needed for this check.
5. PASS. `test_an_index_store_that_fails_makes_the_constructor_raise` passes. `grep -n "except Exception" backend/price_feed/dhan_daily_store.py` is empty (rc=1).
6. PASS. `PipelineScheduler()._load_config()` gives `JobConfig(job_id='nse_holiday_calendar', command='python -m backend.lib.market_calendar.write_holidays', daily 15:45, collision_group='data_pipelines', enabled=False)`. `refresh_price_cache` runs daily at 16:00. `runs_on_this_machine('nse_holiday_calendar')` is True locally, and the job is not in `_SERVER_ONLY_JOBS`. `enabled:false` fits "first live run is the owner's call".
7. PASS. `python -m backend.lib.market_calendar.write_holidays --path <tmp>/h.json` in the sandbox exits 1 with `NotLiveCheckoutError`, and the tmp dir stays empty. The same with `nse_trading_holidays` patched to raise AssertionError: the gate raises first.
8. PASS. 92 passed, 4 skipped (e2e marker) for the changed test files plus `price_feed/tests`, `broker_factory/tests` and `market_calendar/tests`, with connect blocked. The only failure was `test_dhan_daily_store.py::test_cache_past_t_is_still_checked`, which also fails at base.
9. PASS.
   - I first ran both full suites concurrently. That produced spurious diffs from collisions between the two runs.
   - I then re-ran every differing file sequentially on head and base. Head: 64 failure lines. Base: 65. `comm -23 head base` is empty.
   - `stores/tests/test_boundaries.py`: 2 passed.
   - All nine entry points import.
10. PASS for QA. No live fetch, no LLM call, no network, no credentials.

### Findings (each confirmed by the verifier)

- **BLOCK F3: the server's book check stops after deploy.**
  - Where: `backend/api/services/trading_loop_service.py:309`, which now reads `paths.NSE_HOLIDAYS_FILE`, set to `Path.home()/NSE_BSE_Data/nse_holidays.json` at `backend/config/paths.py:237`.
  - Why the file never reaches the server: it is untracked in the NSE_BSE_Data repo (`git status` shows `?? nse_holidays.json`). The writer job is local-only and disabled. Nothing else (sync or git) delivers it. The path also ignores the `/mnt/nse_data` server candidate (`paths.py:186`).
  - Scenario: on the server every due book check raises `HolidayListMissingError` inside the try/finally. `record_next` schedules the next check and `_tick_once` logs an error. No proposal is ever cut, and no alert fires.
  - Base called NSE here and worked.
  - Separately: the stored list holds only 2026 (20 dates). From 2027-01-01 every reader, including this one, raises `HolidayYearMissingError` until the disabled writer runs.
  - Dev disclosed the dependency. The task gives no delivery path, so deploying as is breaks the money path.
- **ALERT F1: sandbox reads now refuse three of the four validation-case companies.**
  - Where: `backend/price_feed/cached_daily_series.py:62-74`, now on the sandbox factory path (`broker_factory/daily_series.py:22`, `prices.py:42`).
  - Repro (`scripts/sandbox_series.py`): `create_symbol_daily_series` in the sandbox through 2026-10-15.

    | Company | Start 2025-08-01 (stance `PRICE_START`, used at `backend/stance/runner.py:188`) | Start 2024-01-01 (`AsOfLedger` default `HISTORY_START`) |
    |---|---|---|
    | ARSSBL | raises `HolidayYearMissingError [2025]` | raises `[2024, 2025]` |
    | 511144 | ok | raises `[2024, 2025]` |
    | CHANDAN | ok | raises `[2024, 2025]` |
    | SHILPAMED | ok | ok |

  - Base returns a series for all eight reads.
  - The cause is twofold. First, the stored list lacks 2024 and 2025. Second, these companies have no registry listing date, so even with a full list they raise "cache starts after the requested start".
  - So a sandbox stance or chain run on the ARSSBL@2026-10-15 case now fails. It fails loudly, not wrong-but-green, but it breaks the release cases.
- **ALERT F2: every backtest now fails at store construction.**
  - Where: `backend/price_feed/dhan_daily_store.py:188-193`. `backtest/cli.py:174-180,315-322` always pass a benchmark (`"Nifty 50"` from `trading/config.py:203`, or `"NIFTY 50"`).
  - Why it can never load:
    - `DhanDailyStore` never fetches as an index (`fetch_daily_candles` with the default `is_index=False`).
    - The stored instrument master has no such key.
    - There is no NIFTY parquet in `dhan_cache/daily`.
  - Repro: in the sandbox, `DhanDailyPriceStore('scienceamit1',['SHILPAMED'],['NIFTY 50'],...)` raises `PriceCacheMissError` at head. At base it logs "Failed to fetch index" and builds.
  - The live path (ValueError from `get_security_id`) was checked by reading the code, not run.
  - Check 5 asked for the raise. The owner should know it makes the backtest CLI unusable until the index read is fixed.

### Suite

The sequential re-run of the differing files shows no new failures (head 64 lines, base 65). The pre-existing failure `test_dhan_daily_store.py::test_cache_past_t_is_still_checked` fails on both.

### Dev claims not confirmed

- Handoff says 98 failed / 8 errors on both sides. I got 103 failed / 8 errors on each side in the concurrent run. Only the head-vs-base diff matters, and I confirmed that.
- Handoff describes the start-rule consequence as "a BSE company listed after 2024-01-01 without a registry date now raises". It understates the effect: the missing 2024/2025 holiday years make even stance-start reads raise (ARSSBL).

### Risks / proposed checks

- Candidate invariant: every file a server-side code path reads must have a named delivery path (git-tracked or synced). A test could list server-reachable path constants and assert each one is tracked.
- Candidate check: a sandbox price read for each frozen validation case at its stance `PRICE_START`, run in the suite.
- Skill proposal: the dev/qa suite command should not run head and base concurrently, because the concurrency tests collide.
