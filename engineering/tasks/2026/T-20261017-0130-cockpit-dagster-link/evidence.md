---
schema: evidence/v1
task: T-20261017-0130-cockpit-dagster-link
round: 1
qa: fail
qa_by: qa@sonnet-5.5
commits: 9a97ee1..2abb419
acceptance_sha256: 1755eedba85e1a4822c245c5f09e5de39b8687e4b563f7c7ef83e97e9ab8fc61
outputs_changed: unverified
---

## Round 1

### Acceptance check results
1. Dagster UI launches: PASS. `ALTO_CHAIN_COMPANIES=ARSSBL,20MICRONS ALTO_PRODUCT_PYTHON=python3 DAGSTER_HOME=<temp> alto_dagster/venv/bin/dagster-webserver -m backend.orchestration.chain.definitions -p 3917`; Python requests: `GET /` 200; GraphQL assetNodes = intake, producers, quarterly, stance, each with partitions ARSSBL, 20MICRONS. Command is in backend/orchestration/docs/dagster_chain.md.
2. Configured URL: PASS. Component tests pass (npm test 8/8). Also real Chrome (playwright, Google Chrome) against Vite dev servers on a stub app mounting the real cockpit router (ENV=local, sandbox data root, no loops): URL set gives one `Open Dagster` link on Queue (top right) and Pipeline with href=URL, target=_blank, rel="noopener noreferrer"; unset gives no link on either.
3. Endpoint: PASS on a real Dagster-written run (own harness: the repo fake product, real `dagster asset materialize`, BAD blocked, GOOD ok, run SUCCESS) gives complete 1 / blocked 1 / failed 0 with state/reason; no `dagster` in sys.modules; chain_state package tests + boundary test pass (13 passed). Opens with `mode=ro`, no write statements. BUT see F1/F2 (the "last run" is wrong in real setups).
4. Pipeline card: PASS in browser (screenshot: counts 1/1/0, "BAD blocked: completeness incomplete: Q1_FY27 missing; ..."). No run: component test only (not browsed).
5. Queue unchanged: PASS (funnel 7/3/2/1 and tables render as before in browser; existing tests pass).
6. Repo checks: PASS with the F1 caveat. tsc -b clean; npm ci succeeded (lockfile consistent); build ok; vitest ok; backend suite below; boundary test pass; entry points backend.api.local and backend.api.main_cockpit import.

### Findings
F1 BLOCK (wrong-but-green). backend/api/services/chain_state/dagster_store.py:43-47 `last_run` takes the newest row of `runs` with no filter on job. The permanent Dagster home (docs/dagster_environment.md) runs a heartbeat job every 5 minutes. Reproduced: real chain run, then `dagster job execute ... -j heartbeat_job` in the same home: endpoint returns status `ok`, run = the heartbeat run, counts 0/0/0, companies []; the Pipeline card shows "0 complete 0 blocked 0 failed" under "run SUCCESS" (screenshot /tmp/qa_app/x/hb_pipeline.png) while a company is blocked. Acceptance 3 and 4 ("no placeholder numbers", last chain run) fail in the intended deployment. Verifier confirmed. Catch: select the last run of the chain job (job name / asset selection) and raise when a run has no planned events; test with a heartbeat row after the chain run.
F2 ALERT. dagster_store.py:40-41 `connect_read_only`: `mode=ro` on Dagster's WAL-mode dbs raises `OperationalError: unable to open database file` when the -wal/-shm sidecars are absent (copy of only the .db files, read-only mount, cleanup). Reproduced; the endpoint 500s and both pages show "Dagster link: Failed to fetch"/"chain state: Failed to fetch". Dagster 1.13.26 on macOS leaves sidecars after exit (verifier), so normal operation works; with Dagster running, WAL readers are not blocked. Also coupling: a store read failure removes the Queue Dagster button, though the URL comes from env alone (DagsterLink.tsx:6). Locked-DB behaviour in rollback mode was not applicable (all Dagster dbs are WAL).
F3 ALERT (not reproduced as a loss, process). frontend/dist is tracked and was not rebuilt, so a server serving dist shows no button until rebuild; `npm run build` rewrites the tracked dist. Bundle: base 6,653,142 B vs head 6,655,892 B (+2.7 kB); test deps not in the bundle.
F4 note: the new dagster-venv test (test_the_cockpit_reader_agrees_with_the_query_on_a_real_run) cannot be run as the conftest says: the alto_dagster venv has no pytest. I ran an equivalent by hand (above). Running it needs pytest installed in that venv (owner decision).

### Ask 3 (PipelineCard.tsx:22 eslint)
Not introduced and the file is not new in the range: `git diff 9a97ee1..2abb419 -- PipelineCard.tsx` is empty; `git blame` line 22 (`export function ageDays`) is 54bf815c, 2026-08-05. Rating: pre-existing, no action. Lint of the changed files is clean (the 5 errors under alto-cockpit are in untouched Watchlist/PipelineCard files).

### Ask 4 (Dagster sqlite from the API)
Wrong home: reads only `$DAGSTER_HOME`; unset reports not_configured honestly; but nothing checks the home is the chain's (F1). Read-only: yes, `file:...?mode=ro`, no writes found. Locked/running Dagster: all Dagster dbs are WAL; reads of Dagster's own live files worked; a write-lock test was not conclusive (see F2), so behaviour against an active writer is not independently proven. Unexpected shapes: metadata kinds other than Text/Int raise ValueError (500), missing run db raises FileNotFoundError; none are swallowed.

### Suite
Separate sandbox roots (/tmp/qa_data_head, /tmp/qa_data_base, data/alto_data created). Head: 95 failed, 1746 passed, 8 errors. Base: 95 failed, 1735 passed, 8 errors. `comm -23 head base` = empty. Boundary test pass. Entry points import. The dagster_tests are not collected under production Python (by design).

### Dev claims not confirmed
After reading handoff.md: every command and count in it reproduced (suite 95/1746/8 vs 95/1735/8, vitest 8, asset names, PipelineCard.tsx:22 pre-existing; handoff itself says the file is pre-existing). Not stated by dev and found by QA: F1 (heartbeat run hides the chain run), F2, F3. The dev did no browser check; QA did.

### Risks
Server deploy: ALTO_DAGSTER_URL pointing at 127.0.0.1 on the thin server would link to the viewer's own machine; DAGSTER_HOME unset there gives not_configured.
Invariant that would catch F1: a test that stores a non-chain run after a chain run and asserts the chain run (or an error) is returned.
