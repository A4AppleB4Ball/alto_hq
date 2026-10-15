import json, sys
from pathlib import Path
from backend.config.paths import STANCES_DIR, DATA_ROOT
from backend.lib.data_access import DataAccess
from backend.lib.quarter_policy import quarter_sort_key
from backend.lib.quarter_versions import chain_quarters

da = DataAccess()
prop = json.load(open(DATA_ROOT / "workspace/scienceamit1/rebalance/proposals/2026-10-15T10-17-21.json"))
targets = {t["symbol"]: t["target_weight"] for t in prop["model_targets"] if t["target_weight"] > 0}
diff = {d["symbol"]: d["action"] for d in prop["diff"]}
held = {h["symbol"] for h in prop["current_snapshot"]["holdings"]}
rows, errors = [], []
syms = sorted(p.name for p in STANCES_DIR.iterdir() if (p / "latest.json").exists())
for s in syms:
    try:
        enum = da.quarter_versions(s)
        if not enum:
            continue
        chain = da.chain_start(s, enum)
        cq = chain_quarters(enum, chain)
        latest_doc_q = max(enum, key=quarter_sort_key)
        latest_chain_q = max(cq, key=quarter_sort_key) if cq else None
        stored = da.list_quarterly_versions(s)
        valid = [v for v in stored if v["valid"]]
        latest_an = max((v["quarter_key"] for v in valid), key=quarter_sort_key) if valid else None
        latest = json.load(open(STANCES_DIR / s / "latest.json"))
        if latest_chain_q and (latest_an is None or quarter_sort_key(latest_an) < quarter_sort_key(latest_chain_q)):
            first_vd = min(v.version_date for v in enum[latest_chain_q])
            rows.append((s, latest_doc_q, latest_chain_q, first_vd, latest_an, len(stored) - len(valid),
                         latest["as_of"], latest["d_stance"], latest["chain"].get("quarterly_analysis_key"),
                         targets.get(s), diff.get(s), s in held))
    except Exception as e:
        errors.append((s, type(e).__name__, str(e)[:150]))
print("stance symbols:", len(syms), "missing:", len(rows), "errors:", len(errors))
for r in rows: print("ROW", r)
for e in errors: print("ERR", e)
