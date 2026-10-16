---
schema: evidence/v1
task: T-20261016-2147-checks-index-quarterly
round: 1
qa: pass
qa_by: qa@3
commits: 9950df7..d3fd000
acceptance_sha256: 5e96a7ee1885f7d74bb14b0077004d946d790b8b106d955ea21de299505f8121
outputs_changed: "no"
---

## Round 1

Approval sha256 matches acceptance.md (v2). Head checked out at .claude/worktrees/T-20261016-2147-qa, base at -qa-base. Raw logs: ../news_server/verify_data/reports/T-20261016-2147-checks-index-quarterly/.
outputs_changed=no: the only shared reader changed is DataAccess.list_quarterly_versions. Its output across all 372 live companies (381 versions) is byte-identical at base and head (lqv_qa-base.json vs lqv_qa.json, cmp identical).

### Acceptance check results

1. PASS. `python -m backend.validation.stage_fleet.cli --case .../511144@2026-10-15 .../CHANDAN@2026-10-15 .../ARSSBL@2026-10-15` exited 0 with read_errors []. 511144 passed all three checks. CHANDAN passed index_dates and failed intake_failures naming `stockscans_chandan_concall_ppt_jun2026ppt: failed at extraction: LLM could not determine the reporting period from this document's content`. ARSSBL failed quarterly_versions with no_analysis for Q1_FY27/2026-07-14, Q1_FY27/2026-07-15, Q2_FY27/2026-10-13 and Q2_FY27/2026-10-15. Hand-checked against the case files: CHANDAN's failed/ holds exactly that record. The FY25 annual (filed_at None) is FY25, below CHAIN_ANNUAL_KEY FY26. The FY26 annual has filed_at 2026-09-07. None of the three companies has a legacy chain start, so the result does not depend on F1. (Not asked: CHANDAN quarterly_versions also fails, Q1_FY27/2026-08-20 no_analysis.)
2. PASS. One test per reason exists and passes: index_dates/tests/test_reasons.py (reporting_period, publish_date, source, annual filed_at, out-of-chain entries ignored), intake_failures/tests/test_failures.py, and quarterly_versions/tests/test_reasons.py (NO_SUCH_VERSION, NOT_IN_CHAIN, STALE_DOCS, STALE_BASE, no_analysis).
3. PASS. quarterly_versions/check.py:40 calls validate_versions. stage_fleet/tests/test_boundaries.py (AST: no cross-check import, no writes) passes.
4. PASS. Every Verdict carries CHECK_ID, CHECK_VERSION and fingerprint(inputs.to_record()). test_changing_one_entry_changes_the_fingerprint passes.
5. PASS. `touch fleet_stamp; python -m backend.validation.stage_fleet.cli --fleet --out ../news_server/verify_data/reports/T-20261016-2147-checks-index-quarterly/fleet_summary.json` exited 0: 372 companies, 0 read errors. index_dates fail 5 / pass 367, intake_failures fail 8 / pass 364, quarterly_versions fail 15 / pass 357. `find -newer fleet_stamp` returned 0 files for the index dir (data/1/screener_announcements), alto_data/intake, workflow_outputs/cache/quarterly_update and alto_data/system. Non-zero exit on a read error: test_run.py, plus the probe under F2 (read errors recorded).
6. PASS. `pytest backend/validation backend/stores/tests/test_boundaries.py`: 121 passed. Entry points intake.runner, stance.runner, e2e.run, workflow.cli and stage_fleet.cli all import.

### Findings (all confirmed by the verifier; none BLOCK)

