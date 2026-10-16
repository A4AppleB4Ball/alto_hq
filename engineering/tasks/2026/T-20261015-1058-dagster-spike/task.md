---
schema: task/v1
id: T-20261015-1058-dagster-spike
title: "Spike: Dagster over the existing CLIs, with a completeness check that blocks ARSSBL's stance"
status: done
created: 2026-10-15T10:58+05:30
created_by: owner
kind: internal
spawned_from: I-20261015-1058-stances-without-quarterly-analysis
related: [D-20261015-1058-dagster-for-compute-chain]
approvals:
  - file: acceptance.md
    sha256: 07865e13d719339bc3912d9393a536b47c3fc59dce2715a0a93085afb3ae4576
    by: owner
    at: 2026-10-15T16:51+05:30
closed: 2026-10-16T17:18+05:30
branch: eng/T-20261015-1058-dagster-spike
---

## Goal

Answer, with evidence on real data, whether Dagster can carry the compute
chain as decided in D-20261015-1058-dagster-for-compute-chain, and what the
follow-up tasks should be. The output is `findings.md` in this folder: an
answer per question in acceptance.md and a proposed next-task list. The
owner creates the follow-up tasks from it.

## Why

I-20261015-1058-stances-without-quarterly-analysis. No follow-up task is
written until this spike says what the real shape is.

## Scope

- Three companies: ARSSBL, CHANDAN (incident) and one company the fleet scan
  shows complete (dev picks it and names it in findings.md).
- Assets wrap the existing code read-only: the document index, quarterly
  analyses and stance chain are observed from their stores; the stance asset
  does not run the product's stance code, it records what it would run.
- One asset check: quarterly completeness per company (every quarter in the
  chain with a results document has a valid analysis).

## Out of scope

- Writing any product store, running any LLM, changing any product code on
  main. Code stays on the branch; whether any of it is kept is a follow-up
  decision.
- The completeness states for "unavailable at source" (designed after the
  spike), the ops agent, the server.
- Adding Dagster to the production Python environment.
