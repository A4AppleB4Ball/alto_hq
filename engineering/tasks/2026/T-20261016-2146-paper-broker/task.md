---
schema: task/v1
id: T-20261016-2146-paper-broker
title: "PaperBroker: a local broker for sandboxes, refused in the live checkout"
status: done
claimed_by:
lease_until: 2026-10-17T23:59+05:30
created: 2026-10-16T21:46+05:30
created_by: owner
kind: internal
related: [E-20261015-1140-validation, T-20261015-0321-checkout-data-root]
approvals:
  - file: acceptance.md
    sha256: f9882844a8ee21b95588a0e3ff035e36c9744d8fd3c1b80d43f23e1ae73d0138
    by: owner
    at: 2026-10-16T23:11+05:30
  - file: evidence.md
    sha256: 4dbb8caacbbdd0d0a4146b9faa2d473a9392512d61ebca85676e75758dc3c0c6
    by: owner
    at: 2026-10-16T23:36+05:30
branch: eng/T-20261016-2146-paper-broker
merge_commit: 0d07e40
closed: 2026-10-17
friction: acceptance 4 depends on an unmerged branch; its gate test cannot import on main, so the suite needed --continue-on-collection-errors and a second, merged-tree comparison
---

## Goal

`backend/executor/paper/` holds `PaperBroker` with the methods the EMS, reconciler and book sync call on `DhanClient` (place_order, order_status, order_by_correlation_id, cancel_order, quote, tick_size, lot_size, holdings, positions, funds, fills, open_buy_orders). It fills against stored prices per the owner's fill model and keeps its holdings, funds and fills under the sandbox data root. The broker factory (`execution/service.py:43`) accepts `"paper"` only when the checkout is `mode: sandbox`. Design: `org/epics/2026/E-20261015-1140-validation.release-runner.md`.

## Why

The release runner and the shadow lane must run TradingManager, approval, EMS and reconciler end to end without Dhan.

## Out of scope

The release runner, the clock driver, liquidity modelling, the shadow lane.
