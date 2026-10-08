"""Phase 3.1: bin every DEV recording for the pooled encoder -> data/processed/dev_bins/<recording_id>.npz
(counts uint16 [W, E, T], electrode_ids) + data/processed/dev_bins_meta.parquet. Prints a summary only.

Electrode set (3.1 decision): the platform's NOMINAL physical layout, silent electrodes as all-zero rows, so silence
is input and N is a platform constant (Axion 16 per well; Potter 59 = ids 0-59 minus reference 14; Charlesworth 60 = corpus
union of electrode numbers). Electrode order carries no meaning (the encoder is permutation-invariant); no position
feature is stored. Windows: Amendment A1 exclusions, then F1 (data/qc.py): n_windows from length_qc, zero after the last
spike for last-spike recordings shorter than one window. Bins: configs/model/set_encoder.yaml input (400 ms, 120 s)."""
import glob, json, os, re, time
from multiprocessing import Pool
import h5py, numpy as np, pandas as pd, yaml
from agepretext.data.index import RecordingIndex
from agepretext.data.qc import integrity_excluded, length_qc
from agepretext.data.sources import epa_mi, g2chvc
from agepretext.data.sources.potter import read_spikes as potter_spikes
from agepretext.data.windows import bin_recording

INP = yaml.safe_load(open("configs/model/set_encoder.yaml"))["input"]
BIN, WIN = INP["bin_ms"], INP["window_s"]
CAP = yaml.safe_load(open("configs/data/qc.yaml"))["potter_max_spike_time_s"]
OUT = "data/processed/dev_bins"
AXION = [f"{r}{c}" for r in "1234" for c in "1234"]
G2C_RE = re.compile(r"ch_(\d+)")


def save(rid, t, c, eids, nw):
    counts, _, _ = bin_recording(t, c, eids, bin_ms=BIN, window_s=WIN, duration_s=nw * WIN)
    np.savez_compressed(os.path.join(OUT, f"{rid}.npz"), counts=counts, electrode_ids=np.asarray(eids))
    return {"recording_id": rid, "n_windows": counts.shape[0], "n_electrodes": len(eids), "n_spikes_binned": int(counts.sum()),
            "n_silent_electrodes": int((counts.sum((0, 2)) == 0).sum())}


def job(item):
    src, path, recs, layout = item          # recs: [(recording_id, well, n_windows)]
    out = []
    if src == "potter":
        t, c = potter_spikes(path); ok = t <= CAP
        return [save(recs[0][0], t[ok], c[ok].astype(int), layout, recs[0][2])]
    if src == "g2chvc":
        with h5py.File(path, "r") as h:
            sp, n = h["spikes"][()], h["sCount"][()]
            el = [int(G2C_RE.match(x.decode()).group(1)) for x in h["names"][()]]
        return [save(recs[0][0], sp, np.repeat(el, n), layout, recs[0][2])]
    if src == "epameadev":
        with h5py.File(path, "r") as h:
            sp, n = h["spikes"][()], h["sCount"][()]
            names = [x.decode() for x in h["names"][()]]
        well = np.repeat([nm.split("_")[0] for nm in names], n)
        el = np.repeat([int(nm.split("_")[1]) for nm in names], n)
        for rid, w, nw in recs:
            k = well == w
            out.append(save(rid, sp[k], el[k], layout, nw))
        return out
    if src == "epa_mi":
        d = epa_mi._read(path)
        parts = d.e.astype(str).str.strip().str.split("_")
        d["w"], d["el"] = parts.str[0], parts.str[1].astype(int)
        for rid, w, nw in recs:
            x = d[d.w == w]
            out.append(save(rid, x.t.to_numpy(), x.el.to_numpy(), layout, nw))
        return out
    raise KeyError(src)


if __name__ == "__main__":
    t0 = time.time(); os.makedirs(OUT, exist_ok=True)
    idx = RecordingIndex.load().table
    dev = set(json.load(open("splits/dev_confirmatory.json"))["partitions"]["dev"])
    d = idx[idx.cluster_id.isin(dev) & ~idx.recording_id.isin(set(integrity_excluded()))].copy()
    assert not d.source.isin(["fragilex", "kapucu_rat", "nfa"]).any()
    d["nw"] = [length_qc(a, b, window_s=WIN)[1] for a, b in zip(d.duration_s, d.duration_source)]
    d["file"], d["well"] = d.payload.str.split("#").str[0], d.payload.str.split("#").str[1]
    # nominal layouts (platform constants)
    g2c = sorted({int(G2C_RE.match(x.decode()).group(1)) for f in glob.glob("data/raw/g2chvc/repo/inst/extdata/*.h5")
                  for x in h5py.File(f, "r")["names"][()]})
    layout = {"potter": [i for i in range(60) if i != 14], "g2chvc": g2c,
              "epameadev": [int(e) for e in AXION], "epa_mi": [int(e) for e in AXION]}
    items = [(s, os.path.join(f"data/raw/{s}", f), list(zip(g.recording_id, g.well, g.nw)), layout[s])
             for (s, f), g in d.groupby(["source", "file"])]
    done = {f[:-4] for f in os.listdir(OUT)}
    items = [it for it in items if not all(r[0] in done for r in it[2])]
    with Pool(4) as p:
        rows = [r for rs in p.imap_unordered(job, items, chunksize=2) for r in rs]
    meta = pd.read_parquet("data/processed/dev_bins_meta.parquet") if os.path.exists("data/processed/dev_bins_meta.parquet") else pd.DataFrame()
    meta = pd.concat([meta, pd.DataFrame(rows)]).drop_duplicates("recording_id", keep="last")
    meta = meta.merge(d[["recording_id", "lab", "source", "cluster_id", "plate_id", "div", "platform"]], on="recording_id")
    meta.to_parquet("data/processed/dev_bins_meta.parquet", index=False)
    print(meta.groupby("lab").agg(recs=("recording_id", "size"), windows=("n_windows", "sum"), E=("n_electrodes", "first"),
                                  silent_el_median=("n_silent_electrodes", "median")).to_string())
    print(f"layouts: potter {len(layout['potter'])}, g2chvc {len(g2c)}, axion 16; {time.time()-t0:.0f}s; "
          f"disk {sum(os.path.getsize(os.path.join(OUT, f)) for f in os.listdir(OUT))/1e6:.0f} MB")
