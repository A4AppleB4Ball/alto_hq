---
schema: task/v1
id: T-20261016-2126-window-end-from-manifest
title: "Scenario window end comes from the case manifest's freeze date, not a constant"
status: awaiting_owner
created: 2026-10-16T21:26+05:30
created_by: owner
kind: internal
related: [E-20261015-1140-validation, T-20261016-1928-scenario-contract, T-20261016-1928-case-freezer]
waiting_on: "Approve acceptance.md"
branch: eng/T-20261016-2126-window-end-from-manifest
---

## Goal

`backend/validation/scenarios/contract.py` drops `WINDOW_END`. The catalog checks each curated scenario's `window.end` equals its case manifest's freeze as-of, the way `window.start` is already checked. Design: `org/epics/2026/E-20261015-1140-validation.scenario-catalog.md` (window end fixed per case at its freeze date).

## Why

Owner, 2026-10-16: a case's window ends at its freeze date, never today. A constant would need a code change for every newly frozen case.

## Out of scope

Freezing new cases; the random live company's window.
