---
schema: task/v1
id: T-20261016-2130-classification-ledger
title: "Log every materiality classification, immaterial ones included, in the stance store"
status: done
closed: 2026-10-17
merge_commit: eb1eee96a89c430938e0d4452c059c287ff976d4
created: 2026-10-16T21:30+05:30
created_by: owner
kind: internal
related: [E-20261016-1756-stance-inputs, E-20261015-1140-validation, T-20261016-1718-completeness-check]
approvals:
  - file: acceptance.md
    sha256: 5e36723fc4d56bb48cb59842ee920577296cca97cb593309ef595d19d7370238
    by: owner
    at: 2026-10-16T23:00+05:30
  - file: acceptance.md
    sha256: 022fb193eb0b36782c7a1618c58e224fa80096e580202419ee4cbfcc8912b986
    by: owner
    at: 2026-10-16T23:40+05:30
  - file: evidence.md
    sha256: 3086f3316a6de7e9df1223c720a52b0feeee23a707c5ea6468aed7296ec0e2b6
    by: owner
    at: 2026-10-17T00:10+05:30
claimed_by: claude-main-20261016-1900
lease_until: 2026-10-17T21:20+05:30
waiting_on: "review evidence.md and approve the merge"
branch: eng/T-20261016-2130-classification-ledger
---

## Goal

When the stance worker's classifier rules an announcement or macro event immaterial, the verdict is stored: item key, as_of, the full signal (type, relevance, quantified, should_run_triad), the classifier config and a timestamp. Proposed home: a sidecar of the company's stance directory, written through the stance store (`backend/stores/stance`, which already owns sidecars) under the per-symbol lock, never by hand.

## Why

Today an immaterial filing returns None from the checkpoint (`backend/stance/worker.py:365` and :288) and leaves nothing durable. A completeness check that asks whether every document was consumed would flag every immaterial document as missing. The invariant is: each document is CONSUMED or CLASSIFIED (`backend/docs/25_future_ideas.md`).

The ledger is also the classifier's cache: a stored verdict for the same item, as_of, classifier config and input fingerprint is reused and the LLM call is skipped.

## Out of scope

The completeness check using the ledger (a follow-up once the ledger exists); backfilling classifications for history; changing what the classifier decides.
