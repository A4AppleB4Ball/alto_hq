"""Read-only: files, bytes, and files created in the last 7/30 days per store."""
import json, os, sys, time
from pathlib import Path

W = Path("/Users/kmrh581/personal/projects/workspace")
STORES = [
 "news_server/data/1/blob_storage", "news_server/data/screener_data/raw_reports",
 "news_server/data/alto_data/intake", "news_server/data/alto_data/triggers",
 "news_server/data/workflow_outputs/runs", "news_server/data/workflow_outputs/cache",
 "news_server/data/1/screener_announcements", "news_server/data/temp",
 "news_server/data/alto_data/exp_buy_now", "news_server/data/alto_data/benchmark_deepseek",
 "news_server/data/alto_data/stances_price_cadence", "news_server/data/alto_data/stances_v2",
 "news_server/data/alto_data/stances", "news_server/data/1/screener_financials",
 "news_server/data/1/companies_announcements", "news_server/data/1/daily_announcements",
 "news_server/data/1/raw_announcements", "news_server/data/1/stockscan_financials",
 "news_server/data/1/corporate_actions", "news_server/data/1/pipeline_state",
 "news_server/data/1/notes", "news_server/data/1/exchange_attachment_hashes",
 "news_server/data/alto_data/book", "news_server/data/alto_data/workspace",
 "news_server/data/alto_data/execution", "news_server/data/alto_data/orders",
 "news_server/data/alto_data/rebalance", "news_server/data/alto_data/scheduler",
 "news_server/data/alto_data/system", "news_server/data/alto_data/strategy",
 "news_server/data/company_timelines", "news_server/data/results",
 "news_server/data/banks_metrics", "news_server/data/dashboard",
 "news_server/data/screener_data", "news_server/verify_data", "news_server/connectors",
 "alto/logs", "alto/.claude/worktrees", "alto/data",
]
now = time.time(); d7 = now - 7 * 86400; d30 = now - 30 * 86400
out = {}
for rel in STORES:
    root = W / rel
    n = b = n7 = n30 = 0
    for dp, dns, fns in os.walk(root):
        dns[:] = [d for d in dns if d not in (".git", "node_modules")]
        for f in fns:
            try: st = os.lstat(os.path.join(dp, f))
            except OSError: continue
            n += 1; b += st.st_size
            if st.st_birthtime >= d7: n7 += 1
            if st.st_birthtime >= d30: n30 += 1
    out[rel] = {"files": n, "bytes": b, "new_7d": n7, "new_30d": n30}
json.dump(out, open(sys.argv[1], "w"), indent=1)
