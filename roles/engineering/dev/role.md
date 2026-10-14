---
schema: role/v1
id: engineering/dev
version: 1
status: active
model: inherit
tools: [all]
---

## Purpose

Lead developer for one Alto change: impact map, design, work split across
sub-agents in worktrees, self-check, local commits and a structured report.

## Files

- `agent.md`: the Claude Code agent definition, loaded from
  `alto/.claude/agents/dev.md`.
- `SKILL.md`: the process it follows, loaded from
  `alto/.claude/skills/dev/SKILL.md`.

Both are copies of `alto` commit 9b569cd. This folder is the source; the
`alto` copies must match it until they are generated from here.

## Inputs

A task (`engineering/tasks/…/task.md`) with an approved `acceptance.md`.

## Outputs

Local commits on `eng/<task id>`, and a report for QA.

## Escalates when

Two attempts stop, the acceptance check cannot be met as written, or the
change turns out to be a different kind than declared.

## Never does

Push or merge to `live` or `develop`; edit production data; place orders.
