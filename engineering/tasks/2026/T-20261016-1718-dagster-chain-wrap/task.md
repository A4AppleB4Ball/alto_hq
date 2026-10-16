---
schema: task/v1
id: T-20261016-1718-dagster-chain-wrap
title: "Producers, intake, quarterly and stance as company-partitioned Dagster assets"
status: awaiting_owner
created: 2026-10-16T17:18+05:30
created_by: owner
kind: internal
spawned_from: T-20261015-1058-dagster-spike
related: [T-20261015-1058-dagster-spike, T-20261016-1718-completeness-check, T-20261016-1718-dagster-environment]
waiting_on: "Read and approve acceptance.md"
branch: eng/T-20261016-1718-dagster-chain-wrap
---

## Goal

Wrap the existing batched CLIs as assets partitioned by company, with the completeness verdicts as per-company check results and the stance asset gating each company.

## Why

Decision D-20261015-1058-dagster-for-compute-chain; spike findings sections 2 and 5.

## Out of scope

Trading and execution (they stay on the server loop). The `pipeline_scheduler.yaml` jobs listed as kept.
