# Acceptance: checks-stance-chain (v3, split by owner 2026-10-16)

`stance_inputs_asof` moved to T-20261016-2235-checks-stance-inputs-asof.
Read-only on product data.

1. **On the frozen cases:** `stance_chain` passes on 511144 and ARSSBL (their
   chains are continuous). QA checks one link of each by hand from `log.jsonl`.
2. **Planted defects** on tmp copies: a gap of one day, an overlap and a
   `covers_to` different from `as_of` each fail naming the link; a cold-start
   link is not a gap.
3. **One rule.** `stance/reconcile.py` and `stance_chain` call the same
   function; `stance/reconcile.py`'s own tests pass unchanged.
4. **Nothing of `stance_inputs_asof` on the branch**: its package, tests and
   the `bse_rows_between` commit `d79734f` are removed.
5. **Verdict contract** as in the completeness check (id, version,
   fingerprint).
6. **Suite.** `pytest backend/validation backend/stance` pass; full suite no
   new failure; boundary test passes.
