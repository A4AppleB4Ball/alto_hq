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

## Findings

Read-only, 2026-10-15, alto `ab8a959`.

**The scheduler today** (`backend/config/pipeline_scheduler.yaml`, live
state `news_server/data/alto_data/scheduler/state.json`):

- Enabled: `quarterly_watch` (every 1340 min), `exchange_feed` (25 min),
  `announcement_reconciler` (05:30), `refresh_price_cache` (16:00),
  `prefetch_universe_prices` (Saturday 06:00), `price_watchlist` (after
  prefetch), `price_watchlist_union` (16:30).
- Disabled: `e2e_morning_0030`, `e2e_morning_0800`, `intake_runner`,
  `stance_runner`, `pipeline_self_heal`, `annual_report_watch`,
  `resolve_concall_publish_dates`, `price_watchlist_backfill`, the macro jobs.
  So the nightly chain (producers → intake → e2e) is not scheduled today;
  it runs by hand.
- `state.json` holds per job only status, last run, exit code, duration and
  trigger: nothing about which companies were covered, failed or skipped.

**A silent failure of the kind story 5 must catch:**
`prefetch_universe_prices` failed on 2026-10-10 06:15 (exit 1): every one of
3759 symbols got `DH-901` (expired Dhan token), logged in
`scheduler/logs/prefetch_universe_prices/2026-10-10_06-15-13_exec_*.log`.
No alert. Its dependent `price_watchlist` has never run (state `None`) and
nothing reports that. The log also shows a new Dhan session per symbol.

**Partial runs skip gates** (I-20261015-1058, story 6):

- e2e gates run only when the gate steps are in `--steps`; a
  `--steps verify,stance` run skips them (`backend/e2e/steps.py:264`).
- The `backfill` step is deprecated (`steps.py:258-261`).
- Stance Agent A runs with "(no quarterly analysis knowable yet)"
  (`backend/stance/worker.py:439-441`); the only trace is
  `quarterly_analysis_key=None` on the record (`:581`).
- `stance/ready.py` does not block on a missing quarterly;
  `stance/reconcile.py:219-229` `_frontier` reads "current" when a company
  has no versions.
- The proposal filters on staleness only (`backend/trading/core.py:26-34`,
  `rebalance_service.py:296`); its warnings are hard-coded `[]` (`:572`).
- `FEED_START_DATE` is 2026-07-01 (`backend/config/scope.py:12`, used by
  `e2e/run.py:440`), but chains start at the annual filing
  (`backend/lib/quarter_versions.py:337-342`), so pre-July filing bodies are
  never fetched.

**Run history volume** (story 2, spike B7): `alto/logs/e2e/` has 244 run
folders plus `progress.jsonl`; one e2e run writes about 4–5k files; 41.7k
log files were created in the last 7 days.

**Machine gate** (`backend/config/machine.py:3-27`): `LOCAL_EXECUTION` is
read from the root `.env`, and a missing or unreadable `.env` means "local
machine". On the server an unreadable `.env` would enable the compute jobs.
This is a fallback where the rules require an error.
