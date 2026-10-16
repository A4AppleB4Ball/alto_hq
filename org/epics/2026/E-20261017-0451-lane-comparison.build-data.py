"""Throwaway: build the dashboard dataset (real Dhan account vs production replay) from the spike outputs."""
import hashlib
import json
import math
import subprocess
from collections import defaultdict

import pandas as pd
from scipy.optimize import brentq

from backend.backtest.cohort import select_symbols
from backend.backtest.signal_loader import load_signals_from_store
from backend.price_feed.dhan_daily_store import DhanDailyPriceStore
from backend.trading.config import PRESETS

O = "/tmp/spike"
START, END = "2026-09-15", "2026-10-16"
BOOK = "/Users/kmrh581/personal/projects/workspace/news_server/data/alto_data/workspace/scienceamit1/book/default"

real_daily = json.load(open(f"{O}/real_daily.json"))
snaps = json.load(open(f"{O}/replay_snaps.json"))
rtrades = json.load(open(f"{O}/replay_trades.json"))
fills = [json.loads(l) for l in open(f"{BOOK}/fills.jsonl")]
ledger = json.load(open(f"{O}/ledger.json"))

days = [r["date"] for r in real_daily]
signals = select_symbols(load_signals_from_store(None, restrict_to_watchlist=False), None)
stamp_hash = hashlib.sha1(signals.to_csv(index=False).encode()).hexdigest()[:10]
commit = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], text=True).strip()

syms = sorted({f["symbol"] for f in fills} | {t["symbol"] for t in rtrades})
store = DhanDailyPriceStore(user_id="scienceamit1", symbols=syms, index_symbols=[PRESETS["v2"].benchmark_index],
                            start=START, end=END, force_refresh=False, candle_interval_minutes=15)
close = {s: {d: store.close_price(s, d) for d in days} for s in syms}
openp = {s: {d: store.open_price(s, d) for d in days} for s in syms}

# ---- ledger flows (dated to the next trading day) and friction
seen, rows = set(), []
for items in ledger.values():
    for r in items:
        if r["voucherdesc"] in ("OPENING BALANCE", "CLOSING BALANCE"):
            continue
        k = (r["voucherdate"], r["vouchernumber"], r["narration"], r["debit"], r["credit"])
        if k in seen:
            continue
        seen.add(k)
        rows.append({"date": pd.to_datetime(r["voucherdate"]).strftime("%Y-%m-%d"), "kind": r["voucherdesc"],
                     "net": float(r["credit"]) - float(r["debit"])})
led = pd.DataFrame(rows)
flow_cal = {}
for _, r in led.iterrows():
    if r["kind"].startswith(("Money added", "Money transferred")):
        flow_cal[r["date"]] = flow_cal.get(r["date"], 0) + r["net"]
flow_day = {d: 0.0 for d in days}
for d, v in flow_cal.items():
    nxt = [x for x in days if x >= d]
    if nxt and d >= days[0]:
        flow_day[nxt[0]] += v
dp_charges = -led[led["kind"].str.startswith("Charges")]["net"].sum()
trade_net_ledger = led[led["kind"].str.startswith("Trades")].groupby("date")["net"].sum().to_dict()

# ---- holdings (shares at end of day) per lane
def holdings_series(events):  # events: list of (date, symbol, signed_shares)
    by_day = defaultdict(list)
    for d, s, q in events:
        by_day[d].append((s, q))
    held, out = {}, {}
    for d in days:
        for s, q in by_day.get(d, []):
            held[s] = held.get(s, 0.0) + q
        held = {s: q for s, q in held.items() if abs(q) > 1e-6}
        out[d] = dict(held)
    return out

real_h = holdings_series([(f["traded_at"][:10], f["symbol"], f["shares"] if f["side"] == "BUY" else -f["shares"]) for f in fills
                          if f["traded_at"][:10] in days])
rep_h = holdings_series([(t["date"], t["symbol"], t["shares"] if t["action"] == "BUY" else -t["shares"]) for t in rtrades])

real_nav = {r["date"]: r["nav"] for r in real_daily}
real_cash = {r["date"]: r["cash"] for r in real_daily}
rep_nav = {s["date"]: s["portfolio_value"] for s in snaps}
rep_cash = {s["date"]: s["cash"] for s in snaps}
rep_flow = {s["date"]: s["contribution"] for s in snaps}


