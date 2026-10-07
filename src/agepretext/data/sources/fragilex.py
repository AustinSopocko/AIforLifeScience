"""Moskalyuk et al. 2020 Fragile-X loader (Phase 2 dev corpus, lab giugliano). configs/data/fragilex.yaml.

Contract
--------
- `recordings(cfg, root)` -> one dict per MEA recording file (macOS metadata ignored). prep_id = "CS<session>",
  plate_id = well_id = "CS<session>_<MEA id>" (physical MEAs are reused across sessions),
  div from filename, genotype = wt | fmr1_ko (covariate, not a treatment),
  duration_s = last spike time, payload = relpath.
- `read_spikes(path)` -> (times_s float64, electrode int16 0..59).
"""
import glob
import os
import re

import numpy as np
import scipy.io as sio

PAT = re.compile(r"(\d+)_(wt|ko)_(I\d+)_div(\d+)_sp_(\d{12})_spikes\.mat$")


def recordings(cfg: dict, root: str) -> list[dict]:
    out = []
    for f in sorted(glob.glob(os.path.join(root, "extracted/MEA_experiments/*/CultureSession*/MEA_*/*_spikes.mat"))):
        if any(s in f for s in cfg["ignore"]):
            continue
        sess, gen, mea, div, ts = PAT.search(os.path.basename(f)).groups()
        t, _ = read_spikes(f)
        out.append(dict(prep_id=f"CS{sess}", plate_id=f"CS{sess}_{mea}", well_id=f"CS{sess}_{mea}", div=int(div), genotype=cfg["genotype"][gen.upper()],
                        timestamp=ts, duration_source="last_spike", duration_s=float(t.max()) if t.size else 0.0, payload=os.path.relpath(f, root)))
    return out


def read_spikes(path: str) -> tuple[np.ndarray, np.ndarray]:
    s = sio.loadmat(path)["spikes"]
    t, c = s[:, 0] / 1000.0, (s[:, 1] - 1).astype(np.int16)
    o = np.argsort(t, kind="stable")
    return t[o], c[o]
