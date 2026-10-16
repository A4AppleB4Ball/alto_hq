# Acceptance: completeness-awaiting-state (DRAFT, not approved)

Read-only on product data; fixtures in temp dirs. Depends on completeness-check (merged).

1. **Fleet before and after.** The check over all stance companies (the CLI
   or the loop in evidence): before, 224 complete / 261 incomplete (259 only
   Due-with-nothing-in, 11 Missing); after, no company is incomplete only
   because of a due quarter with no documents, and the Missing set is the
   same companies with the same quarters (ARSSBL Q1+Q2 FY27, CHANDAN Q1 FY27,
   and the others). Both tables kept.
2. **Awaiting.** A quarter that is due, holds no document and has no later
   quarter holding one is Awaiting: non-blocking, with a reason saying it
   closes when a later quarter holds documents. Older and newer such
   quarters of one company are all Awaiting.
3. **Closes.** When a later quarter holds a document, the same quarter is
   Not released (fixture, before and after).
4. **Nothing else loosened.** Missing, Stale, Due-with-nothing-in's removal
   aside, every existing state test passes unchanged; a stance without a
   chain start still violates.
5. **Version.** The check version changes, so a verdict recorded under the
   old version reads Stale (test).
6. **Docs.** `backend/validation/docs/completeness_design.md` states the new
   state and the owner decision.
7. **Repo checks.** Boundary test, imports, suite vs base: no new failure.