def lane(nav, cash, flow, held):
    out = []
    for i, d in enumerate(days):
        eq = nav[d] - cash[d]
        ret = 0.0 if i == 0 else (nav[d] - flow[d]) / nav[days[i - 1]] - 1
        w = {s: q * close[s][d] / nav[d] for s, q in held[d].items() if close[s][d]}
        # contribution of each name held at the previous close to today's account return
        contrib, book_ret = {}, 0.0
        if i > 0:
            p = days[i - 1]
            eq_prev = sum(q * close[s][p] for s, q in held[p].items())
            for s, q in held[p].items():
                c = q * (close[s][d] - close[s][p])
                contrib[s] = c / nav[p]
            book_ret = sum(contrib.values()) * nav[p] / eq_prev if eq_prev else 0.0
        out.append({"date": d, "nav": nav[d], "cash": cash[d], "equity": eq, "invested": eq / nav[d], "flow": flow[d],
                    "ret": ret, "n": len(held[d]), "w": w, "contrib": contrib, "book_ret": book_ret})
    cum = 1.0
    for r in out:
        cum *= 1 + r["ret"]
        r["cum"] = cum - 1
    peak, dd = 1.0, 0.0
    for r in out:
        g = 1 + r["cum"]
        peak = max(peak, g)
        r["dd"] = g / peak - 1
    return out

L_real = lane(real_nav, real_cash, flow_day, real_h)
L_rep = lane(rep_nav, rep_cash, rep_flow, rep_h)

# ---- gap attribution in rupees (exact): NAV gap = start difference + exposure + selection + trading/fees
attr = []
for i in range(1, len(days)):
    a, b = L_real[i], L_rep[i]; pa, pb = L_real[i - 1], L_rep[i - 1]
    pl_a = a["nav"] - a["flow"] - pa["nav"]; pl_b = b["nav"] - b["flow"] - pb["nav"]
    book_a = sum(a["contrib"].values()) * pa["nav"]; book_b = sum(b["contrib"].values()) * pb["nav"]
    rb_a = book_a / pa["equity"] if pa["equity"] else 0.0; rb_b = book_b / pb["equity"] if pb["equity"] else 0.0
    expo = (pa["equity"] - pb["equity"]) * rb_b
    sel = pa["equity"] * (rb_a - rb_b)
    trade = (pl_a - book_a) - (pl_b - book_b)
    attr.append({"date": days[i], "gap": pl_a - pl_b, "exposure": expo, "selection": sel, "execution": trade,
                 "gap_pp": a["ret"] - b["ret"]})
nav_gap = {"start": L_real[0]["nav"] - L_rep[0]["nav"], "exposure": sum(x["exposure"] for x in attr), "selection": sum(x["selection"] for x in attr),
           "execution": sum(x["execution"] for x in attr), "total": L_real[-1]["nav"] - L_rep[-1]["nav"]}
nav_gap["check"] = nav_gap["start"] + nav_gap["exposure"] + nav_gap["selection"] + nav_gap["execution"] - nav_gap["total"]
gap_cum = L_real[-1]["cum"] - L_rep[-1]["cum"]
sum_daily = sum(x["gap_pp"] for x in attr)

# ---- metrics
def xirr(cfs):
    t0 = cfs[0][0]
    f = lambda r: sum(c / ((1 + r) ** ((t - t0).days / 365)) for t, c in cfs)
    return brentq(f, -0.99, 1e6)

T = pd.Timestamp
real_cf = [(T(days[0]), -real_nav[days[0]])] + [(T(d), -v) for d, v in flow_cal.items() if d >= days[0]] + [(T(days[-1]), real_nav[days[-1]])]
rep_cf = [(T(days[0]), -rep_nav[days[0]])] + [(T(d), -c) for d, c in rep_flow.items() if c] + [(T(days[-1]), rep_nav[days[-1]])]

