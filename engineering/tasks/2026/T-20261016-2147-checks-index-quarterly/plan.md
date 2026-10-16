# Plan: checks-index-quarterly

**Touches (new):** `backend/validation/index_dates/`, `backend/validation/quarterly_versions/`,
`backend/validation/intake_failures/` (each: policy.py, inputs.py, check.py, tests/),
`backend/validation/stage_fleet/cli.py` (fleet + frozen-case runner, read-only),
`backend/validation/cases/access.py` (DataAccess and intake dir over a frozen case).
**Touches (changed):** `backend/lib/data_access.py` gains `stored_quarterly_versions(symbol)`
(the StoredVersion records; `list_quarterly_versions` reuses the same reader, output unchanged);
`backend/stores/intake/repository.py` gains `failed_records(symbol, companies_dir)` read-only.
Callers of `list_quarterly_versions` (asof, stance, e2e, completeness) see no change.
Entry points: none wired (out of scope). Not the money path.

**Change.** Three pure checks over a read step, each returning `verdicts.record.Verdict`
(check id, version, pass/fail, reason, fingerprint of `inputs.to_record()`).
- index_dates: scope = blob-stored concall entries whose quarter >= chain min_quarter and not
  dated before chain start_date; annual entries with fiscal year >= CHAIN_ANNUAL_KEY. Fails per
  entry: missing reporting_period / publish_date / publish_date_source (not in DATED_SOURCES) /
  filed_at. Chain from `DataAccess.chain_start` (lib/chain_start).
- quarterly_versions: `validate_versions(stored, enumeration, chain)` reasons per stored
  analysis; every enumerated version of `chain_quarters` with no stored analysis -> no_analysis.
- intake_failures: each record in `failed/` -> failure (docid, failed_stage, last_error).
Stays the same: every product path; nothing writes.

**Acceptance runs.**
1. `python -m backend.validation.stage_fleet.cli --case <alto_testcases>/cases/{511144,CHANDAN,ARSSBL}@2026-10-15` (load_case verifies hashes first).
2-4. `pytest backend/validation/{index_dates,quarterly_versions,intake_failures,stage_fleet}`.
5. `touch marker; python -m backend.validation.stage_fleet.cli --fleet --out $TMPDIR/x.json; find <index dir> <intake companies> <cache/quarterly_update> -newer marker`.
6. pytest backend/validation, full suite vs base, stores/tests/test_boundaries.py.
