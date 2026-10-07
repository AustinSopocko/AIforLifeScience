"""Ball et al. 2017 EPA "Mutual Information" ontogeny plates (Phase 2 dev corpus, lab epa_shafer). configs/data/epa_mi.yaml.

Contract
--------
- `recordings(cfg, root)` -> one dict per (recording file, CONTROL well) — columns 1 and 8, rows A-F (12 per plate);
  treated wells (cols 2-7) and post-bicuculline `_01` recordings never enter the index.
  prep_id = culture date (shared with EPAmeadev where dates coincide), plate_id = "<date>_<MW plate>",
  well_id = "<plate>:<well>", duration_s = "Analysis Duration (s)" of the matching Neural Statistics Compiler file
  (duration_source "stored"; F1); plate 20140423 has no such file -> last spike, "last_spike", payload = "<relpath>#<well>".
- `read_spikes(path, well)` -> (times_s float64, electrode int16 within the well, ordered by electrode name).
  Axion trailer rows (non-numeric time) are dropped.
"""
import glob
import os
import re

import numpy as np
import pandas as pd

PAT = re.compile(r"ON_(\d{8})_(MW[\d-]+)_(\d+)_(\d\d)\(000\)_Spike Detector")


def _read(path):
    d = pd.read_csv(path, usecols=[2, 3], encoding="latin-1", low_memory=False)
    d.columns = ["t", "e"]
    d["t"] = pd.to_numeric(d.t, errors="coerce")
    return d.dropna()


def stored_duration(spike_list_path: str) -> float | None:
    nsc = re.sub(r"Spike Detector \(8 x STD\)(\(\d+\))_spike_list", r"Neural Statistics Compiler\1", spike_list_path)
    if not os.path.exists(nsc):
        return None                       # plate 20140423_MW1007-38 ships no statistics file
    for line in open(nsc, encoding="latin-1"):
        if line.startswith("Analysis Duration (s)"):
            return float(line.split(",")[1])
    raise ValueError(f"no Analysis Duration in {nsc}")


def recordings(cfg: dict, root: str) -> list[dict]:
    out = []
    wells = [f"{r}{c}" for r in cfg["control_wells"]["rows"] for c in cfg["control_wells"]["cols"]]
    for f in sorted(glob.glob(os.path.join(root, cfg["files_glob"]))):
        m = PAT.match(os.path.basename(f))
        date, mw, divtok, rec = m.groups()
        assert rec == "00", f
        div = cfg["div_token_fix"].get(divtok, int(divtok))
        dur = stored_duration(f)
        src = "stored" if dur is not None else "last_spike"
        dur = dur if dur is not None else float(_read(f).t.max())
        plate = f"{date}_{mw}"
        for w in wells:
            out.append(dict(prep_id=date, plate_id=plate, well_id=f"{plate}:{w}", div=int(div), duration_s=dur,
                            duration_source=src,
                            row=w[0], col=int(w[1:]), payload=f"{os.path.relpath(f, root)}#{w}"))
    return out


def read_spikes(path: str, well: str) -> tuple[np.ndarray, np.ndarray]:
    d = _read(path)
    d = d[d.e.astype(str).str.split("_").str[0] == well]
    names = sorted(d.e.unique())
    c = d.e.map({n: i for i, n in enumerate(names)}).to_numpy(np.int16)
    t = d.t.to_numpy(np.float64)
    o = np.argsort(t, kind="stable")
    return t[o], c[o]