- **ALERT F1: a frozen case is not self-contained (c).** backend/validation/cases/access.py:12-13 states it, and backend/lib/chain_start/resolve.py:20,28 does it: case mode reads the live alto_data/system/legacy_chain_starts.json, which is outside the manifest and its hashes. Repro: /tmp/qa2147/legacy.py. The ORIANA@2026-10-15 case passes quarterly_versions with the live file. With ORIANA's legacy entry removed (in-memory), it fails not_in_chain x2 (Q4_FY26/2026-05-29, Q4_FY26/2026-06-10). The same hash-verified case gives a different verdict when the production file changes, so cases are not reproducible or point-in-time for legacy companies. It is not a BLOCK under the QA severity rules (no money, user data or stored data at risk, and acceptance does not cover legacy companies). The owner should decide whether this becomes a condition of merge: freeze legacy_chain_starts into the case, or have case mode raise for legacy symbols.
- **ALERT F2: a dated source with no publish_date is an anonymous read error (b).** index_dates/check.py:46-53 never sees the entry. lib/concall_dates.py:104 raises during enumeration, first in read_index_inputs and then in quarterly_versions. With publish_date absent the error is `KeyError: 'publish_date'`; with None it is `TypeError: '<=' not supported...`. Neither names the docid. Repro: /tmp/qa2147/probe.py. The behaviour is loud (exit 1), so it does not break the no-fallback rule. But the task asks the check to fail "naming each entry and the missing field", and the operator cannot tell which entry is bad. No test covers it (test_reasons.py:36 only mentions it in a docstring). An empty-string publish_date does come out as missing_publish_date.
- **ALERT F3: case-mode intake reads its own path (owner rule of 2026-10-16, and (d)).** cases/access.py:65-66 globs `<case>/stores/intake/<SYM>/failed/*.json` and does not use existing_company_intake (stores/intake/repository.py:674), which raises for a never-polled company. If a case's intake store is `expected_empty` (freeze.py:95), the case reads intake_failures as pass, while the product would raise for a company intake never polled. At freeze, cases/stores.py:65 _tree returns [] for both a missing and an empty folder, so the two states cannot be told apart. This is mitigated, not closed: expected_empty needs an explicit `--expect-empty intake` from the operator. cases/access.py:47-51 also builds the index path itself, but it uses the same `{symbol}_index.json` form as DataAccess.get_announcement_index (data_access.py:159-160), so the mapping cannot diverge (verifier disproved divergence). No ALERT-to-BLOCK escalation applies. Neither the checks nor the fleet use the company resolver, but neither does DataAccess itself, so nothing diverges from it. The three checks read through DataAccess and the intake store only.

### Owner questions, judged

- (a) Not a silent skip. Entries that are not blob_stored are excluded by the chain itself (lib/quarter_versions.py:220, lib/annual_reports/identity.py:27), so the scope equals "what the chain uses". Gap: a filing that was announced but never stored is invisible to all three checks. That belongs to a separate ingestion-completeness check.
- (b) See F2. It fails loudly, but the entry is not named.
- (c) See F1. ALERT, flagged for the owner's decision.
- (d) Sound for the cases tested: the CHANDAN/ARSSBL/511144 stores are status frozen, and an absent failed/ is read as empty only then. Residual hole: F3.
- (e) The list_quarterly_versions output is byte-identical on real data (above). stored_quarterly_versions is the same code moved. read_record is a thin public wrapper over _read_json. Neither has callers outside validation.

### Suite (serial, committed trees)

Base 9950df7: 66 failed, 1544 passed, 16 skipped. Head d3fd000: 66 failed, 1573 passed, 16 skipped. `comm -23 head base` is empty, so there are no new failures. Logs: suite_qa-base.log, suite_qa.log.

### Dev claims not confirmed

None. Every handoff.md claim matched my runs.

### Risks / out of scope

- While the fleet run was going, at 22:06:27 and 22:06:45, something wrote to production alto_data/stances/ACME/decisions.jsonl (a HUMAN_APPROVED BUY decision for test symbol ACME). This change has no stance writes, so another process wrote it, most likely a test run against the production data root. Owner should look; this is T-20261015-0321-checkout-data-root territory.
- The automatic check that would catch F1: a case-loader invariant that every product input a check reads resolves inside the case dir. Run the case CLI with the data root pointed at an empty temp dir.
