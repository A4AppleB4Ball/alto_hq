# Acceptance: classification-ledger (approved)

Touches the stance worker's recording only, not what the classifier decides.
Read-only on production data; fixtures in temp dirs; no LLM call in the
checks (a stub classifier returns fixed signals).

1. **Immaterial is logged.** With a stub classifier ruling an announcement
   `should_run_triad=false`, running the checkpoint writes one ledger entry:
   item key, as_of, the full signal, the classifier config name, written_at.
   The checkpoint still returns None and no stance record is written, as today.
2. **Material is logged too.** A material verdict writes its entry as well,
   and the stance record is unchanged from the old code (compared field by
   field on the existing worker fixture).
3. **Macro events.** An injected macro event ruled immaterial is logged the
   same way, keyed so it cannot collide with an announcement.
4. **Through the store.** The ledger is written only via
   `backend/stores/stance` under the per-symbol lock; `test_boundaries.py`
   passes; a concurrent-writer test writes two entries without losing one.
5. **Idempotent.** Re-running the same checkpoint does not duplicate an entry
   (same item key, as_of, classifier config and input fingerprint).
5b. **The ledger is the classifier's cache** (owner, 2026-10-16). Before the
   classifier is called, the worker looks the item up in the ledger by item
   key, as_of, classifier config (name and model) and a fingerprint of the
   inputs the classifier is given (prior notes, the knowable analyses it
   reads). A hit returns the stored signal and makes no LLM call, immaterial
   or material; a miss on any of the four calls the classifier and appends.
   Tests with a call-counting stub: second run of the same checkpoint makes 0
   calls and returns the same signal; a changed config, a changed input or a
   different as_of makes 1 call. A corrupt entry raises, never treated as a
   miss.
6. **Readable.** A reader method in the store returns the entries of a symbol;
   a corrupt line raises, never skipped.
7. **Nothing else changed.** The existing stance tests pass, with at most the `company_store` mock argument changed (owner ruling 2026-10-16: no assertion edited); suite
   vs base shows no new failure; entry points import.
