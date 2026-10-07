"""Phase 2 F2: per-platform calibration of the BL-1 feature detector on DEV recordings only
(configs/features/burst_calibration.yaml, declared before this ran). Writes data/processed/f2_calib_features.parquet,
research/f2_burst_calibration.json and the `selected` block of the config. Prints a summary only.
`--round2`: the declared extension round (config `extension_round`, per-platform grids); final selection = best over
rounds 1 + 2; features cached in data/processed/f2_calib_features_round2.parquet."""
import itertools, json, os, sys, time
from multiprocessing import Pool
import h5py, numpy as np, pandas as pd, yaml
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from agepretext.data.index import RecordingIndex
from agepretext.data.qc import length_qc
from agepretext.data.sources import epa_mi, g2chvc
from agepretext.data.sources.potter import read_spikes as potter_spikes
from agepretext.eval.bootstrap import cluster_weighted_mae
from agepretext.features.potter_handcrafted import compute

CFG_PATH = "configs/features/burst_calibration.yaml"
CFG = yaml.safe_load(open(CFG_PATH))
G = CFG["grid"]
KEYS = ("bin_ms", "median_mult", "active_frac", "min_rate_hz")
expand = lambda g: [dict(zip(KEYS, v)) for v in itertools.product(*(g[k] for k in KEYS))]
GRID = expand(G)
ROUND2 = "--round2" in sys.argv
PLAT_GRID = {p: expand(g) for p, g in CFG["extension_round"]["grids"].items()} if ROUND2 else {}
SRC_PLAT = {s: p for p, pc in CFG["platforms"].items() for s in pc["dev_sources"]}
CAP = yaml.safe_load(open("configs/data/qc.yaml"))["potter_max_spike_time_s"]
WIN = yaml.safe_load(open("configs/data/qc.yaml"))["window_s"]


def feats(rid, t, c, span, grid):
    return [{"recording_id": rid, "setting": i, "mfr": f["mean_firing_rate"], "nbr": f["network_burst_rate"]}
            for i, p in enumerate(grid) for f in [compute(t, c, span, p)]]


def job(item):
    """One source file -> feature rows for every dev recording it holds."""
    src, path, recs = item          # recs: [(recording_id, well or None, span_s)]
    grid = PLAT_GRID.get(SRC_PLAT[src], GRID)
    feats_ = lambda rid, t, c, span: feats(rid, t, c, span, grid)
    out = []
    if src == "potter":
        t, c = potter_spikes(path); ok = t <= CAP; t, c = t[ok], c[ok]
        return feats_(recs[0][0], t, c, recs[0][2])
    if src == "g2chvc":
        t, c = g2chvc.read_spikes(path)
        return feats_(recs[0][0], t, c, recs[0][2])
    if src == "epameadev":
        with h5py.File(path, "r") as h:
            sp, n = h["spikes"][()], h["sCount"][()]
            names = [x.decode() for x in h["names"][()]]
        starts = np.concatenate([[0], np.cumsum(n)[:-1]])
        for rid, well, span in recs:
            sel = sorted((nm, i) for i, nm in enumerate(names) if nm.split("_")[0] == well)
            t = np.concatenate([sp[starts[i]:starts[i] + n[i]] for _, i in sel]) if sel else np.zeros(0)
            c = np.concatenate([np.full(n[i], e) for e, (_, i) in enumerate(sel)]) if sel else np.zeros(0, int)
            out += feats_(rid, t, c, span)
        return out
    if src == "epa_mi":
        d = epa_mi._read(path); d["w"] = d.e.astype(str).str.split("_").str[0]
        for rid, well, span in recs:
            x = d[d.w == well]
            names = sorted(x.e.unique())
            out += feats_(rid, x.t.to_numpy(), x.e.map({k: i for i, k in enumerate(names)}).to_numpy(), span)
        return out
    raise KeyError(src)


def oof_mae(df, seed, k):
    """BL-1: ridge alpha 1 on log1p features, standardised on the train fold; 4 group folds by cluster."""
    cl = sorted(df.cluster_id.unique())
    perm = [cl[i] for i in np.random.default_rng(seed).permutation(len(cl))]
    fold = {c: i for i, part in enumerate(np.array_split(np.array(perm, dtype=object), k)) for c in part}
    f = df.cluster_id.map(fold).to_numpy()
    X = np.log1p(df[["mfr", "nbr"]].to_numpy()); y = df.y_true_log_div.to_numpy(); pred = np.empty(len(df))
    for i in range(k):
        tr, te = f != i, f == i
        sc = StandardScaler().fit(X[tr])
        pred[te] = Ridge(alpha=1.0).fit(sc.transform(X[tr]), y[tr]).predict(sc.transform(X[te]))
    return cluster_weighted_mae(df.assign(p=pred), "p")


