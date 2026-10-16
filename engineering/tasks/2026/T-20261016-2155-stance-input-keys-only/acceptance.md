# Acceptance: stance-input-keys-only (draft)

Read-only on product data; new stance links only in a temp stance root.

1. **Baseline from stored state.** Over `alto_data/stances/*/log.jsonl`
   (484 companies, 6324 links on 2026-10-16): 1513 links have
   `chain.quarterly_analysis_key` null (243 companies have a null key on
   their latest link), 5573 links have an available `pe_snapshot` whose
   `ttm_periods` come from Screener quarterly rows. The task prints these
   counts with a `python -I` script over the logs; they match.
2. **Inputs recorded.** A temp-root stance run through the real worker writes
   a link with `inputs`; a test asserts every source the agent prompts
   interpolate appears in it (prompt builders and `inputs` are tested
   against one list so a new prompt input fails the test until recorded).
3. **Check verdicts.** The check returns a `verdicts.record.Verdict` with
   fingerprint: pass on a link whose inputs are all analysis keys / docids;
   fail naming link, input and kind on a link that lists a raw quarterly
   source (test fixture); "not recorded" on an old link, counted, not passed.
4. **Fleet run.** `python -m backend.validation.<check>.cli` over all 484
   companies prints pass / fail / not-recorded counts; today every link is
   "not recorded" except the temp-root ones.
5. **Owner question answered in the record.** The output lists the
   `pe_snapshot` as its own input kind so the owner can decide; the check does
   not silently exempt it.
6. **Suite.** `python -m pytest backend/validation backend/stance -q` and
   `python -m pytest backend/stores/tests/test_boundaries.py -q`: no new
   failure against base.
