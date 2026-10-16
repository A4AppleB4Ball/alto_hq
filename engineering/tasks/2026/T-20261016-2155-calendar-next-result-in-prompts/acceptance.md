# Acceptance: calendar-next-result-in-prompts (draft)

Depends on calendar-next-meeting-asof. The LLM pilot (3 runs) needs the
owner's explicit go; nothing beyond the pilot. Runs go to a sandbox stance
root, never the live `alto_data/stances`.

1. **Render tests.** In `backend/stance/tests/`, the A prompts (first,
   update, annual, event) and the B prompt render the block with a date and
   days away for a company that has one, and the unknown reason for one that
   does not. The D prompt text is byte-identical to base for the same inputs.
2. **Pilot companies chosen from stored state.** Three stance companies with
   a meeting 1..14 days after the pilot as_of (21 / 32 companies had one in
   the next 7 / 14 days on 2026-10-16), listed with their dates before any
   run.
3. **Pilot output.** For each, the stored A and B notes mention the date or
   the result event; a run on a company with no date shows the unknown reason
   in the stored prompt record. QA reads the three notes, not only greps.
4. **Nothing else moved.** Same pilot companies rerun on base: the diff of
   the stance link is the new block's effect only (inputs, chain fields and
   P/E identical).
5. **Point in time.** A run with `--as-of 2026-10-01` on one pilot company
   renders "calendar not captured", never a date.
6. **Suite.** `python -m pytest backend/stance -q` no new failure against base.
