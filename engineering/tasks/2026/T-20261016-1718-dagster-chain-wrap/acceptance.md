# Acceptance: dagster-chain-wrap (v2, replaces v1)

Differences from v1: every check names its command and a measured
number, check 3 runs on a frozen case so no production store is touched, and
the cut-over is split from the build.

Environment: Dagster lives only in `/Users/kmrh581/personal/projects/workspace/alto_dagster/venv`
(production Python has no Dagster). Dagster commands use that venv's python,
with `DAGSTER_HOME` set to a temp dir for tests (never `alto_dagster/home`).
Product-stage runs write to a temp data root created by the case freezer
(`backend/validation/cases`, merged) or with the checkout-data-root flags
(T-20261015-0321-checkout-data-root; this task starts after it merges). LLM
stages: pilot of the 2 named companies only; anything beyond is the owner's.
Depends on completeness-check, dagster-environment (merged), and
checkout-data-root (in flight).

Pilot companies, from the completeness result for the 2026-10-16 stored state:
one complete (20MICRONS, chain Q3_FY26..Q1_FY27 all analysed) and one that
blocks (ARSSBL, Missing quarters per the incident). Pilot as_of must be on or before 2026-10-13 (the last day the Dhan daily cache covers; stance prices are read from the cache with no credentials, per T-20261017-0010; stance runs with `LLM_CONFIG_PATH=backend/config/llm_benchmark_deepseek.yaml`). Same pair as the spike
(CHANDAN is the alternative blocking one).

1. **Batched, one call per stage.** A Dagster run over the two partitions, launched with `dagster job execute`/`materialize` from the venv against the temp root, calls each existing CLI stage (producers, intake, quarterly, stance) once, not once per company. Producers, intake and quarterly name both symbols; stance names the companies that pass the completeness gate (20MICRONS; ARSSBL is gated out). Evidence: the run's event log lists exactly one stage-start event per stage, and each stage's recorded CLI invocation shows its symbol list. Count of stage invocations = 4, not 8.
2. **Per-company verdicts in stored records.** A short Python query (the
   spike's `query.py` pattern, run with the venv python, no UI) prints for each
   of the two companies every asset's state and the completeness verdict
   (`state`, `reason`, missing quarters) read from Dagster's stored check
   results. ARSSBL shows its blocking state and quarters; 20MICRONS shows
   complete. The printed verdict equals
   `python -m backend.validation.completeness.cli ARSSBL 20MICRONS` run
   against the same root, line for line.
3. **A failure stops only its company.** On a frozen case copy, make the
   quarterly stage fail for ARSSBL only (ARSSBL's missing filing body in the frozen case is the failure; no code edit). 20MICRONS' stance materialises (new link in the temp
   `log.jsonl`, hash changed); ARSSBL's stance asset does not materialise,
   its `log.jsonl` hash is unchanged, and its failure reason is in the record
   the query prints.
4. **Not wrong-but-green.** The spike showed a run can be SUCCESS while checks
   failed. For the check 3 run, the query exits non-zero and prints a
   summary line listing the failing company by symbol and reason; a test
   asserts that a run with any failing company is never reported as clean.
5. **Product code unchanged except company-list entry points.** `git diff --stat
   develop...` shows only `backend/orchestration/` plus entry points that had
   to accept a company list; for each such entry point a test fails on base and
   passes after (commands named in the handoff).
6. **Scheduler untouched until cut-over.** `backend/config/pipeline_scheduler.yaml`
   has no diff in this task. The jobs spike section 5 lists as moved
   (`e2e_morning_0030`, `e2e_morning_0800`, `intake_runner`, `stance_runner`,
   `quarterly_watch`, `annual_report_watch`, `exchange_feed`,
   `announcement_reconciler`, ...) are disabled in a separate step only when
   the owner approves cut-over; the 7 currently enabled jobs and
   `execution_runner` stay in the asyncio loop.
7. **Read-only on production.** `find /Users/kmrh581/personal/projects/workspace/news_server/data -newer <marker>`
   after the pilot lists only files the live system itself wrote (stated, as
   in the dagster-environment evidence), none under the two companies'
   stance dirs.
8. **Repo checks.** `python -m pytest backend/stores/tests/test_boundaries.py -q`;
   every entry point imports (`python -c "import <module>"` per changed
   module); the suite against base shows no new failure. Orchestration tests
   run with the venv python and the observer tests also run in production
   Python (they must import without Dagster).
