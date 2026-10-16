# Acceptance: exchange-dedup-by-type (draft)

Depends on document-intelligence-slm. Index changes happen only in a temp
copy of the index dir, through the product's own index writer.

1. **Baseline.** A read-only query over `1/screener_announcements/*_index.json`
   prints the 299 BSE/NSE documents and, for each, its same-type same-period
   sibling from another source (299 of 299 on 2026-10-16). The counts are
   reproduced exactly before any change.
2. **Pair judged by the model, not the filename.** For a sample of 40 pairs
   (seeded), the identified type and period of both copies agree with the
   index label; every pair where they do not is listed and is excluded from
   merging.
3. **Merge result on a temp copy.** After the merge, each pair is one entry
   keeping the complete document and the exchange's `filed_at` /
   `publish_date` with its source; page counts of the kept copy are printed
   (the exchange copy is the <=15 page one).
4. **Downstream unchanged.** For 10 companies with merged pairs, the
   quarterly analysis key and `publish_date` that `DataAccess` returns are
   the same before and after, or the difference is explained pair by pair
   (a later knowable date must never become earlier than the exchange's).
5. **Reversible record.** Each removed entry is logged with its docid so the
   merge can be audited; no blob is deleted.
6. **Suite.** `python -m pytest backend/raw backend/lib -q` and
   `backend/intake` tests: no new failure against base.