def metrics(L, cf, trades_notional, friction):
    r = pd.Series([x["ret"] for x in L[1:]])
    n = len(r)
    sd = r.std()
    sr_d = r.mean() / sd
    se_ann = math.sqrt((1 + 0.5 * sr_d ** 2) / n) * math.sqrt(252)
    down = r[r < 0]
    sortino = r.mean() / math.sqrt((down ** 2).sum() / n) * math.sqrt(252) if len(down) else None
    best = max(L[1:], key=lambda x: x["ret"]); worst = min(L[1:], key=lambda x: x["ret"])
    mdd = min(L, key=lambda x: x["dd"])
    avg_nav = sum(x["nav"] for x in L) / len(L)
    return {"cum": L[-1]["cum"], "xirr": xirr(cf), "sharpe": sr_d * math.sqrt(252), "sharpe_se": se_ann,
            "sortino": sortino, "vol": sd * math.sqrt(252), "mdd": mdd["dd"], "mdd_date": mdd["date"],
            "hit": float((r > 0).mean()), "best": best["ret"], "best_date": best["date"],
            "worst": worst["ret"], "worst_date": worst["date"],
            "avg_invested": sum(x["invested"] for x in L) / len(L), "avg_n": sum(x["n"] for x in L) / len(L),
            "turnover": trades_notional / avg_nav, "friction": friction, "nav_end": L[-1]["nav"], "n_days": n}

real_notional = sum(f["shares"] * f["price"] for f in fills if f["traded_at"][:10] in days)
fills_net = defaultdict(float)
for f in fills:
    d = f["traded_at"][:10]
    fills_net[d] += f["shares"] * f["price"] * (1 if f["side"] == "SELL" else -1)
# a trade-day row in the ledger posts on the trade date; compare cash effect to gross fills
trade_friction = sum(fills_net[d] - trade_net_ledger.get(d, 0.0) for d in fills_net if d in days)
real_friction = trade_friction + dp_charges
rep_friction = sum(t["cost"] + t["slippage"] for t in rtrades)
rep_notional = sum(t["notional"] for t in rtrades)
M_real = metrics(L_real, real_cf, real_notional, real_friction)
money_in_real = real_nav[days[0]] + sum(flow_day.values())
money_in_rep = rep_nav[days[0]] + sum(rep_flow.values())
M_real["money_in"] = money_in_real; M_real["gain"] = real_nav[days[-1]] - money_in_real
M_rep = metrics(L_rep, rep_cf, rep_notional, rep_friction)
M_rep["money_in"] = money_in_rep; M_rep["gain"] = rep_nav[days[-1]] - money_in_rep

dr = pd.Series([a["ret"] - b["ret"] for a, b in zip(L_real[1:], L_rep[1:])])
corr = pd.Series([x["ret"] for x in L_real[1:]]).corr(pd.Series([x["ret"] for x in L_rep[1:]]))
track = {"te": dr.std() * math.sqrt(252), "mean_gap": dr.mean(), "t_stat": dr.mean() / (dr.std() / math.sqrt(len(dr))),
         "corr": corr, "days_real_beat": int((dr > 0).sum()), "n": len(dr), "gap_cum": gap_cum, "sum_daily": sum_daily,
         "compounding": gap_cum - sum_daily}

# ---- overlap per day
overlap = []
for a, b in zip(L_real, L_rep):
    wa, wb = a["w"], b["w"]
    names = set(wa) | set(wb)
    overlap.append({"date": a["date"], "weight_overlap": sum(min(wa.get(s, 0), wb.get(s, 0)) for s in names),
                    "both": len(set(wa) & set(wb)), "real_only": len(set(wa) - set(wb)), "rep_only": len(set(wb) - set(wa))})

# ---- name contributions
names = defaultdict(lambda: {"real": 0.0, "rep": 0.0, "days_real": 0, "days_rep": 0, "w_real": 0.0, "w_rep": 0.0})
for a, b in zip(L_real, L_rep):
    for s, c in a["contrib"].items(): names[s]["real"] += c * L_real[days.index(a["date"]) - 1]["nav"]
    for s, c in b["contrib"].items(): names[s]["rep"] += c * L_rep[days.index(b["date"]) - 1]["nav"]
    for s, w in a["w"].items(): names[s]["days_real"] += 1; names[s]["w_real"] += w
    for s, w in b["w"].items(): names[s]["days_rep"] += 1; names[s]["w_rep"] += w
