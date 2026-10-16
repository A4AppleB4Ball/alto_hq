---
schema: task/v1
id: T-20261016-2155-calendar-sme-gap
title: "Count the SME results meetings NSE lists that the calendar store misses"
status: draft
created: 2026-10-16T21:55+05:30
created_by: claude-main
kind: internal
spawned_from: T-20261016-1718-results-calendar-to-stance
related: [T-20261016-1718-results-calendar-to-stance, E-20261016-1756-stance-inputs]
---

## Goal

Spike follow-up 2. One read-only NSE `index=sme` event-calendar pull, compared with the stored meetings, to count the stance companies whose results meeting NSE lists but the store does not (the "SME generic purposes" gap in `backend/raw/docs/results_calendar.md`).

## Why

The store drops a row whose purpose does not contain `Financial Results` and records no index or purpose, so the gap cannot be counted from the store. Proxy today: 2 of 68 SME-like stance companies have a meeting on record, 3% against 15-17% for main board.

## Out of scope

Changing capture (a fix, if the gap is real, is a separate task).
