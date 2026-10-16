# Plan v2 (written before code; rework of v1 per-name gate, v1 branch kept as eng/T-20261016-1718-proposal-gate-v1-pername @797ec93)

Base: main 79e66a7, fresh branch eng/T-20261016-1718-proposal-gate, worktree .claude/worktrees/proposal-gate.

Touches: backend/api/services/rebalance_service.py (_build_planner_inputs only), backend/trading/proposals/completeness_gate.py (rewritten), backend/trading/scripts/replay_proposal.py (reused, reports the refusal), tests. Callers of the build: routes/rebalance.py generate_proposal (catches ValueError -> HTTP 400 with detail), RebalanceService.auto_generate_if_needed <- trading_loop_service and execution/manager.py (logs exception). No proposal CLI.
Money path: yes, but the gate only adds a raise. No target, ranking, rationing or fingerprint code changes. v1's zeroing/capping, warnings and fingerprint field are removed. Pinned: with nothing blocking, targets/orders/fingerprint equal old code (test on the existing parity fixture compares full inputs with the gate off vs on; replay diff).

Change:
- scope = price watchlist (active_watchlist_symbols, as the service already uses) UNION held positions (current_by_symbol minus LIQUIDCASE) MINUS held names that qualify for rank_exit AND are not on the watchlist.
- "qualifies for rank_exit" = held, priced, and not in `survivors` returned by backend.trading.core.rank_gate, called with the same arguments compute_name_targets gets. That is the one function that yields the RANK_EXIT decision (compute_name_targets emits RANK_EXIT exactly for held and not in survivors). Imported, not re-derived. Ranked book off -> no survivors -> nothing qualifies -> held names stay in scope.
- Every in-scope symbol is checked with check_company (via build_checker); any result with `not ok` is blocking. If any: log ERROR and raise CompletenessBlocked(ValueError) listing symbol, state, reason, each blocking quarter (state), violations. ValueError => route returns 400 with the full text; auto paths log it.
- Checker or calendar read raising propagates (no catch).
Owner will notice: proposal generation fails loudly until blocking companies are fixed; scope no longer includes non-watchlist unheld stance names (v1 did).

Acceptance runs:
1. replay: backend.trading.scripts.replay_proposal on the 2026-10-15 proposal inputs in the branch tree (read-only, output to tmp); compare listed names with an independent check_company loop over watchlist+held from the same inputs.
2. test on fixture all-complete: old (base tree service) vs new inputs equal; plus replay on base tree vs branch when nothing blocks is impossible on real data, so the fixture test is the proof.
3. tests for held outside watchlist: not rank_exit + missing -> raises; rank_exit-qualifying -> passes.
4. tests inject checker failure and calendar read failure -> raise; no proposal saved; route test shows 400 detail.
5. imports of rebalance routes/service/trading_loop_service; test_boundaries; full suite vs base 79e66a7.
