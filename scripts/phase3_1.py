"""Phase 3.1 (DEV only, exploratory): permutation-invariant electrode handling.
Stages (each checkpointed under artifacts/phase3_1/, resumable): lolo -> final -> hlab -> canary -> report.
Parameters are declared in configs/train/sampling.yaml + research/phase3_1_run.yaml (ledgered before this ran).
PHASE31_SMOKE=1 runs a 1-epoch plumbing check into artifacts/phase3_1_smoke (never reported)."""
import hashlib, json, os, sys, time
import numpy as np, pandas as pd, torch, yaml
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from agepretext.data.qc import old_rule_drop
from agepretext.eval.bootstrap import TooFewClusters, cluster_weighted_mae, paired_cluster_mae_bootstrap
from agepretext.eval.identity_probe import group_probe
from agepretext.eval.verdicts import verdict
from agepretext.train.pooled import load_dev, predict, scheme_a_weights, train_pooled

SMOKE = os.environ.get("PHASE31_SMOKE") == "1"
OUT = "artifacts/phase3_1" + ("_smoke" if SMOKE else ""); os.makedirs(OUT, exist_ok=True)
E = yaml.safe_load(open("research/phase3_1_run.yaml"))
MCFG = yaml.safe_load(open("configs/model/set_encoder.yaml"))
TCFG = {**yaml.safe_load(open("configs/train/pretext.yaml")), "threads": E["threads"]}
M = yaml.safe_load(open("configs/train/sampling.yaml"))["m_windows_per_cluster_per_epoch"]
if SMOKE:                                   # plumbing check only; never reported
    TCFG["epochs"], M = 1, 4
    E["probe"]["n_perm"], E["canary"]["seeds"] = 5, 1
PRE = yaml.safe_load(open("protocol/prereg.yaml"))
BS = PRE["statistics"]["bootstrap"]
LOG = open(f"{OUT}/progress.log", "a")


def log(msg):
    LOG.write(f"{time.strftime('%H:%M:%S')} {msg}\n"); LOG.flush()


def bl1_features():
    """Per-platform calibrated BL-1 features (F2 `selected`) from the F2 feature caches (dev, analysed span = F1 windows)."""
    cal = yaml.safe_load(open("configs/features/burst_calibration.yaml"))
    keys = ("bin_ms", "median_mult", "active_frac", "min_rate_hz")
    import itertools
    grids = {p: [dict(zip(keys, v)) for v in itertools.product(*(g[k] for k in keys))]
             for p, g in cal["extension_round"]["grids"].items()}
    F = pd.read_parquet("data/processed/f2_calib_features_round2.parquet")
    meta = pd.read_parquet("data/processed/dev_bins_meta.parquet")[["recording_id", "platform"]]
    F = F.merge(meta, on="recording_id")
    sel = {p: grids[p].index(cal["selected"][p]) for p in grids}
    F = F[F.setting == F.platform.map(sel)]
    return F.set_index("recording_id")[["mfr", "nbr"]]


def baselines(tr: pd.DataFrame, te: pd.DataFrame, w: np.ndarray) -> pd.DataFrame:
    """BL-0 / BL-1, each in two implementations (scheme-A weighted, unweighted); the encoder must beat all four."""
    out = pd.DataFrame(index=te.index)
    y = tr.y_true_log_div.to_numpy()
    out["bl0_w"], out["bl0_u"] = float((w * y).sum() / w.sum()), float(y.mean())
    X, Xt = np.log1p(tr[["mfr", "nbr"]].to_numpy()), np.log1p(te[["mfr", "nbr"]].to_numpy())
    for tag, sw in (("w", w), ("u", None)):
        sc = StandardScaler().fit(X, sample_weight=sw)
        out[f"bl1_{tag}"] = Ridge(alpha=1.0).fit(sc.transform(X), y, sample_weight=sw).predict(sc.transform(Xt))
    return out


def stage_lolo(recs, meta, feats):
    lolo = json.load(open("splits/dev_lolo.json"))
    for f, (lab, fold) in enumerate(sorted(lolo["folds"].items())):
        path = f"{OUT}/lolo_{lab}.parquet"
        if os.path.exists(path):
            continue
        t0 = time.time()
        tr = [r for r in recs if r["cluster_id"] in set(fold["train"])]
        te = [r for r in recs if r["cluster_id"] in set(fold["test"])]
        assert {r["lab"] for r in te} == {lab} and lab not in {r["lab"] for r in tr}
        model, stats = train_pooled(tr, MCFG, TCFG, M, E["seeds"]["lolo"] + f)
        p = predict(model, stats, te)[["recording_id", "y_true_log_div", "y_pred_log_div"]].rename(columns={"y_pred_log_div": "enc"})
        trd = meta.set_index("recording_id").loc[[r["recording_id"] for r in tr]].join(feats)
        trd["y_true_log_div"] = np.log(trd["div"])
        ted = meta.set_index("recording_id").loc[p.recording_id].join(feats)
        b = baselines(trd, ted, scheme_a_weights(tr))
        p = p.set_index("recording_id").join(b).join(meta.set_index("recording_id")[["lab", "cluster_id", "div", "source"]])
        p.reset_index().to_parquet(path, index=False)
        log(f"lolo {lab}: train {len(tr)} rec / {len({r['cluster_id'] for r in tr})} clusters, {time.time()-t0:.0f}s")


