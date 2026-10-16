# Acceptance: checks-stance-chain (v2, amended by owner 2026-10-16)

Read-only on product data.

1. **On the frozen cases:** `stance_chain` passes on 511144 and ARSSBL (their
   chains are continuous); `stance_inputs_asof` passes on 511144. QA checks one
   link of each by hand from `log.jsonl` and the index.
2. **Planted defects** on tmp copies: a gap of one day, an overlap, a
   `covers_to` different from `as_of`, and a trigger document published after
   the link's `as_of` each fail naming the link; a cold-start link is not a gap.
3. **One rule.** `stance/reconcile.py` and `stance_chain` call the same
   function; `stance/reconcile.py`'s own tests pass unchanged.
4. **One resolution path, both exchanges.** Every input (quarterly
   analysis, annual report, trigger announcement) is resolved and dated only
   through `lib` DataAccess / the AsOfLedger and the company resolver, the
   way the stance worker reads them; the check reads no index file or
   exchange day file itself (AST test). It runs on NSE-only and BSE-only
   companies: `stance_inputs_asof` passes or fails with named inputs on
   ARSSBL, CHANDAN and 511144, never raising for the exchange.
5. **Unresolvable input fails.** A recorded id absent from the index is a
   failure with reason `input_not_in_index`, never skipped.
6. **Verdict contract** as in the completeness check (id, version,
   fingerprint).
7. **Suite.** `pytest backend/validation backend/stance` pass; full suite no
   new failure; boundary test passes.
