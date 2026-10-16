---
schema: task/v1
id: T-20261016-2130-classification-ledger
title: "Log every materiality classification, immaterial ones included, in the stance store"
status: awaiting_owner
created: 2026-10-16T21:30+05:30
created_by: owner
kind: internal
related: [E-20261016-1756-stance-inputs, E-20261015-1140-validation, T-20261016-1718-completeness-check]
waiting_on: "Read and approve acceptance.md and the ledger location (sidecar in the stance store)"
branch: eng/T-20261016-2130-classification-ledger
---

## Goal

When the stance worker's classifier rules an announcement or macro event immaterial, the verdict is stored: item key, as_of, the full signal (type, relevance, quantified, should_run_triad), the classifier config and a timestamp. Proposed home: a sidecar of the company's stance directory, written through the stance store (`backend/stores/stance`, which already owns sidecars) under the per-symbol lock, never by hand.

## Why

Today an immaterial filing returns None from the checkpoint (`backend/stance/worker.py:365` and :288) and leaves nothing durable. A completeness check that asks whether every document was consumed would flag every immaterial document as missing. The invariant is: each document is CONSUMED or CLASSIFIED (`backend/docs/25_future_ideas.md`).

## Out of scope

The completeness check using the ledger (a follow-up once the ledger exists); backfilling classifications for history; changing what the classifier decides.
