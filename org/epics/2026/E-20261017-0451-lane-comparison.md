---
schema: epic/v1
id: E-20261017-0451-lane-comparison
title: One page compares the real account, the production replay and many shadow lanes day by day, with enough detail to explain every divergence
status: open
created: 2026-10-17T04:51+05:30
created_by: owner
verticals: [engineering, research, product]
depends_on: []
---

## Goal

The owner sees live results today only on the Positions page. This epic gives
the owner one comparison page of lanes: `real` (Dhan ledger and fills),
`production` (production code replayed day by day, the "should have done"),
and later `shadow-<version>` lanes, up to about 10. Each lane is a saved run
with identical funding, so account values match day by day and any gap is
performance, not set-up. The page shows XIRR and Sharpe (with standard error),
day-by-day divergence, an exact rupee split of the gap, and a decision trace,
so every divergence can be explained, not just measured. Owner session
2026-10-17. Full design: `E-20261017-0451-lane-comparison.design.md` (copy of
`alto/docs/superpowers/specs/2026-10-17-lane-comparison-design.md`; the
design waits for owner approval).

Relation to `E-20261016-2147-shadow-lane`: that epic is the machinery that
runs shadow lanes nightly (parked). This epic is the measuring instrument and
the page they will plug into. It does not run shadows; it needs only saved
runs, so it can proceed first.

Owner of the stories: Engineering builds. Research uses it afterwards to run
experiments; Product (champion vs challengers) reads it for promotion.

## Stories

1. Replay accepts dated deposits instead of the month-end top-up; the default is unchanged — idea
2. Real-lane builder: the Dhan ledger, fills and funding flows give a daily record marked at closes — idea
3. Saved run format (meta, daily, trades, targets) with version stamp, and a writer for replay lanes — idea
4. Metrics from saved runs: XIRR (dated flows and the Positions-page convention), Sharpe ± standard error, drawdown, tracking vs reference — idea
5. Exact rupee gap split (start, exposure, selection, execution), chained daily, check = 0 — idea
6. Comparison page: leaderboard, small multiples, compare charts, overlap, day inspector, decision trace — idea
7. Lane integrity flags on the page: funding, window or price mismatch; missing price stops the run — idea
8. Capture rebalance proposals and the owner's approve/decline decisions (touches the trading flow; owner approval) — idea
9. Decision price on orders for execution quality (touches order path; owner approval) — idea
10. Keep the pre- and post-rationing production book per day — idea
11. Fix the Nifty 50 benchmark fetch so a market line exists — idea
12. Register the first two shadow lanes as saved runs; research protocol for pre-registered metrics and a noise check — idea

## Open questions

- **Stance basis (owner):** replay on stances as recorded at the time, or the
  current stance chain. Recommended: as recorded (point-in-time).
- **Delivery (owner):** how saved runs reach the server and where the page is
  served (static file, API route, cockpit tab). One option: commit runs to
  git like stances.
- **Order path (owner):** whether stories 8 and 9 are in this epic's first
  task or separate tasks with their own approval.
- Which metrics and window length before a promotion is considered
  (Research protocol, shared with the shadow-lane epic).

## Findings

Spike 2026-10-17 (throwaway scripts in `/tmp/spike`, not kept), alto `9a97ee1`,
account scienceamit1, window 2026-09-15 to 2026-10-15.

- Rebuilt real cash from the Dhan ledger ends at ₹126,863.02; the funds API
  reports ₹126,932.95.
- Replay (preset v2, 10 bps) with the same start cash and dated deposits:
  XIRR +5.36%, Sharpe 3.20; real: XIRR −5.25%, Sharpe 0.78. Sharpe standard
  error is about ±3.5 at 21 daily returns.
- The Positions page shows −4.43%: begin 2026-09-01 ₹74,350.16, broker
  `capital_flows`, end 2026-10-17 ₹1,020,500.12. Annualised over about 46 days
  the figure moves several points on a few hundred rupees.
- Final account-value gap real − replay is −₹6,412. Real buys filled about 56
  bps worse than the day's open against 10 bps assumed; real turnover 5.3×
  against 2.5× for the replay.
- Missing today: replay runs are not saved; account snapshots start 24 Sep and
  copy values onto non-trading days; the desired book is saved only from 25 Sep
  and before rationing; owner decisions are not kept; filled orders carry no
  decision price; the Nifty 50 fetch fails (`Symbol 'NIFTY 50' not found in
  Dhan instrument master`).
