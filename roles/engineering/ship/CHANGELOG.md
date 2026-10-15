# engineering/ship

## 3 — 2026-10-15 (minor: trust unchanged)

- Reads its notes from `alto_hq/roles/engineering/ship/notes.md` and the
  owner's decisions from `alto_hq/org/decisions/` (both moved from `alto`'s
  `work/`, which is gone).
- Finds `alto_hq` through `git rev-parse --git-common-dir`, which works the
  same from a worktree; `../alto_hq` did not resolve from
  `.claude/worktrees/<name>/`.

## 2 — 2026-10-15 (major: trust resets to propose-only)

- Lands only tasks with a QA PASS on the approved acceptance check and the
  owner's merge approval (an approval of `evidence.md`, hash checked).
- Records `merge_commit` in `evidence.md`, closes the task, and writes the
  release file in `alto_hq/engineering/releases/` instead of
  `verify_data/reports/`.
- May not edit its own skill.

## 1 — 2026-10-15

Imported from `alto` commit 9b569cd (`.claude/skills/ship/SKILL.md`),
unchanged.
