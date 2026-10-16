"""Copy, read-only, the product inputs the date-accuracy measurement reads into inputs/.
Run from the alto checkout root (needs the product data root; no network):
    python -I $TASK/date_accuracy/extract_inputs.py $TASK/date_accuracy/inputs
Selection is by exchange-stated fields only: BSE CATEGORYNAME == 'Result'; NSE desc == 'Outcome of Board Meeting'.
"""
import json, sys, glob
from pathlib import Path
sys.path.insert(0, ".")
from backend.config.paths import RESULTS_CALENDAR_PATH, DATA_ROOT, DAILY_ANNOUNCEMENTS_DIR
from backend.lib.company_resolver import CompanyResolver

out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
(out / "results_calendar.json").write_text(RESULTS_CALENDAR_PATH.read_text())
(out / "company_mapping.json").write_text(json.dumps(CompanyResolver().list_all()))
stance = sorted(d.name for d in (DATA_ROOT / "stances").iterdir()
                if d.is_dir() and (d / "log.jsonl").exists() and (d / "log.jsonl").stat().st_size > 0)
(out / "stance_keys.json").write_text(json.dumps(stance))
bse, nse, days = [], [], []
for f in sorted(glob.glob(str(DAILY_ANNOUNCEMENTS_DIR / "announcements_2026-10-*.json"))):
    day = Path(f).stem.split("_")[-1]; days.append(day)
    bse += [{"file_day": day, "row": a} for a in json.load(open(f))["announcements"] if a.get("CATEGORYNAME") == "Result"]
for f in sorted(glob.glob(str(DAILY_ANNOUNCEMENTS_DIR / "nse_announcements_2026-10-*.json"))):
    d = json.load(open(f)); day = Path(f).stem.split("_")[-1]
    nse += [{"file_day": day, "row": a} for a in d["announcements"] if a["desc"] == "Outcome of Board Meeting"]
(out / "bse_result_filings.json").write_text(json.dumps(bse))
(out / "nse_outcome_filings.json").write_text(json.dumps(nse))
print(len(stance), len(bse), len(nse), days[0], days[-1])
