#!/usr/bin/env bash
# Submission entry point. Must stay green (exit 0). Usage: bash reproduce.sh [--profile smoke|mvr|full]
# smoke: ledger verify + stub/config sanity + manifest (no data; used by CI).
# mvr/full: also fetch (sha256-verified), recon inventory, index, split --check, then the built pipeline stages.
set -euo pipefail
cd "$(dirname "$0")"
PROFILE=mvr
[[ "${1:-}" == "--profile" ]] && PROFILE="${2:-mvr}"
python -m agepretext.cli ledger verify
if [[ "$PROFILE" != "smoke" ]]; then
  python -m agepretext.cli fetch            # verify against data/manifests (downloads only if missing)
  python -m agepretext.cli recon
  python -m agepretext.cli index
  python -m agepretext.cli split --check    # splits are frozen; re-derivation must match byte-for-byte
  python -m agepretext.cli bin              # WI-P1: Potter QC, binned tensors, hand-crafted features
fi
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
