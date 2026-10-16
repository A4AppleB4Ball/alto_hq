# Acceptance: daily price store everywhere

1. `backend/api/services/price_chart_service.py`, `backend/trading/scripts/rebuild_price_refs.py` and `backend/trading/harness.py` `_resolve_price` build their price store only through `backend/executor/broker_factory/prices.create_daily_price_store`; `_resolve_price` raises when no store is passed instead of building one.
2. A test (AST or grep) shows no module outside `backend/executor/broker_factory` and `backend/price_feed` constructs `DhanPriceStore(`.
3. A dhan user in a live checkout gets the same `DhanPriceStore` arguments as before at each changed site (test pins them); a paper user in a sandbox reads stored prices; a missing symbol raises.
4. Suite: no new failure; boundary test passes; entry points import.

## Amendment (owner 2026-10-17)

2'. Replaces 2. The test allows, by exact file name only, the research and cache scripts `backend/backtest/sweep.py`, `backend/backtest/scripts/{ab_discount_sign,compare_macro_ablation,compare_macro_signal_backtest,compare_tiebreak_modes,compare_trade_book}.py` and `backend/scripts/refresh_price_cache.py`; any other direct `DhanPriceStore(` outside `broker_factory`/`price_feed` fails.
5. `rebuild_price_refs` for a paper user raises a clear error that 15-minute price refs are not available for paper (no AttributeError, no rebuild from daily bars).
