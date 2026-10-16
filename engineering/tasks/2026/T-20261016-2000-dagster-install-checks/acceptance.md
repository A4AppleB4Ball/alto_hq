# Acceptance: dagster-install-checks (owner steps, DRAFT, not approved)

After T-20261016-1718-dagster-environment is merged. Run by the owner on the
Mac; QA reads the stored records and records the owner's confirmation.

1. **Install.** `backend/orchestration/dagster_env/install.sh` run from the
   main checkout loads both launchd agents; both have pids.
2. **Stays up.** `kill -9` of the daemon pid: a new pid within a minute; the
   webserver answers `graphql_check.py` from the venv python.
3. **Sleep.** Sleep the Mac across at least two schedule ticks and wake it:
   the latest missed tick runs and the skipped ticks are logged (stored tick
   records).
4. **Reboot.** After a reboot both agents have pids.
5. **Read-only on live data.** The newest mtime under the data root before
   install vs after one day: no file written by these processes.
