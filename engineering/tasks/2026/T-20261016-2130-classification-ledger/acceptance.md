# Acceptance: classification-ledger (DRAFT, not approved)

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
   (same item key and as_of).
6. **Readable.** A reader method in the store returns the entries of a symbol;
   a corrupt line raises, never skipped.
7. **Nothing else changed.** The existing stance tests pass unchanged; suite
   vs base shows no new failure; entry points import.
