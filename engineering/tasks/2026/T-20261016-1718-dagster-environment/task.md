---
schema: task/v1
id: T-20261016-1718-dagster-environment
title: "Dagster in its own environment with launchd daemon and webserver"
status: needs_owner
created: 2026-10-16T17:18+05:30
created_by: owner
kind: internal
spawned_from: T-20261015-1058-dagster-spike
related: [T-20261015-1058-dagster-spike, E-20261015-1140-orchestration-and-ops]
approvals:
  - file: acceptance.md
    sha256: 3936b74360cb01eb8387c220641d972b84f014199d5c5a0e5b2284a74bd5bac9
    by: owner
    at: 2026-10-16T18:55+05:30
lease_until: 2026-10-17T19:00+05:30
waiting_on: "owner steps in handoff.md: install.sh, kill -9 check, sleep check, reboot check, live data-mtime check"
branch: eng/T-20261016-1718-dagster-environment
---

## Goal

Dagster installed outside the production Python environment, daemon and webserver under launchd, `DAGSTER_HOME` placed, retention for runs.

## Why

The spike (T-20261015-1058-dagster-spike) found Dagster works over the stores. The Mac-sleep behaviour was explained from source, not demonstrated.

## Out of scope

Wrapping the chain; any change to the server.
