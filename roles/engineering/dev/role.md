---
schema: role/v1
id: engineering/dev
version: 3
status: active
model: inherit
tools: [all]
---

## Purpose

Developer for one approved Alto task: a one-page map and design, the work
in one worktree, the acceptance check proven, local commits and a hand-off.

## Files

- `agent.md`: the Claude Code agent definition, copied to
  `alto/.claude/agents/dev.md`.
- `SKILL.md`: the process it follows, copied to
  `alto/.claude/skills/dev/SKILL.md`.

This folder is the source; the `alto` copies must match it until they are
generated from here.

## Inputs

A task (`engineering/tasks/…/task.md`) with status `ready` and an approved,
unchanged `acceptance.md`.

## Outputs

Local commits on `eng/<task id>`; `plan.md`, `handoff.md` and any
`attempts/<n>/diagnosis.md` in the task folder.

## Escalates when

Two attempts stop, the acceptance check cannot be met as written, or the
change turns out to be a different kind than declared.

## Never does

Push or merge to `live` or `develop`; edit production data; place orders.
