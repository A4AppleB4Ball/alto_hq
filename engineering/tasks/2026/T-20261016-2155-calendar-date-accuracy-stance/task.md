---
schema: task/v1
id: T-20261016-2155-calendar-date-accuracy-stance
title: "Re-measure results-calendar date accuracy on stance companies once Q2 documents land"
status: draft
created: 2026-10-16T21:55+05:30
created_by: claude-main
kind: internal
spawned_from: T-20261016-1718-results-calendar-to-stance
related: [T-20261016-1718-results-calendar-to-stance, E-20261016-1756-stance-inputs, D-20261016-2030-calendar-date-accuracy-market-wide]
---

## Goal

Spike follow-up 1. Join each stance company's stored meeting date to the `publish_date` of its Q2FY27 results and concall documents in the document index, and publish the gap table. Decision D-20261016-2030 measured market-wide (BSE 94 of 95 at gap 0, NSE 105 of 107) because only one stance company had Q2FY27 documents; this closes the stance-company half. Not startable before about 2026-11-15.

## Why

The stance prompts will say "next result on date X" (follow-ups 4 and 5). That is only safe if the date is the filing day for the stance population, not just the market.

## Out of scope

Any product code change; fixing wrong dates (a miss becomes its own task).
