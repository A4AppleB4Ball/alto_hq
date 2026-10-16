# Acceptance: stance cold-start window (draft)

1. **One rule.** The worker's cold-start `covers_from` comes from `lib/chain_start`; an AST/grep test shows `SCAN_START` is no longer used for the cold-start window and no date literal decides it.
2. **ARSSBL** on a sandbox copy: a rebuilt cold-start link dated 2026-06-06 has `covers_from` equal to its chain start (≤ `covers_to`) and examines the announcements in that window, or raises naming the missing pre-feed days.
3. **Legacy company:** cold start uses its recorded legacy start; unchanged output on one legacy company.
4. **Inverted window fails:** `stance_chain` and the reconciler both fail a link with `covers_from > covers_to`, naming it; on the live store the read-only fleet run lists every such link (expected: ARSSBL at least).
5. **Repair path:** the listed links are rebuilt through the stance reconciler/rerun command on a sandbox, after which `stance_chain` passes for them. No hand edits of stance stores; the production rerun is the owner's call.
6. **Unchanged elsewhere:** companies whose chain start is 2026-07-01 produce identical cold-start windows before and after.
7. **Suite:** `pytest backend/stance backend/validation backend/lib` pass; full suite no new failure; boundary test passes.

## Amendment v2 (owner 2026-10-16)

8. **Window rule:** cold-start `covers_from` = min(chain start, FEED_START_DATE) (`stance_scan_start`); companies whose chain starts after 2026-07-01 keep 2026-07-01.
9. **Poller:** `backend/stance/poller.py` picks the cold-start date from the same `lib/chain_start` function; no copy of the rule and no `SCAN_START` fallback remains (test).
10. **Check 5 pilot:** SHILPAMED rebuilt in a sandbox stance directory (rewind from 2026-02-06, rerun, LLM spend approved for this one company); `stance_chain` passes for it. ARSSBL's rebuild waits for its 3 missing bodies and is not part of this task.

## Amendment v3 (owner 2026-10-17)

11. **Runner:** `backend/stance/runner.py`'s walk start comes from the same `lib/chain_start` `stance_scan_start`; no `earliest_knowable_analysis_date` copy or fallback remains there (test).
12. **No Kimi:** the check-10 pilot runs on a sandbox-only LLM config with every role on DeepSeek via Foundry (or the local model); no role resolves to kimi-k3.

## Amendment v4 (owner 2026-10-17)

8'. Replaces 8. Cold-start `covers_from`: a legacy company starts at its first quarter version date; any other company at min(2026-07-01, FY26 annual filed date), i.e. its chain start capped at 2026-07-01. Both dates come from `lib/chain_start` / DataAccess.
11'. Replaces 11. The runner's walk start is unchanged from base (first knowable version via `DataAccess.earliest_knowable_analysis_date`); commit c5f9853 is reverted.
10 runs after T-20261016-2336 lands (sandbox prices from the shared cache, read-only), on DeepSeek only.
