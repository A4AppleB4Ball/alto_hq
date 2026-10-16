# Acceptance: hq generated views (draft)

1. Running the command twice gives byte-identical files; it writes only under `_generated/` folders.
2. Every `task.md` under `engineering/tasks/` appears exactly once in `by_status.md` under its frontmatter status, with a working relative link; counts per status match a hand count.
3. `approvals.md` lists exactly the items with status `awaiting_owner` or `needs_owner`, with `waiting_on`.
4. An item whose frontmatter is missing `status` or has a status outside its schema makes the command fail naming the file (no skip).
5. Both files carry a header saying they are generated and naming the command.

## Amendment v2 (owner 2026-10-16, after QA round 1)

6. **No silent skip.** Any file under an item folder pattern that is not a valid item raises naming the file, except epic sidecars `E-….<topic>.md` beside their epic (recognised by that exact form). A task folder with a bad id fails the build.
7. **Versions included.** `version/v1` extends `item/v1`; versions appear in `by_status.md`, and an awaiting_owner version in `approvals.md`.
8. **README** layout tree shows `engineering/_generated/approvals.md`.

## Amendment v3 (owner 2026-10-16, after QA round 2)

6'. Replaces 6. Every file under an item folder pattern is one of: an item; an epic sidecar `E-<epic id>.<topic>.md` or its script `E-<epic id>.<topic>.py` beside an existing epic; or a file inside an item's own folder. Anything else (a stray `README.md`, `notes.md`, a bad id folder) fails the build naming it. Version folders must match `v<n>` or `v<n>.<m>`.
9. A P- item in `org/changes/` and an `org/CHANGELOG.md` entry record the version/v1 and epic sidecar schema changes.
