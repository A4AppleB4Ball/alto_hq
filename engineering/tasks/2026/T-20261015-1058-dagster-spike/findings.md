# Findings: T-20261015-1058-dagster-spike

Dagster 1.13.26 in its own venv. Code: branch `eng/T-20261015-1058-dagster-spike`, `backend/orchestration/dagster_spike/`. Companies: ARSSBL, CHANDAN and **20MICRONS** (chain Q3_FY26, Q4_FY26, Q1_FY27, all analysed). Verdict: **Dagster can carry the chain**, but not with a blocking check in a batched run (Q2).

## 1. Partitioning
**Company only.** Measured on all companies with a stance: 484 with `latest.json` (485 with `log.jsonl`, see Found). 484 partitions per asset and 484 check specs load in 1.2 s. One batched run over all 484 (3 stages) took 76 s, which is the product's own reads. Webserver GraphQL: partition keys 0.31 s, partition statuses 0.31 s, all 484 check results 0.14 s, UI index 0.04 s. Result matches the fleet scan: 10 checks FAILED, stance materialised for 474 of 484. Company × quarter was not measured: the quarter is already in the check metadata (`missing_quarters`), and a second axis would multiply every backfill by ~3 for no extra decision.
Caveat: partitioned asset checks are *preview* in this version. Check names allow only `[A-Za-z0-9_]`; symbols like `BOSCH-HCIL` fail, so the name hex-encodes the symbol (`definitions.py: check_name`). A check result also cannot carry a partition: a check step returns one result per check spec, so per-company results need one spec per company (484 specs).

## 2. Wrapping cost
Pattern (`definitions.py`): a `multi_asset` with `BackfillPolicy.single_run()` calls the observer once with `context.partition_keys`; ~8 lines per stage. Product code changed: **none**. Costs found:
- The default fs IO manager refuses a single run over several partitions; assets must be spec-based (`MaterializeResult`, no returned value).
- **Blocking checks are run-level.** One failing company would block the stance for the other two in the same batched run. So checks are non-blocking, and the stance asset gates each company itself with the same observer (`observe_quarterly`) and materialises only complete ones (skippable asset, explicit per-partition `AssetMaterialization`). A follow-up should keep one completeness function used by both check and gate.
- **Wrong-but-green remains:** the run status is SUCCESS although 2 checks failed. The agent must read check results, not run status (`query.py` does).
- Each stage re-reads the stores (3 reads of the fleet per run). Fine at 76 s.
- Stores: the stance read had to go through `CompanyStore` (`stores/tests/test_boundaries.py`).
- The production Python env has no Dagster; `backend/orchestration/dagster_spike/{definitions,query,fleet_definitions}.py` import it and fail in prod. Only `observers.py` and its tests import without it.

## 3. Running on the Mac
Not demonstrated (the Mac was not slept). From Dagster's source (`_scheduler/scheduler.py:631-642`): a schedule with no partition set that missed several ticks while the daemon was down or the Mac asleep launches **only the latest** missed tick and logs a warning; a partitioned schedule catches up to `max_catchup_runs` (default 5). Daemon and webserver: two launchd agents (`dagster-daemon run`, `dagster-webserver -h 127.0.0.1`), `KeepAlive` true, `DAGSTER_HOME` and the venv python in the plist; sleep suspends them and they resume on wake. A caffeinate/`pmset` wake before 00:30 is the owner's call. A follow-up task proves it on the real Mac.

## 4. Run only what is needed
Add `document_index` upstream (done in the spike) and put `AutomationCondition.eager()` on `quarterly_analysis`: it fires when an upstream is updated and not when nothing changed, skipping partitions with missing or running deps (`automation_condition.py:926-945`). The index asset must report change: an observation whose data version is the index fingerprint per company, so a new results document changes it and only that company's partition runs. Explained from the source; not demonstrated (needs the daemon running).

## 5. Scheduler jobs (`pipeline_scheduler.yaml`, 25 jobs, 7 enabled: quarterly_watch, exchange_feed, announcement_reconciler, refresh_price_cache, prefetch_universe_prices, price_watchlist, price_watchlist_union)
- **Move to Dagster:** `e2e_morning_0030`, `e2e_morning_0800` (the chain, off today), `intake_runner`, `stance_runner`, `quarterly_watch`, `annual_report_watch`, `exchange_feed`, `announcement_reconciler`, `resolve_concall_publish_dates`, `pipeline_self_heal` (the producers and the chain; the `dependency` type becomes asset deps).
- **Keep in the asyncio loop:** `execution_runner` (server only, 5-second loop, trading stays as decided); price jobs (`refresh_price_cache`, `prefetch_universe_prices`, `price_watchlist*`) until the chain is stable, then move as upstream assets.
- **Retire or leave off:** the macro, vahan, npci, power_grid, composite_run, export jobs (all disabled, not the compute chain), the three `aws_login_*` jobs (disabled; a credentials matter, the owner's call).

## 6. Proposed follow-up tasks, in order
1. `completeness-check`: the check and the single gate function in `backend/` (not in `orchestration/`), importable without Dagster. Acceptance: ARSSBL/CHANDAN fail naming their quarters, the ten incident companies fail, a complete company passes, frozen cases pinned.
2. `proposal-gate`: the rebalance proposal refuses a stance whose latest quarter has no valid analysis. Acceptance: re-run of the 2026-10-15 proposal inputs lists ARSSBL and CHANDAN as excluded with reasons.
3. `dagster-environment`: Dagster in its own env, launchd daemon and webserver, `DAGSTER_HOME` placement. Acceptance: survives a reboot and a sleep over the 00:30 tick with the tick recorded.
4. `dagster-chain-wrap`: producers, intake, quarterly and stance as assets for the watchlist, still calling the product CLIs batched. Acceptance: one daily run, per-company status readable by `query.py`.
5. `verdict-fingerprints`: check results carry fingerprint and version and the table reports stale ones (Q8).
Each is separate; 3 and 4 wait for 1.

## 7. Run history
Dagster's event log and compute logs hold what the e2e per-company files hold (step events with timestamps, failures with stack traces, check metadata), queryable per run and per asset. `logs/e2e` is 18 MB over 244 run folders today. Dagster's sqlite instance would replace the per-run folders; keep as files: the product CLIs' own stdout logs (Dagster captures them as compute logs, so no separate file) and `logs/e2e/progress.jsonl` only until the cut-over. Retention: not measured; Dagster has no automatic retention for runs on sqlite by default, so a retention job is part of task 3. Not tested: replacing the e2e files in place.

## 8. Verdict validity
Yes. Each check result stores `fingerprint` (sha256 of the index enumeration and every stored quarterly version it read) and `check_version`. `verdict_is_current(recorded_fingerprint, recorded_version, state)`; tests in `tests/test_verdict_validity.py` against a copy of ARSSBL's index in a temp dir: unchanged copy stays valid; one document's `publish_date` touched in the copy reads stale; a new check version reads stale. The fingerprint is computed through `DataAccess`, so it follows the product's own contract.

## Found
- BHADORA has `log.jsonl` but no `latest.json` (485 vs 484 stances). Not opened as a task.
