---
schema: task/v1
id: T-20261016-2235-checks-stance-inputs-asof
title: "Stage check: no stance link used an input dated after its as-of"
status: awaiting_owner
waiting_on: "ship: owner approved the merge 2026-10-17"
friction: "sandbox checkouts lack production-only state (alto_data/system/legacy_chain_starts.json), so 39 validation/stance tests fail there at base until it is copied in; no case-to-sandbox installer existed (added here)"
created: 2026-10-16T22:35+05:30
created_by: owner
kind: internal
related: [E-20261015-1140-validation, T-20261016-2147-checks-stance-chain, T-20261015-0321-checkout-data-root]
approvals:
  - file: acceptance.md
    sha256: 7f537bc157acc293cfe5937fc7006fc5085e82b2f7302cf9f9d3961c42ba7e73
    by: owner
    at: 2026-10-16T23:43+05:30
  - file: evidence.md
    sha256: 17021c1cce5bade3fe1ccaea089a038a86f7963c4b06944263b1283f10981d98
    by: owner
    at: 2026-10-17T13:00+05:30
---

## Goal

`stance_inputs_asof` in `backend/validation/`, same pattern as completeness: for each link, the recorded `quarterly_analysis_key`, `annual_report_docid` and `trigger_docids` resolve, through `lib` DataAccess / the AsOfLedger and the company resolver (both exchanges), to dates on or before the link's `as_of`; fails naming the link, the input and both dates. Case mode runs from a sandbox checkout whose data root holds the case.

Split from T-20261016-2147-checks-stance-chain; design notes in its handoff.md "v2 blocker". Validation epic story 6.

## Why

Release scenarios FC06 and FC07 expect it. The as-of rule is enforced at read time by the AsOfLedger but never checked afterwards.

## Out of scope

Recording input dates in new stance links; repair.
