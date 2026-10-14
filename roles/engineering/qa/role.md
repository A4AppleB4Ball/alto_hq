---
schema: role/v1
id: engineering/qa
version: 2
status: active
model: inherit
tools: [all]
---

## Purpose

Independent QA for one Alto task. Runs the approved acceptance check
itself, reviews the diff and its callers, confirms findings with a
verifier, and writes `evidence.md` with PASS or FAIL. Never fixes code.

## Files

- `agent.md`: the Claude Code agent definition, copied to
  `alto/.claude/agents/qa.md`.
- `SKILL.md`: the process it follows, copied to
  `alto/.claude/skills/qa/SKILL.md`.

This folder is the source; the `alto` copies must match it until they are
generated from here.

## Known gap (for version 3)

Real-data checks wait for sandbox data roots
(T-20261015-0321-checkout-data-root) and the release runner. Until then
`outputs_changed` is usually `unverified`. Version 3 runs the release
runner and judges the stage-by-stage changes against `acceptance.md`.

## Inputs

The task, its approved `acceptance.md`, the commit range.

## Outputs

`evidence.md` (schema evidence/v1), and the task's status: PASS →
`awaiting_owner`; FAIL → back to dev, or `needs_owner` after round 2.

## Escalates when

A finding cannot be confirmed or refuted, or the acceptance check is
ambiguous.

## Never does

Fix code; read the developer's report before its verdict is written.
