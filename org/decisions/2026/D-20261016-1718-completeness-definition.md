---
schema: decision/v1
id: D-20261016-1718-completeness-definition
title: What makes a company complete, and where the check lives
status: in_force
created: 2026-10-16T17:18+05:30
created_by: owner
decided_by: owner
covers: [T-20261016-1718-completeness-check, I-20261015-1058-stances-without-quarterly-analysis]
standing: true
---

## Decision

The definition is `org/epics/2026/E-20261015-1140-validation.completeness-design.md`: company states (Not initiated), quarter states (Final, Open, Not released, Due with nothing in, Expected, Unknown, Missing, Stale), an Open quarter stays open until the next quarter's data comes in, and which quarters can have documents comes from `raw/results_calendar/due.py`. It lives in `backend/validation/{verdicts,completeness}/`, a consumer of `lib/`, not inside it. Dagster, the proposal gate and e2e import the one function.

## Why

The incident showed pass/fail per job cannot say which company or quarter is incomplete. Owner rules of 2026-10-16 fix what "complete" means; the existing calendar and chain-start code already answer most of it.

## Conditions

Revisit when the results calendar to stance task or the document-intelligence work (SLM metadata for all document types, exchange-parsed quarterly data) lands.
