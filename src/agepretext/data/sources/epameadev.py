"""Cotterill et al. 2016 EPAmeadev loader (Phase 2 dev corpus, lab epa_shafer). configs/data/epameadev.yaml.

Contract
--------
- `recordings(cfg, root)` -> one dict per (file, well) for all 48 wells of every plate file (silent wells kept):
  prep_id = culture date (with `prep_id_corrections`), plate_id = "<date>_<MW plate>", well_id = "<plate>:<well>",
  div from the filename, duration_s = last spike time in the file (no stored recording length), payload = "<relpath>#<well>".
- `read_spikes(path, well)` -> (times_s float64, electrode int16 0..15 within the well), electrodes ordered by name.
All wells are controls (h5 `treatment`); asserted where the field exists.
"""
import glob
import os
import re

import h5py
import numpy as np

PAT = re.compile(r"(ON|CO)_(\d{8})_(MW[\d-]+)_DIV(\d+)_")


def _wells(cfg):
    return [f"{r}{c}" for r in cfg["wells"]["rows"] for c in cfg["wells"]["cols"]]


def recordings(cfg: dict, root: str) -> list[dict]:
    out = []
    for f in sorted(glob.glob(os.path.join(root, cfg["files_glob"]))):
        m = PAT.match(os.path.basename(f))
        kind, date, mw, div = m.group(1), m.group(2), m.group(3), int(m.group(4))
        prep = cfg["prep_id_corrections"].get(date, date)
        with h5py.File(f, "r") as h:
            if "treatment" in h:
                assert {x.decode() for x in h["treatment"][()]} == {"control"}, f
            sp = h["spikes"][()]
        dur = float(sp.max()) if sp.size else 0.0
        plate = f"{prep}_{mw}"
        for w in _wells(cfg):
            out.append(dict(prep_id=prep, plate_id=plate, well_id=f"{plate}:{w}", div=div, plate_kind=kind,
                            duration_source="last_spike", duration_s=dur, row=w[0], col=int(w[1:]), payload=f"{os.path.relpath(f, root)}#{w}"))
    return out


def read_spikes(path: str, well: str) -> tuple[np.ndarray, np.ndarray]:
    with h5py.File(path, "r") as h:
        sp, n = h["spikes"][()], h["sCount"][()]
        names = [x.decode() for x in h["names"][()]]
    starts = np.concatenate([[0], np.cumsum(n)[:-1]])
    sel = sorted((nm, i) for i, nm in enumerate(names) if nm.split("_")[0] == well)
    ts, cs = [], []
    for e, (_, i) in enumerate(sel):
        ts.append(sp[starts[i]:starts[i] + n[i]]); cs.append(np.full(n[i], e, np.int16))
    if not ts:
        return np.zeros(0), np.zeros(0, np.int16)
    t, c = np.concatenate(ts), np.concatenate(cs)
    o = np.argsort(t, kind="stable")
    return t[o], c[o]
