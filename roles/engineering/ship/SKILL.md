---
name: ship
description: Land owner-approved, QA-passed Alto tasks from alto_hq on main — one at a time, full-suite diff, tidy commits, record the merge commit, write the release checklist, push only on the owner's explicit say-so. Use after the owner approves a merge.
---

# ship

Inputs: the `alto_hq` tasks to land. A task may land only when:

- `evidence.md` latest round is `qa: pass`, and its `acceptance_sha256`
  matches the approval of `acceptance.md` in `task.md`;
- `task.md` `approvals` holds `evidence.md` (the owner's merge approval)
  with the sha256 of the file as it is now.

Anything else: stop and report. Land money-path tasks first. Read
`work/ship/notes.md` (in `alto`) first.

Until `live` and `develop` exist, the landing branch is `main`, which the
main checkout runs in production.

## Step 1 — Baseline

On `main`: record `git log --oneline -1` and the full-suite failure list
(`dev` skill, Step 3 command) into `$TMPDIR/ship.base`.

## Step 2 — Land one branch at a time

For each task's `eng/<task>` branch, in order:

1. `git checkout -b ship-<task> main`, then cherry-pick its commits.
2. Conflicts:
   - imports only → keep both sides' needed names; check every name is
     still used and defined;
   - anything else → **stop and show the owner** both sides; do not guess.
3. Semantic check: import every changed and added module, and read the
   failures of tests whose setup misses something new on main. Fix in a
   commit on this branch, and note it in the release file (QA did not see
   it).
4. Full suite vs `$TMPDIR/ship.base`: no new failures. Boundary test
   passes. Entry points import.
5. `git checkout main && git merge --ff-only ship-<task>`, delete the
   branch, refresh `$TMPDIR/ship.base`.

## Step 3 — Tidy commits

Each landed item is one commit: `<Area>: <what changed>`, a short body of
what and why. Fold fix-ups into the item's commit only while unpushed. No
Co-Authored-By or Claude attribution, anywhere.

## Step 4 — Record

- Each task's `evidence.md`: `merge_commit:` the final commit on `main`.
- Each `task.md`: `status: done`, `closed:`.
- Release file `../alto_hq/engineering/releases/<YYYY-MM-DD>.md` (named by
  `v<n>` once product versions exist): commits landed with hashes and
  task ids; what must be true on the server before deploy (files, env,
  logins); what will look different after deploy; checks still
  unverified; obsolete data the owner may delete (never delete it).

Commit these in `alto_hq` (`Ship: <date> <task ids>`, no attribution). Add
to `work/ship/notes.md` only a merge or deploy lesson this run proved.

## Step 5 — Push

Show the owner the commit list, the compare link
(`https://github.com/A4AppleB4Ball/alto/compare/<old>...<new>`) and the
release file. Push only when the owner explicitly says push in this
conversation. Never force-push `main`. Do not edit this skill; propose
changes in the release file.
