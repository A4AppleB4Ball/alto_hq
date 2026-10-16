# Handoff, round 2: results-calendar-to-stance (spike)

Branch eng/T-20261016-1718-results-calendar-to-stance, base a5b5606, no commits (no repo code changed;
artifacts are in this task folder). acceptance.md sha256 5da36768... verified at start (matches task.md).
Read-only on product data; no capture, no reader.load_meetings, no network (the announcement files
already hold BSE Result and NSE Outcome of Board Meeting rows, so no fetch was needed), no LLM.

## QA round 1 finding
- Item 2 not met: FIXED (in findings.md section 2). Market-wide: BSE 95 paired meetings (11 BSE-only),
  NSE 107 (6 NSE-only), gap 0 in 98.9% / 98.1%; pairing rules A/B/C stated and their effect on gap 0
  measured (BSE 94 under all; NSE 105 of 107/110/116); stance subset 4 BSE, 7 NSE, all gap 0.
  Rerun: `python -I date_accuracy/measure.py date_accuracy/inputs` (output in measure_output.txt).
- "Dev claims not confirmed" (94/1 table, SME-like 68 split): the 94/1 BSE table is now reproducible
  from saved inputs. The SME-like 68 split still depends on the bhavcopy proxy; unchanged, labelled a proxy.
- Suggested catch (state data-availability precondition): agreed, proposed for the acceptance template.

## Caveats for QA
- Companies absent from the mapping CSV are "unmapped" (28 BSE, 21 NSE codes); in totals, not in listing class.
- NSE outcome filings are not typed as results outcomes; rule A selects via the stored results meeting. No text read.
- Only stored meetings are measured; missed meetings are not in the gap table (stated in findings).
- Round 1 wrote "116 scrips / 95 with meeting": the same 95 appear now by rule A.

Not done: SME exact count and 50-stance-company accuracy (follow-ups 2 and 1).
Found: mapping CSV lacks about 30% of codes seen in Q2 result filings, which limits any listing-class analysis.
