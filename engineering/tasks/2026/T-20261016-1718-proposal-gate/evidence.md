---
schema: evidence/v1
task: T-20261016-1718-proposal-gate
round: 1
qa: pass
outputs_changed: unverified
---

## Round 1

Head fd33285, base 66871a6. acceptance.md sha256 002c1a09... equals the approval in task.md. Own worktrees: .claude/worktrees/proposal-gate-qa (head), .claude/worktrees/proposal-gate-qabase (base). Raw logs in /tmp/qa_pg/.

### Acceptance checks
1. Replay. `python -m backend.trading.scripts.replay_proposal scienceamit1 2026-10-15T10-57-58 desired_2026-10-15T10-57-52.json /tmp/qa_pg/head.json` -> REFUSED, "15 of 372 companies in scope". Listed: ABDL, ARSSBL (Q1+Q2 missing), BBOX, CHANDAN, EMUDHRA, FAIRCHEMOR, KRISHNADEF, PNGSREVA, RAYMOND, RAYMONDREL, SMCGLOBAL, STEELCAS, TAC, TATVA, THELEELA (Q2). All are Missing, each with state and quarters. My own script (active watchlist 372 + held 18 from the stored snapshot, check_company at created_at, IST) gives the identical 15; held-minus-watchlist is empty. PASS. (Caveat: same completeness function, independent scope.)
2. Nothing blocking. test_nothing_blocking_leaves_the_inputs_identical_to_the_ungated_build compares the full _build_planner_inputs output, gate on vs off; plus existing parity/price_action tests pass. 41 passed across boundaries, gate, API, proposals, parity, price_action. PASS (fixture-level; no base-vs-head order diff on live inputs, hence outputs_changed unverified).
3. Held names. STEADY (off-watchlist, survives) blocks; BROKE (off-watchlist, RANK_EXIT) does not; BROKE on watchlist blocks. Read the gate against compute_name_targets (core.py:459-505): same rank_gate, same "held and not in survivors" rule. PASS.
4. No silent path. Failing checker and unreadable calendar raise; route returns 400 with all companies (test). I also ran the real build_checker with read_calendar pointed at a missing temp file: raises FileNotFoundError (route maps it to 400). Gate logs ERROR with the same text. PASS.
5. Entry points and suite. trading_loop_service, routes.rebalance, rebalance_service, replay_proposal, execution.manager import. test_boundaries passes. Full suite (backend/, dev skill command): base 66 failures, head 66, `comm -23` empty. PASS.

### Point-by-point
- (3) The dev's extra failure test_verify_rejects_tampered_token did not recur: passes in my full head run and 5/5 sequential reruns. The test (auth/tests/test_session.py) flips the last base64 char of the token; a flip that only changes unused trailing bits can leave the signature valid, so it is probabilistic and unrelated to this diff. Flake.
- (4) Callers of auto_generate_if_needed: trading_loop_service.py:171 wraps in try/except Exception and logs "Auto-proposal failed"; execution/manager.py:346 likewise. book-check path (trading_loop_service.py:322) propagates to _tick_once (try/except, logged). Exception is logged, not alerted; acceptable per acceptance 4 ("API response and log").
- (5) Injected-builder calendar test: acceptable, since build_checker calls read_calendar unguarded and I confirmed the real raise; a direct test of build_checker with a missing calendar file would close the gap.

### Findings
No BLOCK. Observations for the owner (not verifier-confirmed, read from code; ALERT at most):
- rebalance_service.py:950 submit_decision re-runs _build_planner_inputs, so the gate also refuses approving an already-cut proposal (claim is released, ValueError raised). While any company blocks, even a human approval of sells fails. Consistent with the whole-proposal rule but worth stating.
- A held name with price<=0 is never rank-exiting and stays in scope (conservative; dev disclosed).

### Dev claims
Dev's handoff claims on the rebased numbers (15 of 372, 66 vs 67) were confirmed except the 67th failure, which I could not reproduce. Original 224 figure is superseded.

### Would catch this class automatically
An invariant that a stored proposal replay on current stores either refuses or equals the stored orders; none exists.
