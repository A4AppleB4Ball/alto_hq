# Plan: hq generated views

**Touches (alto_hq only, no alto code, no data stores):** new package
`scripts/views/` (README rule 7: first tooling item creates `scripts/`), its
`tests/`, and the two generated files `_generated/by_status.md` and
`engineering/_generated/approvals.md`. No item file is read for writing.

**Money path?** No.

**Change.**
- `scripts/views/schemas.py`: loads `org/schemas/*.yaml`; the item types are
  the schemas with `extends: item/v1`; each gives its `file:` pattern and its
  `status.values`.
- `scripts/views/items.py`: globs each item schema's `file:` pattern
  (`<…>` and `X-…` segments become `*`), parses frontmatter, and raises
  naming the file when frontmatter is missing, its `schema` differs from the
  pattern's schema, `status` is missing or outside the schema's values, or
  `waiting_on` is missing where item/v1 requires it.
- `scripts/views/render.py`: pure rendering, sorted by status then id, links
  via `os.path.relpath` from the output file, generated header naming the
  command. No timestamps, so output is deterministic.
- `scripts/views/build.py`: the command, `python -m scripts.views.build`
  from the alto_hq root. Writes only the two files.
- Stays the same: items never move or change. README tree places
  approvals under `management/_generated/`; the approved task says
  `engineering/_generated/approvals.md`, which is followed.

**Acceptance, command by command (from the alto_hq root):**
1. run build twice, `shasum` both files between runs; `git status --short`
   shows only `_generated/` paths changed (plus pre-existing others).
2. Python one-off counts `status:` over every `engineering/tasks/*/*/task.md`
   vs per-status rows in `by_status.md`; each link resolved to an existing file.
3. compare approvals rows with a grep of awaiting_owner/needs_owner items.
4. pytest in `scripts/views/tests/` with temp-dir repos: missing status and
   bad status fail naming the file.
5. `head -3` of both files.
