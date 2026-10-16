---
schema: evidence/v1
task: T-20261016-2147-checks-stance-chain
round: 1
qa: pass
qa_by: qa@engineering
commits: 9950df7..47f5bdb
acceptance_sha256: 0a542f142edafb770f3b3f2e1e8e63371973356bd99ea9ad21c257f29c9df4a4
outputs_changed: unverified
---

## Round 1

QA worktree `alto/.claude/worktrees/T-20261016-2147-qa2` (detached 47f5bdb); base `-qabase` (9950df7).
Logs: `news_server/verify_data/reports/T-20261016-2147-checks-stance-chain/`.
Approval sha matches acceptance.md as it is now. Read-only throughout; nothing written to product data.

### Acceptance check results
1. PASS. `python -m backend.validation.stance_chain.cli --case $C/511144@2026-10-15 --case $C/ARSSBL@2026-10-15`
   gives `511144: continuous (14 links, through 2026-10-07) fp=35ec1616…` and `ARSSBL: continuous (12 links, through 2026-10-13) fp=a63eb4b8…`, exit 0.
   By-hand check from log.jsonl:
   - 511144 link 2026-08-12: prior as_of is 2026-08-08, covers_from is 2026-08-09 (= +1 day), covers_to is 2026-08-12 (= as_of). OK.
   - ARSSBL link 2026-07-14: prior is 2026-07-02, covers_from is 2026-07-03, covers_to is 2026-07-14. OK.
2. PASS. The branch's tests pass. My own plants on a tmp copy of ARSSBL (index 6, as_of 2026-08-22):
   - gap: `broken [(2026-08-22, gap)]`
   - overlap: `broken [(2026-08-22, gap)]`
   - covers_to: `broken [(2026-08-22, covers_to_not_as_of)]`
   - a cold-start link mid-chain: `continuous`
3. PASS. reconcile.py imports `chain_gap` and `link_gap` from `backend.stance.chain.continuity`, and check.py uses `link_gap`; the identity test passes. No file under backend/stance tests changed in the range, and the stance tests pass.
4. PASS. `d79734f` is reachable only from `backup/2147-chain-pre-v3`, not from 47f5bdb. There is no `stance_inputs_asof` package, and grep for `stance_inputs_asof|bse_rows_between` in backend/ is empty.
5. PASS. `test_verdict_carries_id_version_and_fingerprint` passes. The CLI prints `check=stance_chain@1 fp=…`.
6. PASS. `pytest backend/validation backend/stance` gives 216 passed. Full suite: 66 failed at base and 66 at head; `comm -23 new base` is empty. `stores/tests/test_boundaries.py` gives 2 passed. Entry points `backend.stance.reconcile` and `stance_chain.cli` import.

### Findings (the verifier confirmed both; ALERT only)
- **ALERT F1:** `backend/validation/stance_chain/check.py:47-49` adds a rule the shared function does not have. A first link that is not a cold start is reported as `gap`, while the reconciler's `chain_gap` says it is continuous. Reproduction: slice the ARSSBL log from its 4th record. The check returns `broken [(2026-07-14, gap)]` and `chain_gap` returns None.
  Judgement on the question asked: flagging is right for a full log. Every frozen case and live log starts at a cold start, and an untraceable first link means unexamined coverage. It is wrong for a case window that starts mid-chain, and today no such window exists: the cases hold the whole log.
  If cases are ever windowed, the check needs the prior as_of. `chain.prior_as_of` is on every record, so the first link should be checked against `prior_as_of` (a distinct reason such as `no_predecessor`), not called a `gap`. This breaks the "one rule" spirit only mildly: the extra rule is outside continuity.py and the reconciler does not have it. The owner should decide whether the rule belongs in continuity.py.
- **ALERT F2:** Nothing checks a cold-start link's own window. The frozen ARSSBL cold-start link 2026-06-06 has `covers_from 2026-07-01 > covers_to 2026-06-06`, an inverted window, yet it reads continuous. This is outside the acceptance, which only requires that a cold start is not a gap. It is a real data oddity in ARSSBL; it likely comes from the cold-start floor of 2026-07-01 (the backtest scope) applied to a link with an earlier as_of. It needs a follow-up task: a covers_from <= covers_to rule, plus the reason the stance producer wrote this window.

### Suite
Base 9950df7: 66 failed, 1544 passed. Head 47f5bdb: the same 66 failures; none new.

### Dev claims not confirmed
None. Handoff claims 1-6 match what I saw. Dev says 218 passed because that run included test_boundaries (216 + 2).

### Risks / automatic catch
Proposed invariant: every stance link has covers_from <= covers_to, and the first link is a cold start or carries a prior_as_of present in the log.
