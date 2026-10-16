# Acceptance: stance cold-start window (draft)

1. **One rule.** The worker's cold-start `covers_from` comes from `lib/chain_start`; an AST/grep test shows `SCAN_START` is no longer used for the cold-start window and no date literal decides it.
2. **ARSSBL** on a sandbox copy: a rebuilt cold-start link dated 2026-06-06 has `covers_from` equal to its chain start (≤ `covers_to`) and examines the announcements in that window, or raises naming the missing pre-feed days.
3. **Legacy company:** cold start uses its recorded legacy start; unchanged output on one legacy company.
4. **Inverted window fails:** `stance_chain` and the reconciler both fail a link with `covers_from > covers_to`, naming it; on the live store the read-only fleet run lists every such link (expected: ARSSBL at least).
5. **Repair path:** the listed links are rebuilt through the stance reconciler/rerun command on a sandbox, after which `stance_chain` passes for them. No hand edits of stance stores; the production rerun is the owner's call.
6. **Unchanged elsewhere:** companies whose chain start is 2026-07-01 produce identical cold-start windows before and after.
7. **Suite:** `pytest backend/stance backend/validation backend/lib` pass; full suite no new failure; boundary test passes.
