# Handoff: T-20261016-1928-scenario-selection (round 1)

Branch `eng/T-20261016-1928-scenario-selection`, worktree
`alto/.claude/worktrees/T-20261016-1928-scenario-selection`.
Base `79e66a7`; commit `d8d3275` (Validation: per-class scenario selection queries over stored state).
Code: `backend/validation/scenarios/selection/` plus an **empty**
`backend/validation/scenarios/__init__.py`. Merge note: the scenario-contract
task creates the real `scenarios/__init__.py`; keep theirs, drop mine.
Cohort item NOT created (owner picks).

Command (from the worktree): `PYTHONPATH=. python -m backend.validation.scenarios.selection --as-of 2026-10-15 --out $TMPDIR/selN.json`
(`--out` is required and must not exist). Output: `$TMPDIR/sel3.json` / `sel4.json`.
Printed: `fleet 1206, counts {'FC01': 225, 'FC02': 571, 'FC03': 6, 'FC08': 10, 'FC09': 232, 'FC10': 377}, errors 12`.

## Acceptance

1. ARSSBL in FC02 (Q1_FY27, Q2_FY27 `missing`, file `.../screener_announcements/ARSSBL_index.json`) and FC08
   (`stances/ARSSBL/log.jsonl`: "documents up to 2026-07-15 but no analysis; 9 stance links since its first version 2026-07-14, latest 2026-10-13 with quarterly_analysis_key None").
   CHANDAN in FC03 (`intake/companies/CHANDAN/failed/stockscans_chandan_concall_ppt_jun2026ppt.json`, failed:extraction, "LLM could not determine the reporting period from this document's content").
   FC08 lists exactly the ten incident companies. FC03: ALMONDZ BHADORA CHANDAN LOKESHMACH PNGSREVA TAC. Hand re-derivation is QA's.
2. FC01: 225 candidates, all `complete`; 9 BSE-only. **Interpretation for QA/owner:** "every quarter in the window analysed" is
   implemented as every quarter holding documents is `final`/`open`; the remaining quarter (Q2_FY27, filed by nobody yet at 10-15) is
   `unknown`/`expected`, which `complete` already guarantees is non-blocking. Taken literally (all quarters final/open) FC01 is empty
   for every company at this as-of. Also required: FY26 annual stored with `filed_at`, stance log continuous (prior_as_of chain), no intake failed record.
3. FC10: 377, each `not_initiated` from `check.evaluate`.
4. `tests/test_no_outcome_inputs.py`: AST over the package forbids backtest/book/pnl/returns/trading/executor/rebalance/price_context imports and BOOK_DIR/RANKING_PATH/REBALANCE_DIR/... names. Passes.
5. sel3 vs sel4: `cmp` identical. Records `alto_commit` d8d3275..., `news_server_commit` 1cd5641a..., `as_of`, `now` (as-of 23:59 IST), completeness check id/version.
   (sel1 vs sel2 before the commit also identical; sel1 vs sel3 differ only in `alto_commit`.)
6. `find -L ../news_server/data -newer marker -type f`: **empty** for the run-3 window. In two other windows it listed
   `alto_data/workspace/scienceamit1/book/default/snapshots.jsonl`, `dashboard/chat/*.duckdb`, `screener_data/raw_reports/stocks/HDFCBANK/html/...` -
   written by the live API/scraper (book snapshot mtime 20:13:13, after my run ended 20:13:11; code imports none of those stores). QA should run it at a quiet moment or confirm the writer.
   Suite: base 66 failed / new 66 failed (1458 passed), `comm -23 new base` empty. (A first parallel base+new run showed `test_partitioned_storage` flaky; passes alone on both.) `stores/tests/test_boundaries.py` passes. Entry points import.

Targeted: `pytest backend/validation` 38 passed.

## Candidate table (owner picks 3-5, at least one BSE-only healthy)

