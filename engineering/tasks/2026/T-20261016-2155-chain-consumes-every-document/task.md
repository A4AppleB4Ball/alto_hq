---
schema: task/v1
id: T-20261016-2155-chain-consumes-every-document
title: "Every indexed document is consumed by the chain in sequence; a backdated one rebuilds from its date"
status: draft
created: 2026-10-16T21:55+05:30
created_by: claude-main
kind: decision
spawned_from: E-20261016-1756-stance-inputs
related: [E-20261016-1756-stance-inputs, E-20261015-1140-validation, T-20261016-2130-classification-ledger, T-20261016-1718-completeness-check]
---

## Goal

Epic story 3. For each company, every document in `{SYMBOL}_index.json` (announcement, quarterly, annual) is extracted, analysed and consumed (or classified, per the ledger) in `publish_date` order. A document published before the chain's latest link but arriving after it makes the chain redo the analysis and rebuild from that date.

## Why

Measured 2026-10-16: for 100 of 484 stance companies the index holds a quarterly document (concall or quarterly PDF) published on or before the latest link's as_of with a later quarter than the link's `quarterly_analysis_key` (null for most of them). The completeness check says what is missing; nothing makes the chain take the document in. `backend/stance/rewind.py` and `runner_late_inputs` exist and are the starting map. Needs `backend/docs/30_quarter_identity.md` read first.

## Out of scope

Document types the classifier cannot yet identify (story 4); the completeness check itself.