name_rows = []
for s, v in names.items():
    name_rows.append({"symbol": s, "real": v["real"], "rep": v["rep"], "days_real": v["days_real"], "days_rep": v["days_rep"],
                      "avg_w_real": v["w_real"] / len(days), "avg_w_rep": v["w_rep"] / len(days), "diff": v["real"] - v["rep"]})
name_rows.sort(key=lambda r: -abs(r["diff"]))

# ---- execution quality of real fills vs the day's open
bucket_edges = [("before 10:00", "10:00"), ("10:00-12:00", "12:00"), ("12:00-14:00", "14:00"), ("after 14:00", "99")]
exec_rows, exec_bucket = [], defaultdict(float)
for f in fills:
    d = f["traded_at"][:10]
    if d not in days or not openp.get(f["symbol"], {}).get(d):
        continue
    o = openp[f["symbol"]][d]
    adverse = ((f["price"] - o) if f["side"] == "BUY" else (o - f["price"])) / o * 1e4
    exec_rows.append({"date": d, "symbol": f["symbol"], "side": f["side"], "notional": f["shares"] * f["price"], "bps": adverse,
                      "time": f["traded_at"][11:16]})
    hh = f["traded_at"][11:16]
    for name, edge in bucket_edges:
        if hh < edge:
            exec_bucket[name] += f["shares"] * f["price"]
            break
ex = pd.DataFrame(exec_rows)
wavg = lambda g: float((g.bps * g.notional).sum() / g.notional.sum())
execq = {"n": len(ex), "wavg_bps": wavg(ex), "wavg_buy": wavg(ex[ex.side == "BUY"]), "wavg_sell": wavg(ex[ex.side == "SELL"]),
         "median_bps": float(ex.bps.median()), "p90_abs": float(ex.bps.abs().quantile(0.9)),
         "buckets": {k: exec_bucket.get(k, 0.0) / ex.notional.sum() for k, _ in bucket_edges},
         "assumed_bps": 10.0, "worst": ex.reindex(ex.bps.abs().sort_values(ascending=False).index).head(6).to_dict("records")}

# ---- stance events
sg = signals[(signals["as_of"] >= T(START)) & (signals["as_of"] <= T(END))].copy()
sg["date"] = sg["as_of"].dt.strftime("%Y-%m-%d")
ev = []
for _, r in sg.iterrows():
    changed = r["prev_stance"] is not None and r["prev_stance"] == r["prev_stance"] and r["prev_stance"] != r["d_stance"]
    ev.append({"date": r["date"], "symbol": r["symbol"], "prev": r["prev_stance"] if changed or r["prev_stance"] == r["prev_stance"] else None,
               "stance": r["d_stance"], "conviction": r["d_conviction"], "dir": r["a_thesis_direction"], "changed": bool(changed)})
stance_day = defaultdict(lambda: {"links": 0, "changed": 0})
for e in ev:
    stance_day[e["date"]]["links"] += 1
    stance_day[e["date"]]["changed"] += int(e["changed"])

# ---- per-day trade detail
real_by_day = defaultdict(lambda: defaultdict(lambda: {"shares": 0.0, "notional": 0.0, "first": "99", "last": "00"}))
for f in fills:
    d = f["traded_at"][:10]
    if d not in days:
        continue
    k = (f["symbol"], f["side"])
    g = real_by_day[d][k]
    g["shares"] += f["shares"]; g["notional"] += f["shares"] * f["price"]
    g["first"] = min(g["first"], f["traded_at"][11:16]); g["last"] = max(g["last"], f["traded_at"][11:16])
trade_detail = {}
for d in days:
    rl = [{"symbol": s, "side": sd, "shares": g["shares"], "px": g["notional"] / g["shares"], "notional": g["notional"],
           "time": g["first"] if g["first"] == g["last"] else f"{g['first']}-{g['last']}"} for (s, sd), g in real_by_day[d].items()]
    rp = [{"symbol": t["symbol"], "side": t["action"], "shares": t["shares"], "px": t["fill_price"], "notional": t["notional"],
           "reason": t["reason"]} for t in rtrades if t["date"] == d]
    trade_detail[d] = {"real": sorted(rl, key=lambda x: -x["notional"]), "rep": sorted(rp, key=lambda x: -x["notional"])}

