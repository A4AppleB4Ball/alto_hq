---
schema: epic/v1
id: E-20261015-1140-orchestration-and-ops
title: The nightly compute chain runs on Dagster and an ops agent reports on it every day
status: open
created: 2026-10-15T11:40+05:30
created_by: owner
verticals: [operations, engineering]
---

## Goal

Every night the chain (producers on the price watchlist → intake extraction
→ e2e quarterly and stance) runs only what is needed, records per company
what ran, failed and was skipped, and an ops agent turns that into a daily
brief, incidents and proposed fixes for the owner to review
(D-20261015-1058-dagster-for-compute-chain).

## Stories

1. Spike: Dagster over the existing CLIs with a blocking completeness check — T-20261015-1058-dagster-spike
2. Each job's outputs redefined for agents: what it covered, failed, skipped and why — idea (from the spike)
3. The chain on Dagster; the asyncio scheduler's compute jobs retired — idea
4. Run only what is needed: dependencies (latest prices, new filings) trigger work — idea
5. Ops agent: daily brief, incidents matched by check and reason, repairs proposed via owned commands — idea
6. Partial runs can no longer skip a failed gate (I-20261015-1058-stances-without-quarterly-analysis) — idea

## Open questions

- Company-based vs stage-based pipeline: spike's findings, question B1.
