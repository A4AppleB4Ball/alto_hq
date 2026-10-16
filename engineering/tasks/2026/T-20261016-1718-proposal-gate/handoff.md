# Handoff: proposal-gate

Branch eng/T-20261016-1718-proposal-gate (worktree .claude/worktrees/proposal-gate). Base a5b5606.
Commits: see `git log a5b5606..eng/T-20261016-1718-proposal-gate` (2: gate + tests; held-cap revision + replay script).

## Change
backend/trading/proposals/completeness_gate.py: after apply_book_guards, for every name with a stance: not ok (blocking quarter or violation, incl. Not initiated with a stance) -> unheld target 0; held target capped at current weight (a reduction passes). Warnings (no longer `[]`) carry kind, symbol, state, reason, missing_quarters, violations, held, weight before/after. Gate state enters the plan fingerprint (`completeness_blocked`). Any exception from the check/calendar read propagates; no fallback.

## Acceptance
Replay (read-only; clock pinned to 2026-10-15T10:17:21, ledger cut at that time, stance snapshot desired_2026-10-15T10-17-15.json, stored broker snapshot; price refs, approval history, cached closes and the completeness stores are as of NOW, not that day):
`python -m backend.trading.scripts.replay_proposal scienceamit1 2026-10-15T10-17-21 desired_2026-10-15T10-17-15.json OUT.json` run in base tree (script copied in) and branch.
1. Old replay reproduces the incident: 3 BUYs TIMEX 64, ARSSBL 90 (stored: 88), OMNI 17 (stored: 16), warnings key absent. New: ARSSBL and CHANDAN targets 0.0441 -> 0 with warnings: incomplete, ARSSBL missing Q1_FY27 and Q2_FY27, CHANDAN missing Q1_FY27; ARSSBL order gone. PASS.
2. NOT identical line for line, two differences I did not hide:
   a. MAZDA 0.0441->0.0428 and NRAIL 0.0441->0.0383 (held, check says incomplete Q1_FY27, add blocked). No order changed for them. If you consider them complete, the completeness check is the thing to look at, not the gate.
   b. OMNI order quantity 17 -> 61 shares (target weight and action identical). OMNI was cash-limited in the old run; ARSSBL's excluded buy frees its cash. TIMEX 64 identical. This follows from excluding a buy; acceptance 2 as written cannot hold for it. Needs owner reading.
3. Temp-dir fixtures, backend/trading/proposals/tests/test_completeness_gate.py: complete passes untouched, Not initiated with stance excluded with reason, held cannot grow, reduction passes. PASS.
4. Failure injection: tests in trading/proposals/tests (checker raises) and api/services/tests/test_rebalance_completeness_gate.py (check_symbols raises -> _build_planner_inputs raises). PASS. Calendar-unreadable path is read_calendar raising inside build_checker (not separately tested).
5. API service/route/trading loop import OK. There is NO proposal-build CLI in the repo, so that half cannot be run. test_boundaries 2 passed. Full suite: 66 failures base, 66 new, `comm -23` empty.

## Pinned old vs new
api/services/tests/test_rebalance_completeness_gate.py: same book gate off vs on, every non-blocked target identical; test_rebalance_core_parity and price_action tests keep pinned numbers with the gate stubbed to pass-through (gate stub param added to `_service`).

## Behaviour the owner must know
- Held blocked names are not frozen on sells: a REDUCE/exit still goes through (design choice; say if you want sells blocked too).
- Gate runs ~330 completeness checks per build (~10 ms each).
- Replay used cached closes for unheld prices, so quantities differ slightly from stored.

## Not done
- No CLI for proposals exists (acceptance 5 half). Calendar-unreadable not separately tested.
- Acceptance 2 literal reading unmet (a, b above).
