---
schema: task/v1
id: T-20261016-2155-calendar-next-result-in-prompts
title: "Agents A and B see the next result date (or why it is unknown); D unchanged"
status: draft
created: 2026-10-16T21:55+05:30
created_by: claude-main
kind: decision
spawned_from: T-20261016-1718-results-calendar-to-stance
related: [T-20261016-1718-results-calendar-to-stance, E-20261016-1756-stance-inputs, T-20261016-2155-calendar-next-meeting-asof]
---

## Goal

Spike follow-up 5. Add the field `next_result: {date, days_away}` or an explicit unknown reason to Agent A's four prompts (beside `<announcements_since_last_assessment>`) and to Agent B's `<market_data>`, built in `backend/stance/worker.py` from `AsOfLedger.next_results_meeting`. D sees it only through A and B outputs. Pilot of 3 stance runs on companies with a meeting within 14 days.

## Why

Agent B already tests "known dated future event" (B5); today it cannot know the date. Change kind decision (new stance input): research evidence, shadow, then owner promotion.

## Out of scope

Showing D the date directly; changing what any agent concludes.
