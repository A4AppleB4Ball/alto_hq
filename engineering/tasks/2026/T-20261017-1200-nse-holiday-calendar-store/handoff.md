# Handoff: T-20261017-1200 (dev run 1)

- Branch `eng/T-20261017-1200-nse-holiday-calendar-store`, worktree
  `alto/.claude/worktrees/T-20261017-1200-nse-holiday-calendar-store` (sandbox, root
  `alto_sandboxes/T-20261017-1200-nse-holiday-calendar-store/news_server`).
- Base `9a97ee1` (main). Base worktree `.claude/worktrees/T-1200-base` (sandbox, branch `eng/T-1200-base-scratch`, no commits).
- Commits (range `9a97ee1..4677511`):
  - `aba62e8` Price feed: one cache-only daily reader (item 2)
  - `e837890` Price feed: DhanDailyPriceStore raises when an index store fails (item 3)
  - `e35d7a3` Market calendar: every holiday reader reads the stored list; PAPER_HOLIDAYS_FILE removed (item 1)
  - `4677511` Market calendar: write_holidays refuses a non-live checkout; nse_holiday_calendar job (item 4)

## Acceptance checks (run in the sandbox worktree, sockets blocked, proxy 127.0.0.1:9)

1. `grep -rn "nse_trading_holidays" backend --include='*.py' | grep -v tests` -> only
   `lib/market_calendar/nse_holidays.py:11` (def) and `write_holidays.py:14,32`. AST tests
   `test_only_the_writer_imports_nse_trading_holidays`, `test_the_nse_connector_is_imported_only_by_the_fetcher_and_non_holiday_users`
   (allow-list by exact file: exchange_feed, quarterly_watch, annual_report_watch, nse_pipeline, results_calendar/fetch,
   results_calendar/capture, nse_collector) pass.
2. `grep -rn PAPER_HOLIDAYS_FILE backend` -> empty. `git diff 9a97ee1 -- backend/config/paths.py`: removes the
   constant, edits one comment, adds no constant.
3. `lib/market_calendar/tests/test_holiday_readers.py`: for read_cache_only, `_shared_cache_window`, `create_symbol_daily_series`,
   `_paper_broker`, price_watchlist cli `main`, `capture.market.review_days`, `run_book_check_if_due`: with NSE patched to
   raise and a seeded tmp list the seeded result; with the file absent `HolidayListMissingError` matching the path. 19 passed.
4. `grep -rn "CachedPriceMissing\|PriceCacheMissError\|_read_cache_only" backend`: one class
   (`price_feed/cached_daily_series.py:28 class PriceCacheMissError`), no `CachedPriceMissing`, no `_read_cache_only`
   left. NOTE: the merged reader is named `read_cache_only` (public; the grep pattern `_read_cache_only` matched the old
   private method), so the grep as written shows the one class but not the function; `grep -rn "def read_cache_only" backend`
   -> one line `cached_daily_series.py:51`. QA to judge. Tests in `price_feed/tests/test_cache_only_reader.py`: Friday cache
   current for Sat, Sun and stored-holiday Monday; one day short raises naming ACME, "cache ends 2026-10-09",
   "expected a bar on 2026-10-13"; DhanDailyPriceStore and prefetch go through the reader (recorded); broker_factory by source check.
5. `test_an_index_store_that_fails_makes_the_constructor_raise` passes; `grep -n "except Exception" backend/price_feed/dhan_daily_store.py` -> empty.
6. `PipelineScheduler()._load_config()` prints `JobConfig(job_id='nse_holiday_calendar', command='python -m backend.lib.market_calendar.write_holidays',
   schedule daily 15:45, collision_group='data_pipelines', enabled=False, ...)`; refresh_price_cache is 16:00. Gate: not in
   `_SERVER_ONLY_JOBS`, so local machine only (`runs_on_this_machine`), and the writer refuses any non-live checkout.
7. `PYTHONPATH=<sitecustomize blocking connect>:. python -m backend.lib.market_calendar.write_holidays --path /tmp/t1200/h7.json`
   -> `NotLiveCheckoutError: ... this checkout is mode 'sandbox'`, exit=1, file absent. Also a test (subprocess) and a unit test with NSE failing.
8. New tests + T-2336 sandbox price tests (lib/market_calendar, price_feed cache tests, executor/broker_factory, executor/paper,
   trading_loop_service) with a pytest plugin setting `socket.socket.connect` to raise: 117 passed.
9. Full suite (connect blocked) new vs base: both 98 failed / 8 errors (106 lines), `comm -23 new base` empty; new 1759 passed vs
   1732. `stores/tests/test_boundaries.py` passes. All nine listed modules import.
10. No write_holidays live run, no NSE/Dhan/LLM call, no credentials read.

## Behaviour changes the owner must know

- **Server needs the stored list.** `trading_loop_service.run_book_check_if_due` runs on the server and now reads
  `~/NSE_BSE_Data/nse_holidays.json`; before it called NSE. If the server lacks that file the book check raises
  `HolidayListMissingError` every due tick. Put the file on the server before deploying (how it reaches the server is not in this task).
- The scheduler job is `enabled: false`: the first live run is the owner's call; enable it to start the daily refresh.
- The sandbox broker-factory reads (AsOfLedger sandbox path, `_shared_cache_window`) now also apply the start-coverage rule
  T-0040 gave DhanDailyStore (cache must begin by `start` unless the registry says the company listed later). Before, they
  checked only the end. Consequence of one reader; a BSE company listed after 2024-01-01 without a registry date now raises in a sandbox.
- Error messages: the missing day named is now the expected last trading day on or before `end` (was the first missing day).
- Backtests: an index (benchmark) store that fails now fails the replay instead of logging "benchmark unavailable".

## Not done / notes

- Check 4 grep wording vs function name, above.
- `price_feed/tests/test_dhan_daily_store.py::test_cache_past_t_is_still_checked` fails on base and branch alike (pre-existing).

## Found

- `price_watchlist/tests/e2e/test_price_review.py` (e2e, real data) called NSE live through `nse_trading_holidays`; it now
  reads the stored list (the real file), as e2e tests read real data by design.

## Process

- Proposal: the skill's suite command could include `--continue-on-collection-errors` and the socket-blocking plugin used here.
