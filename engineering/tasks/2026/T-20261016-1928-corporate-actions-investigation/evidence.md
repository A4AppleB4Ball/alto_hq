---
schema: evidence/v1
task: T-20261016-1928-corporate-actions-investigation
round: 1
qa: pass
outputs_changed: unverified
head: alto main 79e66a7; alto_hq 270f3fd (findings.md)
at: 2026-10-16
---

## Round 1

Read-only investigation; no code diff, so no suite run (nothing changed). Approval sha256 of acceptance.md matches (a7fec9d0…eb6a8). All checks below run read-only by QA on 2026-10-16.

### Acceptance 1: each goal question answered with file:line / command, dated — PASS
Spot-checked at 79e66a7, all match:
- `backend/price_feed/corporate_actions.py:1-17` docstring (BSE ledger), `:114-129` `_require_covered` raises / `share_factor`.
- `backend/config/paths.py:216-218` CORPORATE_ACTIONS_DIR.
- `grep -rnE "share_basis_prices|SharePrices|load_ledger" backend --include='*.py' | grep -v tests` -> only price_feed internals plus `price_watchlist/experiments/floors/liquidity.py:19` (load_bhavcopy). Matches.
- `grep -n corporate backend/config/pipeline_scheduler.yaml` -> rc=1. Matches.
- `backend/lib/asof.py:17-21` today's-basis note; `backend/trading/position_lots.py:180-207` raises, "Adjustment logic is deliberately absent"; `position_views.py:84-90` raises; `core.py:326-339` dip/jump logic; `planner.py:266,353` notional/price.

### Acceptance 2: real split in window with stored prices and positions — PASS
ORIANA, record date 2026-09-18. Independently read:
- `~/NSE_BSE_Data/dhan_cache/15min/ORIANA.parquet` day open/close: 09-16 1296.2/1255.00, 09-17 1257.0/1349.50, 09-18 276.5/272.90, 09-21 290.0/270.35. Matches.
- `~/NSE_BSE_Data/dhan_cache/daily/ORIANA.parquet` (mtime 2026-10-16 03:54): 09-16 259.24/250.15, 09-17 251.40/269.77, 09-18 276.50/271.75. Matches.
- `alto_data/stances/ORIANA/log.jsonl`: 09-14 link price 245.45 dated 09-11; 09-21 link price 271.3, is_price_action_trigger false. File added in news_server 29688c5c81 2026-10-03. Matches.
- Fill BUY 375 @ 297.4 2026-10-08; snapshots start 2026-09-24 empty; current.json 375 @ 297.4 price 268.05. Matches, but see ALERT 1 for path.
- Watchlist lines `active_watchlist.csv:277`, `price_watchlist.csv:29` show ORIANA. Matches.

### Acceptance 3: FC12 op + expected verdicts or follow-up — PASS
Section 5 gives the op, params, four expected verdicts and three follow-up story lines.

### Confirmed findings (verifier could not disprove)
- ALERT 1: findings.md §3 cites `book/default/fills.jsonl`, `snapshots.jsonl`, `rebalance/current.json` with no user. Under `alto_data/` those files hold no ORIANA and snapshots start 2026-09-15; the data is in `alto_data/workspace/scienceamit1/`. Numbers are right, path is wrong. Confirmed by grep -c ORIANA on both trees.
- ALERT 2: findings.md §4 cites `price_refs.py:101-127` as under trading; the file is `backend/stores/book/price_refs.py` (lines 101-127 = `observe`, updates peak/trough). Confirmed by `find backend -name price_refs.py`.

### Dev claims not confirmed
handoff.md does not exist (dev's write was blocked). Not checked: the filing texts (07-13 / 08-25), the BSE ledger file count and the three bonus entries, NSE bhavcopy last date.

### Check that would catch this class
For investigation tasks: a citation linter that resolves every `path:line` in findings.md against the tree and data root.
