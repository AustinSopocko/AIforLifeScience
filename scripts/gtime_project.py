"""Re-project G-time from the MEASURED per-window costs in artifacts/g_time.json (no new timing) under the operator's
cut sequence. Per-fit cost scales with training-set size (k wells x recordings/well x 2 windows x epochs)."""
import json
import pandas as pd
import sys
g = json.load(open("artifacts/g_time.json")); tw, ti, E = g["sec_per_window_train"], g["sec_per_window_infer"], g["electrodes"]
if "--ms" in sys.argv:   # conservative: use the slower (ledgered) measurement, e.g. --ms 42.517 11.297
    i = sys.argv.index("--ms"); tw, ti = float(sys.argv[i + 1]) / 1000, float(sys.argv[i + 2]) / 1000
idx = pd.read_parquet("data/processed/recording_index.parquet"); hc = pd.read_parquet("data/processed/potter_handcrafted.parquet")
pot = idx[idx.source == "potter"].merge(hc[["recording_id", "usable", "n_windows"]], on="recording_id"); pot = pot[pot.usable]
folds = json.load(open("splits/potter_cv4.json"))["folds"]; pb = pot.groupby("prep_id").size()
ka = idx[idx.source == "kapucu_rat"]; rpw = ka.groupby(["prep_id", "well_id"]).size()
EP, WPR, KS = 40, 2, [1, 2, 4, 8, 16, "all"]
def project(M=3, canary_M=3, draws=30, seeds=5, draws_all=1):
    h = lambda s: s / 3600; c = {}
    c["potter_crossfit"] = h(sum(WPR * pb[f["train"]].sum() * EP * M * tw for f in folds.values()) + pot.n_windows.sum() * M * ti)
    c["potter_final"] = h(WPR * len(pot) * EP * M * tw + pot.n_windows.sum() * M * ti)
    c["c2_canary_x10"] = 10 * h(WPR * len(pot) * EP * canary_M * tw + pot.n_windows.sum() * canary_M * ti)
    kap, fits = 0.0, 0
    for hold in ["190617", "250417", "31017"]:
        pool = rpw.drop(hold, level=0)
        for k in KS:
            kk, d = (len(pool), draws_all) if k == "all" else (k, draws)
            kap += d * seeds * EP * WPR * kk * pool.mean() * tw * 64 / E; fits += d * seeds
    c["kapucu_bl_a2"] = h(kap); c["kapucu_inference"] = h(len(ka) * 5 * (M + 1) * ti * 64 / E)
    return c, sum(c.values()), fits
steps = [("as projected (k=all already 1 draw)", {}), ("1. draws=1 at k=all", {"draws_all": 1}),
         ("2. C2 canary M=1", {"canary_M": 1}), ("3. draws 30->15, seeds 5->2", {"canary_M": 1, "draws": 15, "seeds": 2}),
         ("4. Wagenaar ensemble M 3->1", {"canary_M": 1, "draws": 15, "seeds": 2, "M": 1})]
out = []
for name, kw in steps:
    c, tot, fits = project(**kw); out.append({"step": name, "total_h": round(tot, 2), "bl_a2_fits": fits, **{k: round(v, 2) for k, v in c.items()}})
    print(f"{name:<38} total {tot:6.2f} h | BL-A2 fits {fits:4d} | " + " ".join(f"{k}={v:.2f}" for k, v in c.items()))
for hold in ["190617", "250417", "31017"]:
    pool = rpw.drop(hold, level=0); print(f"fold hold-out {hold}: labelled pool {len(pool)} wells, mean recordings/well {pool.mean():.2f}, held-out wells {len(rpw[hold])}")
json.dump(out, open("artifacts/g_time_reprojection.json", "w"), indent=1)
