# Lane comparison: real, production and shadow runs side by side

## Why

Today the owner sees live results only on the Positions page, which says how the account is doing but not what production *should* have done, nor what an experiment would have done. The owner wants to run live and many shadow versions (up to about 10) together and compare them in depth: what each lane would have given, what was realised, day by day, and why any two lanes diverged. The page must let the owner debug a divergence, not just see its size.

The spike (throwaway, not in the repo) showed this is feasible with data that already exists, and showed what is missing. Findings that shape this design:

- Real account value can be rebuilt daily from the Dhan ledger and fills; the rebuilt cash matched the broker funds API to ₹70. Charges are already net in real account value. Do not add exit costs.
- `backend/backtest/replay.py` replays production day by day, but it supports only a start amount plus a month-end top-up. Real was funded by six dated deposits, so an unmatched replay reads a funding difference as a performance gap. A patched copy with dated deposits matched real day 0 and closed the gap attribution exactly (check = 0).
- The Positions page XIRR (−4.43%) and a window XIRR (−5.25%) differ only in start, end and flows. The reconciliation must be visible, not hidden.
- Nothing saves replay runs; saved account snapshots start 24 Sep and copy values onto non-trading days; the production desired book is saved only from 25 Sep and before rationing; the owner's approve/decline decisions are not kept; filled orders carry no decision price; the Nifty 50 benchmark fetch fails.

## Goals

1. A **lane** is one run of one version over a window, with identical funding. Lanes: `real`, `production` (production code replayed day by day), and `shadow-<version>` per experiment, same engine as production.
2. Every lane is saved as a daily record, so the page reads files and never recomputes. Adding a lane means adding a run, not changing the page.
3. A comparison page with a **reference lane** selector (default production). Every gap means "lane minus reference".
4. Enough detail to explain any divergence: exact rupee gap split, per-name contribution, book overlap, a per-day decision trace, execution quality against the day's open.
5. Fair comparison by construction: same start cash and same dated deposits in every lane, or the lane is badged "not comparable".
6. Honest statistics: XIRR and Sharpe (not CAGR), Sharpe shown with its standard error, ranks marked indistinguishable when intervals overlap.
7. One replay pass over the whole window gives every day's account value; no per-start/end reruns.

## Non-goals

- Not a second source of truth for live trading. Nothing here places or cancels orders.
- No automatic promotion of a shadow to production. That is the owner's decision.
- No classification of why a decision happened using rules or heuristics; the trace shows what each layer wanted and the owner reads it.
- Pairwise rupee attribution for arbitrary lane pairs beyond real vs replay is out of the first slice.
- Not a replacement for the Positions page.

## Anti-goals (failure even if it "works")

