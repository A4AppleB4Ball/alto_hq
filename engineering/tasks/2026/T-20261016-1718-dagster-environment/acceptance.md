# Acceptance: dagster-environment (approved)

Some steps need the owner's Mac (sleep, reboot); QA lists them as owner
steps and records the owner's confirmation.

1. **Isolated.** Dagster is in its own virtualenv outside the repo's
   production environment; production `pip freeze` identical before/after.
2. **Declared, not hand-run.** Launchd agent files for the daemon and the
   webserver (bound to 127.0.0.1) are in the repo with the install command
   documented; `DAGSTER_HOME` is outside the repo and the data root.
3. **Stays up.** After install, `kill -9` of the daemon process restarts it
   within a minute (launchd KeepAlive); the webserver answers a GraphQL query
   from a Python script (no curl).
4. **Sleep.** A schedule with a tick during a Mac sleep: after wake the
   latest missed tick runs and the skipped ticks are logged (owner step:
   sleep the Mac over a tick; QA reads the stored tick records).
5. **Reboot.** After a reboot both agents are running (owner step).
6. **Retention.** A documented command or schedule prunes runs/logs to a
   stated age; QA runs it on a copy and shows the size before/after.
7. **Read-only on product data** until a chain asset is wrapped: no file
   under the data root written by these processes.
