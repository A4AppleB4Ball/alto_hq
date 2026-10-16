---
schema: task/v1
id: T-20261016-2146-paper-broker
title: "PaperBroker: a local broker for sandboxes, refused in the live checkout"
status: awaiting_owner
created: 2026-10-16T21:46+05:30
created_by: owner
kind: internal
related: [E-20261015-1140-validation, T-20261015-0321-checkout-data-root]
waiting_on: "Approve acceptance.md"
branch: eng/T-20261016-2146-paper-broker
---

## Goal

`backend/executor/paper/` holds `PaperBroker` with the methods the EMS, reconciler and book sync call on `DhanClient` (place_order, order_status, order_by_correlation_id, cancel_order, quote, tick_size, lot_size, holdings, positions, funds, fills, open_buy_orders). It fills against stored prices per the owner's fill model and keeps its holdings, funds and fills under the sandbox data root. The broker factory (`execution/service.py:43`) accepts `"paper"` only when the checkout is `mode: sandbox`. Design: `org/epics/2026/E-20261015-1140-validation.release-runner.md`.

## Why

The release runner and the shadow lane must run TradingManager, approval, EMS and reconciler end to end without Dhan.

## Out of scope

The release runner, the clock driver, liquidity modelling, the shadow lane.
