# Acceptance: case-freezer (draft)

Read-only on product data. Writes only under the given `--out`.

1. **ARSSBL and one BSE-only company frozen.** The case holds the document
   index, intake items, workflow cache entries and quarter versions, the
   stance log and the 2026-10-15 proposal entries for the company, and its
   raw sources (exchange, Screener, concalls, prices, macro files in the
   window). QA lists each store from `backend/config/paths.py` for the symbol
   independently and finds every file in the case.
2. **Window start.** `manifest.window.start` = min(2026-07-01, FY26 annual
   report `publish_date`) and names that document. A company with no FY26
   annual `publish_date` raises unless `--not-initiated` is passed (start
   2026-07-01).
3. **Hashes.** `load` passes on the fresh case; changing one byte in any
   file, or adding or removing a file, raises naming the file.
4. **Read-only.** A `find <news_server/data> -newer <marker>` after the run
   lists nothing; tests on tmp fixtures assert the source tree is unchanged.
5. **No fallbacks.** A missing store for the symbol raises with the store
   name; nothing is skipped silently.
6. **Suite.** `pytest backend/validation` passes; full suite shows no new
   failure against base.
