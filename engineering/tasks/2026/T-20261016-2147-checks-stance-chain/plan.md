# Plan: checks-stance-chain

**Touches:** `backend/stance/reconcile.py` (`_chain_gap` body moves out), new
`backend/stance/chain/continuity.py` (the one rule), `backend/lib/events.py`
(`_scan_bse` reads through a new public `bse_rows_between(dir, code, start, end)`
so a check can read a frozen case's day files; behaviour unchanged), new
`backend/validation/stance_chain/` and `backend/validation/stance_inputs_asof/`
(policy, inputs, check, cli, tests). Callers of `_chain_gap`: only
`StanceReconciler.reconcile` (reconcile.py:116). Callers of `_scan_bse`: only
`scan_announcements`. Entry points: stance.ready / reconcile CLI import paths
unchanged.

**Money path?** No. Read-only checks; reconcile verdicts unchanged.

**Change:**
- `chain_gap(records)` / `link_gap(prev, cur)` in `backend.stance.chain.continuity`,
  verbatim rule (covers_from == prior as_of + 1; cold start skipped).
  Reconcile's `_chain_gap` method is deleted and reconcile calls `chain_gap`.
- `stance_chain`: per link, `link_gap` plus `covers_to == as_of`; fails naming the link.
- `stance_inputs_asof`: quarterly key -> `find_version(enumerate_versions(index))`
  `version_date`; annual docid -> index doc `filed_at` (AsOfLedger rule);
  trigger docids -> the BSE day file they appear in (the announcement feed;
  triggers are not in `{SYMBOL}_index.json`). Absent -> `input_not_in_index`;
  undated annual -> `input_undated`; date > as_of -> `input_after_as_of`.
- Same for owner: nothing changes in the product's behaviour.

**Acceptance runs:** (1) `python -m backend.validation.stance_chain.cli --case <case>`
for 511144 and ARSSBL, `python -m backend.validation.stance_inputs_asof.cli --case <511144 case>`
(read-only, loads via `load_case`). (2) planted-defect tests on tmp copies in
`<feature>/tests/`. (3) grep + `pytest backend/stance/tests` with reconcile tests
unmodified (git diff empty there). (4) test. (5) test asserting CHECK_ID/VERSION/fingerprint.
(6) `pytest backend/validation backend/stance`, full suite vs base, boundary test.
