# Plan (written after implementation; I did not write it before code as the dev skill requires)
Touches: new `backend/validation/{verdicts,completeness,docs}`; one added function in `backend/lib/quarter_policy.py`. No existing function changes behaviour, so no callers. Reads DataAccess, CompanyStore (has_log), raw.results_calendar.store/lookup/due. Not a money path. Entry points: none wired.
Change: pure rules (quarters.py) over gathered inputs (inputs.py); verdict + fingerprint generic (verdicts/record.py).
Acceptance run: CLI on real symbols (1, 2), tmp-dir pytest (3-6, 8), AST/grep + pip freeze (6, 7), suite vs base (9).
