# Acceptance: proposal-gate (approved)

Money path: every check compares old and new numbers on the same input.
Depends on T-20261016-1718-completeness-check merged. Read-only on product
data; no order placed or cancelled.

1. **The incident proposal is replayed.** Feed the inputs of
   `workspace/scienceamit1/rebalance/proposals/2026-10-15T10-17-21.json`
   (stances, book, prices as of that day) through the old and the new
   proposal code. New: ARSSBL and CHANDAN are excluded or flagged with their
   completeness state and missing quarters in `warnings` (no longer `[]`).
2. **Everything else is unchanged.** For every other company the model
   target weight, the diff action and the planned order quantity are
   identical between old and new, line for line. Output of both runs kept.
3. **A complete company passes untouched; a Not initiated company with a
   stance is excluded with its reason.** Temp-dir fixtures.
4. **No silent path.** If the completeness function raises or its inputs are
   unreadable, the proposal build raises; it never proceeds without the gate.
   A test injects the failure.
5. **Entry points.** Proposal build via the API service and the CLI both
   import and run in `--dry-run`/read-only mode; `test_boundaries.py` passes;
   full suite shows no new failure against base.
