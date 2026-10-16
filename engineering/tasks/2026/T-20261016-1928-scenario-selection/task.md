---
schema: task/v1
id: T-20261016-1928-scenario-selection
title: "Per-class stored-state queries that propose the release-set companies, recorded as a cohort"
status: in_progress
claimed_by: dev-scenario-selection-1
lease_until: 2026-10-17T20:00+05:30
created: 2026-10-16T19:28+05:30
created_by: owner
kind: internal
related: [E-20261015-1140-validation, T-20261016-1718-completeness-check]
approvals:
  - file: acceptance.md
    sha256: ff3137bec0a1baefe2973b78cc6f15958d74a32d66260660dd6c0799067615ed
    by: owner
    at: 2026-10-16T19:40+05:30
branch: eng/T-20261016-1928-scenario-selection
---

## Goal

`python -m backend.validation.scenarios.selection --as-of 2026-10-15` runs one read-only query per failure class over production stored state (index, quarter versions via the completeness function, intake failures, stance log, prices) and writes candidates with the evidence for each. The owner's pick becomes cohort `research/cohorts/C-…-release-scenarios`. Design: `org/epics/2026/E-20261015-1140-validation.scenario-catalog.md` (story 12).

## Why

Companies must be picked by evidence of the failure class, never by trading outcome, and the pick must be reproducible.

## Out of scope

Freezing the cases, edit-only classes' edit targets (chosen when writing scenarios), FC12 (its investigation task).