def evaluate_lolo(meta):
    d = pd.concat([pd.read_parquet(f"{OUT}/lolo_{l}.parquet") for l in ("eglen_grant", "epa_shafer", "potter_gatech")])
    idx = pd.read_parquet("data/processed/recording_index.parquet").set_index("recording_id")
    d["old_rule_drop"] = [old_rule_drop(*idx.loc[r, ["duration_s", "duration_source"]]) for r in d.recording_id]
    comps = {"BL-0": ("bl0_w", "bl0_u"), "BL-1": ("bl1_w", "bl1_u")}

    def block(x, strata):
        res = {"n_recordings": len(x), "n_clusters": int(x.cluster_id.nunique()),
               "mae": {c: cluster_weighted_mae(x, c, strata_col=strata) for c in ("enc", "bl0_w", "bl0_u", "bl1_w", "bl1_u")}}
        paired, verdicts = {}, {}
        for impl in (0, 1):
            pr = {}
            for b, cols in comps.items():
                try:
                    r = paired_cluster_mae_bootstrap(x, "enc", cols[impl], strata_col=strata, n_resamples=BS["n_resamples"],
                                                     seed=BS["seed"], min_clusters=BS["min_clusters"])
                    paired[f"enc-{cols[impl]}"] = r.__dict__; pr[b] = r
                except TooFewClusters:
                    paired[f"enc-{cols[impl]}"] = None; pr[b] = None
            verdicts["weighted" if impl == 0 else "unweighted"] = verdict("primary", {"paired": pr}, PRE).label
        res["paired_delta"] = paired
        res["verdict_per_implementation"] = verdicts
        res["verdict"] = "SUPPORTS" if set(verdicts.values()) == {"SUPPORTS"} else (
            "INCONCLUSIVE" if "INCONCLUSIVE" in verdicts.values() else "REFUTES")
        return res

    rep = {"primary": block(d, "lab"),
           "overlap_div_7_12": block(d[d["div"].between(7, 12)], "lab"),
           "seal1_qc_sensitivity": block(d[~d.old_rule_drop], "lab"),
           "per_fold": {l: block(g, None) for l, g in d.groupby("lab")},
           "per_div_bin_mae": {}}
    bins = [(2, 6), (7, 12), (13, 20), (21, 39)]
    for l, g in d.groupby("lab"):
        rep["per_div_bin_mae"][l] = {f"{a}-{b}": {c: (cluster_weighted_mae(h, c) if len(h) else None) for c in ("enc", "bl1_w", "bl1_u")}
                                     for a, b in bins for h in [g[g["div"].between(a, b)]]}
    return rep


def stage_final(recs):
    if os.path.exists(f"{OUT}/final_z.parquet"):
        return
    t0 = time.time()
    model, stats = train_pooled(recs, MCFG, TCFG, M, E["seeds"]["final"])
    torch.save(model.state_dict(), f"{OUT}/final_model.pt"); json.dump(stats, open(f"{OUT}/final_stats.json", "w"))
    sub = [r for r in recs if 7 <= r["div"] <= 12]
    predict(model, stats, sub).to_parquet(f"{OUT}/final_z.parquet", index=False)
    log(f"final model: {time.time()-t0:.0f}s")


def stage_hlab(meta, feats):
    if os.path.exists(f"{OUT}/hlab.json"):
        return
    z = pd.read_parquet(f"{OUT}/final_z.parquet").merge(meta[["recording_id", "lab", "cluster_id"]], on="recording_id")
    Z = z[[c for c in z if c.startswith("z_")]].to_numpy()
    real = group_probe(Z, z.lab.to_numpy(), z.cluster_id.to_numpy(), n_perm=E["probe"]["n_perm"], n_jobs=E["threads"])
    hc = feats.loc[z.recording_id]
    hand = group_probe(np.log1p(hc[["mfr", "nbr"]].to_numpy()), z.lab.to_numpy(), z.cluster_id.to_numpy(),
                       n_perm=E["probe"]["n_perm"], n_jobs=E["threads"])
    rc = z.lab.isin(["potter_gatech", "epa_shafer"]).to_numpy()
    rat = group_probe(Z[rc], z.lab[rc].to_numpy(), z.cluster_id[rc].to_numpy(), n_perm=E["probe"]["n_perm"], n_jobs=E["threads"])
    json.dump({"real_lab_probe": real.__dict__, "handcrafted_probe": hand.__dict__, "rat_cortex_potter_vs_epa": rat.__dict__,
               "n_recordings": len(z)}, open(f"{OUT}/hlab.json", "w"), indent=1)
    log("hlab probes done")


