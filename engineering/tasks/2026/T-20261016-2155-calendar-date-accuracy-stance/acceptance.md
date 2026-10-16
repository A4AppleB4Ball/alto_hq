# Acceptance: calendar-date-accuracy-stance (draft)

Read-only on product data. Output is a findings file in this task folder.
Product code is run with `python -m` from the alto root; a scratch script
kept in this folder runs with `python -I` over copied inputs.

1. **Population exists.** Count stance companies (non-empty
   `alto_data/stances/<S>/log.jsonl`, 484 on 2026-10-16) that hold a Q2_FY27
   `concall_transcript` or `quarterly_pdf` with a `publish_date` in
   `1/screener_announcements/<S>_index.json`. The number is at least 50. If it
   is lower, the task stays waiting and nothing below is claimed (on 2026-10-16
   it was 1).
2. **Gap table.** For those companies, stored meeting date (from
   `backend.raw.results_calendar.store.read_meetings`, resolved by
   `lookup.company_listings`) against index `publish_date`, with rule A
   (first filing on or after the meeting, before the next meeting) as the
   headline. The table shows n, gap 0 / 1 / 2-5 / >5 days, and every company
   with gap above 0 or no meeting on record, by name.
3. **Comparable to the spike.** The same market-wide measure is rerun with
   `python -I <spike>/date_accuracy/measure.py <spike>/date_accuracy/inputs`
   (spike = `alto_hq/engineering/tasks/2026/T-20261016-1718-results-calendar-to-stance`)
   and its gap-0 shares (BSE 98.9%, NSE 98.1%) are quoted beside the stance
   figure.
4. **Concall lag.** For the same companies, the gap between the results
   document and the concall document, so the calendar date is shown to be the
   result date, not the concall date.
5. **Read-only.** `find /Users/kmrh581/personal/projects/workspace/news_server/data -newer <marker> -type f`
   is empty after the run; `git status` in alto is clean.
