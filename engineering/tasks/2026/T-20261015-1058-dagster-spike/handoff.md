# Handoff: T-20261015-1058-dagster-spike

Branch `eng/T-20261015-1058-dagster-spike`, base `ab8a959`, commits `d73c2ce`, `99ed529`. Not pushed, not merged. Output: `findings.md`.

## Acceptance checks (A)
`R=../alto_runs/T-20261015-1058-dagster-spike`
1. **Isolated.** venv `$R/venv`, `DAGSTER_HOME=$R/home`. `python -m pip freeze` before/after diff: empty (`pipfreeze.before.txt` / `after.txt`, 508 lines).
2. **Read-only.** Baseline newest mtime 1792063411.27 (`data_mtime.before.txt`). After all runs, one file is newer: `alto_data/scheduler/logs/refresh_price_cache/2026-10-15_16-00-13_exec_40f9caa73064.log`, the live scheduler's own job that was still running at the baseline. The spike writes only under `$R` and the worktree. Weakness: this check cannot attribute writers on a live machine; QA should judge it.
3. **Blocks.** `DAGSTER_HOME=$R/home dagster asset materialize -m backend.orchestration.dagster_spike.definitions --select '*' --partition-range "ARSSBL...20MICRONS"` on a fresh instance. Stored records: ARSSBL check FAILED (missing Q1_FY27, Q2_FY27), CHANDAN FAILED (Q1_FY27), 20MICRONS SUCCEEDED; stance materialised for 20MICRONS only. Deviation: the check is non-blocking and the stance asset gates itself (findings Q2), so "not materialised" holds but Dagster's own blocking is not what does it.
4. **Agent-readable.** `DAGSTER_HOME=$R/home python -m backend.orchestration.dagster_spike.query`: per company last run status, each asset state, check result with missing quarters. Output matches check 3.
5. **One batched run.** Instance holds 1 run; steps started once each: document_index, quarterly_analysis, quarterly_complete, stance.

## Tests
`backend/orchestration/dagster_spike/tests/test_verdict_validity.py` 3 passed; `stores/tests/test_boundaries.py` passes. Full suite not run: no existing file changed, only new files under `backend/orchestration/` (note: it adds files; its tests import without Dagster).

## Behaviour changes
None to the product. Not done: sleep/launchd (Q3) and the automation condition (Q4) are explained from source, not demonstrated; retention (Q7) and company × quarter (Q1) not measured.

## Found
BHADORA has a stance log but no `latest.json`.

Next step for the owner: QA on `ab8a959..99ed529`.
