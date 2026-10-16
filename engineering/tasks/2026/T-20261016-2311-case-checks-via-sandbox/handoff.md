# Handoff: T-20261016-2311-case-checks-via-sandbox

- Branch `eng/T-20261016-2311-case-checks-via-sandbox`, worktree `.claude/worktrees/T-20261016-2311-case-checks-via-sandbox`.
- Base: **7d0c2c1** on eng/T-20261016-2235-checks-stance-inputs-asof (reuses its `cases/install.py`, per the brief; not on main yet). So this branch carries 7d0c2c1 and lands after or with T-2235's installer.
- Commits (7d0c2c1..6b96141):
  - f6b9b33 Validation cases: freeze the legacy chain starts file into each case and install it at its store path (also holds `roots.live_roots`, which belongs with the next commit)
  - a4621bb Validation cases: freeze --live and cases.extend add a store to an existing case through the freezer
  - 4f6cf79 Validation cases: install opens a frozen intake store's queue folders through CompanyIntake
  - 10f21ed Validation cases: live_roots records the freezer checkout's commit
  - 33ab597 Validation: stage_fleet --case installs the case into a sandbox and reads it through DataAccess and the intake store; remove cases/access.py
  - b34db53 Validation: selection names the index and failed/ paths through DataAccess and the intake store
  - 3001bcd Validation: AST test that no validation module outside cases/ builds a store path
  - 6b96141 Validation docs
- alto_testcases: **2f5e6ce** (local only) extends 511144, ARSSBL, CHANDAN, ORIANA, 3IINFOLTD with `legacy_chain_starts` through `python -m backend.validation.cases.extend <case> --store legacy_chain_starts --live`, run from freezer commit 10f21ed. No case file was hand-edited.

Fresh sandboxes used (made with `backend.config.new_sandbox_worktree` from main, at 6b96141): `T-2311-acc` (items 1, 2, 4), `T-2311-fresh` (item 7), `T-2311-suite` (full suite); base suite in `T-2311-base` (detached 7d0c2c1, empty sandbox root). The command outputs are in `outputs/`.

## Acceptance

Baseline before the change: `python -m backend.validation.stage_fleet.cli --case <case>` from the main checkout (old access.py code, live legacy file), for all five cases.

