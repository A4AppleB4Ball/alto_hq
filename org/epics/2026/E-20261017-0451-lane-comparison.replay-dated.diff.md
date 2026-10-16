--- /Users/kmrh581/personal/projects/workspace/alto/backend/backtest/replay.py	2026-10-10 20:21:47
+++ /tmp/spike/replay_dated.py	2026-10-17 03:55:09
@@ -40,6 +40,9 @@
 logger = logging.getLogger("backtest.replay")
 
 _AUTO_REVIEWER = AutoReviewer()
+DATED_FLOWS: dict = {}
+TARGET_LOG: dict = {}
+SIGNAL_LOG: dict = {}
 
 
 @dataclass
@@ -400,6 +403,7 @@
 
     for day_index, date in enumerate(trading_dates):
         day_prices = _close_prices(store, set(positions) | set(signal_states), date)
+        cash += DATED_FLOWS.get(date, 0.0)
 
         if (day_index + 1) % 50 == 0:
             elapsed = time.time() - t_replay_start
@@ -489,6 +493,8 @@
                 _rankable(signal_states, positions, universe, date), positions, cash, day_prices, date, cfg,
                 trading_dates, preference_ranks, decided_signal_dates,
             )
+            TARGET_LOG[date] = {t.symbol: {"w": t.target_weight, "base": t.base_weight, "rank": t.rank, "reason": t.reason} for t in signal_targets}
+            SIGNAL_LOG[date] = {sym: {"stance": st.stance, "conviction": st.conviction, "dir": st.thesis_direction, "signal_date": sd} for sym, st in signal_states.items() for sd in [decided_signal_dates.get(sym)]}
             if universe is not None:
                 universe.update_kept(signal_states, day_prices, date, cfg, preference_ranks)
 
@@ -509,9 +515,7 @@
                 pos.trough_since_last_sell = min(pos.trough_since_last_sell, float(candles["low"].min()))
 
         # --- (4) Monthly contribution ---
-        contribution = cfg.monthly_contribution if date in month_ends else 0.0
-        if contribution:
-            cash += contribution
+        contribution = DATED_FLOWS.get(date, 0.0)
 
         # --- (5) EOD snapshot ---
         eod_prices = {}
