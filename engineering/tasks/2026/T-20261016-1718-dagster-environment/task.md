---
schema: task/v1
id: T-20261016-1718-dagster-environment
title: "Dagster in its own environment with launchd daemon and webserver"
status: awaiting_owner
created: 2026-10-16T17:18+05:30
created_by: owner
kind: internal
spawned_from: T-20261015-1058-dagster-spike
related: [T-20261015-1058-dagster-spike, E-20261015-1140-orchestration-and-ops]
approvals:
  - file: acceptance.md
    sha256: e8af784eca56852c6210d297c8341f07cac3c7c646c2269be1d8479e3a96adc6
    by: owner
    at: 2026-10-16T20:00+05:30
waiting_on: "review evidence.md and approve the merge"
claimed_by: claude-main-20261016-1900
lease_until: 2026-10-17T19:00+05:30
branch: eng/T-20261016-1718-dagster-environment
---

## Goal

Dagster installed outside the production Python environment, daemon and webserver under launchd, `DAGSTER_HOME` placed, retention for runs.

## Why

The spike (T-20261015-1058-dagster-spike) found Dagster works over the stores. The Mac-sleep behaviour was explained from source, not demonstrated.

## Out of scope

Wrapping the chain; any change to the server.
