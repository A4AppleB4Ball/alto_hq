---
schema: evidence/v1
task: T-20261016-1928-scenario-selection
round: 1
qa: pass
qa_by: qa@alto_hq/roles/engineering/qa
commits: 79e66a7..d8d3275
acceptance_sha256: ff3137bec0a1baefe2973b78cc6f15958d74a32d66260660dd6c0799067615ed
outputs_changed: unverified
---

## Round 1

QA worktree: `alto/.claude/worktrees/T-20261016-1928-scenario-selection-qa`, detached at d8d3275. The acceptance sha256 matches the approval. Outputs and logs are in /tmp/qa1928/.

### Acceptance check results

Every run used `python -m backend.validation.scenarios.selection --as-of 2026-10-15 --out /tmp/qa1928/{a,b,c}.json`, run from the QA worktree. Each run printed: `fleet 1206, counts {'FC01': 225, 'FC02': 571, 'FC03': 6, 'FC08': 10, 'FC09': 232, 'FC10': 377}, errors 12`.

1. **PASS.** ARSSBL is in FC02 (Q1_FY27 and Q2_FY27 are `missing`, file ARSSBL_index.json) and in FC08 (stances/ARSSBL/log.jsonl, "9 stance links since its first version 2026-07-14 ... quarterly_analysis_key None"). CHANDAN is in FC03 (failed/stockscans_chandan_concall_ppt_jun2026ppt.json, failed:extraction, the period refusal). I re-derived two of these by hand.
   - **CHANDAN FC03.** I read the failed record directly. It has `failed_stage=extraction` and `last_error="LLM could not determine the reporting period from this document's content"`. It is the only file in the failed folder.
   - **ARSSBL FC08.** I read log.jsonl directly. It holds 12 links, from 2026-06-06 to 2026-10-13, and each link's prior_as_of is the previous link's as_of. Every link has quarterly_analysis_key None. Nine links are on or after 2026-07-14. `workflow_outputs/cache/quarterly_update/ARSSBL` does not exist, so the analysis really is missing.
2. **PASS.** All 225 FC01 candidates are `complete`, and 9 are BSE-only (504028, 511144, 524520, 538546, 538715, 540956, 544248, 544501, 544667). Their quarter states: final 256, open 225, unknown 191, expected 34.
   - **(a) Judgement on dev's reading.** Dev reads "every quarter in the window analysed" as "every quarter that holds documents is final or open". I accept this reading. The unknown and expected quarters are Q2_FY27, which no company had filed by 10-15. A quarter with no documents has nothing to analyse. Under D-20261016-1718, a `complete` company can have such quarters without being blocked. Read literally, no company could be in FC01 at this as-of. The owner should still confirm the reading.
3. **PASS.** All 377 FC10 candidates have company_state `not_initiated`, which comes from `check.evaluate`.
4. **PASS.** `pytest backend/validation/scenarios`: 10 passed, including test_no_outcome_inputs.py. The AST test covers imports and names in every non-test module of the package.
5. **PASS.** `cmp a.json b.json` showed the files identical, and c.json from a third run is also identical. The output records alto_commit d8d3275 and news_server_commit 1cd5641a, plus as_of, now and the completeness check id and version.
6. **PASS.** The suite has no new failure (see Suite).
   - **First window.** `find .../news_server/data -newer /tmp/qa1928/marker -type f` listed one file, `alto_data/workspace/scienceamit1/book/default/snapshots.jsonl`. That file is written by BookStore (`backend/stores/book/`), and the live `uvicorn backend.api.local` was running.
   - **Second window.** I ran the same command again, as written (`touch marker2`, run, `find -newer marker2`). The output was **empty**.
   - **(d) Path versus imports.** The module imports no book, trading or execution store; the AST test enforces this. Its only write is the `--out` file, which must not already exist (`__main__.py:20`). I conclude the first window's file came from a concurrent writer, not from this module.

### Findings (confirmed by the verifier)

- **ALERT: run.py:43-47, a catch-all `except Exception` around `read_company_facts`.**
  - **What it does.** The handler turns any exception into an `errors` row, including programming bugs such as AttributeError or TypeError. The CLI then exits 0 (`__main__.py:22-24`).
  - **Reproduction.** The verifier ran a temp-dir pytest with stubbed stores, where `read_company_facts` raises AttributeError for BBB. `select()` returned normally with BBB only in `errors` and absent from every class.
  - **Real effect.** In the real run, 12 companies cannot be candidates for any class: 10 with a bad publish_date (ValueError) and 2 that are not in the mapping (KeyError, FABTECHCL and PERMAGN). Those are data defects the release set may want.
  - **(b) Judgement.** The path is not silent: errors are in the output record and their count is printed. It is still a fallback against the owner's "no fallbacks, always raise" rule, because it swallows bugs as well as data faults. The owner decides whether this is acceptable or must change. Two options: catch only the known data exceptions, or exit non-zero when `errors` is non-empty. The class queries (lines 48-52) are outside the try and do raise.
- **(c) Note, not a finding.** FC03 compares `last_error` against a copy of the refusal text. Only one source site contains the text (`backend/raw/utils/reporting_period.py:187`). `tests/test_policy.py` pins the copy by calling the real function, and it passes. The match is exact rather than a heuristic, and it matched CHANDAN's stored record. Remaining risk: the copy would drift if someone changed both strings without the test. Exporting the constant from reporting_period.py would be cleaner.

### Suite

The suite ran from committed trees, with base 79e66a7 and head d8d3275 in parallel, using the dev skill's command. Head: 66 failed, 1458 passed. `comm -23 new base` was empty. The base list had 67 entries, one more than head, which is consistent with the flake dev reported. `stores/tests/test_boundaries.py` was not in the failure list. The `__main__` entry point imports.

### Dev claims not confirmed

- Dev reported base 66 failed; my base run had 67 failures, and the difference does not affect the verdict.
- Dev says it is not point-in-time: completeness reads the stores as they are, and `--as-of` only sets `now` and filters stance links. I did not test a past as-of. Running at an older date will not reproduce that day's state.

### Risks and the automatic check

- Whole-root `find -newer` checks are unreliable while the live API is running. A store-scoped list of paths, or comparing the module's write sites against the live writers' paths, would catch this class automatically.
- A rule test that forbids `except Exception` in validation packages, unless the exception is re-raised, would catch the catch-all automatically.
