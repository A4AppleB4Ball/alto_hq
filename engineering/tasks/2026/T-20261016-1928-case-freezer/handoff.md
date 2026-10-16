# Handoff: T-20261016-1928-case-freezer (round 1)

- Branch `eng/T-20261016-1928-case-freezer`, worktree `alto/.claude/worktrees/case-freezer`.
- Base `79e66a7`; commit `905ef7e` "Validation: case freezer and hash-verified case loader" (one item).
- Cases repo: `alto_testcases` local commit `5a999e6` "Cases: ARSSBL and 511144 frozen at 2026-10-15" (not pushed).
- Code only in `backend/validation/cases/` plus the design page `backend/validation/docs/cases.md`.
- BSE-only company for acceptance 1: **511144 (Axis Solution)**. The completeness cli
  reports it `complete`, it has no NSE listing (its company key is the scrip code), and it
  appears in the 2026-10-15 proposals. 504028 (GEE) is also complete but is in no
  2026-10-15 proposal, so I did not pick it.

## Acceptance checks

Commands run from the worktree. `C=/Users/kmrh581/personal/projects/workspace/alto_testcases/cases`.

1. **Frozen.**
   ```
   python -m backend.validation.cases.freeze ARSSBL --as-of 2026-10-15 --out $C --expect-empty quarter_versions raw_announcements stockscan_financials corporate_actions
   python -m backend.validation.cases.freeze 511144 --as-of 2026-10-15 --out $C --expect-empty raw_announcements stockscan_financials corporate_actions
   ```
   ARSSBL: 520 files. 511144: 385 files. The stores are index, intake, workflow_cache
   (annual), quarter_versions, stances, proposal (5 scienceamit1 proposals from
   2026-10-15 that list the symbol), e2e_coverage, bse blobs, BSE and NSE day files for
   every window day, exchange_attachment_hashes, screener_financials, screener_pages,
   index_documents (the blob of every index doc with `blob_stored`), Dhan daily and 15min
   parquet, NSE bhavcopy (ARSSBL only: 60 trading days, since the files stop at
   2026-09-08), and macro events released in the window.
   The `--expect-empty` stores really are absent for these companies. ARSSBL has no
   quarterly_update cache at all (its FC02 state). The manifest records each one as
   `expected_empty`.
   Independent check: a script that walks each paths.py dir and matches the symbol or
   scrip code as a filename token. It found ARSSBL 174 files and 511144 149 files, and
   **0 not in case** (compared by sha256).
2. **Window.** ARSSBL `start 2026-06-06`, with evidence
   `screener_arssbl_annual_report_financialyear2026frombse`, filed_at 2026-06-06.
   511144 `start 2026-07-01`, with the annual filed 2026-08-27 named.
   The no-annual raise and `--not-initiated` are covered by tests.
   **Interpretation:** an annual's index entry has no `publish_date`, only `filed_at`,
   which is the date `lib/chain_start` reads. I used `filed_at`, and the manifest names
   the field (`annual_date_field: filed_at`).
3. **Hashes.** `python -m backend.validation.cases.load $C/ARSSBL@2026-10-15 $C/511144@2026-10-15`
   printed `520 files verified` and `385 files verified`. On a copy of 511144:
   - a flipped byte gave `CaseIntegrityError: ... changed: stores/stances/511144/log.jsonl`
   - an added file gave `added: sources/macro/extra.json`
   - a removed file gave `missing: stores/stances/511144/log.jsonl`
4. **Read-only.** `find news_server/data -newer marker` after the run is **not empty**. It lists:
   - `alto_data/workspace/scienceamit1/book/default/snapshots.jsonl`
   - `dashboard/chat/chat_2026_10.duckdb` and `partition_index.duckdb`
   - in an earlier run, `screener_data/raw_reports/stocks/HDFCBANK/html/...`

   The live API and scheduler write these continuously (snapshots.jsonl was updated again
   at 20:31:38 with no freeze running). The freeze never reads those paths. Taken
   literally, the check fails on a live root. Read-only behaviour itself is pinned:
   - `test_freeze_holds_every_store_and_leaves_source_untouched` asserts the sha256 and
     mtime of every file in the tmp source tree are unchanged, and that no directory was
     added.
   - `git status` runs with `GIT_OPTIONAL_LOCKS=0`.
   - `--out` that overlaps a read root raises.

   QA must decide whether to run it in a quiet window or scope the find.
5. **No fallbacks.** Tests cover these raises:
   - a missing store (quarter_versions, stances, corporate_actions, proposal) raises
     `MissingStore: store <name>: ...`
   - a missing window day file raises
   - a `blob_stored` doc with no blob raises
   - `--expect-empty` on a non-empty store raises
   - an existing case raises (it is never overwritten)
6. **Suite.** `pytest backend/validation` gives 46 passed. Full suite: base 66 failed /
   1448 passed, new 66 failed / 1466 passed. `comm -23 new base` is empty, and
   `stores/tests/test_boundaries.py` passes. In the first full run,
   `api/services/tests/test_partitioned_storage.py` failed, then passed alone and in the
   rerun, so it is flaky. Entry points `freeze`/`load` import.

## Behaviour the owner should know
- Each case is about 220–260 MB, most of it the shared BSE and NSE day files of the
  window. They are copied exactly because the product needs both day files to close a day
  (`lib/market_day`). Every case duplicates them; a shared day-file store across cases
  would be a later choice.
- Company-keyed stores are copied whole, including files dated after the as-of (for
  example intake items). The window bounds only the shared dated files. Hiding post-as-of
  inputs is the replay clock's job.
- The manifest uses the scenario contract's names (`symbol`, `nse_symbol`,
  `window_start`, `files` keyed by the path from the case root). Mismatch to note: the
  `files` keys are `sources/bse/<blob name>` and `stores/...`, so an edit's `target.doc`
  must use that full key, not the design example's `bse/2026-08-12_...pdf`.
- `news_server` is recorded `dirty: true` (tracked changes in the data repo at freeze time).

## Not done / caveats
- `stores.py:_bse_blobs` selects the bse namespace by its two writer names: canonical
  `bse_{code}_` (`lib.announcement_bodies.canonical_docid`) and the legacy `{code}_`.
  Reading 78k sidecars took over 2 minutes, and `BlobIndex` opens duckdb read-write, so I
  used neither.
- `stores.py` imports the private `backend.stance.config._read_event_file` for the macro
  release date (no public reader exists).
- The Dhan cache dirs come from `backend.price_feed.dhan_price_store` (`CACHE_DAILY`,
  `CACHE_15MIN`), because paths.py does not hold them.
- Not covered: the legacy `stock_prices/*_ohlcv_master.json` (absent for both companies),
  `companies_announcements/` (not in paths.py), and workflow `runs/` and `temp/` (not
  stores).

## Found
- **Live-root check impossible:** the API and scheduler write production data
  continuously (book snapshots, dashboard chat duckdb, screener pages). Any "nothing newer
  than marker" check on `news_server/data` needs scoping.
- **Dhan cache outside paths.py:** the Dhan price cache root
  (`~/NSE_BSE_Data/dhan_cache`) is defined in `price_feed/dhan_price_store.py:27`, not in
  `backend.config.paths`.
- **Constructors that mkdir:** `StepCache.__init__` (`stores/workflow_cache/step_cache.py:43`)
  and `RebalanceStore.__init__` mkdir on construction, so a read-only consumer cannot use
  them safely on a fresh root.
