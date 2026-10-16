---
schema: task/v1
id: T-20261016-1928-case-freezer
title: "Freeze one company's sources and stores into alto_testcases as a hash-verified case"
status: ready
claimed_by:
lease_until: 2026-10-17T20:00+05:30
created: 2026-10-16T19:28+05:30
created_by: owner
kind: internal
related: [E-20261015-1140-validation, T-20261016-1718-completeness-check]
approvals:
  - file: acceptance.md
    sha256: 91b9f0009c780efcdaed2739091ee21f36acfaf55a145680a9071eea65fd90f4
    by: owner
    at: 2026-10-16T23:40+05:30
branch: eng/T-20261016-1928-case-freezer
friction: acceptance 4's literal `find -newer` cannot be empty on a live data root (the API process writes book snapshots and dashboard chat continuously); a check scoped to the freeze's read set, or a quiet window, is needed.
---

## Goal

`python -m backend.validation.cases.freeze SYMBOL --as-of 2026-10-15 --out ../alto_testcases/cases` copies one company's raw sources and product stores into `cases/<SYMBOL>@2026-10-15/` with a `manifest.yaml` (window start and its evidence, alto and news_server commits, sha256 per file). `backend.validation.cases.load` re-verifies every hash and raises on any mismatch. Design: `org/epics/2026/E-20261015-1140-validation.scenario-catalog.md` (story 1).

## Why

Every release scenario starts from a frozen real case. Without exact copies, a release diff cannot tell a code change from a data change.

## Out of scope

Applying edits, running the product on a case, selecting companies.
