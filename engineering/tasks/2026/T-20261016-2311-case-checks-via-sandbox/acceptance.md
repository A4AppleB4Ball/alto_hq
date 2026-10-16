# Acceptance: case checks via sandbox (draft)

1. The three checks give the same verdicts as today on 511144, CHANDAN and ARSSBL, run from a sandbox root holding the case.
2. ORIANA: verdict is the same with the live `legacy_chain_starts.json` removed or changed (the case's frozen copy is read).
3. AST test: no module under `backend/validation` builds a store path or opens index/intake files itself.
4. A company whose intake was never polled raises in case mode as it does live.
5. Suite: `pytest backend/validation` pass; full suite no new failure; boundary test passes.

## Amendment (owner 2026-10-16, after QA of T-20261016-2235)

6. **Cases carry every store a check needs.** The freezer freezes `alto_data/system/legacy_chain_starts.json` (hashed in the manifest) and `cases.install` places it into the sandbox root; the five existing cases are re-frozen or extended through the freezer (never hand-edited) with their hashes verified.
7. **Fresh sandbox suite.** In a fresh sandbox with the cases installed and no file copied from live, `pytest backend/validation backend/stance` has no failure caused by a missing `legacy_chain_starts.json`.
