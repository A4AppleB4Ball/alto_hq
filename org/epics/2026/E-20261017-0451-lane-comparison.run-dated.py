import json
from dataclasses import asdict, replace
import replay_dated as rd
from backend.backtest.cohort import select_symbols
from backend.backtest.signal_loader import load_signals_from_store
from backend.backtest.universe import PublishedUniverse
from backend.price_feed.dhan_daily_store import DhanDailyPriceStore
from backend.price_watchlist.union.config import MAX_KEPT_STANCES
from backend.trading.config import PRESETS
START, END = "2026-09-15", "2026-10-16"
rd.DATED_FLOWS.update({"2026-09-21": 499632.0, "2026-09-25": 150000.0, "2026-10-08": 30000.0, "2026-10-12": 150000.0})
signals = select_symbols(load_signals_from_store(None, restrict_to_watchlist=False), None)
cfg = replace(PRESETS["v2"], initial_capital=193994.0, monthly_contribution=0.0)
store = DhanDailyPriceStore(user_id="scienceamit1", symbols=sorted(signals["symbol"].unique()), index_symbols=[cfg.benchmark_index],
                            start=START, end=END, force_refresh=False, candle_interval_minutes=15)
res, trades, snaps = rd.run_replay(cfg, signals, store, rd.ReplayConfig(slippage_bps=10.0), start=START, end=END, verbose=False,
                                   universe=PublishedUniverse(MAX_KEPT_STANCES), return_detail=True)
json.dump([asdict(t) for t in trades], open("/tmp/spike/replay_trades.json", "w"))
json.dump([asdict(s) for s in snaps], open("/tmp/spike/replay_snaps.json", "w"))
print("trades", len(trades), "final", round(snaps[-1].portfolio_value), "twr", round(res["twr_pct"], 2))
for s in snaps[:6]: print(s.date, round(s.portfolio_value), round(s.cash), s.num_positions, s.contribution)

json.dump(rd.TARGET_LOG, open('/tmp/spike/replay_targets.json','w'))
json.dump(rd.SIGNAL_LOG, open('/tmp/spike/replay_signals.json','w'))
print('target days', len(rd.TARGET_LOG))
