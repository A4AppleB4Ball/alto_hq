---
schema: task/v1
id: T-20261016-2155-exchange-dedup-by-type
title: "De-duplicate BSE/NSE filings against Screener and StockEdge copies once types are identified"
status: draft
created: 2026-10-16T21:55+05:30
created_by: claude-main
kind: decision
spawned_from: E-20261016-1756-stance-inputs
related: [E-20261016-1756-stance-inputs, T-20261016-2155-document-intelligence-slm]
---

## Goal

Epic story 5. When the same document arrives from an exchange (cut at 15 pages) and from Screener, StockEdge or Stockscans, keep one: the complete one, with the exchange's filing date as its knowable date. Identity comes from identified type and period (story 4), not from filename or month labels.

## Why

Measured 2026-10-16: 299 BSE/NSE documents are in the index (228 concall_ppt, 71 concall_transcript) and all 299 have a same-type, same-period copy from another source in the same company index. Owner rule: duplicates from the 15-page filter are fine for now, so this waits for story 4 and ranks below correctness work.

## Out of scope

Changing the filing-date policy (`backend/raw/docs/filing_policy.md`); deleting blobs without a repair command.
