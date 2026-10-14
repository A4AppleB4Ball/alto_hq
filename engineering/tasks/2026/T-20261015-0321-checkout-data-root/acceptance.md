# Acceptance: T-20261015-0321-checkout-data-root

Done when every check below passes, run by QA, with its output in
evidence.md.

## 1. Live resolves exactly as today

- Before the change, on `live`/main: dump every path constant and accessor
  result of `backend.config.paths` to a file (name → resolved absolute path).
- After the change, with the main checkout's `mode: live` file: dump again.
- The two dumps are identical, line for line.

## 2. Missing or wrong file fails at import

Each of these raises at `import backend.config.paths`, naming the file and
the problem:

- no `.alto_checkout.yaml`;
- a missing field, an unknown field, an unknown `mode`;
- `mode: sandbox` with `data_root` equal to the live data root;
- `mode: sandbox` with `data_root` inside the live data root;
- `mode: live` in a worktree.

## 3. A sandbox reads and writes only its own root

In a worktree made by the new command:

- every path in the dump from check 1 resolves under the sandbox root;
- `python -m backend.e2e.run --companies <one golden company> --dry-run`
  resolves only sandbox paths;
- after a run of one real, non-LLM step (e.g. `documents`) in the sandbox,
  the live data root has no file modified since the run started (compare
  mtimes of the live root before and after).

## 4. Non-production LLM config is refused on live

- On the live checkout, `--llm-config <benchmark yaml>` raises before any
  work starts.
- With `LLM_CONFIG_PATH=<benchmark yaml>` exported on the live checkout,
  any LLM-using command raises before any work starts.
- In a sandbox, the same `--llm-config` works as today.

## 5. Nothing else changed

- The existing test suite passes as before on the live checkout (failures
  that existed before the change are listed with their pre-change output).
- `outputs_changed: no`: the golden companies' stores are untouched by the
  change itself.

## Not checked here

- The server checkout's live file (a deploy step after merge).
- Removal of the symlink (done on the owner's go).