def stratum_rate(recs):
    rates = []
    for r in recs:
        if 7 <= r["div"] <= 12:
            c = r["counts"].sum(axis=(0, 2)) / (r["counts"].shape[0] * yaml.safe_load(open("configs/model/set_encoder.yaml"))["input"]["window_s"])
            rates += c[c > 0].tolist()
    return float(np.median(rates))


def inject(recs, positive: set, rate_hz: float, seed: int):
    """Pseudo-lab canary: in every recording of a canary-positive cluster, a seeded random 10% of electrodes
    (Axion 2 of 16, MCS 6 of 59/60) get extra Poisson spikes at the stratum median electrode rate in every bin."""
    lam = rate_hz * MCFG["input"]["bin_ms"] / 1000
    out = []
    for r in recs:
        if r["cluster_id"] not in positive:
            out.append(r); continue
        h = int(hashlib.sha1(f"{seed}|{r['recording_id']}".encode()).hexdigest()[:8], 16)
        g = np.random.default_rng(h)
        W, En, T = r["counts"].shape
        k = max(1, int(round(E["canary"]["electrode_fraction"] * En)))
        el = g.choice(En, size=k, replace=False)
        c = r["counts"].copy()
        c[:, el, :] = np.minimum(c[:, el, :].astype(np.int64) + g.poisson(lam, size=(W, k, T)), 65535).astype(np.uint16)
        out.append({**r, "counts": c})
    return out


def stage_canary(recs, meta):
    rate = stratum_rate(recs)
    clusters = meta.drop_duplicates("cluster_id")[["cluster_id", "lab"]].sort_values("cluster_id")
    lo, hi = map(int, os.environ.get("CANARY_SEEDS", f"0-{E['canary']['seeds'] - 1}").split("-"))   # resumable chunks
    for s in range(lo, hi + 1):
        path = f"{OUT}/canary_{s:02d}.json"
        if os.path.exists(path):
            continue
        t0 = time.time()
        g = np.random.default_rng(E["seeds"]["canary"] + s)
        pos = set()
        for lab, cl in clusters.groupby("lab"):
            ids = sorted(cl.cluster_id)
            pos |= set(g.choice(ids, size=len(ids) // 2, replace=False).tolist())
        rc = inject(recs, pos, rate, E["seeds"]["canary"] + s)
        model, stats = train_pooled(rc, MCFG, TCFG, M, E["seeds"]["canary"] + s)
        sub = [r for r in rc if 7 <= r["div"] <= 12]
        z = predict(model, stats, sub)
        cl = pd.Series([r["cluster_id"] for r in sub]); lab = pd.Series([r["lab"] for r in sub])
        Z = z[[c for c in z if c.startswith("z_")]].to_numpy()
        res = group_probe(Z, cl.isin(pos).astype(int).to_numpy(), cl.to_numpy(), strata=lab.to_numpy(),
                          n_perm=E["probe"]["n_perm"], n_jobs=E["threads"])
        json.dump({"seed": s, "rate_hz": rate, "positive_clusters": sorted(pos), "probe": res.__dict__,
                   "detected": res.p_value < E["canary"]["detection_alpha"]}, open(path, "w"), indent=1)
        log(f"canary seed {s}: p={res.p_value:.4f} excessBA={res.excess_balanced_accuracy:.3f} {time.time()-t0:.0f}s")


if __name__ == "__main__":
    stages = sys.argv[1:] or ["lolo", "final", "hlab", "canary", "report"]
    meta = pd.read_parquet("data/processed/dev_bins_meta.parquet")
    feats = bl1_features()
    recs = load_dev(meta) if set(stages) & {"lolo", "final", "canary"} else None
    log(f"start {stages}; m={M}; threads={E['threads']}")
    if "lolo" in stages: stage_lolo(recs, meta, feats)
    if "final" in stages: stage_final(recs)
    if "hlab" in stages: stage_hlab(meta, feats)
    if "canary" in stages: stage_canary(recs, meta)
    if "report" in stages:
        rep = {"lolo": evaluate_lolo(meta), "hlab": json.load(open(f"{OUT}/hlab.json"))}
        cs = [json.load(open(f"{OUT}/canary_{s:02d}.json")) for s in range(E["canary"]["seeds"]) if os.path.exists(f"{OUT}/canary_{s:02d}.json")]
        power = float(np.mean([c["detected"] for c in cs])) if cs else None
        real_p = rep["hlab"]["real_lab_probe"]["p_value"]
        a, req = E["canary"]["detection_alpha"], E["canary"]["required_power"]
        label = "INCONCLUSIVE" if power is None or power < req else ("SUPPORTS" if real_p >= a else "REFUTES")
        rep["canary"] = {"n_seeds": len(cs), "power": power, "rate_hz": cs[0]["rate_hz"] if cs else None,
                         "per_seed": [{"seed": c["seed"], "p": c["probe"]["p_value"], "excess_ba": c["probe"]["excess_balanced_accuracy"]} for c in cs]}
        rep["hlab_identity_rule"] = label
        json.dump(rep, open(f"{OUT}/report.json", "w"), indent=1, default=float)
        log("report written")
