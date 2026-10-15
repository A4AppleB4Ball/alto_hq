---
schema: decision/v1
id: D-20261015-1058-dagster-for-compute-chain
title: The Mac compute chain moves to Dagster, assets partitioned by company
status: in_force
created: 2026-10-15T10:58+05:30
created_by: owner
decided_by: owner
covers: [I-20261015-1058-stances-without-quarterly-analysis, T-20261015-1058-dagster-spike]
standing: true
---

## Decision

The local compute chain (producers → intake → quarterly → stance) is
orchestrated by Dagster: each store is an asset partitioned by company,
completeness is an asset check that blocks downstream, and the ops agent
reads Dagster's run and check records. Stages still run batched; status is
per company. Trading and execution stay on the server's existing loop.

Adopted only after a spike proves it on two incident companies; no
follow-up tasks before the spike's findings.

## Why

The incident showed per-job exit codes cannot say which company or quarter
is incomplete. Building that ledger, dependency chaining, backfills and run
history on the asyncio scheduler would rebuild an orchestrator by hand.
Prefect and Airflow are task-centric and would still need the ledger.

## Conditions

Revisit if the spike shows partition scale, the daemon on a sleeping Mac, or
the wrapping cost of the existing CLIs is unworkable.
