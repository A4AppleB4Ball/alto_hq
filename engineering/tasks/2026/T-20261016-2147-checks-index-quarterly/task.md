---
schema: task/v1
id: T-20261016-2147-checks-index-quarterly
title: "Stage checks: index entries carry their dates and period; stored quarterly versions are valid"
status: awaiting_owner
created: 2026-10-16T21:47+05:30
created_by: owner
kind: internal
related: [E-20261015-1140-validation, T-20261016-1718-completeness-check]
waiting_on: "Approve acceptance.md"
branch: eng/T-20261016-2147-checks-index-quarterly
---

## Goal

Two checks in `backend/validation/`, each its own feature folder following the completeness pattern (policy module with CHECK_ID/CHECK_VERSION, a read step building an inputs record, a pure evaluate returning `verdicts.record.Verdict` with a fingerprint):

- `index_dates`: every document index entry of a company has `reporting_period` and its knowable date (`publish_date` with its source for quarterly documents, `filed_at` for annual reports, per `backend/docs/40_data_contracts.md:42-56`); fails naming each entry and the missing field.
- `quarterly_versions`: wraps `lib/quarter_versions.validate_versions` (no re-derivation); fails naming each stored analysis and its reason (NO_SUCH_VERSION, NOT_IN_CHAIN, STALE_DOCS, STALE_BASE), and each enumerated version with no stored analysis.

Validation epic story 6.

## Why

Release scenarios (FC01, FC03, FC04) expect these verdicts; no check scans for them today.

## Out of scope

Wiring into e2e, Dagster or the proposal; repairing data.
