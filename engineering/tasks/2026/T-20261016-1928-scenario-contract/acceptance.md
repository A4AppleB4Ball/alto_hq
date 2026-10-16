# Acceptance: scenario-contract (draft)

Code only; no product data read.

1. **Valid catalog passes.** A tmp catalog with 4 curated scenarios plus the
   random-live entry covering FC01–FC12 between them validates.
2. **Each rule fails with its reason**, one test each: unknown edit op;
   edit target absent from the case manifest; case missing or failing its
   hash; checkpoint outside the window; expected file missing; unknown
   check id (ids come from a registry the validator is given; today the
   completeness check's id); a class covered by no scenario; more than 5
   curated scenarios; no BSE-only company in the set; `window.start`
   differing from the case manifest.
3. **Edits are never applied here.** The module imports nothing that writes;
   an AST test asserts no write calls in `scenarios/contract.py` and
   `catalog.py`.
4. **Doc.** `backend/validation/docs/scenarios.md` states the contract and
   the coverage rules, not a code copy.
5. **Suite.** `pytest backend/validation` passes; full suite no new failure.
