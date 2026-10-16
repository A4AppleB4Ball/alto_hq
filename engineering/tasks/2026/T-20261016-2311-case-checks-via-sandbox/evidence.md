---
schema: evidence/v1
task: T-20261016-2311-case-checks-via-sandbox
round: 1
qa: pass
range: 7d0c2c1~1..6b96141 (+ alto_testcases 2f5e6ce)
outputs_changed: unverified
---

## Round 1

Approval sha256 ab1b86b4… matches acceptance.md. Own sandboxes (via `backend.config.new_sandbox_worktree`, base 6b96141): `t2311-qa` (items 1,2,4,5), `t2311-qa-fresh` (item 7). Baseline: detached `t2311-qa-base` at 7d0c2c1~1 (old CaseAccess), sandbox root holding a read-only copy of the live legacy file (= what old case mode read). Live root only read. Scratch: news_server/verify_data/reports/T-20261016-2311-case-checks-via-sandbox/.

### Acceptance
1. PASS. Base: `stage_fleet.cli --case 511144 CHANDAN ARSSBL ORIANA`; head (empty sandbox): `--case 511144 CHANDAN ARSSBL`. Identical verdict lines: 511144 pass x3; CHANDAN qv FAIL Q1_FY27/2026-08-20 no_analysis, intake FAIL stockscans_chandan_concall_ppt_jun2026ppt; ARSSBL qv FAIL no_analysis x4 (Q1_FY27 07-14, 07-15; Q2_FY27 10-13, 10-15); rc 0.
2. PASS (emulated). Live root cannot be changed (owner rule), so my audit hook (`deny_live.py`) raises FileNotFoundError on every open under the live news_server root, i.e. the live file is removed for the process. ORIANA pass x3, same as base. legacy opens: only the sandbox path and the case's frozen copy.
3. PASS. `pytest backend/validation/tests/test_no_store_paths.py stores/tests/test_boundaries.py`: 49 passed. Exemption of cases/ owner-accepted.
4. PASS. Froze 3MINDIA (index, never polled) with `freeze --live --not-initiated --expect-empty intake ...` into /tmp. Case mode: `intake_failures: READ ERROR FileNotFoundError: No intake queue for 3MINDIA at <sandbox>/...`, rc 1. Live: `existing_company_intake('3MINDIA', root=<live intake>)` raises the same (read-only).
5. PASS. Full suite (dev skill command) base 66 FAILED/ERROR lines, head 61; `comm -23 new base` empty (head fixes 5 test_arssbl_validity errors). Boundary test passes; pytest backend/validation inside the suite run has no new failure.
6. PASS. All five cases `load_case` verify; each holds `legacy_chain_starts` frozen, sha256 d7cfa388…8826 (= live), manifest `extensions: [{stores:[legacy_chain_starts], commits: alto 0d07e40 dirty, news_server dirty, freezer 10f21ed clean}]` - added through cases.extend, not hand-edited.
7. PASS. Fresh sandbox, `cases.install` of the five cases (index, intake, workflow_cache, quarter_versions, legacy_chain_starts, stances), nothing from live: `pytest backend/validation backend/stance` 306 passed.

### Judgments asked
- freeze --live / cases.extend: read-only on live. They copy from `live_roots()` into `--out`, guarded by `_guard_out`; extend refuses a store already held and re-verifies. My runs left live untouched.
- Legacy copy vs 10-15: the live file's last change is news_server f9f91a4/0fe64a5 on 2026-10-08 (mtime Oct 8), so the 10-17 copy equals the 10-15 state. Dev's caveat is resolved. Provenance is in `extensions`. Because the store is `not_dated`, `past_as_of` cannot flag a later change; the only guard is `extensions.at`.
- DataAccess.announcement_index_path / repository.stage_folder_path: these are extractions of the existing formula, and the old readers now call them. That is one path, not a second.

### Findings (verifier confirmed)
- ALERT backend/validation/tests/test_no_store_paths.py:36-51: the AST rules miss `from backend.stores.intake import repository as r; r.companies_root()`, `import backend.config.paths as p; p.X`, and `d.joinpath("failed")`. A future module could build a store path and check 3 would still pass. No current module uses these forms.

### Dev claims not confirmed
None. Dev's caveat on the legacy date is now confirmed unchanged since 10-08.

### Automatic catch
Extend the AST test to cover `Import`/aliased module attributes and `joinpath`/`Path(...)` calls with stage-folder constants.
