# Plan (round 2): spike, no product code
Touches: nothing in alto. Reads results_calendar store file, company mapping, stored daily BSE/NSE announcement files (read-only). Writes only date_accuracy/ and findings.md here. Not money path.
Change: acceptance item 2 re-done market-wide per D-20261016-2030. Items 1,3,4,5 unchanged.
Run: python -I date_accuracy/measure.py date_accuracy/inputs (offline); inputs copied by extract_inputs.py.
