---
schema: task/v1
id: T-20261017-0010-dhan-prices-read-without-credentials
title: "Stance price reads use the cached daily prices with no Dhan credentials, and raise a named error on a miss"
status: awaiting_owner
waiting_on: "review evidence.md and approve the merge"
created: 2026-10-17T00:10+05:30
created_by: claude-main
kind: internal
related: [T-20261016-1718-dagster-chain-wrap, T-20261015-0321-checkout-data-root]
approvals:
  - file: acceptance.md
    sha256: 9ca723ab66cb7fa0e9a595abb0353b1b8c46cf708458f968c7efa11def4f11d8
    by: owner
    at: 2026-10-17T00:12+05:30
---

## Goal

Only price ingestion holds Dhan credentials. Every other reader (stance, backtests, Dagster assets, QA, tests) reads the cached daily prices without credentials; a sandbox never refetches.

## Why

`DhanDailyStore.__init__` (`backend/price_feed/dhan_daily_store.py:85`) builds the Dhan client and instrument mapper before it reads the cache, so stance in a sandbox halts with "DHAN_CLIENT_ID or DHAN_CLIENT_KEY not set" (`backend/executor/credentials.py:161`). The cache path `~/NSE_BSE_Data/dhan_cache/daily` (`dhan_price_store.py:~28`) is not in `backend.config.paths`.

## Out of scope

The executor and broker calls (keep credentials); copying secrets into sandboxes; the price ingestion job itself.