# ---- production intended book (desired_snapshots) and replay targets, per day
import os
snapdir = f"{BOOK}/desired_snapshots"
snapfiles = sorted(os.listdir(snapdir))
prod_by_day = {}
for fn in snapfiles:
    d = fn.split("_")[1][:10]
    prod_by_day[d] = fn  # last file of a day wins (sorted)
rep_targets = json.load(open(f"{O}/replay_targets.json")); rep_sig = json.load(open(f"{O}/replay_signals.json"))
trace = {}
last_prod = None
for d in days:
    if d in prod_by_day:
        last_prod = json.load(open(f"{snapdir}/{prod_by_day[d]}"))
    prod = last_prod if (last_prod is not None and any(k <= d for k in prod_by_day)) else None
    rows = []
    syms_d = set(L_real[days.index(d)]["w"]) | set(L_rep[days.index(d)]["w"]) | set(rep_targets.get(d, {}))
    if prod is not None:
        syms_d |= {k for k, v in prod.items() if v.get("target_weight", 0) > 0}
    for sy in syms_d:
        p = prod.get(sy) if prod is not None else None
        rt = rep_targets.get(d, {}).get(sy)
        sg_ = rep_sig.get(d, {}).get(sy) or {}
        rows.append({"symbol": sy, "real_w": L_real[days.index(d)]["w"].get(sy, 0.0), "rep_w": L_rep[days.index(d)]["w"].get(sy, 0.0),
                     "rep_target": rt["w"] if rt else None, "rep_reason": rt["reason"] if rt else None, "rep_rank": rt["rank"] if rt else None,
                     "prod_target": p["target_weight"] if p else None, "prod_reason": p["reason"] if p else None,
                     "stance": (p or {}).get("signal", {}).get("stance") or sg_.get("stance"),
                     "conviction": (p or {}).get("signal", {}).get("conviction") or sg_.get("conviction"),
                     "dir": (p or {}).get("signal", {}).get("thesis_direction") or sg_.get("dir"),
                     "signal_date": (p or {}).get("signal", {}).get("signal_date") or sg_.get("signal_date")})
    trace[d] = {"has_prod": prod is not None, "prod_file": prod_by_day.get(d), "rows": rows}

cur = json.load(open("/Users/kmrh581/personal/projects/workspace/news_server/data/alto_data/workspace/scienceamit1/rebalance/current.json"))
pcf = [(T(cur["performance_start_date"]), -cur["performance_start_value"])]
pcf += [(T(f["date"]), -f["amount"]) for f in cur["capital_flows"] if f["date"] > cur["performance_start_date"]]
pcf += [(T("2026-10-17"), 1020500.12)]
M_real["xirr_page"] = xirr(sorted(pcf))
out = {
    "nav_gap": nav_gap, "trace": trace, "days": days, "real": L_real, "rep": L_rep, "attr": attr, "metrics": {"real": M_real, "rep": M_rep}, "track": track,
    "overlap": overlap, "names": name_rows[:40], "execq": execq, "stance_day": stance_day, "stance_events": ev,
    "trades": trade_detail, "deposits": {d: v for d, v in flow_cal.items() if d >= days[0]},
    "stamp": {"commit": commit, "stance_hash": stamp_hash, "signals": len(signals), "preset": "v2", "slippage_bps": 10.0,
              "fills": len([f for f in fills if f["traded_at"][:10] in days]), "ledger_cash_check": 126863.02, "funds_api_cash": 126932.95,
              "dp_charges": dp_charges, "trade_friction": trade_friction},
}
json.dump(out, open(f"{O}/dash_data.json", "w"), default=float)
print("ok", len(days), "days; keys", list(out))
print("real", {k: (round(v, 4) if isinstance(v, float) else v) for k, v in M_real.items()})
print("rep ", {k: (round(v, 4) if isinstance(v, float) else v) for k, v in M_rep.items()})
print("track", {k: round(v, 4) for k, v in track.items()})
print("attr sums", {k: round(sum(a[k] for a in attr) * 100, 2) for k in ("gap", "exposure", "selection", "execution")})
print("exec", {k: v for k, v in execq.items() if k not in ("worst",)})
print("top names", [(r["symbol"], round(r["real"] * 100, 2), round(r["rep"] * 100, 2)) for r in name_rows[:6]])
