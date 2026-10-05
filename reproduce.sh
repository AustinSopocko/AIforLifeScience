#!/usr/bin/env bash
# Submission entry point. Must stay green (exit 0). Usage: bash reproduce.sh [--profile smoke|mvr|full]
# S0: environment + stub/config sanity, then prints the artefact manifest (artefacts.yaml).
# Nothing is computed yet; every unbuilt artefact is listed as TODO. No network, no data access.
set -euo pipefail
cd "$(dirname "$0")"
python -m agepretext.cli ledger verify
PROFILE=mvr
[[ "${1:-}" == "--profile" ]] && PROFILE="${2:-mvr}"
python - "$PROFILE" <<'PY'
import glob, importlib, os, pkgutil, sys
import yaml
import agepretext
profile = sys.argv[1]
assert os.path.exists(f"configs/profiles/{profile}.yaml"), f"unknown profile {profile}"
mods = [m.name for m in pkgutil.walk_packages(agepretext.__path__, "agepretext.")]
for m in mods:
    importlib.import_module(m)
cfgs = glob.glob("configs/**/*.yaml", recursive=True) + ["protocol/prereg.yaml", "workitems.yaml"]
for f in cfgs:
    yaml.safe_load(open(f))
arts = yaml.safe_load(open("artefacts.yaml"))["artefacts"]
check = lambda a: a.get("tracked") or profile != "smoke"
missing = [a["path"] for a in arts if a["status"] == "DONE" and check(a) and not glob.glob(a["path"].split(" ")[0])]
todo = sum(a["status"] == "TODO" for a in arts)
print(f"reproduce.sh profile={profile}: {len(mods)} modules import, {len(cfgs)} YAML files parse")
print("ARTEFACT MANIFEST")
for a in arts:
    print(f"  [{a['status']}] {a['wi']:<6} {a['path']:<44} {a['what']}")
print(f"{len(arts)} artefacts: {len(arts) - todo} DONE, {todo} TODO")
if missing:
    sys.exit(f"DONE artefacts missing: {missing}")
PY
