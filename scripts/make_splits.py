"""WI-03: write (or --check) the four frozen SplitManifests from configs/splits.yaml. Prep IDs only; no data values."""
import sys, yaml
from agepretext.data.index import RecordingIndex
from agepretext.data.splits import make_group_splits
from agepretext.invariants import SplitPurpose
cfg = yaml.safe_load(open("configs/splits.yaml")); idx = RecordingIndex.load()
check = "--check" in sys.argv
for name, c in cfg.items():
    if name == "seed":
        continue
    kw = {k: v for k, v in c.items() if k not in ("purpose",)}
    m = make_group_splits(idx, name=name, purpose=SplitPurpose(c["purpose"]), seed=cfg["seed"], **kw)
    path = f"splits/{name}.json"
    if check:
        assert open(path).read() == m.to_json(), f"{path} differs from re-derivation"
    else:
        open(path, "w").write(m.to_json())
    sizes = {k: len(v) for k, v in m.partitions.items()}
    print(f"{name}: {'checked' if check else 'written'} sha={m.sha256()[:12]} partitions={sizes} folds={len(m.folds)}")
