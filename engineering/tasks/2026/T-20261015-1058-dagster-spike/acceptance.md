# Acceptance: T-20261015-1058-dagster-spike

Done when each check passes, run by QA, with its output in evidence.md, and
`findings.md` answers every question in section B with evidence.

## A. Checks

1. **Isolated.** Dagster is installed in its own virtualenv; `DAGSTER_HOME`
   is under `../alto_runs/T-20261015-1058-dagster-spike/`. The production
   environment's `pip freeze` is identical before and after.
2. **Read-only on product data.** Record the newest mtime under
   `../news_server/data` before the spike runs; after the full demo run,
   no file there has a newer mtime written by the spike's processes.
3. **The check blocks.** One run over the three companies: the completeness
   check fails for ARSSBL and CHANDAN, naming each missing quarter (ARSSBL
   Q1_FY27 and Q2_FY27; CHANDAN Q1_FY27); their stance asset is not
   materialised; the complete company's check passes and its stance asset
   is materialised. Shown from Dagster's stored records, not the console.
4. **Agent-readable.** A short Python query against the Dagster instance
   (no UI) prints, per company, last run status, each asset's state and each
   check's result with its reason. QA runs it and compares with check 3.
5. **One batched run.** The three companies are processed in a single run
   that calls the existing code once per stage with all three companies,
   not one run per company.

## B. Questions findings.md answers

1. Partitioning: company only, or company × quarter? Measured: create the
   partitions for all 484 companies with a stance (and × quarters if
   chosen); report UI and query time.
2. Wrapping cost: lines and pattern to wrap one existing CLI stage as an
   asset; what had to change in product code, if anything.
3. Running on the Mac: how the daemon and webserver are kept up (launchd),
   and what happens to a schedule when the Mac sleeps through it.
4. "Run only what's needed": which Dagster mechanism (automation conditions,
   sensors) would trigger a company's quarterly analysis when a new results
   document lands; demonstrated or explained with the docs.
5. What the scheduler jobs in `backend/config/pipeline_scheduler.yaml`
   become: kept, moved, or retired, per job.
6. Proposed follow-up tasks, each with a one-line acceptance check, in
   order. No more than needed for the next step.
