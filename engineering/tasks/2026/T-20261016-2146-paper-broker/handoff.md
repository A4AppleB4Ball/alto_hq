# Handoff: T-20261016-2146-paper-broker

- Branch `eng/T-20261016-2146-paper-broker`, base `main` 9950df7. Commits:
  d9e98db (PaperBroker + fill model), c6d2870 (broker factory + checkout gate + wiring),
  f706d57 (cockpit broker switch stays dhan/kite). Local only, not pushed.
- **Merge order: must land after T-20261015-0321-checkout-data-root.** The gate reads
  `backend.config.paths.CHECKOUT.mode` (lazy import in `backend/executor/broker_factory/gate.py`).
  On main alone, building any broker raises ModuleNotFoundError, i.e. live Dhan trading stops.
- Check-4 tree: `.claude/worktrees/T-20261016-2146-check4`, a detached merge of this branch onto
  `eng/T-20261015-0321-checkout-data-root` 20e6afe (merge HEAD b4a6523). Its `.alto_checkout.yaml` is
  `mode: sandbox`, root `alto_sandboxes/T-20261016-2146-check4/news_server` (empty, mine).
  Its baseline is `.claude/worktrees/T-20261016-2146-check4-base` (20e6afe, same yaml).

## Acceptance checks
All run from `backend/` with `PYTHONPATH=.. SESSION_SECRET=x ALLOWED_EMAILS=a@b.c GOOGLE_CLIENT_ID=x GOOGLE_CLIENT_SECRET=x GOOGLE_REDIRECT_URI=http://x python -m pytest -v -p no:cacheprovider --rootdir=.`
in the check-4 tree: `executor/broker_factory/tests executor/paper/tests` gives **15 passed**.

1. Interface: `executor/paper/tests/test_interface.py` (2 passed). AST scan of manager.py, reconcile.py,
   ledger_sync.py, plus the modules they hand the client to (slice_placement.py: order_by_correlation_id;
   fill_ledger.py: fills; trading/portfolio.py: holdings, positions, funds, open_buy_orders,
   ledger_totals, transaction_charges, is_token_valid; dependencies.py: ltp). ledger_sync.py itself
   calls no client method directly; it passes the client on. Signatures compared to DhanClient
   with `inspect.signature` (name, kind, default).
2. Fill model: `executor/paper/tests/test_fill_model.py` (6 passed): yesterday's-data → today's open;
   today's-data → next trading day's open (over a holiday); sell; off-lot refused and whole lots fill;
   no bar on fill day → REJECTED "FC11: no stored price…", no fill even once the next day has a bar;
   stance dated after the session raises (look-ahead). Slippage: `PAPER_SLIPPAGE_BPS` in
   `backend/executor/paper/fill_model.py`.
3. Book: `executor/paper/tests/test_book.py` (2 passed). Hand calculation of cash, avg cost,
   marks, current.json and the FillLedger after 4 fills and 1 FC11 rejection.
4. Live refusal: `executor/broker_factory/tests/test_checkout_gate.py` (4 passed on the check-4 tree):
   live+paper raises, sandbox+dhan raises without reading credentials, sandbox+paper builds
   PaperBroker, live+dhan still builds DhanClient. Also against the tree's real sandbox declaration
   (no patching of CHECKOUT): `create_broker_client` with dhan →
   `BrokerNotAllowedInCheckout: Broker 'dhan' may only be built in a live checkout; this checkout is mode 'sandbox'.`
