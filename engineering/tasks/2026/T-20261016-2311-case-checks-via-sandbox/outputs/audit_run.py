"""Run stage_fleet.cli with an audit hook: any open() under the live data root
raises (as if every live file, the legacy chain starts included, were removed),
and every path opened is counted."""
import os, runpy, sys
LIVE = "/Users/kmrh581/personal/projects/workspace/news_server"
opened = {"live": [], "sandbox": 0}
def hook(event, args):
    if event == "open" and isinstance(args[0], (str, bytes, os.PathLike)):
        p = os.path.realpath(os.fsdecode(args[0]))
        if p.startswith(LIVE + "/"):
            opened["live"].append(p)
            raise PermissionError(f"live path opened: {p}")
        if "alto_sandboxes" in p:
            opened["sandbox"] += 1
sys.addaudithook(hook)
sys.argv = ["cli"] + sys.argv[1:]
try:
    runpy.run_module("backend.validation.stage_fleet.cli", run_name="__main__")
finally:
    print(f"AUDIT live opens: {opened['live']}; sandbox opens: {opened['sandbox']}", file=sys.stderr)
