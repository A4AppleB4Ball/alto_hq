---
schema: task/v1
id: T-20261015-0321-checkout-data-root
title: Every checkout names its own data root; a sandbox can never resolve to production
status: in_progress
created: 2026-10-15T03:21+05:30
created_by: owner
kind: internal
approvals:
  - file: acceptance.md
    sha256: 704f994a7a59944b5480b0bbe8d19a07fb74c7403e020a4b7b59e3befdd72f63
    by: owner
    at: 2026-10-16T19:40+05:30
  - file: acceptance.md
    sha256: 0d5e9c9923dfbb324bdcd5428c1b9b9724493636b1386191fea565feecaa6a95
    by: owner
    at: 2026-10-17T00:40+05:30
claimed_by:
branch: eng/T-20261015-0321-checkout-data-root
friction: "No role exists for an owner-led design session, so created_by is owner."
---

## Goal

Each `alto` checkout declares, in one required gitignored file, which data
root it uses and whether it is the live checkout or a sandbox.
`backend/config/paths.py` resolves every store from that file, so:

- the live checkout resolves exactly the paths it resolves today;
- a sandbox (an agent worktree, the release runner's copies) resolves only
  its own root, and can never resolve to production;
- a checkout without the file fails at import instead of guessing.

## Why

- `paths.py:41-47` derives the data root from the checkout's location
  (`ALTO_ROOT.parent / "news_server"`), with no override.
- Agent worktrees live at `alto/.claude/worktrees/agent-*`, and the symlink
  `alto/.claude/worktrees/news_server -> …/workspace/news_server` makes every
  one of them read and write the production data root.
- The release runner (golden snapshot, live vs candidate) and data
  protection both need a checkout to point at an isolated root.
- The research audit found experiments can write production stores: a
  benchmark `--llm-config` with no `--stance-output-dir`, and a stray
  `LLM_CONFIG_PATH`.

## Design

1. **The checkout file.** `alto/.alto_checkout.yaml`, gitignored:

   ```yaml
   mode: live                 # live | sandbox
   data_root: <absolute path to the news_server root>
   ```

2. **`paths.py`** reads it at import and raises when:
   - the file is missing or a field is missing or unknown;
   - `mode: sandbox` and `data_root` resolves to the live data root, or
     inside it;
   - `mode: live` and the checkout is not the main checkout on this machine.
   `NEWS_SERVER_ROOT` comes from `data_root`; everything below it is
   unchanged. No default, no fallback.

3. **LLM config in live mode.** `--llm-config` / `LLM_CONFIG_PATH` naming a
   non-production config raises when `mode: live`. In a sandbox it works as
   today. The env var stays the way a selected config reaches child
   processes.

4. **Worktrees.** A command creates a worktree together with its sandbox
   checkout file and an empty (or snapshot) data root under a sandbox root
   outside the live data root. The `.claude/worktrees/news_server` symlink is
   removed (owner's call on timing: existing agent worktrees stop resolving
   data until they get a sandbox file).

5. **Live files.** The main Mac checkout and the server checkout each get a
   `mode: live` file with today's exact path. The server file is a deploy
   step (owner's call).

## Out of scope

- The golden snapshot and the release runner (next tasks).
- Moving or renaming the data repo.
- Changing what the machine gate (`backend/config/machine.py`) decides.

## Impact map starting points (for dev)

- `backend/config/paths.py` and every module that imports from it at import
  time.
- `backend/config/llm_settings.py` (`select_llm_config`, `get_llm_settings`).
- `backend/api/services/server_side_data_pull_sync/sync.py`,
  `backend/scripts/stance_sync_trigger.py` (server data paths).
- Help texts naming `news_server/data/alto_data/` (`stance/runner.py`,
  `backtest/scripts/compare_*`).
- `.gitignore` in `alto`.
