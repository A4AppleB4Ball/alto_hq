# Acceptance: paper-broker (draft)

Money path. No order is placed or cancelled at Dhan; no Dhan API call is made.

1. **Interface.** A test enumerates every broker method called in
   `execution/manager.py`, `execution/reconcile.py` and
   `stores/book/ledger_sync.py` (AST scan) and asserts `PaperBroker` has each
   with the same parameters as `DhanClient`.
2. **Fill model (owner, 2026-10-16).** An order whose stance was computed on
   data up to the day before fills at that day's open; one computed on the
   day's data fills at the next trading day's open; both with the fixed
   slippage from one named constant. Tests cover both, a sell, a partial lot
   rounding, and an order on a day with no stored price, which is rejected
   with a reason (FC11) and never filled at another day's price.
3. **Book.** After fills, `holdings`, `positions`, `funds` and `fills` agree
   with each other, and `refresh_from_broker` builds the same book state a
   hand calculation gives in the test.
4. **Live refusal.** With the checkout `mode: live`, building a `"paper"`
   broker raises; with `mode: sandbox`, building `"dhan"` raises. Depends on
   T-20261015-0321-checkout-data-root; until it lands this check is run on its
   branch.
5. **End to end in a tmp sandbox.** One approved proposal goes through
   `RebalanceService.submit_decision` → intent book → `ExecutionService.tick`
   → `Reconciler.run` with `PaperBroker`, and ends with the order filled and
   the book updated; no network access (a test blocks sockets).
6. **Suite.** Executor, execution and book tests pass; full suite no new
   failure; boundary test passes.

## Amendment v2 (owner 2026-10-16, after QA round 2)

5a. **Planner inputs for a paper user.** Every price read on the proposal and approval path (`RebalanceService._trading_calendar` and `_build_planner_inputs`, and the same reads in `trading_loop_service` and `strategy_service`) goes through the checkout-gated daily price store, so a paper user reads the sandbox's stored prices and a dhan user is unchanged.
5b. **Two approvals in a row.** The end-to-end test replaces neither `_build_planner_inputs` nor the price reads (it may still give `plan_orders`' result). It approves a first proposal from a flat book, then a second while holding the first fill; both fill and the ledger matches a hand calculation.
