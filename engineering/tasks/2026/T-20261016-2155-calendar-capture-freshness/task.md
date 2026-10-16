---
schema: task/v1
id: T-20261016-2155-calendar-capture-freshness
title: "A stance run refuses a results calendar captured more than 20 hours ago"
status: draft
created: 2026-10-16T21:55+05:30
created_by: claude-main
kind: internal
spawned_from: T-20261016-1718-results-calendar-to-stance
related: [T-20261016-1718-results-calendar-to-stance, E-20261016-1756-stance-inputs, T-20261016-1718-completeness-check]
---

## Goal

Spike follow-up 6. Once stance reads the calendar from the store (not through `reader.load_meetings`), nothing guarantees the daily capture ran first. A stance run whose store `last_captured_at` is older than the capture policy's `REFRESH_HOURS` (20) raises before any LLM call.

## Why

A stale calendar in a prompt is a wrong-but-green input: "no meeting on record" when the exchange has since listed one. The store was last captured 2026-10-16T03:42 and is refreshed only when a consumer happens to call the reader.

## Out of scope

Scheduling the capture (the scheduler or Dagster owns that).
