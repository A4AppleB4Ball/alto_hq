# Handoff (attempt 2): T-20261016-1718-dagster-chain-wrap

Branch `eng/T-20261016-1718-dagster-chain-wrap`, rebased onto main `1665a1c` (contains T-20261017-0010 `354cbda`; the "354cbda" base you named is an ancestor of main). Commits: `341cfd3`, `049e488`, `0908f38`, `5660894`, `6a80302`. No code change this attempt (the rebase was clean). Not pushed. acceptance.md hash 1d9c1ac2... verified unchanged. Self-assessment only; QA decides.

## Run (all checks 1-4)
Sandbox root `alto_sandboxes/chainG1` (checkout file `.alto_checkout.yaml`, gitignored). Restore: `python -m backend.orchestration.chain.case_root <ARSSBL case> <20MICRONS case> --live-system-dir ... --system-files results_calendar.json --live-blob-index ... --live-day-files-dir ... --day-files-from 2026-01-01 --day-files-to 2026-10-15 --universe-add 20MICRONS --rewind 20MICRONS=2026-08-06`.
No Dhan secrets and no `active_broker.json` copied (the live-workspace copy was blocked by the permission system and is not needed now). Launch (venv, `DAGSTER_HOME=/tmp/dh_G1`, `ALTO_CHAIN_COMPANIES=ARSSBL,20MICRONS`, `ALTO_CHAIN_END_DATE=2026-08-14` (as_of <= 10-13), `LLM_CONFIG_PATH=backend/config/llm_benchmark_deepseek.yaml`): `dagster asset materialize -m backend.orchestration.chain.definitions --select '*' --partition-range "ARSSBL...20MICRONS"`; exit 0, run SUCCESS. Read: `python -m backend.orchestration.chain.query` (venv), exit 1. Output saved `/tmp/G1.query`.

1. PASS. Query: `stage producers/intake/quarterly/stance: started 1x` (4 invocations). Commands: producers `--companies ARSSBL 20MICRONS`; intake `--symbols ARSSBL 20MICRONS`; quarterly `--companies ARSSBL,20MICRONS`; stance `--end-date 2026-08-14 --symbols 20MICRONS` (gate passers only).
2. PASS. ARSSBL `check FAILED` `incomplete (Q1_FY27 missing; Q2_FY27 missing)`; 20MICRONS `check SUCCEEDED` `complete`. The `|` lines of the query vs `python -m backend.validation.completeness.cli ARSSBL 20MICRONS` on the same root: diff IDENTICAL.
3. PASS. Failure is ARSSBL's own missing filing body (no edit): quarterly log `ARSSBL: blocked, announcements_incomplete ... bse_544530_... (2026-06-06 ...): no stored body`, stage exit 1. ARSSBL stance `not materialized [gated: ...]`; its `log.jsonl` sha256 `dd882e9026a24249` before (case) and after, 12 lines both. 20MICRONS stance materialised, real LLM pass (deepseek, 2 checkpoints from 5 candidate dates): `log.jsonl` 21 lines `4338e1098f6ce908` (after rewind) -> 23 lines `10bf291d1c67f520`; new links as_of 2026-08-06 (Q1 FY27 results) and 2026-08-14 (acquisition). No price error (cache read, no credentials).
4. PASS. Run SUCCESS, query exit 1, `SUMMARY: FAILING ARSSBL: completeness incomplete: Q1_FY27 missing; Q2_FY27 missing; stance not materialized; stage quarterly exited 1`. Tests: `chain/tests/test_report.py::test_a_blocked_company_is_never_clean`, `dagster_tests/test_chain_run.py::test_one_call_per_stage_and_a_blocked_company_stops_only_itself`.
5. PASS. `git diff --name-only main..HEAD | grep -v ^backend/orchestration/` is empty (19 files, +1001). No entry point changed.
6. PASS. `git diff main..HEAD -- backend/config/pipeline_scheduler.yaml`: empty.
7. PASS with a caveat. `touch /tmp/marker_G` before; `find news_server/data -newer /tmp/marker_G -type f` lists one file: `alto_data/workspace/scienceamit1/book/default/snapshots.jsonl` (mtime 02:38:24, during my run). The sandbox checkout writes only under `alto_sandboxes/chainG1`, no stance dir of either company is touched; I attribute it to the live system's own book snapshot writer, but I did not prove that independently.
8. PASS. `stores/tests/test_boundaries.py`: 2 passed. Imports: case_root, stages, verdicts, report, names, settings, verdict_source in production Python; definitions and query in the venv (they need the settings env vars by design). `pytest backend/orchestration/chain/tests`: 20 passed; `dagster_tests` (PYTHONPATH venv site-packages): 4 passed. Full suite, base main `1665a1c` vs branch: 61 failures each, `comm -23 new base` empty.

## Watchlist edit
`--universe-add 20MICRONS` appended to the worktree's tracked `data/metadata/price_watchlist.csv`. Handled explicitly: reverted with `git checkout data/metadata/price_watchlist.csv` after the run; never staged; `git status` clean except pre-existing untracked `backend/data/dashboard/`. The case freezer does not need it (case_root adds it only to run stance for a company that left the universe).

## Notes
- Production data root not written by me. `.alto_checkout.yaml` still points at `chainG1` (ignored file).
- Calendar copy is stale so verdicts print `calendar_stale=True`, same in the CLI.
- Found (earlier, unchanged): 20MICRONS left the universe on 2026-10-07 so its production stance chain cannot advance.
