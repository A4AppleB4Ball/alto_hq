---
schema: evidence/v1
task: T-20261015-1058-dagster-spike
round: 1
qa: pass
qa_by: qa@high-level
commits: ab8a959..99ed529
acceptance_sha256: 07865e13d719339bc3912d9393a536b47c3fc59dce2715a0a93085afb3ae4576
outputs_changed: unverified
---

## Round 1

Scope: the owner asked for a high-level validation. I ran A1-A5 myself, skimmed the diff for rule violations, and ran the boundary test and the new tests. I skipped the full-suite base-vs-head diff and the verifier batch, as the owner directed. This is not a full QA. The spike adds only new files, and none of them is imported by existing code.

Worktree: .claude/worktrees/T-20261015-1058-dagster-spike-qa at 99ed529. Fresh DAGSTER_HOME: alto_runs/T-20261015-1058-dagster-spike/home_qa2 (a first accidental run went to home_qa and is ignored).

### A1 Isolated: PASS
- Dagster 1.13.26 runs from alto_runs/.../venv. DAGSTER_HOME is under alto_runs.
- `python -m pip freeze` for the production env, taken before and after my run, was identical (`diff` empty). It also matches the dev's pipfreeze.before.txt.

### A2 Read-only: PASS, with a caveat
- I touched a marker, ran the full demo, then ran `find news_server/data -newer marker -type f`.
- One file was newer: alto_data/workspace/scienceamit1/book/default/snapshots.jsonl, modified at 16:39:38.
- A live uvicorn backend.api.local process (pid 72592) is running on this machine, and the spike code has no book path. I attribute the write to that process, but I could not prove it. The check cannot attribute writers on a live machine, which is the same weakness dev noted.
- A cleaner check would run the demo against a copy of the data root, or fail on any write by the spike's pids.

### A3 The check blocks: PASS
Command (DAGSTER_HOME=home_qa2, PYTHONPATH=worktree):
`dagster asset materialize -m backend.orchestration.dagster_spike.definitions --select '*' --partition-range 'ARSSBL...20MICRONS'`
- It returned rc=0 and made 1 run.
- Stored records, read through the instance and not the console, show:
  - ARSSBL: check FAILED, missing Q1_FY27 and Q2_FY27; stance not materialised.
  - CHANDAN: check FAILED, missing Q1_FY27; stance not materialised.
  - 20MICRONS: check SUCCEEDED; stance materialised.
- Caveat: the check itself is non-blocking. The stance asset re-observes completeness and skips incomplete companies (definitions.py:55-61). The outcome matches check 3, but Dagster's own blocking is not what produces it. Dev disclosed this.

### A4 Agent-readable: PASS
`python -m backend.orchestration.dagster_spike.query` printed, per company, last_run=SUCCESS, the three asset states and the check result with its missing quarters. It matches A3 exactly.

### A5 One batched run: PASS
The instance holds 1 run. The log shows one RUN_START. Each of document_index, quarterly_analysis, quarterly_complete and stance is a single multi-asset step that takes all partition keys.

### Tests
`pytest backend/orchestration backend/stores/tests/test_boundaries.py` gave 5 passed.

### Diff skim
- No relative imports, no `except`, no fallbacks, no data/ paths, and no Co-Authored-By or Claude lines in commit messages.
- The code reads through DataAccess and CompanyStore only.
- Tests are in `<feature>/tests/`.
- No product file changed.

### Findings (not run through a verifier, per the owner)
- ALERT: findings.md Q3 (launchd and sleep behaviour) and Q4 (automation condition) are explained from docs, not demonstrated. Q1 company x quarter is not measured. Acceptance B asks for evidence. The owner should judge whether that is enough for the spike. I did not review findings.md in depth. This is the only review of the B questions, and it was brief.
- ALERT: quarterly_complete reads through observe_quarterly three separate times (document_index, quarterly_analysis and the check) with no shared state. That is fine for a spike.

### Dev claims not confirmed
None contradicted. I read handoff.md after my checks ran and before I wrote this file. Everything I compared matched.

### Suggested automatic check
Run the demo under a data-root copy, or record the spike's pids, to prove A2 on a live machine.
