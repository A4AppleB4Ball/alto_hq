---
schema: task/v1
id: T-20261016-1718-completeness-check
title: "Completeness check: backend/validation/verdicts and completeness, from the approved definition"
status: ready
created: 2026-10-16T17:18+05:30
created_by: owner
kind: internal
spawned_from: T-20261015-1058-dagster-spike
related: [T-20261015-1058-dagster-spike, E-20261015-1140-validation, D-20261016-1718-completeness-definition]
approvals:
  - file: acceptance.md
    sha256: 16c2b27a1ab8868ddee6ac35f70a0a08c46e2f8e0370327d55cfc9a50c456171
    by: owner
    at: 2026-10-16T17:18+05:30
branch: eng/T-20261016-1718-completeness-check
---

## Goal

Build `backend/validation/verdicts/` (verdict record: state, reason, input fingerprint, check id and version, staleness test) and `backend/validation/completeness/` (company and quarter states, readers over the stores and the results calendar store) as one function every consumer imports. Move the design page into `backend/validation/docs/`. The spike's `observers.py` fingerprint and `verdict_is_current` are the starting point. No Dagster.

## Why

I-20261015-1058-stances-without-quarterly-analysis: a stance with no quarterly analysis reached a proposal and nothing said so. The definition is approved in D-20261016-1718-completeness-definition.

## Out of scope

Dagster, the proposal gate, e2e wiring, the results calendar feeding the stance agents, and the `lib/` regrouping. Not a new capture of the calendar.
