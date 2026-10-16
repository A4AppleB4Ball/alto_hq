---
schema: task/v1
id: T-20261016-1718-completeness-check
title: "Completeness check: backend/validation/verdicts and completeness, from the approved definition"
status: awaiting_owner
waiting_on: "review evidence.md and approve the merge"
created: 2026-10-16T17:18+05:30
created_by: owner
kind: internal
spawned_from: T-20261015-1058-dagster-spike
related: [T-20261015-1058-dagster-spike, E-20261015-1140-validation, D-20261016-1718-completeness-definition]
approvals:
  - file: acceptance.md
    sha256: 61464ed90664af481852e84b89d31e5f6340629b2cefec9f8d7176153288750c
    by: owner
    at: 2026-10-16T18:10+05:30
  - file: evidence.md
    sha256: 36435bbd3108801abf480873b9c0351405f72a6edf4542bd0ab9ce177d601e3a
    by: owner
    at: 2026-10-16T18:40+05:30
claimed_by: claude-main-20261016-1900
lease_until: 2026-10-17T19:00+05:30
branch: eng/T-20261016-1718-completeness-check
friction: acceptance 7 as written (`python -I -c "import backend..."`) cannot run in any environment: -I drops cwd and PYTHONPATH and backend is not installed; ran with sys.path.insert under -I instead.
---

## Goal

Build `backend/validation/verdicts/` (verdict record: state, reason, input fingerprint, check id and version, staleness test) and `backend/validation/completeness/` (company and quarter states, readers over the stores and the results calendar store) as one function every consumer imports. Move the design page into `backend/validation/docs/`. The spike's `observers.py` fingerprint and `verdict_is_current` are the starting point. No Dagster.

## Why

I-20261015-1058-stances-without-quarterly-analysis: a stance with no quarterly analysis reached a proposal and nothing said so. The definition is approved in D-20261016-1718-completeness-definition.

## Out of scope

Dagster, the proposal gate, e2e wiring, the results calendar feeding the stance agents, and the `lib/` regrouping. Not a new capture of the calendar.
