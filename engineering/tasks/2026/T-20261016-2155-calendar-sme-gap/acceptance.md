# Acceptance: calendar-sme-gap (draft)

One network read (NSE `index=sme`, the same endpoint capture uses, through
`backend/raw/results_calendar/fetch.py`; no curl). It writes only into a temp
dir. Owner approves the read.

1. **Population fixed first.** The 68 stance companies that are NSE-listed
   and not in the NSE EQ bhavcopy (spike section 1) are listed in the output
   with how each was identified.
2. **Pull is raw and saved.** The unfiltered `sme` response for the window
   (day after 2026-09-30 to 90 days ahead) is saved in a temp dir with its row
   count and fetch time; no row is dropped before counting.
3. **The number.** Of the 68, how many have an NSE row in that response whose
   purpose mentions results in any form, against how many have a stored
   meeting (`read_meetings`, 2 on 2026-10-16). Every company in the first set
   and not the second is named with its raw NSE purpose text, so the owner can
   judge whether the purposes are results meetings. No keyword rule decides.
4. **Read-only.** No file under `news_server/data` is newer than a marker
   taken before the run; the saved response is outside it.
