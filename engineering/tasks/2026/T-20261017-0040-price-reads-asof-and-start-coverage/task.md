---
schema: task/v1
id: T-20261017-0040-price-reads-asof-and-start-coverage
title: "Non-live price reads clamp a non-trading as_of to the last trading day and check that the cache covers the start"
status: awaiting_owner
waiting_on: "review evidence.md and approve the merge"
created: 2026-10-17T00:40+05:30
created_by: claude-main
kind: internal
spawned_from: T-20261017-0010-dhan-prices-read-without-credentials
related: [T-20261017-0010-dhan-prices-read-without-credentials]
approvals:
  - file: acceptance.md
    sha256: 20964c290ed0feffd6229e8f04910725a656e623678cb2173c3dea55bc0e3e67
    by: owner
    at: 2026-10-17T01:10+05:30
  - file: acceptance.md
    sha256: c7880926001da95f832f0938d2084823331d2c912a26744448f7fd2125272814
    by: owner
    at: 2026-10-17T02:10+05:30
---

## Goal

Close the two QA ALERTs of dhan-prices-read-without-credentials in `backend/price_feed/dhan_daily_store.py` (`_read_cache_only`, ~lines 132-141).

## Why

1. A non-live read needs the cache to reach `end` exactly, so a Saturday or holiday `as_of` raises `PriceCacheMissError` although the cache holds every trading day through the last close.
2. A non-live read never checks that the cache begins at or before `start` (live mode's `covers_window` does), so a truncated cache returns a short series silently.

## Out of scope

Refetching in non-live modes; the price ingestion job.
