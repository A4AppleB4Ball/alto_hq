# Acceptance: cockpit-dagster-link

Starts after dagster-chain-wrap is merged.

1. **Dagster UI launches.** Using the venv at `/Users/kmrh581/personal/projects/workspace/alto_dagster/venv`, `dagster-webserver -m backend.orchestration.chain.definitions` with `DAGSTER_HOME` in a temp dir starts and serves the asset graph on localhost (HTTP status and the asset names shown in a Python request, not curl). The command is written in the chain docs.
2. **Configured URL.** The Dagster URL comes from one setting; with it unset, no button renders (test); with it set, the button on the Queue page (top right) and on the Pipeline page opens it with `target="_blank"` and `rel="noopener noreferrer"` (component tests).
3. **Chain-state endpoint.** A read-only API endpoint returns, for the last run, each company's asset states and completeness verdict (`state`, `reason`), reading Dagster's stored records through a module that does not import Dagster into the API process (boundary test passes). A test with a stored run where one company fails returns it as failing, whatever the run status says.
4. **Pipeline card.** The Pipeline page shows counts (complete, blocked, failed) and lists failing companies with reasons. With no run stored it says so; no placeholder numbers.
5. **Queue page unchanged** apart from the button: the funnel counts and tables behave as before (existing tests pass).
6. **Repo checks.** Frontend tests and type check for the changed files, boundary test, entry-point imports, full backend suite vs base with `comm -23`.
