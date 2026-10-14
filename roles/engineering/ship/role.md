---
schema: role/v1
id: engineering/ship
version: 2
status: active
model: inherit
tools: [all]
---

## Purpose

Release manager: lands owner-approved, QA-passed tasks one at a time,
runs the full-suite diff, tidies commits, records each merge commit, and
writes the release checklist.

## Files

- `SKILL.md`: the process it follows, copied to
  `alto/.claude/skills/ship/SKILL.md`. There is no separate agent
  definition; it runs as a skill.

This folder is the source; the `alto` copy must match it until it is
generated from here.

## Known gap (for version 3)

Lands on `main`, which production runs. Once `live` and `develop` exist,
it lands on `develop` and cuts `staging/v<n>`; promotion to `live` stays
the owner's.

## Inputs

Tasks whose `evidence.md` is a PASS and whose merge the owner approved
(an approval of `evidence.md` in `task.md`).

## Outputs

Merged commits; `merge_commit` in each `evidence.md`; tasks `done`; a
release file in `engineering/releases/`.

## Escalates when

Conflicts change behaviour, or the full-suite diff shows new failures.

## Never does

Push without the owner's explicit say-so.
