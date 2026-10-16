---
schema: task/v1
id: T-20261016-2336-daily-price-store-everywhere
title: "Every daily price read goes through the checkout-gated price store"
status: awaiting_owner
waiting_on: "review evidence.md and approve the merge (check 11 holiday half pending on the NSE holiday follow-up task)"
lease_until: 2026-10-18T12:00+05:30
friction: the full-suite baseline must be a sandbox worktree when the head is one (a production-root base differs by ~40 data-root failures); acceptance 2's scope (all of backend) is wider than the Goal's three sites; the mismatch was visible only after a grep
created: 2026-10-16T23:36+05:30
created_by: owner
kind: internal
related: [T-20261016-2146-paper-broker]
approvals:
  - file: acceptance.md
    sha256: 38c4da22fb594140d8ec136e04062d6108e2f92ae84a03b32a27d964561046a5
    by: owner
    at: 2026-10-17T02:05+05:30
---

## Goal

The three remaining direct `DhanPriceStore` builds (price chart service, rebuild_price_refs script, trading harness `_resolve_price`) go through `create_daily_price_store`, so a paper sandbox never reaches Dhan prices and a live checkout is unchanged.

## Why

QA round 3 of T-20261016-2146-paper-broker (observations); a chart route raises in a paper sandbox.

## Out of scope

The price feed and the Dhan CLI/auth route (read-only Dhan builds outside the factory).
