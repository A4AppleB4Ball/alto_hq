"""Throwaway spike: production replay vs real Dhan account, daily. Not product code."""
import json
from dataclasses import asdict, replace

import pandas as pd

from backend.backtest.cohort import select_symbols
from backend.backtest.replay import ReplayConfig, run_replay
from backend.backtest.signal_loader import load_signals_from_store
from backend.backtest.universe import PublishedUniverse
from backend.price_feed.dhan_daily_store import DhanDailyPriceStore
from backend.price_watchlist.union.config import MAX_KEPT_STANCES
from backend.trading.config import PRESETS

OUT = "/tmp/spike"
START, END = "2026-09-15", "2026-10-16"
BOOK = "/Users/kmrh581/personal/projects/workspace/news_server/data/alto_data/workspace/scienceamit1/book/default"

fills = [json.loads(l) for l in open(f"{BOOK}/fills.jsonl")]
fills_df = pd.DataFrame(fills)
fills_df["date"] = fills_df["traded_at"].str[:10]

signals = select_symbols(load_signals_from_store(None, restrict_to_watchlist=False), None)
cfg = PRESETS["v2"]
symbols = sorted(set(signals["symbol"]) | set(fills_df["symbol"]))
store = DhanDailyPriceStore(
    user_id="scienceamit1", symbols=symbols, index_symbols=[cfg.benchmark_index],
    start=START, end=END, force_refresh=False, candle_interval_minutes=15,
)
# ---- Real: ledger cash path + fills holdings, marked at daily closes
ledger = json.load(open(f"{OUT}/ledger.json"))
seen, rows = set(), []
for items in ledger.values():
    for r in items:
        if r["voucherdesc"] in ("OPENING BALANCE", "CLOSING BALANCE"):
            continue
        key = (r["voucherdate"], r["vouchernumber"], r["narration"], r["debit"], r["credit"])
        if key in seen:
            continue
        seen.add(key)
        rows.append({"date": pd.to_datetime(r["voucherdate"]).strftime("%Y-%m-%d"),
                     "kind": r["voucherdesc"], "debit": float(r["debit"]), "credit": float(r["credit"])})
led = pd.DataFrame(rows)
led["net"] = led["credit"] - led["debit"]
led["flow"] = led.apply(
    lambda r: r["net"] if r["kind"].startswith("Money added") or r["kind"].startswith("Money transferred") else 0.0, axis=1)
OPENING_CASH = 74350.16
cash_by_day = led.groupby("date")["net"].sum().cumsum()
flow_by_day = led.groupby("date")["flow"].sum()
print("ledger cash end (all dates):", round(OPENING_CASH + led["net"].sum(), 2))

days = [d.strftime("%Y-%m-%d") for d in store.trading_days if START <= d.strftime("%Y-%m-%d") <= END]
real, held = [], {}
fills_by_day = {d: g for d, g in fills_df.groupby("date")}
for d in days:
    for _, f in fills_by_day.get(d, pd.DataFrame()).iterrows():
        held[f["symbol"]] = held.get(f["symbol"], 0.0) + (f["shares"] if f["side"] == "BUY" else -f["shares"])
    held = {s: q for s, q in held.items() if abs(q) > 1e-6}
    cash = OPENING_CASH + cash_by_day[cash_by_day.index <= d].iloc[-1]
    px = {}
    for s in held:
        c = store.close_price(s, d)
        px[s] = c
    missing = [s for s, c in px.items() if c is None]
    equity = sum(q * px[s] for s, q in held.items() if px[s] is not None)
    real.append({"date": d, "nav": cash + equity, "cash": cash, "equity": equity,
                 "flow": float(flow_by_day.get(d, 0.0)), "n": len(held),
                 "holdings": dict(held), "missing_price": missing})
json.dump(real, open(f"{OUT}/real_daily.json", "w"))
print("window days:", len(days), "real rows:", len(real))
