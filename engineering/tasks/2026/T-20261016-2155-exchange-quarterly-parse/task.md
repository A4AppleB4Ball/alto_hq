---
schema: task/v1
id: T-20261016-2155-exchange-quarterly-parse
title: "Parse the quarterly results the exchanges publish instead of relying on Screener"
status: draft
created: 2026-10-16T21:55+05:30
created_by: claude-main
kind: decision
spawned_from: E-20261016-1756-stance-inputs
related: [E-20261016-1756-stance-inputs, T-20261016-2155-document-intelligence-slm, T-20261016-2147-checks-index-quarterly]
---

## Goal

Epic story 6. A spike first: what BSE and NSE actually publish per quarter (XBRL or PDF results filings), whether it can be parsed to the same fields `backend/lib/financials` reads from Screener, and how many companies it covers on the filing date. Then, only on the spike's findings, the parser.

## Why

Screener's quarterly periods feed `ttm_eps` in the P/E snapshot and the financials; they are dated by our own publish_date rule, after the fact. Exchange filings carry the filing date on the day. Change kind decision (new input source); the spike itself is read-only. Per the memory rule, a spike before a task list.

## Out of scope

Replacing Screener before parity is shown; the P/E decision (owner question in stance-input-keys-only).
