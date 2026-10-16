# Acceptance: calendar-moved-meetings (draft)

Read-only on product data; tests run on a temp copy of the store.

1. **Baseline named.** Before the change the run prints the codes with more
   than one stored meeting (8 on 2026-10-16, from
   `python -m` over `store.read_meetings`) and the 542727 pair.
2. **One answer per company.** After the change, for every one of those 8
   codes and for the six unfiled BSE meetings (from
   `<spike>/date_accuracy/measure_output.txt`), the new next-meeting function
   returns exactly one date or an explicit none, with the reason (moved,
   held, unfiled). 542727 returns one date.
3. **Deterministic and add-only.** Two runs over the same store give the same
   answer; the store file still holds every meeting ever captured (count not
   below 1149; a superseded meeting is marked, never deleted). Test on a temp
   store.
4. **Not wrong-but-green.** A meeting is marked superseded only on the two
   stored facts in the goal (absent from a later listing, no result filed);
   a test shows a meeting merely in the past with no filing yet is not
   marked.
5. **Consumers unchanged where right.** `due.results_meeting_held` and the
   completeness check give the same states as before for every company whose
   meetings are unambiguous: `python -m backend.validation.completeness.cli`
   over 20 stance companies prints identical lines before and after.
6. **Suite.** `python -m pytest backend/raw/results_calendar backend/validation -q`
   shows no new failure against base.
