# Acceptance: dagster-environment (approved, split)

Install, kill, sleep and reboot checks moved to
T-20261016-2000-dagster-install-checks (owner steps after merge), per the
owner's decision of 2026-10-16.

1. **Isolated.** Dagster is in its own virtualenv outside the repo's
   production environment; production `pip freeze` identical before/after.
2. **Declared, not hand-run.** Launchd agent files for the daemon and the
   webserver (bound to 127.0.0.1) are in the repo with the install command
   documented; `DAGSTER_HOME` is outside the repo and the data root.
3. **Retention.** A documented command or schedule prunes runs/logs to a
   stated age; QA runs it on a copy and shows the size before/after.
4. **Read-only on product data** until a chain asset is wrapped: no file
   under the data root written by these processes.
