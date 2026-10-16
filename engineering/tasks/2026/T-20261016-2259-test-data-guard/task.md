---
schema: task/v1
id: T-20261016-2259-test-data-guard
title: "Tests cannot write to the production data root: a test mode, a per-run temp root, and a conftest guard"
status: ready
waiting_on: "dev: add session-failure test for a direct live-root write (check 3b); fix watcher false positive on workspace/*/system/dhan_instruments.json"
created: 2026-10-16T22:59+05:30
created_by: claude-main
kind: internal
related: [T-20261015-0321-checkout-data-root]
depends_on: [T-20261015-0321-checkout-data-root]
approvals:
  - file: acceptance.md
    sha256: 548696372fb90bf55e97871abdd206456477c4c24552181f3d64a957c06735db
    by: owner
    at: 2026-10-16T23:05+05:30
  - file: acceptance.md
    sha256: be3cff5b1589b1c43f5d23ecf3a88da3b62edecf917bbf1c43c2dd63434ed6e7
    by: owner
    at: 2026-10-17T03:00+05:30
---

## Goal

Under pytest, every path in `backend.config.paths` resolves into a fresh per-run temp root, and any test that reaches the live root fails loudly.

## Why

2026-10-16: `stances/ACME/decisions.jsonl` and `trades.jsonl` appeared in production. `RebalanceService._stances_root = STANCES_DIR` (`backend/api/services/rebalance_service.py:90`) plus `write_decision_ledger` (~line 1012) write there from `test_rebalance_price_action_cooldown.py`, which patches only `WORKSPACE_ROOT`. Nothing stops this class.

## Out of scope

Deleting the existing ACME debris (owner's call). A fixed shared `alto_data_unit_tests` folder: a per-run temp root is proposed because it needs no cleanup and parallel runs cannot collide.
