# Handoff: T-20261016-1718-dagster-environment
Branch eng/T-20261016-1718-dagster-environment, base a5b5606, commit 063b6af (worktree .claude/worktrees/T-20261016-1718-dagster-environment). Not pushed, not merged. Nothing installed into launchd.

## Acceptance
1. Isolated: venv at /Users/kmrh581/personal/projects/workspace/alto_dagster/venv (freeze in alto_runs/T-20261016-1718-dagster-environment/venv.freeze.txt). Production `pip freeze` before/after (pipfreeze.before/after.txt, 508 lines): diff empty. PASS.
2. Declared: plists in backend/orchestration/dagster_env/launchd/, `plutil -lint` OK for both; webserver args `-h 127.0.0.1 -p 3000`; install command in backend/orchestration/docs/dagster_environment.md (`backend/orchestration/dagster_env/install.sh`, never run). DAGSTER_HOME is alto_dagster/home. PASS by inspection.
   Smoke without launchd: temp DAGSTER_HOME, webserver on 127.0.0.1:3999 answered graphql_check.py (version 1.13.26); lsof showed LISTEN on 127.0.0.1 only.
3. Stays up: NOT RUN (owner).
4. Sleep: NOT RUN (owner).
5. Reboot: NOT RUN (owner).
6. Retention: prune_runs.py --days 30 on a copy of a temp home with 6 runs: dry-run 1460 KB, 0 runs. `--days 0` on the copy: 6 runs deleted, 1460 KB -> 1028 KB. Ticks purge via dagster.yaml retention (30 days), not exercised. PASS on copy.
7. Read-only: the code location touches no product data; not measured on a live machine (see the spike's caveat on attribution).

## Owner steps (exact)
a. After merging to main (plists point at the main checkout): `/Users/kmrh581/personal/projects/workspace/alto/backend/orchestration/dagster_env/install.sh`. (Before merge, run it from the worktree path by editing nothing: the plists reference the main path, so merge first.)
b. Check 3: `launchctl list | grep com.alto.dagster`, `kill -9 <daemon pid>`, within 60 s the list shows a new pid; then `/Users/kmrh581/personal/projects/workspace/alto_dagster/venv/bin/python /Users/kmrh581/personal/projects/workspace/alto/backend/orchestration/dagster_env/graphql_check.py` returns version and daemon health.
c. Check 4: sleep the Mac across at least two */5 ticks, wake; QA reads tick records for heartbeat_schedule (latest missed tick run, skipped ticks logged).
d. Check 5: reboot; `launchctl list | grep com.alto.dagster` shows both with pids.
e. Check 7: compare newest mtime under the data root before install and after a day.

## Not done / notes
Checks 3, 4, 5 and the live part of 7 (owner steps). Daemon health showed unhealthy in the smoke test only because no daemon ran. Untested: the VACUUM in prune_runs.py ran on the copy (size drop includes it). Tick retention not exercised.
