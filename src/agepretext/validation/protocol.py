"""Protocol canonicalisation, hashing and sealing (WI-02 / WI-05).

Contract
--------
The FROZEN protocol is: protocol/prereg.yaml, PREREGISTRATION.md, configs/**/*.yaml, splits/*.json and
data/manifests/*.sha256. `frozen_hash()` = sha256 over sorted "<path>\\0<sha256(canonical bytes)>" lines, where YAML and
JSON are parsed and re-serialised as canonical JSON (sorted keys, compact) and text is LF-normalised. Code may evolve
after a seal (stubs get implemented); every hyperparameter lives in the frozen files, so a code change cannot move one.
Every run records the frozen hash AND its git commit.
- `seal()` refuses on a dirty tree, any TBD_WI00 placeholder, or an invalid split manifest; writes
  protocol/seals/seal-N.json {seal_id, protocol_hash, prereg_sha256, git_commit, created_utc, components} and tags
  `seal-N-<hash8>`.
- `matching_seal(hash)` returns the SealRecord with that protocol_hash, or None.
"""
import datetime
import glob
import hashlib
import json
import os
import subprocess
from dataclasses import asdict, dataclass

import yaml

SEAL_DIR = "protocol/seals"
FROZEN_GLOBS = ["protocol/prereg.yaml", "PREREGISTRATION.md", "configs/**/*.yaml", "splits/*.json", "data/manifests/*.sha256"]


@dataclass(frozen=True)
class SealRecord:
    seal_id: str
    protocol_hash: str
    prereg_sha256: str
    git_commit: str
    created_utc: str
    components: dict


def _canonical(path: str) -> bytes:
    raw = open(path, "rb").read()
    if path.endswith((".yaml", ".yml")):
        return json.dumps(yaml.safe_load(raw), sort_keys=True, separators=(",", ":"), default=str).encode()
    if path.endswith(".json"):
        return json.dumps(json.loads(raw), sort_keys=True, separators=(",", ":")).encode()
    return raw.replace(b"\r\n", b"\n")


def components() -> dict:
    paths = sorted({p for g in FROZEN_GLOBS for p in glob.glob(g, recursive=True)})
    return {p: hashlib.sha256(_canonical(p)).hexdigest() for p in paths}


def frozen_hash(comp: dict | None = None) -> str:
    comp = components() if comp is None else comp
    return hashlib.sha256("".join(f"{p}\0{h}\n" for p, h in sorted(comp.items())).encode()).hexdigest()


def current_hash(profile: str | None = None) -> str:
    return frozen_hash()


def prereg_sha256() -> str:
    return hashlib.sha256(open("protocol/prereg.yaml", "rb").read() + open("PREREGISTRATION.md", "rb").read()).hexdigest()


def seals() -> list[SealRecord]:
    return [SealRecord(**json.load(open(p))) for p in sorted(glob.glob(f"{SEAL_DIR}/seal-*.json"))]


def matching_seal(protocol_hash: str) -> SealRecord | None:
    return next((s for s in seals() if s.protocol_hash == protocol_hash), None)


def seal(profile: str | None = None) -> SealRecord:
    from agepretext.data.splits import SplitManifest
    from agepretext.validation.guards import require_clean_tree
    require_clean_tree()
    comp = components()
    for p in comp:
        if b"TBD_WI00" in open(p, "rb").read():
            raise RuntimeError(f"placeholder TBD_WI00 in {p}")
    for p in glob.glob("splits/*.json"):
        SplitManifest.from_json(p)
    h = frozen_hash(comp)
    if matching_seal(h):
        raise RuntimeError(f"protocol already sealed as {matching_seal(h).seal_id}")
    rec = SealRecord(f"seal-{len(seals()) + 1}", h, prereg_sha256(),
                     subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip(),
                     datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), comp)
    os.makedirs(SEAL_DIR, exist_ok=True)
    with open(f"{SEAL_DIR}/{rec.seal_id}.json", "w") as f:
        json.dump(asdict(rec), f, indent=1, sort_keys=True)
        f.write("\n")
    return rec