| Symbol | Name | Classes | Quarters | Notes |
|---|---|---|---|---|
| ARSSBL | Anand Rathi Shar | FC02, FC08, FC09 | Q1/Q2 FY27 missing | incident case |
| CHANDAN | | FC02, FC03, FC08 | Q1 FY27 missing | incident case |
| TAC | | FC02, FC03, FC08 | Q1 FY27 missing | alternative FC03 |
| PNGSREVA | | FC02, FC03, FC08, FC09 | Q1 FY27 missing | covers 4 real classes |
| 504028 | GEE | FC01, FC09 | Q3,Q4 FY26 final; Q1 FY27 open | BSE-only, 27 links to 10-05, annual 08-13 |
| 538546 | Bansal Roofing | FC01, FC09 | same | BSE-only, 25 links, annual 08-20 |
| 538715 | Dhabriya Poly. | FC01, FC09 | same | BSE-only, 29 links, annual 09-08 |
| 540956 | Bhatia Communic. | FC01, FC09 | same | BSE-only, 24 links, annual 07-01 |
| 544248 | Mach Conferences | FC01, FC09 | Q4 FY26 final; Q1 FY27 open | BSE-only, 16 links |
| 544501 | Sugs Lloyd | FC01, FC09 | Q3,Q4 FY26 final; Q1 open | BSE-only, 34 links |
| 544667 | Dachepalli Pub. | FC01, FC09 | same | BSE-only, 32 links |
| 511144 | Axis Solution | FC01 | Q1 FY27 open | BSE-only, 14 links |
| 524520 | KMC Speciality | FC01 | Q1 FY27 open | BSE-only, 5 links |
| 20MICRONS | 20 Microns | FC01, FC09 | Q3,Q4 FY26 final; Q1 open | NSE, 27 links |
| 3BBLACKBIO | 3B Blackbio | FC01 | Q1 FY27 open | NSE, 5 links |
| FC10 | 3IINFOLTD, 500166, 500360, 504605, 506854, ... (377) | FC10 | - | not_initiated |

Full lists with evidence in the JSON output. FC01 quarter Q2_FY27 is `unknown` (no meeting on record) for all listed.

## Behaviour / design notes

- Fleet = intake queue folders union stance logs (1206). 12 companies whose inputs raise (bad publish_date, not in mapping) are listed
  under `errors` with the exception, never dropped; one broad `except` in `run.py:select` does this - QA may judge it.
- Completeness reads the stores as they are, not as of the date; as-of only sets `now` and filters stance links (`as_of <= as-of`). Not point-in-time for the index.
- FC03 matches `last_error` by exact equality to the product's refusal message, duplicated in `selection/policy.py`; `tests/test_policy.py` pins it against `extract_reporting_period_via_llm`. Better: export the constant from `backend/raw/utils/reporting_period.py` (outside my scope).
- FC02 = any quarter `missing` or `due_nothing_in` (catalog: "Due/Missing"), so it is broad (571) and overlaps FC08. FC08 = a stance link on/after the first version of a `missing`/`stale` quarter (due_nothing_in quarters not considered).
- FC09 = chain start before FEED_START_DATE (no body check); broad (232). Prices not read (BSE-only companies have no NSE price files); FC11 is an edit class anyway.
- Not done: edit-only classes, FC12 (out of scope).

## Found

- `find -newer` read-only checks on the production data root are polluted by the live API (book snapshots, dashboard chat duckdb) and screener scraping; acceptance checks of this form need a store-scoped path list or a quiet window.

## QA ALERT fix (after QA round 1 PASS with ALERT, run.py:43-47 broad except)

Commit `f37b816` (Validation: selection lists only the product's refusals, raises otherwise, exits non-zero on errors). Range now `79e66a7..f37b816`.

- `selection/inputs.py`: new `UnreadableCompany` with two subclasses, one for each kind of error seen in the 12 rows:
  `NotInMapping` (resolver does not know the symbol: FABTECHCL, PERMAGN) and `RefusedPublishDate` (a `ValueError` from
  `backend.lib.concall_dates.doc_publish_date` on an index entry; this is checked per document before any other read, so the
  `ValueError` is caught only around that one product reader: BIGBLOC, JSL, KDDL, MALLCOM, MOLDTKPAC, POLYMED, RAIN, SCHAEFFLER, SHK, STYL).
- `run.py:select` catches only `UnreadableCompany`; any other exception (including a bare ValueError/KeyError) propagates.
- CLI writes the output, prints `ERROR <symbol>: <reason>` per company on stderr, and exits 1 if any errored. At 2026-10-15 it exits 1 (12 errors), as it should.
- Tests: `selection/tests/test_errors.py`. Known refusals are listed; ValueError, KeyError and RuntimeError propagate; unknown symbol gives NotInMapping;
  publish-date wrapping only wraps ValueError (TypeError propagates); the CLI writes and then exits 1.
- Rerun: sel5 and sel6 are `cmp`-identical. The candidates and counts are unchanged from sel3 apart from `alto_commit`, and the error reasons now name the class.
  `find -L ../news_server/data -newer marker` was empty for that window. `pytest backend/validation` 45 passed. Full suite: 66 failed / 1465 passed; `comm -23 new base` empty.
- `backend/validation/scenarios/__init__.py`: kept. The scenario-contract branch (`efe5533`) adds an identical empty file (0 bytes), so git merges
  the add/add without a conflict. Removing mine would break the package import on this branch until theirs lands.
