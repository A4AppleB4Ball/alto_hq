---
schema: evidence/v1
task: T-20261016-2126-window-end-from-manifest
round: 1
qa: pass
qa_by: qa@alto
commits: b893361..926dce1
acceptance_sha256: b79dc63f54c78cb3beee40105f5b7d6362eb134a173c520b6ad8249bbcc847ec
outputs_changed: unverified
---

## Round 1

QA worktree: `alto/.claude/worktrees/T-20261016-2126-qa` (detached at 926dce1); base worktree `-qa-base` at b893361. Logs: `news_server/verify_data/reports/T-20261016-2126-window-end-from-manifest/`. acceptance.md sha256 matches the owner approval.

### Acceptance check results
1. PASS. `grep -rn "WINDOW_END" backend` -> empty. `grep -rn "2026-10-15" backend/validation/scenarios --include='*.py' | grep -v tests` -> empty (rc=1).
2. PASS. `pytest backend/validation/scenarios/tests/test_catalog.py -k "window_end or frozen or as_of"` -> 4 passed: equal end validates; end 2026-10-14 vs as_of 2026-10-15 raises CatalogError naming both dates; cases frozen 2026-10-15 and 2026-11-20 validate in one catalog; manifest without as_of rejected.
3. PASS (read-only). alto_testcases has five cases, not two; all five checked. For each, `scenarios.catalog.load_case(root, id).as_of` and `cases.load.load_case(dir)['as_of']` both = 2026-10-15 (3IINFOLTD, 511144, ARSSBL, CHANDAN, ORIANA). `git status` in alto_testcases clean afterwards.
4. PASS. `pytest backend/validation` -> 90 passed. Full suite (dev skill command, committed trees, serial): base 66 failed / 1519 passed; head 66 failed / 1523 passed; `comm -23 head base` empty. `stores/tests/test_boundaries.py` 2 passed; catalog, selection, freeze, load entry points import.

### Findings
None (no verifier run: nothing to disprove).

Judgements:
- Manifests without `as_of` now rejected: correct. The freezer (`backend/validation/cases/freeze.py:117`) always writes `as_of`, `cases/load.py:50` already relied on it, and every real manifest carries it. Rejecting is the no-fallback behaviour required; no product path writes manifests otherwise.
- Docstring edits in `scenarios/selection/__init__.py:4` and `__main__.py:2` (`--as-of 2026-10-15` -> `YYYY-MM-DD`): CLI usage examples, not logic; the placeholder is accurate and loses nothing. The grep's intent (no hard-coded window date in scenario code) is met, not gamed. Acceptable.
- No other consumer of `WINDOW_END` existed; docs (`backend/validation/docs/scenarios.md`) updated in the same change.

### Suite
Base 66F/1519P/16S, head 66F/1523P/16S; no new failures (the 4 extra passes are the new tests).

### Dev claims not confirmed
None; handoff matches what I ran. Dev's note on `prices_dhan_15min` `past_as_of: true` in four cases is outside this diff; not judged.

### Risks
- Full catalog CLI not run on real data: no scenarios exist yet in alto_testcases/scenarios.
- Invariant that would catch this class: a catalog test that freezes a case at a non-default date end-to-end (freezer output -> catalog) rather than hand-written fixtures.
