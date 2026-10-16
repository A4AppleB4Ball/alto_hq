# Plan

Base: 9801fba (main lacks backend/executor/broker_factory/prices.py). Worktree
`.claude/worktrees/T-20261016-2336-daily-price-store-everywhere`, declared `mode: sandbox`
on an empty root under `alto_sandboxes/` (no production reach).

**Touches:** `backend/api/services/price_chart_service.py` (`_load_daily_bars_from_dhan`,
API chart route), `backend/trading/scripts/rebuild_price_refs.py` (`rebuilt_refs`, CLI),
`backend/trading/harness.py` (`_resolve_price`; callers `_resolve_prices`, line 270, line 434
all forward the caller's `price_store`).

**Money path:** yes (harness prices). Tests pin the DhanPriceStore arguments for a dhan user
at each site; `_resolve_price` with a store is unchanged.

**Change:** each site calls `create_daily_price_store(user, symbols, start, end)`; for dhan
that is `DhanPriceStore(user, symbols, [], start, end)`, identical to before. `_resolve_price`
raises ValueError when `price_store is None` instead of building one (the owner will notice:
any caller relying on the implicit build now raises).

**Known gap:** acceptance 2 as written covers backend/backtest/* and backend/scripts/refresh_price_cache.py,
which also build DhanPriceStore and are outside the goal's three sites. Test written as stated;
reported if it fails.

**Checks:** 1 grep of the three files; 2 `pytest backend/executor/broker_factory/tests/test_no_direct_dhan_price_store.py`;
3 `pytest backend/executor/broker_factory/tests/test_price_store_sites.py`; 4 full suite vs base, boundary test, entry-point imports.
