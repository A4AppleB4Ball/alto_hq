# Acceptance: scenario-selection (draft)

Read-only on product data.

1. **Real-state classes found.** The output lists ARSSBL for FC02 and FC08
   and CHANDAN for FC03 (the incident's known cases), each with the evidence
   record (quarter state, file, reason) that put it there; QA re-derives two
   of them by hand.
2. **Healthy candidates.** FC01 candidates are `complete` per the completeness
   function with every quarter in the window analysed; at least one is
   BSE-only.
3. **FC10.** Candidates are `not_initiated` per the completeness function.
4. **No outcome inputs.** An AST test asserts the module reads no P&L,
   returns, backtest or book store.
5. **Reproducible.** Two runs at the same as-of give identical output; the
   output records the alto and news_server commits.
6. **Read-only + suite.** `find <data> -newer <marker>` empty; full suite no
   new failure.
