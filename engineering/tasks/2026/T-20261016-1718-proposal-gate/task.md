---
schema: task/v1
id: T-20261016-1718-proposal-gate
title: "Rebalance proposal refuses a stance whose latest quarter has no valid analysis"
status: ready
created: 2026-10-16T17:18+05:30
created_by: owner
kind: internal
spawned_from: T-20261015-1058-dagster-spike
related: [T-20261016-1718-completeness-check, E-20261015-1140-validation]
approvals:
  - file: acceptance.md
    sha256: 96d8d825f250802e302482ae8d623022a548566ae6463770b702b5c0cf1868c8
    by: owner
    at: 2026-10-16T18:55+05:30
branch: eng/T-20261016-1718-proposal-gate
---

## Goal

The proposal uses the completeness function and excludes or flags blocked companies with the reason, instead of filtering on signal age only (`backend/trading/core.py`, `rebalance_service.py`). Acceptance to be written once the completeness check exists.

## Why

Stage 5 of the incident's root cause: `warnings` is hard-coded empty and the buy of ARSSBL reached the proposal.

## Out of scope

Order placement and execution; changing target weights of complete companies. Money path: needs old-vs-new pinned weights.
