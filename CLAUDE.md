# alto_hq

The company's records: roles, policies, decisions, epics, tasks, incidents.
The product is the sibling repo `../alto`; its data is `../news_server`.
Read `README.md` first. It is the conventions (currently `hq/v2`, see
`org/CHANGELOG.md`).

## Which repo is home

- Start a session here for planning and records only: epics, decisions,
  incidents, policies, and authoring roles.
- Start in `../alto` for anything that changes code or runs the product
  (dev, QA, ship, ops repairs). The task's records are reached from there
  through `$HQ`.

## Rules

- **IDs.** Every item is `<TYPE>-<YYYYMMDD>-<HHMM>-<slug>` with the creation
  time in IST. The ID is the join key across repos. Items never move; status
  is a field in the file.
- **Schemas.** Every file declares its schema in frontmatter. Its fields and
  body sections are in `org/schemas/`. A format change is a `P-` item in
  `org/changes/`, plus an `org/CHANGELOG.md` entry and a migration. It is
  never a silent edit.
- **Employees propose; the owner decides.** Only the owner approves an
  `acceptance.md`, a decision or a trust change. Record the owner's rulings
  as `D-` items, and never re-argue one.
- **Plan small.** An epic holds stories as one-liners, and a story becomes a
  task only when it is next. Follow-up work comes from what a spike or task
  found, not from a speculative list.
- **Findings carry their evidence.** Each finding names a file:line, a
  command or a measurement, and its date. A script that produced numbers is
  kept beside the item that cites it.
- **Facts about the product** go in the owning package's `docs/` in
  `../alto`, not here.
- **Roles are authored here** (`roles/<vertical>/<role>/role.md`, with a
  CHANGELOG entry per version). `../alto/.claude/agents/` and its
  dev/qa/ship skills are copies, updated in the same change. A role may not
  edit its own definition.
- **No secrets here.** Never copy credentials, tokens or transcripts into
  these records. Write summaries only.
- **Commits.** Commit locally, with no Co-Authored-By or Claude attribution
  lines. Pushing is the owner's call.

## Where the README describes the target, not today

- `alto` has only `main` for now; the `live`, `develop` and `staging/`
  branches don't exist yet. The main checkout runs production.
- The data repo's working branch is `alto`, not `live`.
- `alto_runs/`, `_generated/` and the validator don't exist yet.
