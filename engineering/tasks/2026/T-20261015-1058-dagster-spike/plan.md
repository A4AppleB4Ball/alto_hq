# Plan: T-20261015-1058-dagster-spike

**Touches.** New package `backend/orchestration/dagster_spike/` on the branch only; no existing product file changes.
Read-only callers: `DataAccess.quarter_versions / chain_start / list_quarterly_versions`, `chain_quarters`, `STANCES_DIR/<sym>/latest.json` and `log.jsonl`. No entry point changes. Not a money path.

**Change.** Assets partitioned by company (static partitions): `document_index` -> `quarterly_analysis` -> `stance`. All three observe stores; `stance` records what it would run, never runs stance code.
Asset check `quarterly_complete` on `quarterly_analysis`: every chain quarter has a valid analysis; fails naming missing quarters; metadata carries input fingerprint (sha256 of the records read) and check version (question 8). One single-run partition range over the three companies, so each stage calls the existing reader once with all three.
Stance must be unmaterialised only for failing companies while the passing one materialises; Dagster's blocking check works per run, so this is a thing to measure and report.

**Environment.** Own venv and `DAGSTER_HOME` under `../alto_runs/T-20261015-1058-dagster-spike/`. Data root is production via worktree symlink, so everything is read-only.

**Acceptance commands.** (1) pip freeze before/after diff. (2) newest mtime under `../news_server/data` before/after, listing files newer than baseline and who writes them. (3) one `dagster asset materialize` over the 3 partitions, then read the instance's event log. (4) `query.py` against the instance. (5) run count == 1 and stage reader calls == 1 per stage.
