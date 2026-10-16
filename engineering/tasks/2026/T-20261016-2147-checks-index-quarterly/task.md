---
schema: task/v1
id: T-20261016-2147-checks-index-quarterly
title: "Stage checks: index entries carry their dates and period; quarterly versions are valid; intake failures are reported"
status: awaiting_owner
waiting_on: "review evidence.md and approve the merge"
lease_until: 2026-10-17T22:00+05:30
created: 2026-10-16T21:47+05:30
created_by: owner
kind: internal
related: [E-20261015-1140-validation, T-20261016-1718-completeness-check]
approvals:
  - file: acceptance.md
    sha256: 5e96a7ee1885f7d74bb14b0077004d946d790b8b106d955ea21de299505f8121
    by: owner
    at: 2026-10-16T21:51+05:30
branch: eng/T-20261016-2147-checks-index-quarterly
friction: "frozen cases copy files not folders, so an empty failed/ is absent in a case; handled in validation/cases/access.py via the manifest store status"
---

## Goal

Three checks in `backend/validation/`, each its own feature folder following the completeness pattern (policy module with CHECK_ID/CHECK_VERSION, a read step building an inputs record, a pure evaluate returning `verdicts.record.Verdict` with a fingerprint):

- `index_dates`: every document index entry the company's chain uses (from its chain start, `lib/chain_start`) has `reporting_period` and its knowable date (`publish_date` with its source for quarterly documents, `filed_at` for annual reports, per `backend/docs/40_data_contracts.md:42-56`); fails naming each entry and the missing field.
- `quarterly_versions`: wraps `lib/quarter_versions.validate_versions` (no re-derivation); fails naming each stored analysis and its reason (NO_SUCH_VERSION, NOT_IN_CHAIN, STALE_DOCS, STALE_BASE), and each enumerated version with no stored analysis.

- `intake_failures`: every item in the company's intake `failed/` folder is a failure naming its document, stage and error (FC03: a reporting period the LLM could not determine fails here, because such a document never reaches the index).

Validation epic story 6.

## Why

Release scenarios (FC01, FC03, FC04) expect these verdicts; no check scans for them today.

## Out of scope

Wiring into e2e, Dagster or the proposal; repairing data.
