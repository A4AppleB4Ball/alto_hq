# engineering/dev

## 2 — 2026-10-15 (major: trust resets to propose-only)

Why: version 1 was slow, fragmented and burned tokens on retries, and its
"done" was unit tests the developer wrote itself, not a check on real
behaviour.

- Starts only from an `alto_hq` task with an approved, unchanged
  `acceptance.md`. It no longer writes its own task or done-when.
- Done means the acceptance check passes as written; tests support it.
- Stop rule: two failed attempts or a spent budget → diagnosis, stop.
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
