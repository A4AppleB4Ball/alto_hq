---
schema: task/v1
id: T-20261016-1718-dagster-chain-wrap
title: "Producers, intake, quarterly and stance as company-partitioned Dagster assets"
status: in_progress
claimed_by: claude-main-20261016-1900
lease_until: 2026-10-17T19:00+05:30
created: 2026-10-16T17:18+05:30
created_by: owner
kind: internal
spawned_from: T-20261015-1058-dagster-spike
related: [T-20261015-1058-dagster-spike, T-20261016-1718-completeness-check, T-20261016-1718-dagster-environment, E-20261015-1140-orchestration-and-ops]
approvals:
  - file: acceptance.md
    sha256: 1f91064262fdbadbec954475beba86bdc62b7714320f31c37298665379a3faf2
    by: owner
    at: 2026-10-16T18:55+05:30
  - file: acceptance.md
    sha256: c7cbbdb519303c7236ead797dad5dc652f63d50a41461e82552a5335254e1bc2
    by: owner
    at: 2026-10-16T23:05+05:30
branch: eng/T-20261016-1718-dagster-chain-wrap
---

## Goal

Wrap the existing batched CLIs as assets partitioned by company, with the completeness verdicts as per-company check results and the stance asset gating each company.

## Why

Decision D-20261015-1058-dagster-for-compute-chain; spike findings sections 2 and 5.

## Out of scope

Trading and execution (they stay on the server loop). The `pipeline_scheduler.yaml` jobs listed as kept.
