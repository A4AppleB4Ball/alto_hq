# Plan: paper-broker

**Touches:** new `backend/executor/paper/` (fill_model, prices, state, stance_dates, broker);
`backend/execution/service.py` `_create_broker_client` (+ checkout-mode gate, paper skips credentials in
`_ensure_broker`/`tick` token check); `backend/executor/credentials.py` (`VALID_BROKERS`, `EXECUTION_BROKERS`
gain "paper"; `has_valid_token` true for paper without reading credentials);
`backend/stores/book/ledger_sync.py` (`sync_ledger` accepts brokers that report fills: dhan, paper);
`backend/config/paths.py` (`PAPER_PRICES_DIR`, `WorkspacePaths.paper_broker_dir`).
Callers of the changed functions: `_create_broker_client` (service, trading_loop_service:133,:221),
`active_broker`/`execution_broker` (credentials users), `sync_ledger` (reconcile, refresh_from_broker).

**Money path: yes.** Dhan behaviour unchanged: "dhan" build path identical except it now raises in a
sandbox checkout. Tests pin that dhan in live still builds DhanClient.

**Change:** PaperBroker duck-types DhanClient. Fill model: data_through < session day -> fills at that
day's open; data_through == session day -> next regular NSE trading day's open; data_through > day raises
(look-ahead). Price = open * (1 +/- PAPER_SLIPPAGE_BPS/1e4). No stored bar on the fill day -> REJECTED
with reason (FC11), never another day's price. Limit price ignored (owner fill model). Fills settle at
once (holdings only; positions empty; unsettled 0). State under `workspace/<uid>/paper_broker/`.
Prices from `PAPER_PRICES_DIR/{SYMBOL}.parquet` (DhanDailyStore cache schema), read-only, no network.

**Checkout gate:** reads `backend.config.paths.CHECKOUT.mode` (T-20261015-0321 contract). paper only
in sandbox, dhan only in live. Branch must land after T-0321.

**Checks:** 1-3, 5 as pytest files under `executor/paper/tests/`; 4 in `execution/tests/` run on a
temp merge of this branch onto `eng/T-20261015-0321-checkout-data-root`; 6 full suite vs base.

## Round 2 (answers evidence.md round 1)
- **B1:** `execution/market_analysis/adv.py` (callers: `execution/manager.py:479,1154` only) builds its store through a new `executor/broker_factory/prices.py:create_daily_price_store`, which uses the same `execution_broker` + `require_broker_allowed` gate as `create_broker_client`: dhan → DhanPriceStore (unchanged for live), paper → `StoredDailyPrices(PAPER_PRICES_DIR)`, the store the paper broker fills against. Missing history raises. Money path: live numbers unchanged (same DhanPriceStore call).
- **A2:** `PaperAccountStore.update()` = load/modify/save under `stores.locking.exclusive_lock`, written with `atomic_write_text`; reads settle in memory only; ids from persisted `orders_issued`.
- e2e test: only seeds stores (checkout, prices, holidays, instrument cache, strategy config, desired.json, account) and fixes the clock; the proposal's planner inputs/plan_orders stay given.
- Checks run on a detached merge of the branch onto 20e6afe, `mode: sandbox`, empty temp root.

## Round 3 (Amendment v2, B2)
- Touches: `backend/executor/broker_factory/prices.py` (paper branch returns `DailyPriceWindow`, new `backend/executor/paper/price_window.py`: symbols + start..end view with `series`, `latest_close`, `trading_days`); call sites `rebalance_service._trading_calendar`, `strategy_service._trading_calendar`, `trading_loop_service._process_user_tick_locked` switch from `DhanPriceStore(...)` to `create_daily_price_store(...)`, same arguments. Callers: `_build_planner_inputs` (proposal + submit_decision), strategy preview, trigger tick.
- Money path: yes. Dhan users pinned by tests asserting the identical DhanPriceStore call; paper reads stored prices.
- Checks: 5a by `executor/broker_factory/tests/test_daily_price_store.py`; 5b by `executor/paper/tests/test_end_to_end.py` (no patch of `_build_planner_inputs` or price reads; `plan_orders` given); suite vs base 9013baa.
