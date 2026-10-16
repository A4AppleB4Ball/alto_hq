---
schema: task/v1
id: T-20261016-1718-results-calendar-to-stance
title: "Results calendar tells stance agents A, B and D the next result date before it publishes"
status: ready
created: 2026-10-16T17:18+05:30
created_by: owner
kind: internal
spawned_from: T-20261015-1058-dagster-spike
related: [E-20261015-1140-validation, E-20261016-1756-stance-inputs]
approvals:
  - file: acceptance.md
    sha256: 9a9090124cd9e4d8be4afc8a47f3b966417dda24e2fef0b54e562698cb5a05b0
    by: owner
    at: 2026-10-16T18:55+05:30
claimed_by: claude-main-20261016-1900
lease_until: 2026-10-17T19:00+05:30
branch: eng/T-20261016-1718-results-calendar-to-stance
---

## Goal

The stance agents receive 'next result expected on date X' from the results calendar store when a meeting date is published, so they can account for the market anticipating the result. A spike first: which of the stored meeting dates are usable and the two known calendar gaps (BSE-only meetings before 2026-10-07; SME generic purposes).

## Why

Owner request 2026-10-16. Same store as the completeness Expected state.

## Out of scope

Changing how stances are computed beyond adding the input.
