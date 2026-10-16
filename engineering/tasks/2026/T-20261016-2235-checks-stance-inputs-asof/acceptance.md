# Acceptance: checks-stance-inputs-asof (draft)

Read-only on product data. Run from a sandbox checkout (T-20261015-0321) whose root holds the case.

1. **Frozen cases:** passes on 511144; QA checks one link by hand from `log.jsonl` and the index.
2. **Planted defect:** a trigger document published after the link's `as_of` fails naming the link, input and both dates.
3. **One resolution path, both exchanges.** Every input is resolved and dated only through `lib` DataAccess / the AsOfLedger and the company resolver; the check reads no index or exchange day file itself (AST test). On ARSSBL, CHANDAN and 511144 it passes or fails with named inputs, never raising for the exchange.
4. **Unresolvable input fails** with reason `input_not_in_index`, never skipped.
5. **Verdict contract** as in the completeness check.
6. **Suite.** `pytest backend/validation backend/stance` pass; full suite no new failure; boundary test passes.

## Amendment (owner 2026-10-16, after QA round 1)

7. **Fingerprint independent of `--through`.** The same inputs and reasons give the same fingerprint for different `--through` dates (test).
8. Check 6 is run after T-20261016-2311-case-checks-via-sandbox lands, in a fresh sandbox with no file copied from live.
