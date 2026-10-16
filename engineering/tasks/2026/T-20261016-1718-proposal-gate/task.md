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
claimed_by: claude-main-20261016-1900
lease_until: 2026-10-17T19:00+05:30
approvals:
  - file: acceptance.md
    sha256: 002c1a097865fc39ffffea8b0526084094ee6953d26919b0040bc55a29ac46d7
    by: owner
    at: 2026-10-16T21:10+05:30
branch: eng/T-20261016-1718-proposal-gate
friction: acceptance 2 assumes only ARSSBL and CHANDAN differ; cash-limited buys and held incomplete names also move
---

## Goal

The proposal uses the completeness function and excludes or flags blocked companies with the reason, instead of filtering on signal age only (`backend/trading/core.py`, `rebalance_service.py`). Acceptance to be written once the completeness check exists.

## Why

Stage 5 of the incident's root cause: `warnings` is hard-coded empty and the buy of ARSSBL reached the proposal.

## Out of scope

Order placement and execution; changing target weights of complete companies. Money path: needs old-vs-new pinned weights.
