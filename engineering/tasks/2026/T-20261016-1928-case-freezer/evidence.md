---
schema: evidence/v1
task: T-20261016-1928-case-freezer
round: 1
qa: fail
qa_by: qa@alto_hq/roles/engineering/qa
commits: 79e66a7..905ef7e
acceptance_sha256: cacd9db1248f72af4cfde032f4e132e49977b56f228cead4a1ca6a283e88741d
outputs_changed: unverified
---

## Round 1

Logs: `news_server/verify_data/reports/T-20261016-1928-case-freezer/`. QA worktree `.claude/worktrees/case-freezer-qa` @905ef7e. The approval hash matches.

### Acceptance check results

1. **Frozen: PASS.** I re-froze ARSSBL and 511144 into `/tmp/qa_cf_out` using dev's `--expect-empty` sets. The output is identical by sha256 to `alto_testcases@5a999e6` (520 and 385 files). The four expected-empty stores really are absent; ARSSBL's quarterly_update runs were all `skipped` with `announcements_incomplete`. I also walked `news_server/data` for every path containing the symbol and compared by sha256. The only files missing from the case are under `alto_data/exp_buy_now`, `alto_data/benchmark_deepseek`, `workflow_outputs/runs/*` (run traces) and `temp/`. None of these are product stores (`indep_*.log`).
2. **Window start: FAIL as written.** The acceptance says `min(2026-07-01, FY26 annual publish_date)`. Both FY26 annual index entries have `publish_date: null` and only `filed_at` set (ARSSBL 2026-06-06, 511144 2026-08-27). Read literally, both companies must raise. The code uses `filed_at` (window.py:20), and the results are ARSSBL start 2026-06-06 and 511144 start 2026-07-01, with the docid named. On substance I agree with this: `lib/chain_start/resolve.py:33` reads `filed_at`. But a check that passes only with a changed field is a failure under QA rules. The fix is an owner amendment of acceptance 2 to `filed_at`; no code change is needed. The negative path works: no annual raises `NoAnnualPublishDate`, and `--not-initiated` gives start 2026-07-01.
3. **Hashes: PASS.** `load_case` passes on both committed cases. One changed byte, one added file and one removed file each raise `CaseIntegrityError` naming the file, on both cases.
4. **Read-only: PASS.** I touched a marker, ran both freezes, then ran `find news_server/data -newer marker`. The output was empty (`find_newer2.log`; this happened to be a quiet window). Dev saw API writes on a live root; those are unrelated to the freeze. I ran the freeze under an audit hook covering open-for-write, mkdir, rename, remove, utime, sqlite3.connect and a wrapped duckdb.connect. Outside `--out`, the only event was `os.mkdir(news_server/data/workflow_outputs/cache)` (see F1). **No DuckDB or sqlite connection was opened.** `BlobIndex` (rw) is reached only through `announcement_bodies._index()`, and the freezer never calls it. It imports only the pure `canonical_docid`. `dhan_price_store._ensure_cache_dirs` is not called; only its constants are imported. `CompanyStore()` does not mkdir. The tmp-fixture test asserts that hashes and mtimes are unchanged.
5. **No fallbacks: PASS.** A live run without `--expect-empty` raised `MissingStore: store quarter_versions ...` and `store raw_announcements ...`. The tests cover the other raises.
6. **Suite: PASS.** `pytest backend/validation` gives 46 passed. The full suite with head run alone gives 67 failed, all 67 also failing on base, so there are 0 new failures. When I ran the two suites concurrently, `test_partitioned_storage` failed once on head. It passes 3 out of 3 alone and passes in the solo full run, so it is flaky, as dev said. The boundary test passes and the entry points import.

### Findings (verifier confirmed)

- **F1 ALERT: freeze issues a mkdir on the live root.** `backend/validation/cases/roots.py:56` calls `StepCache().cache_dir`, and `backend/stores/workflow_cache/step_cache.py:43` runs `mkdir(parents=True, exist_ok=True)`. On the production root the directory already exists, so the mkdir is a no-op and nothing is written; this is not a BLOCK. On a root missing the cache dir, the freeze would create one, and then it would fail with MissingStore instead of reporting the absent root. Seen with the audit hook, and the verifier reproduced it with a mkdir recorder. Use the path constant (`CACHE_DIR`) instead of constructing the store. (The verifier's extra claim that the path resolves to an empty worktree dir is disproved: `.claude/worktrees/news_server` is a symlink to the production `news_server`.)
- **F2 ALERT: point-in-time leak in company-keyed stores.** stores.py `_dhan` (and `_tree` for intake and stances) copies whole files. In both cases `sources/prices_dhan_15min/*.parquet` holds 25 bars dated 2026-10-16 (max 2026-10-16 15:15), after the as-of of 2026-10-15. The manifest does not record this. A later replay that reads raw parquet without going through the AsOfLedger would see the future. This is not a BLOCK under acceptance 1, which windows only the shared dated sources, but the manifest should record `max_date` per store, or the design page should state that replay must filter. Confirmed with pandas.
- **Contract:** both manifests validate against `CaseManifest` in `eng/T-20261016-1928-scenario-contract:backend/validation/scenarios/contract.py`. Its fields are `symbol`, `nse_symbol` (null for 511144), `window_start`, and `files` keyed by case-root-relative posix path to sha256. That is OK. Minor: some keys contain `:` (for example `sources/bse/544530_2025-10-14T16:14:49.987_602d.json`), which is not portable to Windows checkouts.

### Suite
Base 79e66a7: 67 failed. Head solo: 67 failed, same set (`comm -23` empty).

### Dev claims not confirmed
- The handoff says acceptance 4 is "not empty" on the live root. In my quiet-window run it was empty. The freeze's own write surface is only F1.
- The handoff gives the suite as "66 failed / 1466"; my count is 67 on both base and head. The difference is environmental; the claim of no new failures holds.

### Risks / automatic check
- A test that runs `freeze` under a `sys.addaudithook` write guard over the read roots would catch F1-class writes automatically.
- Proposal for the acceptance template: name index fields as they exist in the stored index (verify against a real `{SYMBOL}_index.json` before approval).

### Verdict
FAIL, on acceptance 2 as written only. Recommended: the owner amends acceptance 2 to `filed_at`; then the round-2 rerun is a re-judgement, with no code change needed. F1 and F2 are ALERTs.
