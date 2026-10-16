# Plan (written retroactively with the handoff; design was fixed before code)

Touches: backend/api/services/rebalance_service.py (_build_planner_inputs, _plan fingerprint, _build_proposal warnings), new backend/trading/proposals/completeness_gate.py. Callers of the proposal build: routes/rebalance.py generate_proposal, trading_loop_service (book check, auto). No proposal CLI exists.
Money path: yes. Gate runs after apply_book_guards so rationing/ranking of other names is untouched. Unheld blocked -> target 0; held blocked -> target capped at current weight (reductions pass). Warnings carry state, missing quarters, before/after weights. Completeness errors propagate.
Acceptance: replay script backend/trading/scripts/replay_proposal.py in base and branch trees, diff outputs; tests; entry-point imports; full suite vs base.