5. End to end: `executor/paper/tests/test_end_to_end.py` (1 passed). Sockets blocked
   (connect, create_connection, getaddrinfo). Real submit_decision → intent book →
   ExecutionService.tick ×8 → Reconciler.run. Order events: QUEUED→ANALYZING→PLACING→
   LIVE (PAPER-1)→FILLED "Reconciled: broker reports TRADED (60 shares)". The ledger and current.json are updated.
   Patched: time-of-day helpers, planner inputs/plan_orders, lot lookup, ADV, previous_close, and
   `execution.service.create_broker_client` (returns the test's broker; the factory is check 4).
6. Suite (full, `.` from backend, `--continue-on-collection-errors`):
   - branch vs main: 67 → 66 failed; `comm -23` = only `ERROR executor/broker_factory/tests/test_checkout_gate.py`
     (ModuleNotFoundError backend.config.checkout: the expected dependency).
   - check-4 merge vs dependency branch: 92 → 91 failed; `comm -23` empty.
   - `stores/tests/test_boundaries.py` passes in both. Entry points import (intake.runner, stance.runner,
     e2e.run, workflow.cli, execution.runner, raw.master_pipeline, backtest.replay, api.main_cockpit,
     api.local) on both trees.

## Behaviour changes the owner must know
- One broker factory, `backend/executor/broker_factory/build.py`. `execution/service.py` and
  `RebalanceService._create_broker_client` (used by the trading loop) both go through it. The rebalance
  service had its own copy of the Dhan builder, so a sandbox could have reached Dhan through it.
  Its "not authenticated" message is now "No access_token — complete broker login first".
- `credentials.VALID_BROKERS` now includes "paper". `SELECTABLE_BROKERS` = dhan, kite drives the cockpit
  dropdown, and PUT /api/system/broker answers 400 for paper. `has_valid_token` is True for paper and reads no credentials.
  Also removed the unreachable duplicate body of `has_valid_token`.
- `ledger_sync.sync_ledger` accepts dhan and paper (`FILL_REPORTING_BROKERS`).
- Paths: `PAPER_BROKER_DIR`, `PAPER_PRICES_DIR`, `PAPER_HOLIDAYS_FILE` (shared, under DATA_ROOT);
  `WorkspacePaths.paper_broker_dir` (account.json per user). Added `BookStore.desired_path()` and
  `DhanInstrumentMapper.tick_map()`.

## Owner decisions needed / not done
- **Slippage value.** The epic says "fixed slippage from the research protocol". No research protocol
  states a number. I used 5 bps (backtest/replay.py ReplayConfig default) in `PAPER_SLIPPAGE_BPS`
  (backend/executor/paper/fill_model.py:20). Please confirm it or name the value.
- **"Partial lot rounding" (check 2).** I read this as: an off-lot quantity is refused and never rounded, as in
  DhanClient, and whole lots fill. The broker makes no partial fills (no liquidity model). If you meant
  something else, say so.
- **Stance date source.** `DesiredStanceDates` reads `signal.signal_date` from desired.json and raises
  for a symbol with no entry, so a sell of a name dropped from desired cannot be placed with paper.
  The intent book carries no stance date.
- Limit price does not gate a paper fill (owner model: open + slippage). Fills settle at once
  (positions() is always empty; unsettled is 0). There are no charges.
- Seeding (prices parquet, holidays json, account.open deposit, active_broker "paper") belongs to the
  release runner and is not built here.

## Found (outside the task)
- `execution/market_analysis/adv.py:48` (`average_daily_volume`) and `previous_close` build
  `DhanPriceStore`, which can fetch from Dhan. A real paper sandbox EMS would make Dhan calls through them.
  The release runner needs stored-price readers here; the e2e test patches them.
- `paper` factory uses `DhanInstrumentMapper` for lots/ticks; a stale instrument cache downloads the
  public instrument master (unauthenticated HTTP). It should be seeded in a sandbox.
- `scripts/refresh_price_cache.py` picks users by `has_valid_token`; a paper user now qualifies (sandbox only).

## Proposed process change
- The dev skill's suite command needs `--continue-on-collection-errors`. Without it a single
  collection error stops pytest, and the FAILED list comes back with one line (first run of this task).

# Round 2 (last attempt)

- Branch `eng/T-20261016-2146-paper-broker`, new commits 401cc22 (A2), 70c1c1c (B1). Range for QA: 9950df7..70c1c1c.
- Check tree: `.claude/worktrees/T-20261016-2146-r2-merge` = detached merge of 70c1c1c onto 20e6afe (merge HEAD local, not on any branch),
  `.alto_checkout.yaml` mode sandbox, root `alto_sandboxes/T-20261016-2146-r2/news_server` (created empty, only `data/alto_data/`).
  Baseline `.claude/worktrees/T-20261016-2146-r2-mbase` (20e6afe), own empty root `alto_sandboxes/T-20261016-2146-r2-base/news_server`.

## Findings answered
- **B1 fixed (70c1c1c).** `previous_close`/`average_daily_volume` (`backend/execution/market_analysis/adv.py:48,81`) now build their store with
  `backend/executor/broker_factory/prices.py:create_daily_price_store`, gated by the same `execution_broker` + `require_broker_allowed(checkout_mode())`
  as `create_broker_client`. dhan → `DhanPriceStore(user, [symbol], [], start, today)` (the identical call as before, so live is unchanged);
  paper → `StoredDailyPrices(PAPER_PRICES_DIR)`, the store PaperBroker fills from (added `series()`). Missing symbol raises FileNotFoundError.
  `test_end_to_end.py` no longer patches previous_close, ADV, create_broker_client, `_lot_sizes_for`/`load_lot_sizes`, `load_active_config`,
  `_load_desired`, `_reject_if_stale`, `is_market_open`, `is_past_hard_cutoff`, `initial_delay`, `hold_for_open_auction`. It seeds the sandbox
  (CHECKOUT mode sandbox over tmp, prices, holidays, today's instrument-master cache, `migrate_to_preset(v2)`, desired.json signal_date, account)
  and fixes one clock (`ist_now` in manager/adv/reconcile/lib.market_day and `jitter.datetime`, advanced 1 min per tick).
  **Still patched, stated in the test docstring:** `RebalanceService._build_planner_inputs` and `plan_orders` — the proposal is given, since
  planning from stored stances (completeness gate, watchlist, stance store) is not this task. If QA reads "may only seed stores" as covering the
  planner too, this is not done.
  Fail-before: the new test on the round-1 merge (check4 tree, files copied in then restored) fails with `DhanPriceStore requires BROKER=dhan. Current: paper` on every placement attempt.
  Fixture change: stored daily volume is 1,000,000 (`paper_fixtures.VOLUME`); at 1,000 the real ADV picks split TWAP and the 30-share slice trips the min-notional guardrail, which is real behaviour, not a bug.
- **A2 fixed (401cc22).** `PaperAccountStore.update()` (`backend/executor/paper/state.py`) loads/modifies/saves under `stores.locking.exclusive_lock`
  with `atomic_write_text`; `open()` also under the lock. `place_order`/`cancel_order` settle and write inside it; every read path settles in memory
  and never writes. Order ids are `PAPER-{orders_issued}` from a persisted counter. New `executor/paper/tests/test_account_concurrency.py`
  (3 tests: two broker instances on two threads placing+reading 25 orders each, reads leave account.json byte-identical, ids not reused after a cancel);
  all 3 fail on round-1 code, pass now. account.json now requires `orders_issued` (no default); round-1 sandbox accounts must be reopened.
- **A1 (merge order), unchanged:** ship must land T-20261015-0321-checkout-data-root (20e6afe) before this branch; on main alone the gate raises ImportError for every broker build, now including the daily price store for previous close/ADV.

## Acceptance checks (round 2, r2-merge tree, from backend/ with the dummy env)
- QA's command `pytest executor/paper executor/broker_factory executor/tests/test_credentials.py api/routes/tests/test_broker_switch.py config/tests` → **73 passed**.
- Check 5: `executor/paper/tests/test_end_to_end.py` → 2 passed (e2e filled 60 @ 102×(1+5bps), ledger + current.json; and stored-price previous close/ADV with a missing symbol raising). Sockets blocked.
- Checks 1–4: unchanged tests pass inside the 73.
- Check 6: `executor execution stores/book stores/tests/test_boundaries.py` → 38 failed, 268 passed; all 38 are in the baseline list. Full suite `--continue-on-collection-errors`:
  merge 83 failed/1551 passed/8 errors; base 83 failed/1531 passed/8 errors; `comm -23` empty (91 lines each). Boundary test 2 passed.
  Entry points import (intake.runner, stance.runner, e2e.run, workflow.cli, execution.runner, raw.master_pipeline, backtest.replay, api.main_cockpit, api.local).
- No order placed or cancelled, no credentials read, no production data written (suite writes landed in the temp sandbox root).

## Not done / open
- Owner decisions untouched: 5 bps slippage, off-lot refusal, signal_date source.
- Planner inputs in the e2e test remain given (above).
- Found, not fixed: `price_feed/feed.py:43`, `dhan_client_cli.py:23`, `api/routes/dhan_auth.py:259` build DhanClient outside the factory (QA observation); the paper factory still downloads the instrument master if no fresh cache is seeded.

## Owner decisions (2026-10-16, in session)

Accepted as built: 5 bps slippage (`PAPER_SLIPPAGE_BPS`); off-lot orders refused, never rounded, no partial fills; stance date from `signal.signal_date` in desired.json (a name absent from desired raises); limit price not gating, instant settlement, no charges.

# Round 3 (owner-authorized new round after QA round 2 FAIL B2)

- Branch `eng/T-20261016-2146-paper-broker` rebased onto main 9013baa (T-20261015-0321-checkout-data-root now on main; rebase was clean, no merged-tree workaround). Rebased commits d147853, 365b1cd, a413fd7, 6b33fb2, 5660c81; new c7bd3ca (B2 fix), 9801fba (e2e test). Range for QA: `9013baa..9801fba`.
- Worktree `.claude/worktrees/T-20261016-2146-paper-broker`, `.alto_checkout.yaml` mode sandbox, root `alto_sandboxes/T-20261016-2146-r3/news_server`. Baseline `.claude/worktrees/T-20261016-2146-r3-base` (9013baa), root `alto_sandboxes/T-20261016-2146-r3-base/news_server`.

## B2 fixed (c7bd3ca)
- `create_daily_price_store(user, symbols, start, end)`: dhan → `DhanPriceStore(user, symbols, [], start, end)` (unchanged); paper → `DailyPriceWindow(StoredDailyPrices(PAPER_PRICES_DIR), symbols, start, end)` (`backend/executor/paper/price_window.py`), DhanPriceStore-shaped: `series`, `latest_close(symbol, as_of)`, `trading_days`, `has`. A symbol with no stored prices raises FileNotFoundError when the window is built (DhanPriceStore instead records `failed_symbols`; paper never skips).
- Call sites now on the factory, arguments identical: `backend/api/services/rebalance_service.py` `_trading_calendar`, `backend/api/services/strategy_service.py` `_trading_calendar`, `backend/api/services/trading_loop_service.py` trigger tick. No `DhanPriceStore(` construction is left in those three modules. `test_trading_loop_service.py` now patches `create_daily_price_store` instead of `DhanPriceStore` (same intent: recompute must not build a candle store).
- `_build_planner_inputs`'s other price read, `price_unheld_targets(self._create_broker_client(), ...)`, already went through the broker factory (paper `quote`).

## Acceptance checks (from backend/, dummy env, `PYTHONPATH=..`)
- QA's round-2 command `pytest executor/paper executor/broker_factory executor/tests/test_credentials.py api/routes/tests/test_broker_switch.py config/tests` → **81 passed** (73 before + 7 new + 1 replaced e2e).
- 5a: `executor/broker_factory/tests/test_daily_price_store.py` → 7 passed. Dhan user, live: rebalance and strategy calendars build DhanPriceStore with exactly `(USER, ["A","B"], [], today-(min_holding_days*5+30), today)` and `(USER, ["A","B"], [], "2024-01-01", "2026-10-07")`. Paper user, sandbox: both calendars come from the stored prices, clipped to the window; latest_close/series; missing symbol raises; paper user in live checkout raises BrokerNotAllowedInCheckout. The trading-loop site has no dedicated test of its own; it is the same one-line factory call (trading_loop_service.py:147).
- 5b: `executor/paper/tests/test_end_to_end.py` → 2 passed, sockets blocked. `test_two_approvals_in_a_row_fill_through_the_real_planner_inputs`: real `submit_decision` → real `_load_desired` + `_build_planner_inputs` (watchlist, custom picks, completeness gate over real `build_checker`, `_trading_calendar` via the paper store, PositionLots entry date) → given `plan_orders` result → intent book → EMS ticks → Reconciler. Approval 1 (Mon 10-05, flat): BUY ACME 60, planner received holdings `{}` and calendar `[]`; fills at 102×(1+5bps). Approval 2 (Wed 10-07, holding ACME 60, entry_date 10-05): planner received holdings `{ACME: 60}` and calendar `["2026-10-01","2026-10-05","2026-10-07"]` (ACME's stored days); BUY RELIANCE 10 fills at 1006×(1+5bps). Hand calc: FillLedger = [(ACME,BUY,60,p1),(RELIANCE,BUY,10,p2)], current.json holdings {ACME:60, RELIANCE:10}, cash = 100000 − 60·p1 − 10·p2.
  - Fail-before: with c7bd3ca's two source files reverted, the test fails at the second approval (test_end_to_end.py:262) with `RuntimeError: DhanPriceStore requires BROKER=dhan. Current: paper`.
  - What the test patches: clock (`ist_now` in manager/adv/reconcile/market_day, `datetime` in jitter and rebalance_service); `plan_orders` (allowed by 5b); path constants of store modules that bind them at import, pointed at tmp: `paths.STANCES_DIR`, `stance.repository.STANCES_DIR`, `union.store.PRICE_WATCHLIST_PATH`, `custom_picks.CUSTOM_WATCHLIST_PATH`, `company_resolver.MAPPING_PATH`, `chain_start.store.LEGACY_CHAIN_STARTS_PATH`, and `read_calendar.__defaults__` (its default path is bound at def time).
  - Seeded: desired.json full signals for ACME and RELIANCE, published watchlist, custom picks, company mapping, empty legacy chain starts, fresh empty results calendar. ACME/RELIANCE have no index and no stance log, so the completeness gate judges them Not initiated, which does not block. A stance log for them was **not** seeded (it would need a chain start and the full index fixtures); the gate runs, but over Not-initiated companies.
  - The second order is RELIANCE 10 (not 20): at 20 the EMS guardrail flags max_single_name_weight 0.20 > 0.15, real behaviour.
- Check 6 suite (dev-skill command + `--continue-on-collection-errors`, both trees on their own sandbox roots): new 100 failed / 1580 passed / 8 errors; base 9013baa 100 failed / 1553 passed / 8 errors; `comm -23 new base` **empty** (108 lines each). `stores/tests/test_boundaries.py` 2 passed. Entry points import: intake.runner, stance.runner, e2e.run, workflow.cli, execution.runner, raw.master_pipeline, backtest.replay, api.main_cockpit, api.local.
- No order placed or cancelled, no credentials read, no production data written (suite writes went to the two sandbox roots above).

## Still open / Found
- `price_chart_service.py:117` and `trading/scripts/rebuild_price_refs.py:22` still build DhanPriceStore directly (charts and a maintenance script; not on the proposal/approval path, not in 5a's list).
- A1 merge-order alert is gone: the dependency is on main.
