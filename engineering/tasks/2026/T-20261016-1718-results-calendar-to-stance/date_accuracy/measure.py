"""Stored meeting date vs the date the results were filed, per exchange. Offline.
    python -I measure.py <inputs dir>
Last ended quarter Q2FY27 (ended 2026-09-30). Meetings: stored, 2026-10-01..2026-10-15
(filings are read through 10-15). BSE actual = Result / Financial Results filing (NEWS_DT date);
NSE actual = 'Outcome of Board Meeting' filing (an_dt date).

Pairing rules (gap = filing date - meeting date), per exchange and code:
  A forward : a meeting pairs with the first filing on or after it and before the code's next meeting.
              Gap >= 0 by construction. Meetings with no such filing are 'unfiled'.
  B backward: a filing pairs with the latest meeting on or before it (the spike's rule). Gap >= 0 by construction.
  C nearest : a filing pairs with the nearest meeting of the code on either side (tie: earlier).
              Gap may be negative; this is the rule that can show a filing BEFORE the stored date.
Headline = A. Effect on gap 0 = share of gap 0 under A, B, C and what each leaves out.
"""
import json, sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

inp = Path(sys.argv[1])
LO, HI = date(2026, 10, 1), date(2026, 10, 15)
cal = json.loads((inp / "results_calendar.json").read_text())["meetings"]
mapping = json.loads((inp / "company_mapping.json").read_text())
stance = set(json.loads((inp / "stance_keys.json").read_text()))
D = lambda s: date.fromisoformat(s[:10])

meet = {"BSE": defaultdict(set), "NSE": defaultdict(set)}
for m in cal:
    d = date.fromisoformat(m["meeting_date"])
    if LO <= d <= HI:
        meet[m["exchange"]][m["code"]].add(d)
fil = {"BSE": defaultdict(set), "NSE": defaultdict(set)}
for r in json.loads((inp / "bse_result_filings.json").read_text()):
    a = r["row"]
    if a["SUBCATNAME"] != "Financial Results":
        raise ValueError(f"unexpected Result subcategory {a['SUBCATNAME']!r}")
    fil["BSE"][str(a["SCRIP_CD"])].add(D(a["NEWS_DT"]))
for r in json.loads((inp / "nse_outcome_filings.json").read_text()):
    a = r["row"]; d = D(a["sort_date"])
    fil["NSE"][a["symbol"].upper()].add(d)

# listing class of a code: both / BSE-only (no NSE listing) / NSE-only (no BSE scrip code)
cls, key_of = {}, {}
for e in mapping:
    key = e["nsecode"].upper(); has_bse = bool(e["bsecode"]); has_nse = key != e["bsecode"]
    c = "both" if has_bse and has_nse else "BSE-only" if has_bse else "NSE-only"
    if has_bse: cls[("BSE", e["bsecode"])] = c; key_of[("BSE", e["bsecode"])] = key
    if has_nse: cls[("NSE", key)] = c; key_of[("NSE", key)] = key

def pair_A(ms, fs):
    ms = sorted(ms); out = []
    for i, m in enumerate(ms):
        nxt = ms[i + 1] if i + 1 < len(ms) else date.max
        f = min((x for x in fs if m <= x < nxt), default=None)
        out.append((m, None if f is None else (f - m).days))
    return out

def pair_B(ms, fs):
    out = []
    for f in sorted(fs):
        m = max((x for x in ms if x <= f), default=None)
        if m is not None: out.append((m, (f - m).days))
    return out

def pair_C(ms, fs):
    out = []
    for f in sorted(fs):
        if ms:
            m = min(ms, key=lambda x: (abs((f - x).days), x))
            out.append((m, (f - m).days))
    return out

def dist(gaps):
    c = Counter(gaps); n = len(gaps)
    return {"n": n, "gap0": c.get(0, 0), "gap0_pct": round(100 * c.get(0, 0) / n, 1) if n else None,
            "by_gap": dict(sorted(c.items()))}

report = {}
for ex in ("BSE", "NSE"):
    res = {"A": defaultdict(list), "B": defaultdict(list), "C": defaultdict(list)}
    unfiled = defaultdict(list); filing_no_meeting = defaultdict(list); stance_gaps = []
    codes = set(meet[ex]) | set(fil[ex])
    for code in sorted(codes):
        ms, fs = meet[ex].get(code, set()), fil[ex].get(code, set())
        k = cls.get((ex, code), "unmapped")
        for m, g in pair_A(ms, fs):
            if g is None: unfiled[k].append(code)
            else:
                res["A"][k].append(g)
                if key_of.get((ex, code)) in stance: stance_gaps.append(g)
        if fs and not ms: filing_no_meeting[k].append(code)
        for _, g in pair_B(ms, fs): res["B"][k].append(g)
        for _, g in pair_C(ms, fs): res["C"][k].append(g)
    rep = {}
    for rule in "ABC":
        allg = [g for v in res[rule].values() for g in v]
        rep[rule] = {"all": dist(allg), **{k: dist(v) for k, v in sorted(res[rule].items())}}
    rep["A_stance_subset"] = dist(stance_gaps)
    rep["meetings_in_window_unfiled(A)"] = {k: len(v) for k, v in unfiled.items()}
    rep["filing_codes_without_meeting_in_window"] = {k: len(v) for k, v in filing_no_meeting.items()}
    rep["meeting_codes_in_window"] = len(meet[ex])
    report[ex] = rep
print(json.dumps(report, indent=1, default=str))
