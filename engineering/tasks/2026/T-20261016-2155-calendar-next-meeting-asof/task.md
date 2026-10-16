---
schema: task/v1
id: T-20261016-2155-calendar-next-meeting-asof
title: "AsOfLedger.next_results_meeting(symbol, as_of) with a typed unknown reason"
status: draft
created: 2026-10-16T21:55+05:30
created_by: claude-main
kind: internal
spawned_from: T-20261016-1718-results-calendar-to-stance
related: [T-20261016-1718-results-calendar-to-stance, E-20261016-1756-stance-inputs, T-20261016-2155-calendar-moved-meetings]
---

## Goal

Spike follow-up 4. One method on the `AsOfLedger` (`backend/lib/asof.py`, beside `latest_annual_analysis`) returning the earliest meeting captured at or before `as_of` whose date is after `as_of`, as a typed result: a date with days away, or an unknown with a reason (calendar not captured for that as_of, none on record, held). Reads the store as it is, never through `reader.load_meetings` (that can call the network inside a stance run).

## Why

Point-in-time safety: the calendar did not exist before 2026-10-07, so any earlier as_of must answer "calendar not captured", not an invented date and not a silent skip, like `PESnapshot` does for P/E.

## Out of scope

Putting the field in prompts (next task); changing capture.
