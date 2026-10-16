# Plan: window-end-from-manifest

- **Touches:** backend/validation/scenarios/contract.py (drop WINDOW_END; CaseManifest gains required `as_of: date`), scenarios/catalog.py (load_scenario: window.end must equal case.as_of), selection/__init__.py and __main__.py (docstring example date -> YYYY-MM-DD, required by check 1's grep), docs/scenarios.md, cases/manifest.py docstring, scenarios/tests. Only caller of WINDOW_END was catalog.py. Entry point: `python -m backend.validation.scenarios.catalog`.
- **Money path?** No.
- **Change:** window end comes from each case's manifest `as_of`; a manifest without `as_of` is rejected. window.start rule unchanged. The freezer already writes `as_of`.
- **Checks:** 1 grep as written; 2 new tests in scenarios/tests/test_catalog.py; 3 `python -m backend.validation.cases.load` on the real cases plus catalog `load_case` printing `as_of`; 4 `pytest backend/validation` + full suite vs base b893361.
