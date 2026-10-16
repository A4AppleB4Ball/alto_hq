# Acceptance: calendar-next-meeting-asof (draft)

Depends on calendar-moved-meetings (the rule for a moved meeting). Read-only
on product data.

1. **Cases pinned by tests** in `backend/lib/tests/`: as_of before the first
   capture, a future meeting, a held meeting (as_of after it), a moved meeting
   (two stored dates, one superseded), no meeting on record, a meeting
   captured after `as_of` (not knowable).
2. **The spike's anchor.** `as_of` 2026-10-01 returns "calendar not captured"
   for every one of the 484 stance companies; a loop over them prints the
   reason counts.
3. **Today's coverage.** At as_of 2026-10-16 the method returns a date for
   the companies the spike counted (48 with a future meeting, `captured_at`
   permitting) and an explicit reason for the rest (422 had none); the printed
   counts are within the spike's numbers, with each difference explained.
4. **No network, no write.** A test patches the fetch layer to raise and the
   method still answers; the store file hash is unchanged by calls.
5. **Typed, not a string.** The result is a typed record with a reason enum;
   a test fails if a caller can read a date from an unknown result.
6. **Suite.** `python -m pytest backend/lib backend/raw/results_calendar -q`
   shows no new failure against base; `python -m pytest backend/stores/tests/test_boundaries.py -q` passes.
