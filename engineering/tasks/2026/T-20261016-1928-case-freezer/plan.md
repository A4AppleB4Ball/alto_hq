# Plan: case-freezer

**Touches:** new package `backend/validation/cases/` only (`stores.py` store
specs, `window.py` window start, `manifest.py` hashing + manifest I/O,
`freeze.py` CLI, `load.py` verify, `tests/`). No existing function changes, so
no callers change. Reads production stores read-only through
`backend.config.paths` constants, `WorkspacePaths`, `CompanyResolver`,
`stored_annual_entry`/`doc_publish_date`, `stance.config._read_event_file`
(macro release date), Dhan cache dirs from `backend.price_feed.dhan_price_store`.
Never instantiates stores whose constructors mkdir (StepCache, RebalanceStore).

**Money path?** No. Nothing reads the case into trading.

**Change:** `freeze SYMBOL --as-of D --out DIR [--not-initiated] [--expect-empty STORE ...]`
copies each declared store's files for the company byte-for-byte into
`DIR/<SYMBOL>@D/{stores,sources}/<store>/...`, writes `manifest.yaml`
(symbol, nse_symbol, bse_code, window_start, window {start,end,evidence},
commits {alto, news_server}, stores {name: count | expected_empty},
files {relpath: sha256}). Every declared store must yield files or the run
raises naming it, unless named in `--expect-empty` (recorded in the manifest).
Window-bounded shared files: BSE/NSE day files, NSE bhavcopy, macro events
with release date in [start, as_of]. Company-keyed files copied whole.
Proposals: per-user files dated D whose `model_targets`/`diff` hold the symbol.
`load(case_dir)` re-hashes every file and raises naming any changed, added
or missing file. Out dir must be outside the data roots (raises otherwise).

**How each check is run:**
1. `python -m backend.validation.cases.freeze ARSSBL --as-of 2026-10-15 --out ../alto_testcases/cases [--expect-empty ...]`
   and same for 504028 (GEE, BSE-only, `complete` per completeness cli); then an
   independent listing script over paths.py dirs compared to the manifest.
2. Print `manifest.window`; test for the not-initiated raise and flag.
3. `load` on both cases; tests flip a byte / add / remove a file.
4. `touch marker` before; `find news_server/data -newer marker` after; tmp-fixture tests compare tree digests.
5. Tests: each store missing raises with its name.
6. `pytest backend/validation`; full suite vs base.
