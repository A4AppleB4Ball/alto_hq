---
schema: task/v1
id: T-20261016-2311-case-checks-via-sandbox
title: "Stage checks on frozen cases read through DataAccess in a sandbox checkout; remove validation/cases/access.py path building"
status: ready
created: 2026-10-16T23:11+05:30
created_by: owner
kind: internal
related: [T-20261016-2147-checks-index-quarterly, T-20261015-0321-checkout-data-root]
approvals:
  - file: acceptance.md
    sha256: ab1b86b4a14fff96db01ffab4f35699952cacbdb8511b32b895e66075510b8a2
    by: owner
    at: 2026-10-16T23:43+05:30
---

## Goal

Case mode for `index_dates`, `quarterly_versions` and `intake_failures` copies the case (including its own `legacy_chain_starts.json`) into a sandbox data root and runs the checks there through DataAccess and the intake store readers. `backend/validation/cases/access.py` path building is removed. The case freezer freezes `legacy_chain_starts.json` into each case.

## Why

QA of T-20261016-2147-checks-index-quarterly: F1 case mode reads the live legacy_chain_starts.json; F3 access.py builds the intake path itself, against the one-resolution-path rule. checkout-data-root (9013baa) now allows it.
