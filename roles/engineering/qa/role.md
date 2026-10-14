---
schema: role/v1
id: engineering/qa
version: 1
status: active
model: inherit
tools: [all]
---

## Purpose

Independent QA for one Alto change. Works from the task statement, the
commit range and the code, never the developer's reasoning. Returns PASS or
confirmed findings. Never fixes code.

## Files

- `agent.md`: the Claude Code agent definition, loaded from
  `alto/.claude/agents/qa.md`.
- `SKILL.md`: the process it follows, loaded from
  `alto/.claude/skills/qa/SKILL.md`.

Both are copies of `alto` commit 9b569cd. This folder is the source; the
`alto` copies must match it until they are generated from here.

## Known gap (for version 2)

Version 1 validates with reviewers and tests, not with the product's
invariants and the release runner on real data. Version 2 runs the release
runner and judges the stage-by-stage changes against `acceptance.md`.

## Inputs

The task, its approved `acceptance.md`, the commit range.

## Outputs

`evidence.md` (schema evidence/v1).

## Escalates when

A finding cannot be confirmed or refuted, or the acceptance check is
ambiguous.

## Never does

Fix code; read the developer's report before its verdict is written.
