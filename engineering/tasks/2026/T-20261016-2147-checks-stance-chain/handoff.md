# Handoff: T-20261016-2147-checks-stance-chain (acceptance v3)

- Branch `eng/T-20261016-2147-checks-stance-chain`, worktree
  `alto/.claude/worktrees/T-20261016-2147-checks-stance-chain`, base `9950df7`.
- Commits (local only), range `9950df7..47f5bdb`:
  - `74f18dc` Stance: continuity rule moved to `backend/stance/chain/continuity.py`; reconcile imports it
  - `9fc6cdc` Validation: `stance_chain` check
  - `47f5bdb` Validation docs: stance chain check (rewritten, `stance_inputs_asof` text removed)
- v3 split: `6c97bee` (stance_inputs_asof) and `d79734f` (bse_rows_between) dropped by rebase.
  Pre-split tip kept as local branch `backup/2147-chain-pre-v3` (f538c5e) for T-20261016-2235; delete when not needed.

## Acceptance checks

1. Frozen cases (`PYTHONPATH=.` from worktree root, C=alto_testcases/cases, cases hash-verified by `load_case`):
   ```
   $ python -m backend.validation.stance_chain.cli --case $C/511144@2026-10-15 --case $C/ARSSBL@2026-10-15
   511144: continuous (14 link(s) continuous through 2026-10-07) check=stance_chain@1 fp=35ec1616df47...
   ARSSBL: continuous (12 link(s) continuous through 2026-10-13) check=stance_chain@1 fp=a63eb4b8186f...
   exit 0
   ```
   The hand check of one link each is QA's.
2. Planted defects on tmp copies, `backend/validation/stance_chain/tests/test_stance_chain.py`, all PASSED:
   one-day gap, overlap, covers_to != as_of each fail naming the link; cold-start link is not a gap;
   also link without chain block fails, missing log raises.
3. One rule: reconcile.py:59 imports `chain_gap, link_gap` from `backend.stance.chain.continuity`
   (used at :117 and :271); `stance_chain/check.py:14,46` uses `link_gap`.
   `test_reconcile_and_the_check_share_one_rule` passes. `git diff 9950df7 -- backend/stance/tests` is empty.
4. Nothing of stance_inputs_asof: `git diff 9950df7 --stat` lists only stance/chain, stance/reconcile.py,
   validation/stance_chain, validation/docs/stance_checks.md; `backend/lib/events.py` identical to base;
   `grep -rn "inputs_asof\|bse_rows_between" backend` (source) empty.
5. Verdict contract: `test_verdict_carries_id_version_and_fingerprint` passes (check_id, check_version, fingerprint).
6. `pytest backend/validation backend/stance backend/stores/tests/test_boundaries.py`: 218 passed.
   Full suite from backend/: base 9950df7 66 failed/errored, new 66; `comm -23 new base` empty.
   Entry points import: stance.reconcile, stance.runner, e2e.run, intake.runner, workflow.cli, stance_chain.cli.

## Behaviour changes
None in the product: reconcile uses the moved rule unchanged. New read-only check and CLI.

## Notes
- A first link that is not a cold start is reported as a gap (nothing precedes it).

Next: QA on `9950df7..47f5bdb`.
