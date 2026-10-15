# engineering/qa

## 3 — 2026-10-15 (minor: trust unchanged)

- Reads its notes from `alto_hq/roles/engineering/qa/notes.md` and the
  owner's decisions from `alto_hq/org/decisions/` (both moved from `alto`'s
  `work/`, which is gone).
- Finds `alto_hq` through `git rev-parse --git-common-dir`, which works the
  same from a worktree; `../alto_hq` did not resolve from
  `.claude/worktrees/<name>/`.

## 2 — 2026-10-15 (major: trust resets to propose-only)

Why: version 1 judged with reviewers and its own tests, so a change could
pass without anyone running what "done" meant; and its sub-agent trees and
one verifier per finding made it slow and costly.

- Starts only from an `alto_hq` task whose `acceptance.md` approval hash
  matches; runs every acceptance check itself, as written. A check not run
  or changed to pass is a FAIL.
- Review done by QA itself, at most two sub-agents one level deep;
  scenario tests only where the diff reaches; one verifier for all findings.
- Writes `evidence.md` (rounds, acceptance hash, `outputs_changed` with
  `unverified` until the release runner exists) and sets the task status.
- Records in the `alto_hq` task folder; `work/qa/notes.md` gets only proven
  facts; may not edit its own skill.
- Data safety: no data-writing commands in worktrees until the
  checkout-data-root task is merged.

## 1 — 2026-10-15

Imported from `alto` commit 9b569cd (`.claude/agents/qa.md`,
`.claude/skills/qa/SKILL.md`), unchanged.
