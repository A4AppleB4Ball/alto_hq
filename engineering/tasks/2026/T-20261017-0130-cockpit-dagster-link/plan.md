# Plan (written alongside the work)
Touches: new backend/api/services/chain_state/ (sqlite3 reader, logic, settings), backend/api/cockpit/chain_state.py + router line,
frontend alto-cockpit shared/chain/, QueuePage header, PipelinePage + ChainRunCard, vitest setup, chain docs. No money path.
Change: read-only GET /api/cockpit/chain-state; ALTO_DAGSTER_URL / DAGSTER_HOME settings; Queue funnel untouched.
Checks: webserver via requests with temp DAGSTER_HOME; pytest chain_state + dagster_tests; vitest + tsc; full suite comm -23 under sandbox roots.
