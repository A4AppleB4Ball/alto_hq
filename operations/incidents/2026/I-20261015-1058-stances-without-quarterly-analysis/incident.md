---
schema: incident/v1
id: I-20261015-1058-stances-without-quarterly-analysis
title: Ten companies hold stances with no quarterly analysis; the proposal buys one of them
status: open
created: 2026-10-15T10:58+05:30
created_by: owner
detected_by: "owner, reading the 2026-10-15 proposal; confirmed by a read-only fleet scan (fleet_scan.py in this folder)"
severity: wrong-output
companies: [ARSSBL, CHANDAN, PNGSREVA, ABDL, EMUDHRA, FAIRCHEMOR, RAYMOND, SMCGLOBAL, TAC, KRISHNADEF]
related: [T-20261015-1058-dagster-spike, E-20261015-1140-orchestration-and-ops, E-20261015-1140-validation]
---

## What was seen

The pending proposal `workspace/scienceamit1/rebalance/proposals/2026-10-15T10-17-21.json`
(warnings: []) buys 88 ARSSBL (≈₹45.6k, target 4.41%) and targets CHANDAN at
4.41%. Neither company has any `quarterly_update` analysis
(`workflow_outputs/cache/quarterly_update/{ARSSBL,CHANDAN}` absent); every
stance link has `quarterly_analysis_key: null`. A fleet scan (484 companies
with a stance) finds 10 with no analysis for their latest quarter with
documents, all 10 with none at all.

## Root cause

- e2e stopped all of them at their gates, but a stopped company is visible
  only in the console summary; nothing alerts.
- Partial runs (`--steps verify,stance`, 2026-10-14 and 10-15, by hand) skip
  quarterly and every gate (`backend/e2e/steps.py:264` accepts any subset).
- Agent A runs with "(no quarterly analysis knowable yet)"
  (`backend/stance/worker.py:439-441`); the record does not mark the gap.
- The proposal filters on signal age only (`backend/trading/core.py:26-34`,
  `backend/api/services/rebalance_service.py:296`); `warnings` is hard-coded
  empty (`:572`).
- Upstream: pre-July filing bodies never stored because the feed starts at
  2026-07-01 (`backend/config/scope.py:12`) while chains start at the annual
  filing (ARSSBL, ABDL, EMUDHRA, FAIRCHEMOR, RAYMOND, SMCGLOBAL, KRISHNADEF);
  reporting-period extraction failed on one document and blocks the company
  (CHANDAN, TAC, PNGSREVA).

## Impact

One wrong buy pending owner decision (ARSSBL); one wrong target (CHANDAN,
no order only because cash was rationed). No held position affected.

## Plan

The owner handles the pending proposal by hand. The lasting fix comes from
the completeness model built on the orchestrator
(D-20261015-1058-dagster-for-compute-chain), starting with
T-20261015-1058-dagster-spike; its findings decide the follow-up tasks.
Resolved when the completeness check passes for all ten and a stance with an
unanalysed quarter can no longer reach a proposal.
