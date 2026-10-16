# Acceptance: checks-index-quarterly (draft)

Read-only on product data.

1. **On the frozen cases** (alto_testcases, read only): `index_dates` passes
   on 511144; on CHANDAN it fails naming the entry whose reporting period was
   not determined. `quarterly_versions` passes on 511144 and fails on ARSSBL
   naming Q1 and Q2 FY27 as having no stored analysis. QA confirms each from
   the case files by hand.
2. **One test per reason** on tmp fixtures: missing `reporting_period`,
   missing `publish_date` / source, annual without `filed_at`, and each
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