1. **PASS.** In `T-2311-acc`, starting empty: `PYTHONPATH=$PWD python outputs/audit_run.py --case …/511144@2026-10-15 …/CHANDAN@2026-10-15 …/ARSSBL@2026-10-15` exited 0. The verdict lines match the baseline exactly: 511144 passes all three checks. CHANDAN fails quarterly_versions Q1_FY27/2026-08-20 no_analysis, and fails intake_failures on stockscans_chandan_concall_ppt_jun2026ppt. ARSSBL fails quarterly_versions no_analysis x4 (Q1_FY27/2026-07-14, 07-15; Q2_FY27/2026-10-13, 10-15). The audit hook raises on any open() under the live data root and recorded **0** live opens, against 123 sandbox opens (`outputs/acc1.txt`).
2. **PASS, with a limit.** The ORIANA case passes all three checks, same as the baseline, while every open of a live file raises (the same as the live `legacy_chain_starts.json` being removed): 0 live opens (`outputs/acc2.txt`). The case's copy holds ORIANA's entry (Q3_FY26 / 2026-01-01), the entry QA showed changes the verdict. A copy of the case with ORIANA's entry changed is refused: `CaseIntegrityError: changed: stores/legacy_chain_starts/legacy_chain_starts.json`. The limit: I did not change or remove the real live file, because the worktree rules forbid writing production. Blocking the live opens stands in for that change.
3. **PASS, with an exemption the owner should rule on.** `pytest backend/validation/tests/test_no_store_paths.py` gives 47 passed. On the old code the same test fails 2 (stage_fleet/cli via access.py, and scenarios/selection/inputs.py). The rules: no `backend.config.paths` store names (an allowlist of DATA_ROOT, ALTO_ROOT, NEWS_SERVER_ROOT, RESULTS_CALENDAR_PATH); no intake path builders (companies_root, stage_record_paths, read_record, INTAKE_DIR); no `_index.json` / `legacy_chain_starts.json` literals; no `/ "<stage folder>"` joins. **`backend/validation/cases/` is exempt.** Freeze, extend and install exist to copy store files byte for byte, so they must name them. The acceptance says "no module under backend/validation". If the owner reads that literally, item 3 is not met, and the freezer would have to obtain every source path from product readers instead.
4. **PASS.** 3MINDIA has an index but no live intake queue. I froze it with `freeze 3MINDIA --as-of 2026-10-15 --out $TMPDIR/... --live --not-initiated --expect-empty intake …` into a temp dir; it is not committed to alto_testcases. Case mode exits 1 with `intake_failures: READ ERROR FileNotFoundError: No intake queue for 3MINDIA at <sandbox>/…/intake/companies/3MINDIA`. Live, `production_failed_records('3MINDIA')` raises the same FileNotFoundError at the live path (`outputs/acc4.txt`).
5. **PASS.** `pytest backend/validation` gives 189 passed. `stores/tests/test_boundaries.py`, `stores/intake` and `lib/tests` give 166 passed. Full suite (`--continue-on-collection-errors`): base 7d0c2c1 has 95 failed / 8 errors / 1563 passed; branch has 95 failed / 8 errors / 1620 passed. `comm -23 new base` is empty (103 lines each; `outputs/suite.{base,new}`). Every changed entry point imports, plus intake.runner, stance.runner, e2e.run and workflow.cli.
6. **PASS.** The freezer has a `legacy_chain_starts` spec (whole file, sha256 in `files`); `install` places it at `LEGACY_CHAIN_STARTS_PATH`. All 5 committed cases were extended through `cases.extend`, each copy sha256 d7cfa388…8826, the same as live. `python -m backend.validation.cases.load` verifies all five.
7. **PASS.** In fresh sandbox `T-2311-fresh` I installed every store each of the 5 cases froze (`cases.install`). No file was copied from live. `pytest validation stance` gave **306 passed, 0 failed**, with no `legacy_chain_starts` in the output (`outputs/acc7.txt`). For contrast, the same stance tests in the empty `T-2311-suite` sandbox fail 7, with 37 "legacy_chain_starts.json not found" lines.

## Behaviour changes the owner must know
- `stage_fleet --case` now runs **only from a sandbox checkout**; it raises `NotASandbox` in the main checkout. It writes the case's stores into that sandbox's data root and leaves them there. A second case with different bytes for a shared file (for example a different legacy file) raises `FileExistsError`. Use a fresh sandbox per as-of.
- Freezing from a worktree needs `--live`: a worktree resolves only its sandbox. `live_roots` maps this checkout's data root and repo onto the main checkout's declared ones. The Dhan cache and NSE checkout under `~` are used unchanged.
- New `cases.extend`. The manifest gains `extensions: [{stores, at, commits}]`, and commits now include `freezer`.
- Product code, read-only helpers only, no behaviour change: `DataAccess.announcement_index_path`, `stores.intake.repository.stage_folder_path` and `FAILED_FOLDER`. `get_announcement_index` and `stage_record_paths` use them.

## Not done / caveats
- The cases' legacy copy is the live file as of the extension (2026-10-17), not as of 2026-10-15. It is written once by a migration, but I did not prove it unchanged since 10-15.
- The extension's recorded `alto`/`news_server` commits are `dirty: true`, because the main checkout and the data repo had uncommitted changes. `freezer` 10f21ed is clean.
- f6b9b33 mixes in `live_roots` (see the commit list).
- `alto_testcases/cases/20MICRONS@2026-10-15` is untracked (not mine). I did not touch or extend it, so it has no legacy store and case mode will refuse it.
- I left the extra worktrees and branches `eng/T-2311-{acc,fresh,suite}` and `.claude/worktrees/T-2311-base`, plus sandbox roots under `alto_sandboxes/`, for QA to reuse. Delete them after QA.

## Found
- `.claude/worktrees/` holds about 90 worktrees, many from finished tasks. Stale worktrees could be mistaken for current state, and each one now needs its own `.alto_checkout.yaml`.
