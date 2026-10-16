# Acceptance: checks-index-quarterly (v2, owner-approved 2026-10-16)

Read-only on product data.

1. **On the frozen cases** (alto_testcases, read only):
   - 511144 passes all three checks.
   - CHANDAN passes `index_dates` (its FY25 annual without `filed_at` is
     before its chain start, so out of scope) and fails `intake_failures`
     naming `stockscans_chandan_concall_ppt_jun2026ppt`, stage extraction,
     "LLM could not determine the reporting period".
   - ARSSBL fails `quarterly_versions` naming Q1 and Q2 FY27 as having no
     stored analysis.
   QA confirms each from the case files by hand.
2. **One test per reason** on tmp fixtures: missing `reporting_period`,
   missing `publish_date` / source, annual without `filed_at`, an entry
   before the chain start that is ignored, a failed intake item, and each
   `validate_versions` reason.
3. **No re-derivation.** `quarterly_versions` calls
   `lib/quarter_versions.validate_versions`; an AST test asserts neither check
   imports from another check's folder or writes any file.
4. **Verdict contract.** Each verdict carries its check id, version and a
   fingerprint of what it read; changing one index entry changes the
   fingerprint.
5. **Fleet run, read-only.** A CLI over all companies writes a summary
   (pass / fail counts per reason) and exits non-zero on any read error;
   `find -newer` over the stores it reads is empty after the run.
6. **Suite.** `pytest backend/validation` passes; full suite no new failure;
   boundary test passes.
