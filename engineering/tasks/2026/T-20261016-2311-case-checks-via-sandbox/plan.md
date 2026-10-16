# Plan — T-20261016-2311-case-checks-via-sandbox

Base: eng/T-20261016-2235 commit 7d0c2c1 (reuses `backend/validation/cases/install.py`, per the brief). Not a money path.

**Touches:** `backend/validation/cases/{stores,roots,freeze,install,access}.py`, `backend/validation/stage_fleet/cli.py`, `backend/validation/scenarios/selection/inputs.py` (index/failed path strings), `backend/lib/data_access.py` (one index-path method), `backend/validation/docs/{cases,stage_checks}.md`, tests under `cases/tests`, `stage_fleet/tests`. Cases in `alto_testcases` (through the freezer only). Entry points: `validation.stage_fleet.cli`, `validation.cases.{freeze,install}`. No product entry point changes behaviour.

**Change:**
- New store spec `legacy_chain_starts` (section stores): the whole `LEGACY_CHAIN_STARTS_PATH` file, hashed in the manifest. `CaseRoots` gains its path; `install` places it at the same path in the sandbox.
- Freezer gains `--extend CASE --store NAME`: adds a store not yet in a verified case, re-hashes, records the extension in the manifest. Used to extend the 5 committed cases (never hand-edited).
- `install` of a frozen intake store also opens each company's queue through `CompanyIntake` (the writer), so a frozen-but-empty `failed/` exists as it does live. An `expected_empty` intake places nothing: case mode raises like live for a never-polled company.
- `stage_fleet --case` requires a sandbox checkout, installs index, intake, workflow_cache, quarter_versions and legacy_chain_starts, then runs the checks through `DataAccess()` and `production_failed_records`. `cases/access.py` is deleted.
- AST test: no module under `backend/validation` (except the freezer/installer, whose job is to copy store files) builds an index/intake/chain-start path or lists a store dir.
- Stays the same: check logic and verdicts, `--fleet` mode.

**Acceptance, command by command (from the sandbox worktree):**
1. `python -m backend.validation.stage_fleet.cli --case <511144|CHANDAN|ARSSBL>` → compare to the live-run verdicts captured before the change.
2. ORIANA case run; then remove/alter the sandbox's... no: alter the *live* file is forbidden, so prove independence by the sandbox reading only the case copy (live path never resolved in sandbox), plus a temp-dir test with a changed live-roots file.
3. `pytest backend/validation/stage_fleet/tests/test_boundaries.py`.
4. Test + CLI run on a case whose intake is expected_empty (temp case) → raises read error.
5. `pytest backend/validation`; full suite vs base; boundary test.
6. `freeze --extend` on the 5 cases; `cases.load` verifies all.
7. Fresh sandbox, install the cases, `pytest backend/validation backend/stance`; grep failures for legacy_chain_starts.
