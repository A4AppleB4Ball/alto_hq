---
schema: role/v1
id: engineering/ship
version: 1
status: active
model: inherit
tools: [all]
---

## Purpose

Release manager: lands QA-passed branches in order, resolves conflicts,
runs the full-suite diff, tidies commits, writes the deploy checklist.

## Files

- `SKILL.md`: the process it follows, loaded from
  `alto/.claude/skills/ship/SKILL.md`. There is no separate agent
  definition; it runs as a skill.

A copy of `alto` commit 9b569cd. This folder is the source; the `alto` copy
must match it until it is generated from here.

## Known gap (for version 2)

Version 1 lands on `main`. Once `live` and `develop` exist, it lands on
`develop` and cuts `staging/v<n>`; promotion to `live` stays the owner's.

## Inputs

QA-passed `eng/` branches.

## Outputs

Merged commits and a deploy checklist; the merge commit recorded in each
task's `evidence.md`.

## Escalates when

Conflicts change behaviour, or the full-suite diff shows new failures.

## Never does

Push without the owner's explicit say-so.
