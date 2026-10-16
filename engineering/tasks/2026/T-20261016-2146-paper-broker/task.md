---
schema: task/v1
id: T-20261016-2146-paper-broker
title: "PaperBroker: a local broker for sandboxes, refused in the live checkout"
status: needs_owner
waiting_on: "QA round 2 FAIL (B2): the paper approval path raises in RebalanceService._trading_calendar via DhanPriceStore; decide whether to widen scope to the planner inputs or accept check 5 with the planner mocked"
claimed_by:
lease_until: 2026-10-17T23:59+05:30
created: 2026-10-16T21:46+05:30
created_by: owner
kind: internal
related: [E-20261015-1140-validation, T-20261015-0321-checkout-data-root]
approvals:
  - file: acceptance.md
    sha256: 3b391c3c9004c78c0de337009837d167bd4dcc348042619406e48baec59650ef
    by: owner
    at: 2026-10-16T21:51+05:30
branch: eng/T-20261016-2146-paper-broker
friction: acceptance 4 depends on an unmerged branch; its gate test cannot import on main, so the suite needed --continue-on-collection-errors and a second, merged-tree comparison
---

## Goal

`backend/executor/paper/` holds `PaperBroker` with the methods the EMS, reconciler and book sync call on `DhanClient` (place_order, order_status, order_by_correlation_id, cancel_order, quote, tick_size, lot_size, holdings, positions, funds, fills, open_buy_orders). It fills against stored prices per the owner's fill model and keeps its holdings, funds and fills under the sandbox data root. The broker factory (`execution/service.py:43`) accepts `"paper"` only when the checkout is `mode: sandbox`. Design: `org/epics/2026/E-20261015-1140-validation.release-runner.md`.

## Why

The release runner and the shadow lane must run TradingManager, approval, EMS and reconciler end to end without Dhan.

## Out of scope

The release runner, the clock driver, liquidity modelling, the shadow lane.
