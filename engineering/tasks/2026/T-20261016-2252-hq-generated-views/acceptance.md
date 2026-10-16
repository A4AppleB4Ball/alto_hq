# Acceptance: hq generated views (draft)

1. Running the command twice gives byte-identical files; it writes only under `_generated/` folders.
2. Every `task.md` under `engineering/tasks/` appears exactly once in `by_status.md` under its frontmatter status, with a working relative link; counts per status match a hand count.
3. `approvals.md` lists exactly the items with status `awaiting_owner` or `needs_owner`, with `waiting_on`.
4. An item whose frontmatter is missing `status` or has a status outside its schema makes the command fail naming the file (no skip).
5. Both files carry a header saying they are generated and naming the command.
