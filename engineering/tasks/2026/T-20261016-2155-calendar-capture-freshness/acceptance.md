# Acceptance: calendar-capture-freshness (draft)

Temp store and temp stance root only; no network.

1. **Raises when stale.** With a temp store whose `last_captured_at` is 21
   hours before `now`, the stance entry point raises a named error carrying
   the age, before any classifier or agent call (a test counts LLM-client
   calls: zero).
2. **Passes when fresh.** At 19 hours the run proceeds. The limit is the one
   constant `REFRESH_HOURS` in `backend/raw/results_calendar/reader.py`;
   grep shows no second copy of 20.
3. **Never captured raises.** An absent store raises, not skips.
4. **Live store today.** From the alto root,
   `python -c "from backend.raw.results_calendar.store import last_captured_at; print(last_captured_at())"`
   prints the live capture time (2026-10-16 03:42 IST on 2026-10-16); the
   task records the age and whether the guard would have passed.
5. **Shares the policy with completeness.** The completeness check's
   `calendar_stale` and this guard give the same verdict for the same age
   (one test sweeps 0..30 hours).
6. **Suite.** `python -m pytest backend/stance backend/raw/results_calendar -q`
   no new failure against base.
