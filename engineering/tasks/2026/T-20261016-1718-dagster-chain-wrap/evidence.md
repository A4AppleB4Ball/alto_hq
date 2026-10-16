---
schema: evidence/v1
task: T-20261016-1718-dagster-chain-wrap
round: 1
qa: pass
qa_by: qa@sonnet-5.5
commits: 1665a1c..6a80302
acceptance_sha256: 1d9c1ac2848825db59fe908d95dae096e2439497b67d7cdf77dcdd7aebfe2dc9
outputs_changed: unverified
runs: [fb2eab5a-7032-4878-8795-25f5524ff842]
---

## Round 1

Cleanup first: the stopped QA run was still alive (dagster materialize, a stance runner for 20MICRONS and orphan watchers, cwd `.claude/worktrees/dcw-qa`, DAGSTER_HOME `/tmp/qa_dcw/dhome3`). Killed them, removed that worktree and `/tmp/qa_dcw`. The dev worktree was untouched. Raw logs: `/Users/kmrh581/personal/projects/workspace/news_server/verify_data/reports/T-20261016-1718-dagster-chain-wrap/`.

Own sandbox: worktree `dcw-qa2` at 6a80302, `.alto_checkout.yaml` mode sandbox, data_root `/tmp/qa_dcw2/news_server`, DAGSTER_HOME `/tmp/qa_dcw2/dhome`. Frozen cases ARSSBL@2026-10-15 and 20MICRONS@2026-10-15 restored with `backend.orchestration.chain.case_root` (results_calendar, blob index and day files 2026-01-01..2026-10-13 copied read only from live; `--universe-add 20MICRONS --rewind 20MICRONS=2026-09-01`). No credentials and no live workspace files copied or read. Run: venv `dagster asset materialize -m backend.orchestration.chain.definitions --select '*' --partition-range 'ARSSBL...20MICRONS'`, ALTO_CHAIN_END_DATE=2026-10-13, LLM_CONFIG_PATH=backend/config/llm_benchmark_deepseek.yaml. Run exit 0, RUN_SUCCESS (about 10 min, real deepseek stance pass for 20MICRONS only).

### Acceptance checks
1. PASS. `python -m backend.orchestration.chain.query` prints `started 1x` for each of producers, intake, quarterly, stance (4 invocations). Commands: producers `... resolve_concall_publish_dates --exchange-copies-end 2026-10-13 --companies ARSSBL 20MICRONS`; intake `--symbols ARSSBL 20MICRONS`; quarterly `--companies ARSSBL,20MICRONS`; stance `--end-date 2026-10-13 --symbols 20MICRONS`.
2. PASS. ARSSBL `check FAILED`, `incomplete (Q1_FY27 missing; Q2_FY27 missing)`; 20MICRONS `check SUCCEEDED`, `complete`. `diff` of the query's `|` lines against `python -m backend.validation.completeness.cli ARSSBL 20MICRONS` run after the run on the same root: IDENTICAL; also identical to the CLI before the run.
3. PASS. ARSSBL fails on its own missing body (`bse_544530_... (2026-06-06): no stored body`), no code edit; stance `not materialized [gated: ...]`. ARSSBL log.jsonl md5 0fe5164e... before and after. 20MICRONS log.jsonl md5 7e521b58... (24 links after rewind) -> 1c658367... (27 links). Note the 3 new links are the rewound dates 2026-09-09, 09-22, 10-05 rebuilt; no link after 10-05 was added (nothing new triggered up to 10-13). Hash changed and links are new in the sandbox log, but they are not links beyond the previous head.
4. PASS. Query exit 1 with run SUCCESS; `SUMMARY: FAILING ARSSBL: completeness incomplete: Q1_FY27 missing; Q2_FY27 missing; stance not materialized; stage quarterly exited 1`. My own test (`.../test_never_clean.py`, exhaustive over verdict ok x 4 asset states): exit code and summary are clean exactly when verdict ok and all four assets materialised; passes. Dev tests also pass.
5. PASS. `git diff --stat 1665a1c..6a80302` touches only `backend/orchestration/` (19 files). No entry point changed, so no entry-point tests are due. (There is no `develop` branch; base is main 1665a1c.)
6. PASS. No diff to `backend/config/pipeline_scheduler.yaml`; no other config touched.
7. PASS, with the exclusions stated. Marker `/tmp/qa_dcw2/marker` taken before restore. `find news_server/data -newer marker -type f` excluding `workspace/*/book/*` and `scheduler/*` lists only `1/pipeline_state/exchange_feed_next_poll.json`, `1/daily_announcements/announcements_2026-10-16.json`, `nse_announcements_2026-10-16.json`; none under either company's stance dirs. Independent proof these are the live server's: scheduler log `scheduler/logs/exchange_feed/2026-10-17_03-09-07_*.log` shows `exchange_feed_runner --once` fetching 2026-10-16 and writing exactly those files at 03:09:10-17 (scheduler jobs run in the uvicorn API process pid 72592, cwd main checkout, started Oct 16 03:32). All paths in my run log are `/private/tmp/qa_dcw2/...`; zero references to the live root. The `snapshots.jsonl` (scienceamit1/book/default) is written by `portfolio_service.py:304 upsert_snapshot` in that API process: with no dagster/stance/workflow/intake process alive (`ps` empty) its mtime kept changing (03:20:12, 03:20:58, 03:21:30).
8. PASS. `stores/tests/test_boundaries.py`: 2 passed. Imports of chain modules stages, report, names, settings, verdict_source, verdicts, case_root in production Python: ok (definitions and query run in the venv). `backend/orchestration/chain/tests`: 20 passed in production Python (no Dagster). `dagster_tests` with venv site-packages: 4 passed. Full suite (dev skill command) base 1665a1c vs head 6a80302 in separate sandbox roots: both 95 failed + 8 errors (103 ids); head has 1676 passed vs 1656 (the 20 new tests). `comm -23 new base`: empty.

### Findings (confirmed by the verifier)
- ALERT, `backend/orchestration/chain/definitions.py:57-58` (`refuse`): the log tail attached to a company's refusal is the last 15 lines of the whole batched stage log. In the pilot ARSSBL's block shows mostly 20MICRONS lines and one ARSSBL line; with more companies the reason may fall outside the tail. Reproduce: `/tmp/qa_dcw2` query output, lines under ARSSBL quarterly. The reason itself is also in the `[reason]` bracket from the verdict, so the check is not at risk.
- (Verifier refuted: reason truncation at 300 chars, and "quarterly materialized while check failed", which is the documented design.)

### Dev claims not confirmed
- Handoff says 61 failures each in the suite; I measure 95 + 8 errors each in my roots (same ids base vs head, so no effect). Dev used as_of 2026-08-14 and its links were new later dates; mine used 2026-10-13 with a different rewind.
- Check 7 dev caveat (snapshots writer) is now proven independently as above.

### Risks
- Wrong-but-green: Dagster run status is SUCCESS even with ARSSBL blocked; only the query's exit code and SUMMARY tell the truth. Anything that watches run status alone will read green. Proposed check: an alert/sensor that runs the query's summary rule (cut-over task).
- Stance exit 0 without a new link for a passed company is not detected by the wrapper.
- `case_root --universe-add` edits the tracked `data/metadata/price_watchlist.csv` in the sandbox worktree (mine shows modified; not committed).
