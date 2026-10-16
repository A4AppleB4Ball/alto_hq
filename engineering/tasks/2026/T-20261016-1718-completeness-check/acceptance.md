# Acceptance: completeness-check

Done when each check passes, run by QA, with its output in evidence.md. The
rules are in `org/epics/2026/E-20261015-1140-validation.completeness-design.md`
(approved as D-20261016-1718-completeness-definition). All runs are read-only
on product data: real-data checks read the stores; every other case uses a
temp-dir fixture.

1. **Incident companies fail, naming quarters.** The function over the ten
   companies of I-20261015-1058-stances-without-quarterly-analysis returns
   Missing for each, with the quarters `fleet_scan.py` (in that incident
   folder) reports; ARSSBL Q1_FY27 and Q2_FY27, CHANDAN Q1_FY27.
2. **A complete company passes.** 20MICRONS (Q3_FY26, Q4_FY26, Q1_FY27 all
   analysed): no Missing, no Stale, no violation.
3. **Not initiated.** A company with no chain start (neither FY26 annual nor a
   Q1 FY27 document) returns Not initiated, not complete. A stance for such a
   company is returned as a violation. Temp-dir fixtures for both.
4. **Every state is pinned.** One test per quarter state of the design table
   (Final, Open, Not released, Due with nothing in, Expected, Unknown,
   Missing, Stale), each on a temp-dir fixture, asserting state and reason.
   Open stays Open until a newer quarter holds a document.
5. **Stale and validity.** In a temp-dir copy of ARSSBL's inputs: unchanged
   inputs keep the recorded verdict valid; one touched document reads Stale;
   a new check version reads Stale; a backdated document makes the quarter
   Stale.
6. **Calendar read-only.** `backend/validation/` imports neither
   `raw.results_calendar.reader` nor `capture` (grep). With the calendar store
   older than the refresh window, the check reports a stale-calendar state and
   neither the store file nor any file under the data root changes mtime.
   A company with no meeting on record reports "no meeting on record".
7. **No Dagster.** In the production environment,
   `python -I -c "import sys; sys.path.insert(0, '.'); import backend.validation.completeness"`
   (run from the repo root; `-I` ignores PYTHONPATH and the working
   directory) succeeds and
   `pip freeze` is unchanged.
8. **Label conversion.** Calendar labels (`Q1FY27`) convert to quarter keys
   (`Q1_FY27`) through `backend.lib.quarter_policy`; a test covers every
   quarter label from the cutoff.
9. **Repo checks.** `stores/tests/test_boundaries.py` passes, every entry
   point imports, and the full backend suite shows no new failure against the
   base commit.
