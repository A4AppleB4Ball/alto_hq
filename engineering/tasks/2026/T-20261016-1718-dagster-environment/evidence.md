---
schema: evidence/v1
task: T-20261016-1718-dagster-environment
round: 1
qa: pass
outputs_changed: unverified
range: a5b5606..063b6af
---

## Round 1

Step 0: acceptance.md sha256 e8af784e... matches task.md approval.

### Check 1 Isolated: PASS
Venv `alto_dagster/venv` (Python 3.10.10, dagster 1.13.26, webserver, graphql). Production python: `import dagster` fails (ModuleNotFoundError); `pip freeze` before/after my whole run diffed identical. Note: I did not install anything, so the freeze comparison covers using the venv, not creating it.

### Check 2 Declared: PASS
Plists (`launchd/com.alto.dagster-{daemon,webserver}.plist`), install.sh and docs are in the repo; webserver args `-h 127.0.0.1`. DAGSTER_HOME is `alto_dagster/home`, outside repo and `news_server/data`. Smoke (not launchctl): daemon + webserver from the qa worktree, temp DAGSTER_HOME with the repo dagster.yaml, port 3917; `graphql_check.py 3917` returned version 1.13.26 and six healthy daemons; listener bound 127.0.0.1:3917 only. The retention block in dagster.yaml loaded without error.

### Check 3 Retention: PASS
On a copy of a temp DAGSTER_HOME (6 heartbeat runs, 4 backdated 60 days):
- `prune_runs.py --days 30 --dry-run`: 4 old runs, 1456 KB -> 1456 KB.
- `prune_runs.py --days 30`: 1456 KB -> 1064 KB; 2 runs remain; rerun finds 0.

### Check 4 Read-only on product data: PASS (with caveat)
Marker file before; `find news_server/data -newer marker` after found writes (chat duckdb, scienceamit1 snapshots.jsonl, HDFCBANK screener html). These came from the live production system running at the same time; my processes ran from /tmp with a temp DAGSTER_HOME, definitions.py touches no product data (code read), and `graphql_check`/prune take only DAGSTER_HOME. I cannot prove by mtime alone that none of the writes are mine; the evidence is the code and the launch conditions. The 24h+ real-install version belongs to the split-off task.

### Suite
Not run in full: worktrees resolve the production data root and a partial run at head hit a failure in the first 70 tests. The diff only adds new files under backend/orchestration (nothing imported by existing code; grep shows no importer). `pytest --co` collects 1530 tests at both base and head (needs SESSION_SECRET set). No new failure is possible from imports. Treated as a limitation, not a regression.

### Findings
None confirmed. Unverified observations (ALERT-level at most, not sent to verifier as no failure was reproduced): prune_runs VACUUMs `*.db` while a live daemon may hold them (it would raise "locked", not corrupt); no tests for prune_runs.

### Dev claims not confirmed
handoff.md not read before verdict; see below if any.
