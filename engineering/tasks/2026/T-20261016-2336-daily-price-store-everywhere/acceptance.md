# Acceptance: daily price store everywhere

1. `backend/api/services/price_chart_service.py`, `backend/trading/scripts/rebuild_price_refs.py` and `backend/trading/harness.py` `_resolve_price` build their price store only through `backend/executor/broker_factory/prices.create_daily_price_store`; `_resolve_price` raises when no store is passed instead of building one.
2. A test (AST or grep) shows no module outside `backend/executor/broker_factory` and `backend/price_feed` constructs `DhanPriceStore(`.
3. A dhan user in a live checkout gets the same `DhanPriceStore` arguments as before at each changed site (test pins them); a paper user in a sandbox reads stored prices; a missing symbol raises.
4. Suite: no new failure; boundary test passes; entry points import.

## Amendment (owner 2026-10-17)

2'. Replaces 2. The test allows, by exact file name only, the research and cache scripts `backend/backtest/sweep.py`, `backend/backtest/scripts/{ab_discount_sign,compare_macro_ablation,compare_macro_signal_backtest,compare_tiebreak_modes,compare_trade_book}.py` and `backend/scripts/refresh_price_cache.py`; any other direct `DhanPriceStore(` outside `broker_factory`/`price_feed` fails.
5. `rebuild_price_refs` for a paper user raises a clear error that 15-minute price refs are not available for paper (no AttributeError, no rebuild from daily bars).

## Amendment 2 (owner 2026-10-17)

6. **Sandbox price reads.** In a sandbox checkout, every daily price read used by the stance run (the AsOfLedger price path, `backend/lib/asof.py`) and by `create_daily_price_store` for non-paper users reads the shared Dhan price cache (`~/NSE_BSE_Data/dhan_cache`, resolved through `backend.config.paths`) read-only: no Dhan client is built, no credentials are read, nothing is written to the cache. A missing price raises naming the symbol and date (no fetch). Live checkouts are unchanged (pinned by test).
7. **No look-ahead.** A sandbox price read for an as-of date never returns a price after that date (test).
8. **No Kimi:** any LLM run uses DeepSeek on Foundry or the local model.

## Amendment 3 (owner 2026-10-17, after QA round 1)

9. **Every sandbox price read checks the cache is current** (both the AsOfLedger path and `create_daily_price_store`) and raises naming the symbol and date; no stale close is returned.
10. `rebuild_price_refs` raises a clear error for any user in a sandbox (not only paper).
11. In a sandbox, the Dhan instrument master and the NSE holiday calendar are read from stored copies (resolved through `backend.config.paths`), read-only; a sandbox makes no network call; a missing copy or a year it does not cover raises naming what is missing.
12. `backend/api/services/daily_price_service.py` gets its daily series through the checkout-gated factory; live arguments unchanged (test).
