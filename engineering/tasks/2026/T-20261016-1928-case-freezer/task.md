---
schema: task/v1
id: T-20261016-1928-case-freezer
title: "Freeze one company's sources and stores into alto_testcases as a hash-verified case"
status: awaiting_owner
created: 2026-10-16T19:28+05:30
created_by: owner
kind: internal
related: [E-20261015-1140-validation, T-20261016-1718-completeness-check]
waiting_on: "Approve acceptance.md"
branch: eng/T-20261016-1928-case-freezer
---

## Goal

`python -m backend.validation.cases.freeze SYMBOL --as-of 2026-10-15 --out ../alto_testcases/cases` copies one company's raw sources and product stores into `cases/<SYMBOL>@2026-10-15/` with a `manifest.yaml` (window start and its evidence, alto and news_server commits, sha256 per file). `backend.validation.cases.load` re-verifies every hash and raises on any mismatch. Design: `org/epics/2026/E-20261015-1140-validation.scenario-catalog.md` (story 1).

## Why

Every release scenario starts from a frozen real case. Without exact copies, a release diff cannot tell a code change from a data change.

## Out of scope

Applying edits, running the product on a case, selecting companies.
