# Plan: classification-ledger

**Touches:** `backend/stores/stance/repository.py` (CompanyStore: sidecar
`classification_ledger.jsonl`, 3 methods), new `backend/stance/classification_cache.py`
(item keys, fingerprint, `classify_cached`), `backend/stance/worker.py`
(`_gate_anns_today`, macro gate). Only callers of classify_announcement /
classify_macro_event are worker.py and tests. Entry: stance.runner -> run_checkpoint.

**Money path?** Indirectly (stance records). Classifier output passes through
unchanged (stored signal == returned signal, JSON round-trip); a test compares the
material-path stance record field by field vs the old code.

**Change:** Store gets `classification_entries(symbol)` (reader, corrupt line raises),
`classification_lookup(symbol, identity)`, `append_classification(symbol, entry)`
(under the per-symbol lock `exclusive_lock(log_path)`; idempotent on identity).
Identity = item_key + as_of + classifier config (name, model) + input fingerprint.
Item keys: `announcement:<scrip>:<news_id>,...` (sorted) / `macro:<event_name>`; no collision.
Fingerprint = sha256 of canonical JSON of exactly the argument tuple handed to the
classifier (announcements, prior note, analyses; macro: name, detail, prior, analysis,
financials). Worker: lookup before building LLMClient; hit -> stored signal, no client;
miss -> classify, append. Unchanged: classifier decisions, prompts, records.
Owner-visible: one new file per symbol dir; reruns make no classifier calls.
Known limit: the macro classifier also reads prices through `da` (not hashable);
stated in docstring and handoff.

**Acceptance runs:** new test file covering checks 1-6 with a call-counting stub and a
temp-dir store; then existing stance + store tests (incl. test_boundaries), suite vs base,
import of entry points.
