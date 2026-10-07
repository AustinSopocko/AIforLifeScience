"""Charlesworth et al. 2015 g2chvcdata loader (Phase 2 dev corpus, lab eglen_grant). configs/data/g2chvc.yaml.

Contract
--------
- `recordings(cfg, root)` -> one dict per untreated array recording. Files whose name carries a drug token
  (cfg drug_tokens) are skipped and counted in `recordings.excluded`. prep_id = meta/DIV0 (plating date),
  plate_id = well_id = filename stem with the DIV token and "-preSham" removed, div = meta/age,
  region = hippocampus | cortex, genotype = meta/genotype, duration_s = recordingtime span, payload = relpath.
- `read_spikes(path)` -> (times_s float64, channel int16 index into the sorted channel names).
"""
import glob
import os
import re

import h5py
import numpy as np


def _s(x):
    return x.decode() if isinstance(x, bytes) else x


def recordings(cfg: dict, root: str) -> list[dict]:
    out, excl = [], {t: 0 for t in cfg["drug_tokens"]}
    for f in sorted(glob.glob(os.path.join(root, cfg["files_glob"]))):
        b = os.path.basename(f)
        hit = [t for t in cfg["drug_tokens"] if t.lower() in b.lower()]
        if hit:
            excl[hit[0]] += 1
            continue
        with h5py.File(f, "r") as h:
            g = lambda k: _s(h[k][()][0])
            rt = h["recordingtime"][()]
            prep, age, reg, gen = g("meta/DIV0"), int(g("meta/age")), g("meta/region"), g("meta/genotype")
        stem = re.sub(r"[-_]DIV\d+", "", b[:-3]).replace("-preSham", "")
        out.append(dict(prep_id=prep, plate_id=stem, well_id=stem, div=age, region=cfg["regions"][reg], genotype=gen,
                        duration_s=float(rt[1] - rt[0]), payload=os.path.relpath(f, root)))
    recordings.excluded = excl
    return out


def read_spikes(path: str) -> tuple[np.ndarray, np.ndarray]:
    with h5py.File(path, "r") as h:
        sp, n = h["spikes"][()], h["sCount"][()]
        names = [_s(x) for x in h["names"][()]]
    order = {nm: i for i, nm in enumerate(sorted(names))}
    c = np.repeat(np.array([order[nm] for nm in names], np.int16), n)
    o = np.argsort(sp, kind="stable")
    return sp[o], c[o]
