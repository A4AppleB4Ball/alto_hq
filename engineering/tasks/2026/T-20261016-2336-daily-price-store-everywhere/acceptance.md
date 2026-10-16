# Acceptance: daily price store everywhere

1. `backend/api/services/price_chart_service.py`, `backend/trading/scripts/rebuild_price_refs.py` and `backend/trading/harness.py` `_resolve_price` build their price store only through `backend/executor/broker_factory/prices.create_daily_price_store`; `_resolve_price` raises when no store is passed instead of building one.
2. A test (AST or grep) shows no module outside `backend/executor/broker_factory` and `backend/price_feed` constructs `DhanPriceStore(`.
3. A dhan user in a live checkout gets the same `DhanPriceStore` arguments as before at each changed site (test pins them); a paper user in a sandbox reads stored prices; a missing symbol raises.
4. Suite: no new failure; boundary test passes; entry points import.