if __name__ == "__main__":
    t0 = time.time()
    idx = RecordingIndex.load().table
    dev = set(json.load(open("splits/dev_confirmatory.json"))["partitions"]["dev"])
    d = idx[idx.cluster_id.isin(dev)].copy()
    assert not d.source.isin(["fragilex", "kapucu_rat", "nfa"]).any()
    q = [length_qc(a, b, window_s=WIN) for a, b in zip(d.duration_s, d.duration_source)]
    d = d.assign(keep=[k for k, _ in q], span=[n * WIN if n else np.nan for _, n in q])[lambda x: x.keep]
    d["file"] = d.payload.str.split("#").str[0]
    d["well"] = d.payload.str.split("#").str[1]
    root = {s: f"data/raw/{s}" for s in d.source.unique()}
    items = [(s, os.path.join(root[s], f), list(zip(g.recording_id, g.well, g.span)))
             for (s, f), g in d.groupby(["source", "file"])]
    cache = "data/processed/f2_calib_features" + ("_round2" if ROUND2 else "") + ".parquet"
    if os.path.exists(cache):
        F = pd.read_parquet(cache)
    else:
        with Pool(4) as p:
            F = pd.DataFrame([r for rows in p.imap_unordered(job, items, chunksize=2) for r in rows])
        F.to_parquet(cache, index=False)
    F = F.merge(d.assign(y_true_log_div=np.log(d["div"]))[["recording_id", "cluster_id", "platform", "y_true_log_div"]],
                on="recording_id")
    ob = CFG["objective"]["cv"]
    res, sel = {}, {}
    r1 = json.load(open("research/f2_burst_calibration.json")) if ROUND2 else None
    for plat, pc in CFG["platforms"].items():
        if not pc["dev_sources"]:
            continue
        sub = F[F.platform == plat]
        grid = PLAT_GRID.get(plat, GRID)
        maes = [oof_mae(sub[sub.setting == i], ob["seed"], ob["k"]) for i in range(len(grid))]
        cand = list(zip(grid, maes))
        if ROUND2:                      # union with round 1; a setting present in both keeps its round-1 value
            seen = {json.dumps(g, sort_keys=True) for g in r1["grid"]}
            cand = list(zip(r1["grid"], r1["results"][plat]["all_mae"])) + [(g, m) for g, m in cand
                                                                            if json.dumps(g, sort_keys=True) not in seen]
        allg, allm = [g for g, _ in cand], [m for _, m in cand]
        best = int(np.argmin(allm)); order = np.argsort(allm, kind="stable")
        dflt = next(i for i, p in enumerate(allg) if p == CFG["seal1_default"])
        res[plat] = {"n_recordings": int(sub.recording_id.nunique()), "n_clusters": int(sub.cluster_id.nunique()),
                     "selected": allg[best], "selected_mae": allm[best], "seal1_default_mae": allm[dflt],
                     "seal1_default_rank": int(np.where(order == dflt)[0][0]) + 1, "n_settings": len(allg),
                     "top5": [{**allg[i], "mae": allm[i]} for i in order[:5]],
                     **({"round2_grid": grid, "round2_mae": maes} if ROUND2 else {"all_mae": maes})}
        sel[plat] = allg[best]
    sel["multiwell_64"] = sel["mcs_8x8"]
    out = "research/f2_burst_calibration" + ("_round2" if ROUND2 else "") + ".json"
    json.dump({"grid": GRID, "results": res}, open(out, "w"), indent=1)
    line = "selected:   " + json.dumps(sel, sort_keys=True).replace('"', "")
    txt = open(CFG_PATH).read()
    txt = txt.replace("selected: null", line) if not ROUND2 else txt.rstrip("\n") + "\n" + line + "   # final: best over rounds 1 + 2; frozen at Seal 2\n"
    open(CFG_PATH, "w").write(txt)
    for plat, r in res.items():
        print(f"{plat}: {r['n_recordings']} rec / {r['n_clusters']} clusters; selected {r['selected']} MAE {r['selected_mae']:.4f}; "
              f"Seal-1 default MAE {r['seal1_default_mae']:.4f} (rank {r['seal1_default_rank']}/{r.get('n_settings', len(GRID))})")
        for x in r["top5"]:
            print("   ", x)
    print(f"done in {time.time() - t0:.0f}s")
