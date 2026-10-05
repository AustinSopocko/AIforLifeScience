"""WI-P1: Wagenaar dense -> data/processed/potter_bins/<recording_id>.npz (uint16 counts [W, E, 600]) and
data/processed/potter_handcrafted.parquet. Prints a summary only."""
import os, time
from multiprocessing import Pool
import numpy as np, pandas as pd, yaml
from agepretext.data.index import RecordingIndex
from agepretext.data.sources.potter import read_spikes
from agepretext.data.windows import bin_recording
from agepretext.features import potter_handcrafted as hc

cfg = yaml.safe_load(open("configs/model/set_encoder.yaml"))["input"]
QC = yaml.safe_load(open("configs/data/potter.yaml"))["qc"]; MIN_S, MAX_T = QC["min_duration_s"], QC["max_spike_time_s"]
OUT = "data/processed/potter_bins"

def one(row):
    rid, payload = row
    t, c = read_spikes(os.path.join("data/raw/potter", payload))
    ok = t <= MAX_T
    t, c = t[ok], c[ok]
    if t.max() < MIN_S:
        return {"recording_id": rid, "usable": False, "n_windows": int(t.max() // cfg["window_s"]), "n_electrodes": 0}
    eids = np.unique(c)
    counts, _, eids = bin_recording(t, c, eids, bin_ms=cfg["bin_ms"], window_s=cfg["window_s"])
    np.savez_compressed(os.path.join(OUT, f"{rid}.npz"), counts=counts, electrode_ids=eids)
    f = hc.compute(t, c, duration_s=counts.shape[0] * cfg["window_s"])
    return {"recording_id": rid, "usable": True, "n_windows": counts.shape[0], "n_electrodes": len(eids), **f}

if __name__ == "__main__":
    t0 = time.time(); os.makedirs(OUT, exist_ok=True)
    idx = RecordingIndex.load().table
    rows = list(idx[idx.source == "potter"][["recording_id", "payload"]].itertuples(index=False, name=None))
    with Pool(4) as p:
        res = p.map(one, rows, chunksize=4)
    df = pd.DataFrame(res).sort_values("recording_id")
    df.to_parquet("data/processed/potter_handcrafted.parquet", index=False)
    u = df[df.usable]
    print(f"{len(u)} of {len(df)} recordings binned (QC excluded {(~df.usable).sum()}) in {time.time()-t0:.0f}s; windows/rec median {u.n_windows.median():.0f} "
          f"(min {u.n_windows.min()}, max {u.n_windows.max()}); electrodes median {u.n_electrodes.median():.0f}")
    print(f"zero-burst recordings: {(u.network_burst_rate == 0).sum()}; disk {sum(os.path.getsize(os.path.join(OUT, f)) for f in os.listdir(OUT))/1e6:.0f} MB")
