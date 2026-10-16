# Acceptance: proposal-gate (DRAFT v2, not approved)

Owner rule, 2026-10-16: the proposal is blocked when any company in its
scope has missing or stale data, because one company's old analysis impairs
the accuracy of the whole proposal (ranking, cash allocation). Scope is the
price watchlist plus every held position, including a held company that left
the price watchlist but does not yet qualify for rank_exit: that position
stays, so the block still applies to it.

Money path: old and new numbers pinned. Read-only on product data; no order
placed or cancelled. Depends on completeness-check (merged).

1. **Replay of the 2026-10-15 inputs.** The new code refuses to build the
   proposal. The error lists every company the completeness function reports
   as blocking in scope (Missing, Stale, Due with nothing in, a stance without
   a chain start), each with its state and missing quarters; ARSSBL and
   CHANDAN are in it. The listed set equals the function's output over scope,
   computed independently by QA.
2. **Nothing blocking: nothing changes.** On a fixture where every company in
   scope is complete, targets, actions and order quantities are identical to
   the old code, line for line.
3. **Held names.** A held company outside the price watchlist that does not
   qualify for rank_exit, with a missing quarter, blocks the proposal. A held
   company outside the watchlist that does qualify for rank_exit is being
   sold and does not block (owner to confirm this reading).
4. **No silent path.** If the completeness function or the calendar read
   fails, the build raises; no partial proposal is written. Tests inject both
   failures. The refusal is visible where the owner reads it (API response and
   log), not only in a log file.
5. **Entry points and suite.** The API service, route and trading-loop service
   import and run read-only; `test_boundaries.py` passes; full suite shows no
   new failure against base.
