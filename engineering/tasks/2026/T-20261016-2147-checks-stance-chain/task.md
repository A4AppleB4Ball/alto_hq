---
schema: task/v1
id: T-20261016-2147-checks-stance-chain
title: "Stage check: stance chain is continuous"
status: done
closed: 2026-10-16
merge_commit: 4c44dbf
lease_until: 2026-10-17T23:00+05:30
created: 2026-10-16T21:47+05:30
created_by: owner
kind: internal
related: [E-20261015-1140-validation, T-20261016-2235-checks-stance-inputs-asof]
approvals:
  - file: acceptance.md
    sha256: 0a542f142edafb770f3b3f2e1e8e63371973356bd99ea9ad21c257f29c9df4a4
    by: owner
    at: 2026-10-16T22:34+05:30
  - file: evidence.md
    sha256: 490e66f70cad8a9f6cf0bcfd5fd7972158a8a96d50892510de8599bddf5091f9
    by: owner
    at: 2026-10-16T22:51+05:30
branch: eng/T-20261016-2147-checks-stance-chain
---

## Goal

One check in `backend/validation/`, same pattern as completeness (split 2026-10-16: `stance_inputs_asof` is T-20261016-2235-checks-stance-inputs-asof):

- `stance_chain`: over a company's `log.jsonl`, each non-cold-start link's `chain.covers_from` is the prior `as_of` + 1 day and `covers_to` equals its `as_of`. Reuses the rule in `stance/reconcile.py:145-164` by moving it to one importable function both use (no copy).
Validation epic story 6.

## Why

Release scenario FC08 expects this verdict.

## Out of scope

Recording input dates in new stance links; repair.
