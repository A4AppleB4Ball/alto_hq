# Handoff: T-20261016-2235-checks-stance-inputs-asof (round 1)

- Branch `eng/T-20261016-2235-checks-stance-inputs-asof`, sandbox worktree
  `alto/.claude/worktrees/T-20261016-2235` (root `alto_sandboxes/T-20261016-2235`), base `9013baa`.
- Commits (local only), range `9013baa..f653467`:
  - `33e295b` Lib: `AsOfLedger.filings_between` (every filing, none excluded) + `lib/tests/test_asof_filings.py`
  - `7d0c2c1` Validation: `cases.install` places a hash-verified case into a sandbox checkout's data root
  - `e8f6f19` Validation: `stance_inputs_asof` check (policy, inputs, check, cli, tests)
  - `f653467` Validation docs: `validation/docs/stance_checks.md`
- v1 (`backup/2147-chain-pre-v3`) not reused.

## Why a lib change (owner please note)
`announcements_between` drops filings that are now index documents. 511144's 2026-08-12 trigger
`bse_511144_1c1a1516…` and ARSSBL's 2026-10-13 trigger `bse_544530_7fc3bc1b…` were plain announcements when
the link ran and have since been matched to index documents, so through `announcements_between` they read
`input_not_in_index` and 511144 failed. A trigger's date is its filing date, so I added
`AsOfLedger.filings_between` (lib/asof.py, additive; `scan_announcements` clamped at FEED_START_DATE, no exclusion).
No existing method changed; independent of T-20261016-2252's change to `announcements_between`.

## Case mode
No tool put a case into a sandbox root, so `backend/validation/cases/install.py` does it: refuses unless
`paths.CHECKOUT.mode == "sandbox"`, targets from `cases.roots.production_roots()`, refuses a differing
existing file, raises on a store it does not place or one not frozen.

## Acceptance checks (from the sandbox worktree, `PYTHONPATH=.`)
Setup: `python -m backend.validation.cases.install $C/<case> --store index --store workflow_cache
--store quarter_versions --store stances --store bse_day_files --store nse_day_files --store exchange_attachment_hashes`
for 511144, ARSSBL, CHANDAN (223 / 271 / 221 files placed).

1+3. `python -m backend.validation.stance_inputs_asof.cli 511144 ARSSBL CHANDAN --through 2026-10-15`
```
511144: as_of_clean (35 input(s) over 14 link(s) dated on or before their as_of) check=stance_inputs_asof@1 fp=77456dbe…
ARSSBL: as_of_clean (13 input(s) over 12 link(s) dated on or before their as_of) check=stance_inputs_asof@1 fp=e66d3df9…
CHANDAN: as_of_clean (11 input(s) over 6 link(s) dated on or before their as_of) check=stance_inputs_asof@1 fp=45f4322e…
exit 0
```
   (BSE: 511144, ARSSBL; NSE-only: CHANDAN.) Hand check of one link is QA's.
2. Planted, real: second sandbox `.claude/worktrees/T-20261016-2235-plant` (branch `tmp/T-20261016-2235-plant`),
   511144 installed, the 2026-10-07 trigger appended to the 2026-08-12 link's `trigger_docids` in the sandbox log:
   `511144: leaked (link 2026-08-12: trigger_docids bse_511144_4ed443ba-… input_after_as_of (input dated 2026-10-07, link as_of 2026-08-12))`, exit 1.
   Also `test_planted_trigger_after_as_of_names_link_input_and_both_dates`.
3. AST test `test_package_reads_no_file_itself`: package calls no open/read_text/json load/glob/day-file/scan helper
   and imports none of backend.config.paths, backend.lib.events, backend.raw, json, os, pathlib, csv, pandas.
4. `test_unresolvable_input_fails_as_not_in_index` (trigger, quarterly, annual); real plant `bse_511144_ghost`
   in the plant sandbox: `link 2026-10-07: trigger_docids bse_511144_ghost input_not_in_index (input dated None, …)`.
5. `test_verdict_carries_id_version_and_fingerprint`; CLI prints `check=stance_inputs_asof@1 fp=…`.
6. `pytest backend/validation backend/stance backend/stores/tests/test_boundaries.py backend/lib/tests/test_asof_filings.py`:
   262 passed. Full suite from backend/ (both in sandboxes): base `9013baa` (`.claude/worktrees/T-20261016-2235-base`)
   71 failed/errored, head 66; `comm -23 new base` empty. Entry points import: stance.reconcile, stance.runner,
   e2e.run, intake.runner, workflow.cli, stance_inputs_asof.cli, cases.install.
   Note: in a fresh sandbox 39 validation/stance tests fail at base too, all on missing
   `alto_data/system/legacy_chain_starts.json`; I copied that file read-only from live into both sandboxes before the runs.

## Behaviour changes
None in the product: one additive ledger method; new read-only check, new sandbox-only installer.

## Not done / notes
- `--through` is required (no default); for a case it is the case as_of. A recorded trigger filed after `--through`
  reads `input_not_in_index`.
- Annual date is `filed_at` of the analysis whose `annual_report_docid` matches (`list_annual_analyses`); a docid
  with no stored analysis reads `input_not_in_index`.
- Leftover worktrees for QA/cleanup: `-base`, `-plant` (branches `tmp/T-20261016-2235-base`, `tmp/T-20261016-2235-plant`).

## Found
- Triggers recorded by stance links can later become index documents (511144 2026-08-12, ARSSBL 2026-10-13), so a
  re-run of the same link today would not see that announcement. Not a leak, but a reproducibility gap worth an owner look.

Next: QA on `9013baa..f653467`.
