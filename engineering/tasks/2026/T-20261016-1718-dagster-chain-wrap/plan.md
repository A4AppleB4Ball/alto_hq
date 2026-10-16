# Plan: dagster-chain-wrap (written after the first build, to match what was built)

**Touches.** New only: `backend/orchestration/chain/` (stages, verdicts, report, names, settings, verdict_source, definitions, query, case_root, tests, dagster_tests) and `backend/orchestration/docs/dagster_chain.md`. No product file changes: every stage CLI already takes a company list (`intake.runner --symbols`, `workflow.cli --companies`, `stance.runner --symbols`, `resolve_concall_publish_dates --companies`). No money path.

**Change.** Dagster code location (venv python, no product deps) with four company-partitioned assets, each calling its CLI once per run via the product python; completeness verdicts (single function, `backend.validation.completeness`) as per-company checks and the stance gate; `query.py` prints stored records, ends with a SUMMARY and exits non-zero if any company failed. Owner notices: nothing in production changes; scheduler untouched.

**Design call to flag.** The stance CLI is given the companies that pass the gate, so with ARSSBL blocked the stance command lists only 20MICRONS. Check 1's wording (both symbols in all four invocations) and checks 2/3 (ARSSBL blocked, its stance not run) cannot both hold; I kept the gate.

**Checks, how run.** Sandbox worktree + `case_root` restore of the ARSSBL and 20MICRONS cases (20MICRONS frozen for this task); `dagster asset materialize -m backend.orchestration.chain.definitions --select '*' --partition-range ARSSBL...20MICRONS` with the venv; then `query`; compare with `backend.validation.completeness.cli`; hashes of `log.jsonl` before/after; `find -newer` on the live data root; boundaries test, imports, suite vs base.
