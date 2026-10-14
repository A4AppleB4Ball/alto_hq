---
name: ship
description: Land QA-passed Alto branches on main — rebase in order, resolve conflicts, full-suite diff, tidy commits, write the deploy checklist, push only on the user's explicit say-so. Use after qa passes.
---

# ship

Inputs: the tasks to land. Find them with
`grep -l '^status: ready-to-ship' work/tasks/*/task.md`; read each
`handoff.md` and `qa.md`. Land money-safety first. Only land a task whose
latest `qa.md` round is PASS. Read `work/ship/notes.md` first.

## Step 1 — Baseline

On `main`: record `git log --oneline -1` and the full-suite failure list
(`dev` skill, Gate 4 command) into `$TMPDIR/ship.base`.

## Step 2 — Land one branch at a time

For each branch, in order:

1. `git checkout -b ship-<name> main`, then cherry-pick its commits.
2. Conflicts:
   - imports only → keep both sides' needed names, check every name is
     still used/defined;
   - anything else → **stop and show the user** both sides; do not guess.
3. Semantic check: import every changed and added module (an import of a
   moved module fails here), and read the failures of tests whose setup
   misses something new on main (for example a new required map or
   argument). Fix in a commit on this branch.
4. Full suite vs `$TMPDIR/ship.base`: no new-only failures (a moved test
   file is the same test). Boundary test passes. Entry points import.
5. `git checkout main && git merge --ff-only ship-<name>`, delete the
   branch, and refresh `$TMPDIR/ship.base`.

## Step 3 — Tidy commits

Each landed item is one commit: `<Area>: <what changed>`, a short body
of what and why. Fold merge fix-ups into the item's commit only while
it is unpushed. No Co-Authored-By or Claude attribution, anywhere.

## Step 4 — Deploy checklist

From every hand-off and QA report, collect behaviour changes and write
`../news_server/verify_data/reports/ship-<date>.md`:

- commits landed, with hashes
- what must be true on the server before deploy (files, env vars, logins)
- what will look different after deploy (new errors, stopped jobs, fresh plans)
- live checks still unverified
- obsolete data the user may delete (never delete it yourself)

Update memory: each landed `task.md` → `status: shipped`, a log line with
the final hashes and the checklist path. Tend `work/ship/` (`work/README.md`,
"Role spaces"): merge and deploy lessons, and improve this skill.

## Step 5 — Push

Show the user the commit list, the GitHub compare link
(`https://github.com/A4AppleB4Ball/alto/compare/<old>...<new>`) and the
checklist. Push only when the user explicitly says push in this
conversation. Never force-push `main`.
