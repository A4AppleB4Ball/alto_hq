# Acceptance: window-end-from-manifest (draft)

Code only; no product data read.

1. `WINDOW_END` no longer exists; `grep -rn "2026-10-15" backend/validation/scenarios --include='*.py' | grep -v tests` is empty.
2. A scenario whose `window.end` equals its case manifest's as-of validates;
   one that differs raises CatalogError naming both dates. Two cases frozen
   at different dates validate in one catalog.
3. Both real cases in alto_testcases load and their manifests carry the
   freeze as-of the catalog reads.
4. `pytest backend/validation` passes; full suite no new failure.
