---
schema: task/v1
id: T-20261016-2155-stance-input-keys-only
title: "A stance link records its inputs, and every input is an analysis key, never raw quarterly data"
status: draft
created: 2026-10-16T21:55+05:30
created_by: claude-main
kind: internal
spawned_from: E-20261016-1756-stance-inputs
related: [E-20261016-1756-stance-inputs, E-20261015-1140-validation, T-20261016-2147-checks-stance-chain, T-20261016-2130-classification-ledger]
---

## Goal

Epic story 2. Each new stance link carries an `inputs` list naming every source the agents read (quarterly analysis key, annual report docid, announcement docids, macro event, price window, P/E snapshot), and a check in `backend/validation/` (same pattern as completeness) fails any link whose inputs include raw quarterly data (Screener quarterly rows, a quarterly PDF, a financials table) rather than an analysis key.

## Why

Today a link records only `chain.quarterly_analysis_key`, `annual_report_docid` and `trigger_docids`. What else the agents read (bodies, macro, the P/E snapshot's `ttm_eps` built from Screener quarterly periods in `backend/lib/pe_asof.py`) is not in the record, so the rule cannot be checked from stored state. The epic's open question applies: this is a validation check with the rule stated here.

## Out of scope

Backfilling `inputs` on history (old links report "not recorded", not pass); deciding whether the P/E snapshot may stay (owner question).
