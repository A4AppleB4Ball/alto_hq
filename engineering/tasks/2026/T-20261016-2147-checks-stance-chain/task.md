---
schema: task/v1
id: T-20261016-2147-checks-stance-chain
title: "Stage checks: stance chain is continuous; no link used an input dated after its as-of"
status: ready
created: 2026-10-16T21:47+05:30
created_by: owner
kind: internal
related: [E-20261015-1140-validation]
approvals:
  - file: acceptance.md
    sha256: e93c7e448e0e6399feebf9c552d9f118232a7477eb080c18f3a57d450ed98f37
    by: owner
    at: 2026-10-16T21:51+05:30
branch: eng/T-20261016-2147-checks-stance-chain
---

## Goal

Two checks in `backend/validation/`, same pattern as completeness:

- `stance_chain`: over a company's `log.jsonl`, each non-cold-start link's `chain.covers_from` is the prior `as_of` + 1 day and `covers_to` equals its `as_of`. Reuses the rule in `stance/reconcile.py:145-164` by moving it to one importable function both use (no copy).
- `stance_inputs_asof`: for each link, the recorded `quarterly_analysis_key`, `annual_report_docid` and `trigger_docids` resolve in the index to dates on or before the link's `as_of`; fails naming the link, the input and both dates.

Validation epic story 6.

## Why

Release scenarios FC06, FC07 and FC08 expect these verdicts. The as-of rule is enforced at read time by the AsOfLedger but never checked afterwards.

## Out of scope

Recording input dates in new stance links; repair.
