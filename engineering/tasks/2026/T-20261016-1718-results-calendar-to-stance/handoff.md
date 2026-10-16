# Handoff: results-calendar-to-stance (spike)

Branch eng/T-20261016-1718-results-calendar-to-stance, base a5b5606, no commits (no code changed).
Acceptance (spike): `findings.md` in this folder, items 1-5. acceptance.md sha256 verified
9a909012... at start. Read-only throughout; no capture, no network, no LLM.

Item 2 is only partly met: the 50-company stance sample does not exist in stored data (1 stance
company has Q2FY27 docs; Q1FY27 meetings were never captured). Measured market-wide instead
(95 BSE scrips, gap 0 in 94, 1 in 1) and said so. Owner to judge whether that satisfies item 2;
follow-up 1 closes it.

Found: `backend/raw/results_calendar/store.py` keeps no NSE index or purpose, so SME meetings
cannot be told apart or counted from the store.
Friction: task.md claimed_by kept as the caller's run id with mine appended; not cleared.
