---
schema: epic/v1
id: E-20261016-1756-stance-inputs
title: Every company's stance uses everything knowable on that day, from analysed documents only
status: open
created: 2026-10-16T17:56+05:30
created_by: owner
verticals: [engineering, research]
depends_on: [E-20261015-1140-validation]
---

## Goal

The stance agents (A, B, D) read what is knowable: analysed quarterly and
annual documents, announcements, and the date of the next result when it is
published. Never raw quarterly data directly. Document types are identified
by small models, and exchange-published quarterly data replaces Screener.

## Stories

1. Results calendar tells stance agents the next result date before it publishes (spike first: coverage, date accuracy, the two known gaps) — T-20261016-1718-results-calendar-to-stance
2. A stance input is an analysis key, never raw quarterly data; checked structurally from the stance record's inputs — idea
3. Every indexed document (announcements, quarterly, annual) is extracted, analysed and consumed by the chain in sequence; a backdated document redoes the analysis and rebuilds the chain — idea
4. Document intelligence: small models (qwen 4b/9b) identify each document's type and metadata — idea
5. De-duplicate BSE/NSE filings (15-page cut) against Screener/StockEdge copies once document types are identified — idea
6. Parse the quarterly data published by the exchanges instead of relying on Screener — idea
7. Every classified document is logged, including the ones ruled immaterial: a classification ledger beside the stance log, so a document is CONSUMED or CLASSIFIED, never silently absent — T-20261016-2130-classification-ledger

## Open questions

- Stories 2 and 3 are validation checks (E-20261015-1140-validation, story 6); do they live there as checks and here as the rule? Decide when story 2 is next.

## Findings

Owner rules, 2026-10-16: an Open quarter stays open until the next quarter's data comes in; duplicates from the BSE/NSE 15-page filter are fine for now; the calendar already exists at `backend/raw/results_calendar/` (`backend/raw/docs/results_calendar.md`).
