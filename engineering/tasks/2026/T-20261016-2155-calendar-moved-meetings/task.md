---
schema: task/v1
id: T-20261016-2155-calendar-moved-meetings
title: "Calendar store: a moved or postponed meeting resolves to one next date or none"
status: draft
created: 2026-10-16T21:55+05:30
created_by: claude-main
kind: internal
spawned_from: T-20261016-1718-results-calendar-to-stance
related: [T-20261016-1718-results-calendar-to-stance, E-20261016-1756-stance-inputs, T-20261016-1718-completeness-check]
---

## Goal

Spike follow-up 3. The store is add-only, so a meeting that moved leaves its old date on record next to the new one. Record superseded meetings (absent from a later listing and no result filed) and give one deterministic rule for "the next meeting" per company.

## Why

On 2026-10-16 the store holds 1149 meetings and 8 exchange codes with two or more meetings (e.g. BSE 542727: 2026-10-15 and 2026-10-23, BSE 523862: 10-08 and 10-10). Six BSE meetings dated 10-01..10-14 have no result filing. "Which is the next result" is ambiguous for these, and `due.results_meeting_held` counts a stale past date as held.

## Out of scope

Prompt wiring (follow-up 5); the as-of query (follow-up 4).