- A number that looks fine on stale or unmatched inputs (the product's worst failure is wrong-but-green). A lane with a different start, a missing price, or a mismatched stance snapshot must say so on the page.
- A comparison that quietly differs in capital, deposits, or window.
- Fallback rules that hide missing data; missing data raises an error.

## Constraints

- Follow repo rules: absolute imports from the workspace root, no relative imports, no fallbacks, no heuristics, modular code. New code goes in a feature folder with an `__init__.py`; tests in `<feature>/tests/`; docs in the package's `docs/`.
- Data paths come from `backend/config/paths.py`.
- Read prices through the existing `DhanDailyPriceStore`; read stances through the existing signal loader. Do not re-derive quarter or as-of logic (see `backend/docs/30_quarter_identity.md`).
- `GET /api/portfolio` writes a snapshot as a side effect; the page must not call it.
- Compute stays on the local Mac; the server serves.
- Releases are tracked separately (versions `v<n>`, tags and registry from alto_hq), so replaying current code against the lane's recorded version is acceptable; a run records the commit it used.

## The design

### 1. Dated-deposit replay (first slice)

Extend the replay to accept dated deposits (a dated flow map) in place of the month-end contribution. Cash is added at the start of the deposit day, and the day's contribution is recorded. The existing fixed-capital behaviour stays the default so current backtests and sweeps do not change. Replay also returns, per day, the target weights with reason and rank, and the signal state used, so the page can show the decision trace.

### 2. Saved runs

A run is a folder, keyed by lane id and window, holding:

- `meta.json`: lane id, kind (`real` | `production` | `shadow`), version, git commit, preset/config, stance-data hash and row count, slippage assumption, start cash, dated deposits, window, created time.
- `daily.jsonl`: one row per trading day: nav, cash, equity, flow, holdings (shares), weights, prices used.
- `trades.jsonl`: orders or fills with side, shares, price, notional, cost, slippage, reason (replay) or time (real).
- `targets.jsonl`: per-day, per-name target weight, reason, rank, stance, conviction, signal date.

Real is built by a builder reading the Dhan ledger, fills, and funding flows, marking holdings at daily closes. Replay and shadow lanes are written by the replay. The window ends at the last day the price store has a bar; the run stamp says so.

### 3. Metrics (computed from saved daily records)

- XIRR on dated flows, and the Positions-page convention XIRR for real (begin at `performance_start_date`/value, broker `capital_flows`, end at the last snapshot), shown side by side with the reconciliation.
- Sharpe with standard error `sqrt((1 + 0.5 sr²)/n) * sqrt(252)`, Sortino, volatility, max drawdown and date, hit rate, best/worst day, deployed %, turnover, friction.
- Versus reference: tracking error, correlation, t-stat of the daily gap, ₹ value gap.
- Gap split in rupees (exact): start difference + exposure `(E_r − E_p) × book_return_p` + selection `E_r × (book_return_r − book_return_p)` + execution/fees residual. Only real vs replay has an execution term; shadow vs production is pure selection and exposure.

### 4. The page

Level 1 leaderboard (one row per lane, sortable, ± standard error, sparkline) and a small-multiples panel. Level 2 compare charts for the selected lanes: account value, cumulative return, gap to reference, drawdown, capital deployed; gap decomposition per lane; lane-by-lane book overlap. Level 3 day inspector: per-lane tiles, holdings by lane, real fills vs replay orders, and the decision trace (what each layer wanted, what each account held). Only a few lanes get a categorical color; the rest are grey until selected. A fixed color per lane, light and dark themes, a table view of every chart, a legend whenever there are two or more series. Layout reference: `.superpowers/brainstorm/36632-1792187579/content/performance-dashboard-v8.html` (throwaway mockup, four lanes, two shadows being copies of production).

### 5. Capturing what is missing today

- **Proposals and decisions:** save each rebalance proposal and the owner's approve/decline with a timestamp, so the human step is visible in the trace.
- **Decision price on orders:** record the price at decision time on each order, so execution quality has its own baseline instead of the day's open.
- **Production book:** keep the pre-rationing and post-rationing book per day from now on (earlier days are not recoverable).
- **Benchmark:** fix the Nifty 50 fetch (`Symbol 'NIFTY 50' not found in Dhan instrument master`) so a market line exists.

## First slice

Dated-deposit replay; saved runs with the version stamp for `real` and `production`; the leaderboard and compare views reading them; the proposal and decision capture. Shadows follow once the first two lanes are saved and verified.

## Acceptance for the first slice

- Real and production lanes start from the same cash and receive the same deposits; their day-0 account values match to the rupee.
- The rupee gap split reconciles to the final value gap (check = 0).
- The page's real XIRR under the Positions convention equals the Positions page figure (−4.43% on the data recorded on 2026-10-17), and the window XIRR is shown beside it.
- Two additional lanes added by saving two more runs appear on the page with no page code change.
- A lane with mismatched funding or a missing price is flagged on the page, not drawn silently.

## Settled after the builder check (my calls, marked)

- **Funding source (my call):** the Dhan ledger's "Money added/transferred" rows are the one list of deposits, dated to the next trading day when posted on a non-trading day. Window start is the first real fill day (2026-09-15). Start cash is the real account value on that day; replay lanes copy it and the same deposit list. The Positions-page XIRR is computed separately from the broker `capital_flows`, and both are shown.
- **Gap split (my call):** chained daily, summed over the window. Exposure and selection come from per-name contributions of holdings at the previous close. Execution/fees is the remainder by definition, so the check = 0 proves the daily terms add up to the account-value gap, not that the remainder is right; the execution term is validated separately against the fills' price versus the day's open.
- **Shadow identity (my call):** a shadow is a config (preset) plus the git commit it ran on, both recorded in `meta.json`. How experiments pick their code is out of the first slice.
- **Mismatch and missing data (my call):** funding must match exactly in dates and amounts, and day-0 values within ₹1. A missing price stops the run with an error and nothing is saved; the page only flags lanes that were saved but differ in funding or window.
- **Nifty 50 benchmark (my call):** a separate small task, not part of the first slice.

## Left to the owner (open)

- Replay's stance basis: point in time as recorded, or the current stance chain.
- How saved runs reach the server and where the page is served.
- Whether proposal/decision capture and decision price on orders touch order-path code in this task.

## Left to the builder

File and module names within the feature folder, run storage layout details beyond the contents above, the chart library or plain SVG, and how the page is served (static file, API route, or cockpit tab).

## Calls I made (check these)

- Reference lane defaults to production; pairwise rupee attribution only for real vs replay in slice one.
- Real and replay are separate lanes; they are not collapsed into one row.
- Saved runs use plain files (JSONL), not a database.
- Window ends at the last day the price store covers.
