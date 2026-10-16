# Findings: corporate actions (FC12), 2026-10-16

Read-only. Written by dev (text returned to the session, saved by the
session). alto main, news_server as of 2026-10-16. Acceptance sha256
verified a7fec9d0…eb6a8.

## 1. Where corporate actions enter

- A share-basis ledger exists: `backend/price_feed/corporate_actions.py:1-17`
  fetches BSE `actions()` per BSE code into `CORPORATE_ACTIONS_DIR`
  (`backend/config/paths.py:216-218`, `news_server/data/1/corporate_actions`).
  `classify` parses bonus/split ratios (`:54-76`); `share_factor` (`:121-129`)
  raises outside the fetched window (`:114-119`).
- Its only consumer is `backend/price_feed/share_basis_prices.py:39`
  (`adjust_to_basis`, `:78-93`); nothing in the production path uses it.
  `grep -rnE "share_basis_prices|SharePrices|load_ledger" backend --include='*.py' | grep -v tests`
  → only `backend/price_watchlist/experiments/floors/liquidity.py:19`
  (imports `load_bhavcopy`, not the ledger).
- No scheduled fetch: `grep -n corporate backend/config/pipeline_scheduler.yaml` → rc=1.
- Stored ledger: 20 files, 2024-01-01..2026-09-29, fetched 2026-09-29T23:49.
  Non-dividend actions: 500180 Bonus 1:1 (ex 2025-08-26), 500325 Bonus 1:1
  (ex 2024-10-28), 541729 Bonus 1:1 (ex 2025-11-26); none in the window.
  NSE-only names have no BSE code, so no ledger.
- Split/record-date filings enter as ordinary announcements
  (`backend.lib.events`); stance agents see them as text.
- **No structured corporate-action data reaches any production price,
  stance or trading computation.**

## 2. Are Dhan and cached prices adjusted

- Daily: adjusted to today's share basis (`backend/price_feed/dhan_daily_store.py:1-16`);
  a detected re-adjustment refetches the series (`:104-131`).
- 15-min `DhanPriceStore`: as traded, raw (`dhan_daily_store.py:4-5`); used by
  trading (`backend/trading/harness.py:46,52`) and the live feed (`feed.py:10`).
- NSE bhavcopy: raw, but last file `~/NSE_BSE_Data/NSE/EQ/2026-09-08-NSE-EQ.txt`.
- `backend/lib/asof.py:17-21`: as-of price is on today's basis, so a level can
  differ from what traded on T; `daily_price_series` (`:90-110`) only clamps dates.

## 3. Real case in the window: ORIANA, split 1:5, record date 2026-09-18

- Watchlist: `data/metadata/active_watchlist.csv:277`, `price_watchlist.csv:29`
  (held, stance, price); NSE-only (`watchlist.csv:670`).
- Filings: 2026-07-13 "Stock split" Rs 10 → 5 × Rs 2; 2026-08-25 record date 18-Sep-2026.

| day | 15-min raw (open / close) | daily adjusted (open / close) |
|---|---|---|
| 2026-09-16 | 1296.2 / 1255.00 | 259.24 / 250.15 |
| 2026-09-17 | 1257.0 / 1349.50 | 251.40 / 269.77 |
| 2026-09-18 | 276.5 / 272.90 | 276.50 / 271.75 |
| 2026-09-21 | 290.0 / 270.35 | — |

  Raw breaks −79.8%; daily is continuous (1349.5/5 = 269.9). Daily cache written 2026-10-16 03:54.
- Stance (`alto_data/stances/ORIANA/log.jsonl`): link 09-14 used price 245.45
  dated 2026-09-11 while raw was ≈1250 (EPS 24.83, P/E 9.89, HOLD MEDIUM,
  text mentions post-split estimates); link 09-21 price 271.3, P/E 10.93, HOLD
  MEDIUM, no price-action trigger. The chain was computed after the split
  (file's first news_server commit 29688c5c81, 2026-10-03), so the pre-split
  link saw post-split levels: a price-level leak, not news (public 2026-07-13).
  What a live 2026-09-14 run saw is not checkable from stored state.
- Positions did not cross the date: first fill BUY 375 @ 297.4 on 2026-10-08
  (`book/default/fills.jsonl`); `snapshots.jsonl` starts 2026-09-24 empty;
  `rebalance/current.json` 375 @ 297.4, price 268.05.

## 4. Positions and target quantities across a split

- Lots: broker shares change with no fill → `PositionLots.reconcile` raises
  (`backend/trading/position_lots.py:180-207`, "Adjustment logic is
  deliberately absent"); `position_views.py:84-90` raises with no lot. Trading
  stops loudly rather than mis-sizing.
- Targets: notional / live raw price, rounded to lot (`backend/trading/planner.py:266`, `:353`): new basis automatically.
- Price refs: `price_refs.py:101-127` updates peak/trough from raw ticks. For
  an ACCUMULATE holding a pre-split `peak_since_last_buy` reads ≈−80%
  drawdown (`backend/trading/core.py:326-334`) → maximum dip-buy weight, if
  the reconcile did not raise first. Jump-trim vs trough (`:337-339`) is not
  falsely triggered.

## 5. FC12 proposal

The product needs a change before FC12 can expect "adjusted"; today's
designed behaviour is to raise. Op for today's product:

```yaml
- op: corporate_action
  target: {symbol: ORIANA}
  as: {kind: split, ratio: 5, ex_date: 2026-09-18,
       announce: {approved: 2026-07-13, record_date_filing: 2026-08-25}}
```

Applies to: 15-min bars from ex_date (÷ ratio); daily bars before ex_date
(÷ ratio, only at checkpoints on/after ex_date); paper-broker holding
(× ratio, no fill); adds the two filings to the index. Raises if the symbol
has no price series in the window.

Expected verdicts:
- 2026-09-17: no new-basis price visible before ex_date — expected FAIL today (`asof.py:17-21`).
- 2026-09-18 stance: no price-action trigger or stance change from the break — expected PASS.
- 2026-09-18 trading: reconcile raises "corporate action moved shares", no order planned — expected PASS (loud stop).
- 2026-10-15: general invariants.

Follow-up story lines:
1. Schedule the ledger fetch; add an NSE source for NSE-only names.
2. AsOfLedger prices on the share basis in force on T (`share_basis_prices`), not Dhan's today-basis daily.
3. Apply the ledger share factor to lots and price refs instead of raising; FC12 then expects "adjusted, no raise".
