# Handoff: proposal-gate (v2 rework)

Branch eng/T-20261016-1718-proposal-gate, worktree .claude/worktrees/proposal-gate, base main 79e66a7. Commits f7be4bc, e7bbda6. v1 (per-name zero/cap) preserved as branch eng/T-20261016-1718-proposal-gate-v1-pername (797ec93). Acceptance hash 002c1a09... verified unchanged. plan.md written before code.

## Change
- backend/trading/proposals/completeness_gate.py rewritten: scope_symbols, rank_exiting, require_complete, CompletenessBlocked(ValueError), build_checker (kept). Only raises; no target, warning or fingerprint change.
- rebalance_service._build_planner_inputs: gate runs before target computation.
- "Qualifies for rank_exit": backend.trading.core.rank_gate (the one function; compute_name_targets emits RANK_EXIT for held names outside its survivors), called with the same arguments. Ranked book off -> nothing qualifies.
- Scope = price watchlist (active_watchlist_symbols) + held (minus LIQUIDCASE) - (held off-watchlist names that rank_gate drops). A watchlist name that is rank-exiting still blocks.

## Acceptance
1. Replay (`python -m backend.trading.scripts.replay_proposal scienceamit1 2026-10-15T10-17-21 desired_2026-10-15T10-17-15.json OUT.json`, branch tree, clock pinned to creation time, stores as of now, output to tmp): REFUSED, "224 of 372 companies in scope are blocking", each with state and quarters; ARSSBL and CHANDAN listed. A separate loop over watchlist (372) + held (18, all on watchlist) through check_company gives the same 224 (diff empty); same function, so QA should recompute independently. Old code, same inputs (base tree): 3 BUYs TIMEX 64, ARSSBL 90, OMNI 17.
2. test_rebalance_completeness_gate.py::test_nothing_blocking_leaves_the_inputs_identical_to_the_ungated_build: full _build_planner_inputs output equal with the gate and with it disabled, on the parity fixture. Existing parity/golden tests pass unchanged (a stub checker added to their fixtures only).
3. Held-name tests: STEADY off-watchlist survivor + missing quarter -> raises; BROKE off-watchlist (RANK_EXIT target in result) + missing -> builds; BROKE on watchlist -> raises.
4. Tests: checker raising, calendar read raising -> build raises; route test: generate_proposal returns HTTP 400 with all blocking companies in detail; gate logs ERROR with the same text. A proposal is saved only after _build_planner_inputs, so nothing is written on refusal.
5. API route/service/trading_loop_service/execution.manager import OK; test_boundaries 2 passed. Full suite: base 66 failures, new 66, comm -23 empty (one parallel-run flake, test_partitioned_storage, passes alone and on rerun).

## Owner must know
- On live data the proposal is refused now: 224 of 372 companies blocking (mostly Q1_FY27 due_nothing_in / missing). Until fixed or the rule is relaxed, no proposal builds; auto paths log the error.
- Scope no longer includes unheld non-watchlist stance names (v1 did).
- A held name with price<=0 is not in `holdings`, so it never counts as rank-exiting and stays in scope.

## Not done
- Calendar-unreadable tested via an injected builder raising, not the real read_calendar.
- Did not verify trading_loop_service's handling of the exception from auto_generate_if_needed (execution/manager.py:346 catches and logs).
