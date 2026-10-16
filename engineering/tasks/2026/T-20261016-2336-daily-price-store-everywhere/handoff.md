# Handoff — T-20261016-2336-daily-price-store-everywhere (attempt 1, not done)

Branch `eng/T-20261016-2336-daily-price-store-everywhere`, worktree
`alto/.claude/worktrees/T-20261016-2336-daily-price-store-everywhere`.
Base **9801fba** (local main 35e1342 did not yet contain `backend/executor/broker_factory/prices.py`).
Commits: 10604c7 (chart), f1d06a7 (rebuild_price_refs), 9c843a2 (harness), 4dac7e7 (site tests), 189c6a9 (AST guard test).
The worktree carries an untracked `.alto_checkout.yaml` declaring `mode: sandbox` on an empty root
`alto_sandboxes/T-20261016-2336-daily-price-store-everywhere/news_server` — nothing touched production.

## Acceptance
1. PASS. `grep -n "DhanPriceStore(\|create_daily_price_store" ` over the three files: only
   `create_daily_price_store` calls remain (price_chart_service.py:117, rebuild_price_refs.py:39);
   harness `_resolve_price` (harness.py:227) raises `ValueError("No price store passed ...")` when
   `price_store is None`. Pinned by `test_resolve_price_raises_without_a_store`.
2. **FAIL, as written.** `pytest backend/executor/broker_factory/tests/test_no_direct_dhan_price_store.py`
   lists 7 modules still constructing `DhanPriceStore(`, none of them the Goal's three sites:
   backtest/scripts/ab_discount_sign.py, compare_macro_ablation.py, compare_macro_signal_backtest.py,
   compare_tiebreak_modes.py, compare_trade_book.py, backtest/sweep.py, scripts/refresh_price_cache.py.
   I did not change them: they are research/cache-warm scripts with a fixed price user and extra
   kwargs (`force_refresh=...`) the factory does not take, and the Goal names only three sites.
   I did not loosen the test. Owner decision needed: (a) widen the task to route those 7 through the
   factory (factory gains kwargs; backtests then require the price user's active broker = dhan and a
   live checkout), or (b) amend acceptance 2 to also exempt `backend/backtest` and
   `backend/scripts/refresh_price_cache.py` (proposal; I have not edited acceptance.md).
3. PASS. `pytest backend/executor/broker_factory/tests/test_price_store_sites.py` — 9 passed: dhan/live
   pins `DhanPriceStore("default",[sym],[],start,end)` (chart) and `(user, symbols, [], start, today)`
   (rebuild); paper/sandbox reads stored prices with zero Dhan builds; missing symbol raises
   (FileNotFoundError / KeyError).
4. Suite (from backend/, --continue-on-collection-errors): base 9801fba 100 failed/1580 passed/8 errors;
   new 101 failed/1589 passed/8 errors. `comm -23 new base` = only the acceptance-2 test above.
   `stores/tests/test_boundaries.py` passes. Imports OK: intake.runner, stance.runner, e2e.run, workflow.cli,
   execution.runner, raw.master_pipeline, backtest.replay, api.app_factory, api.local, api.main_cockpit.

Targeted: trading, api/services/tests, executor, boundaries — only pre-existing failures plus test 2.

## Behaviour changes the owner must know
- Any caller of `TradingManager._resolve_price` / `_resolve_prices` / `process_trigger` without a
  `price_store` now raises instead of silently building a DhanPriceStore from 2024-01-01. No caller
  in the suite relied on it.
- `rebuild_price_refs` for a paper user builds the stored-price window, then raises
  `AttributeError: series_15min` — paper prices are daily only, so 15-min price refs cannot be rebuilt
  for paper. Acceptance 3 "paper reads stored prices" holds only up to that point; an explicit error
  (or a daily-bar ref rebuild) is a design call for the owner. rebuild_price_refs.py:41.
- Chart route for a paper "default" user in a sandbox now reads stored prices instead of raising.

## Found
- `PriceSource = DhanPriceStore | LatestPrices` (harness.py:52) does not name `DailyPriceWindow`; type only.
