# Acceptance: case checks via sandbox (draft)

1. The three checks give the same verdicts as today on 511144, CHANDAN and ARSSBL, run from a sandbox root holding the case.
2. ORIANA: verdict is the same with the live `legacy_chain_starts.json` removed or changed (the case's frozen copy is read).
3. AST test: no module under `backend/validation` builds a store path or opens index/intake files itself.
4. A company whose intake was never polled raises in case mode as it does live.
5. Suite: `pytest backend/validation` pass; full suite no new failure; boundary test passes.
