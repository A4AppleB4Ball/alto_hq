# engineering/dev

## 4 — 2026-10-15 (minor: trust unchanged)

- Reads its notes from `alto_hq/roles/engineering/dev/notes.md` and the
  owner's decisions from `alto_hq/org/decisions/` (both moved from `alto`'s
  `work/`, which is gone).
- Finds `alto_hq` through `git rev-parse --git-common-dir`, which works the
  same from a worktree; `../alto_hq` did not resolve from
  `.claude/worktrees/<name>/`.
- A fact about the product goes in the owning package's `docs/`, not in
  the notes.

## 3 — 2026-10-15 (minor: trust unchanged)

- A failed QA round counts as one of the task's two attempts; round 2
  answers every confirmed finding in `handoff.md`.
- Budget stop removed: no budget an agent can measure exists until run
  metering (`alto_runs/`) is built.

## 2 — 2026-10-15 (major: trust resets to propose-only)

Why: version 1 was slow, fragmented and burned tokens on retries, and its
"done" was unit tests the developer wrote itself, not a check on real
behaviour.

- Starts only from an `alto_hq` task with an approved, unchanged
  `acceptance.md`. It no longer writes its own task or done-when.
- Done means the acceptance check passes as written; tests support it.
- Stop rule: two failed attempts → diagnosis, stop. (A budget stop was in the first draft and removed in 3.)
- Works itself in one worktree. Sub-agents only for a large read-only
  search or an independent piece over half a day, one level deep. Was:
  "lead, don't type", sub-agent trees, a worktree per piece.
- Impact map and design merged into one page (`plan.md`).
- Full suite once at the end against a committed baseline; no per-piece
  verifier sub-agents (QA is the independent check).
- Records go to the `alto_hq` task folder. `work/dev/notes.md` only gets
  facts a run proved; no reorganising every run.
- May not edit its own skill or definition; proposes changes instead.
- Data safety: no data-writing commands in worktrees until the
  checkout-data-root task is merged (worktrees resolve production data).

## 1 — 2026-10-15

Imported from `alto` commit 9b569cd (`.claude/agents/dev.md`,
`.claude/skills/dev/SKILL.md`), unchanged.
