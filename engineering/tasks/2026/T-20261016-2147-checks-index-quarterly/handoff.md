# Handoff: T-20261016-2147-checks-index-quarterly (round 1)

Branch `eng/T-20261016-2147-checks-index-quarterly`, worktree `.claude/worktrees/T-20261016-2147`.
Base `9950df7`. Commits: c660a51 (DataAccess.stored_quarterly_versions; intake read_record),
e7b77e9 (index_dates), 6c97598 (quarterly_versions), e96ae01 (intake_failures),
d3fd000 (cases/access.py, stage_fleet CLI, validation/docs/stage_checks.md). Not pushed.

## Acceptance
1. `python -m backend.validation.stage_fleet.cli --case $C/511144@2026-10-15 $C/CHANDAN@2026-10-15 $C/ARSSBL@2026-10-15`
   (C=alto_testcases/cases; each case hash-verified by load_case first). Output:
   ```
   511144 index_dates: pass / quarterly_versions: pass / intake_failures: pass
   CHANDAN index_dates: pass
   CHANDAN quarterly_versions: FAIL Q1_FY27/2026-08-20: no_analysis
   CHANDAN intake_failures: FAIL stockscans_chandan_concall_ppt_jun2026ppt: failed at extraction: LLM could not determine the reporting period from this document's content
   ARSSBL index_dates: pass
   ARSSBL quarterly_versions: FAIL Q1_FY27/2026-07-14, Q1_FY27/2026-07-15, Q2_FY27/2026-10-13, Q2_FY27/2026-10-15: no_analysis
   ARSSBL intake_failures: pass        exit=0, read_errors []
   ```
   (CHANDAN's quarterly_versions failure is not asked about by the acceptance; its case has no stored quarterly analysis.)
2. Per-reason tests: `validation/index_dates/tests/test_reasons.py` (missing reporting_period, publish_date, source, legacy "llm" source, annual without filed_at, 4 out-of-chain entries ignored incl. dated before chain start), `validation/intake_failures/tests/test_failures.py`, `validation/quarterly_versions/tests/test_reasons.py` (NO_SUCH_VERSION, NOT_IN_CHAIN, STALE_DOCS, STALE_BASE, no_analysis).
3. `validation/stage_fleet/tests/test_boundaries.py`: AST, no check imports another check's folder, no write call/write-mode open; quarterly_versions/check.py imports and calls `validate_versions`.
4. Every verdict carries CHECK_ID/CHECK_VERSION/fingerprint(inputs.to_record()); `test_changing_one_entry_changes_the_fingerprint` (index_dates).
5. `touch marker; python -m backend.validation.stage_fleet.cli --fleet --out $TMPDIR/t2147.summary.json` 22:01:54-22:02:01 IST, exit 0, 372 companies, 0 read errors.
   States: index_dates fail 5 / pass 367; intake_failures fail 8 / pass 364; quarterly_versions fail 15 / pass 357.
   Reasons: missing_filed_at 1, missing_publish_date 4, missing_publish_date_source 4, missing_reporting_period 1; failed_item 9; no_analysis 27.
   `find <index dir> <intake companies> <cache/quarterly_update> <legacy_chain_starts.json> <universe csv> -newer marker` -> empty.
   Read-error -> non-zero: `stage_fleet/tests/test_run.py` (summary records it; cli exits 1 iff read_errors).
6. `pytest backend/validation`: 119 passed. Full suite: base 66 failed / new 66 failed (1573 passed), `comm -23 new base` empty. `stores/tests/test_boundaries.py` 2 passed. Entry points intake.runner, stance.runner, e2e.run, workflow.cli import.

## Behaviour changes the owner must know
- `DataAccess.list_quarterly_versions` now reads through a new `_stored_quarterly_outputs` (same code moved; output unchanged); new public `stored_quarterly_versions`.
- `stores/intake/repository.read_record(path)`: public validated read for copied queues.
- index_dates scope (`index_dates/policy.py`, `scope.py`): blob_stored concall entries with quarter >= chain min_quarter and not dated before start_date; annual reports FY >= CHAIN_ANNUAL_KEY (FY26). Entries with no reporting_period are in scope unless dated before start. Not-stored copies are out of scope. Owner may want to confirm this reading of "entries the chain uses".
- A concall entry with a dated source but no publish_date makes `lib.concall_dates` raise during enumeration: a read error, not a `missing_publish_date` verdict (test docstring, `index_dates/tests/test_reasons.py`).
- Case mode reads legacy chain starts from the product (cases don't freeze them); an empty failed/ folder absent from a case is read as empty only when the manifest records the intake store frozen (`validation/cases/access.py`).
- `stage_fleet/run.py` catches every exception per check as a read error (recorded, printed, exit 1) — the acceptance asks for that; it never counts as a pass.

## Not done
- No wiring into e2e/Dagster/proposal (out of scope). No CLI-level subprocess test of exit 1 (logic covered in test_run.py).

## Found
- None outside the task.
