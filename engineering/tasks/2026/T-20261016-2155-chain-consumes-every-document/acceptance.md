# Acceptance: chain-consumes-every-document (draft)

Money path adjacent (stances feed trading): read-only on product data, all
runs in a temp stance root. LLM runs beyond a 2-company pilot need the owner.
Depends on classification-ledger (merged) and completeness-check (merged).

1. **Gap list from stored state.** A read-only query prints, per stance
   company, documents whose `publish_date` <= the latest link's `as_of` and
   whose quarter is later than the link's `quarterly_analysis_key` or that
   are in neither the chain's inputs nor the classification ledger. The
   2026-10-16 proxy count is 100 of 484 companies; the task states its exact
   definition and its count, and QA recounts two companies by hand.
2. **Backdated document, temp copy.** Take one company's stance dir and index
   into a temp root, insert a document dated before the latest link (the
   freezer in `backend/validation/cases` is the way to copy). The reconciler
   reports the chain stale from that date; the rebuild runs the analysis and
   re-chains from the first affected link; the later links are new links, the
   old ones are kept as superseded, none overwritten.
3. **In sequence.** The rebuilt chain's `covers_from` / `covers_to` pass
   `stance_chain` (T-20261016-2147-checks-stance-chain) and no link uses an
   input dated after its as_of.
4. **Nothing silently absent.** After the pilot (two named companies from the
   gap list, owner picks), the gap query returns an empty list for them, each
   document being consumed or classified.
5. **No-op when complete.** A company with an empty gap list is untouched:
   its log hash is identical after a reconcile run.
6. **Suite.** `python -m pytest backend/stance backend/intake backend/validation -q`
   no new failure against base.
