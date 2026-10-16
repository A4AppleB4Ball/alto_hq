# Handoff: cockpit-dagster-link
Branch eng/T-20261017-0130-cockpit-dagster-link, base 9a97ee1. Worktree .claude/worktrees/cockpit-dagster-link (sandbox .alto_checkout.yaml, untracked).
Commits: (1) chain-state endpoint + backend tests, (2) docs for launching UI, (3) frontend button + card + vitest setup. `git log 9a97ee1..HEAD`.

## Acceptance
1. UI launch: `/tmp/cdl/web.py` (not committed) ran `alto_dagster/venv/bin/dagster-webserver -m backend.orchestration.chain.definitions -p 3987` with a temp DAGSTER_HOME and ALTO_CHAIN_COMPANIES=ARSSBL,20MICRONS; Python requests: `GET /` -> 200; GraphQL assetNodes -> intake, producers, quarterly, stance, partitions [ARSSBL, 20MICRONS]. Command is in backend/orchestration/docs/dagster_chain.md ("The Dagster UI and the cockpit"). Note: the asset names were checked through GraphQL, since the HTML page is a JS app.
2. URL setting: ALTO_DAGSTER_URL, returned by the endpoint as dagster_url. Component tests (shared/chain/tests/dagsterLink.test.tsx, pipelinePage.test.tsx): unset -> no button on Queue and Pipeline; set -> href, target=_blank, rel="noopener noreferrer". Queue test asserts the button sits in the header block with the title.
3. Endpoint: backend/api/services/chain_state/tests/test_chain_state.py (11 pass): blocked company reported failing under run status SUCCESS; AST test + subprocess test that no dagster module is loaded. dagster_tests/test_chain_run.py::test_the_cockpit_reader_agrees_with_the_query_on_a_real_run (real Dagster run, 1 pass) shows the sqlite reader and query.py agree on each company's failure text.
4. Card: pages/pipeline/components/chainRunCard.test.tsx; "No chain run stored." with no numbers.
5. Queue: only the header button added; the vitest Queue test checks funnel counts still render. No prior frontend tests existed.
6. vitest 8 pass; `tsc -b` clean; eslint on touched files: only a pre-existing error in PipelineCard.tsx:22. Boundary test + chain tests 22 pass; entry points import. Full backend suite (separate sandbox roots /tmp/cdl/root_head, root_base, each with data/alto_data): new 95 failed/1746 passed/8 errors; base 95 failed/1735 passed/8 errors; `comm -23 new base` empty.

## Behaviour the owner must know
- The endpoint reads Dagster's sqlite files (history/runs.db, history/runs/<id>.db) directly: Dagster's internal layout, pinned to 1.13.x; unexpected shapes raise. Chosen because Dagster cannot be imported in the API.
- Dagster runs on the Mac, the cockpit server is thin: on the server, DAGSTER_HOME is unset and the card says "not configured". Set DAGSTER_HOME (and ALTO_DAGSTER_URL) in the API process on the Mac to populate it. The URL is localhost-based, so the button works only from the Mac's browser.
- Categories: blocked = verdict not ok; failed = verdict errored / asset missing with ok verdict / no verdict. Card lists both with reasons.
- Added devDependencies vitest, jsdom, @testing-library/react (+ lockfile) and a `test` script; vite.config.ts now imports defineConfig from vitest/config.

## Not done / found
- No Playwright/browser check of the live pages (no data to serve in sandbox).
- Found: frontend/src/features/alto-cockpit/pages/pipeline/components/PipelineCard.tsx:22 fails eslint react-refresh rule (pre-existing). Untracked backend/data/dashboard/ appears in main and worktree (pre-existing).
