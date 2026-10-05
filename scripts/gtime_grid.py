"""Re-project G-time for BL-A2 grid schedules (G1 taper, G2 verdict-point restriction) + earlier cuts.
Uses the conservative ledgered 42.517 / 11.297 ms per window. No timing, no fits."""
import json
import math
import pandas as pd
TW, TI, E = 0.042517, 0.011297, 56
idx = pd.read_parquet("data/processed/recording_index.parquet"); hc = pd.read_parquet("data/processed/potter_handcrafted.parquet")
pot = idx[idx.source == "potter"].merge(hc[["recording_id", "usable", "n_windows"]], on="recording_id"); pot = pot[pot.usable]
folds = json.load(open("splits/potter_cv4.json"))["folds"]; pb = pot.groupby("prep_id").size()
rpw = idx[idx.source == "kapucu_rat"].groupby(["prep_id", "well_id"]).size()
EP, WPR, N = 40, 2, 24
def fpc(k): return (1 / k) * (N - k) / (N - 1)          # between-draw variance of a k-of-N mean (w/o replacement)
def project(bl, M=3, canary_M=3):
    h = lambda s: s / 3600; c = {}
    c["wagenaar_crossfit"] = h(sum(WPR * pb[f["train"]].sum() * EP * M * TW for f in folds.values()) + pot.n_windows.sum() * M * TI)
    c["wagenaar_final"] = h(WPR * len(pot) * EP * M * TW + pot.n_windows.sum() * M * TI)
    c["c2_canary_x10"] = 10 * h(WPR * len(pot) * EP * canary_M * TW + pot.n_windows.sum() * canary_M * TI)
    s = fits = 0
    for hold in ["190617", "250417", "31017"]:
        pool = rpw.drop(hold, level=0)
        for k, (d, sd) in bl.items():
            kk = len(pool) if k == "all" else k
            s += d * sd * EP * WPR * kk * pool.mean() * TW * 64 / E; fits += d * sd
    c["kapucu_bl_a2"] = h(s); c["kapucu_inference"] = h(192 * 5 * (M + 1) * TI * 64 / E)
    return c, sum(c.values()), fits
orig = {1: (30, 5), 2: (30, 5), 4: (30, 5), 8: (30, 5), 16: (30, 5), "all": (1, 5)}
taper = {1: 30, 2: 20, 4: 12, 8: 6, 16: 3}
g1 = {**{k: (d, 5) for k, d in taper.items()}, "all": (1, 5)}
g12 = {**g1, 4: (30, 5)}                                                     # G2: full grid at verdict points k=4, all
half = {k: (1 if k == "all" else max(1, math.ceil(d / 2)), 2) for k, (d, _) in g12.items()}   # cut step 3 on the G1+G2 grid
print("k  overlap(k/N)  rel.between-draw var  taper draws  MC-SE ratio vs k=1@30")
for k, d in taper.items():
    print(f"{k:<3} {k/N:10.2f} {fpc(k):18.3f} {d:12d} {math.sqrt(fpc(k)/d)/math.sqrt(fpc(1)/30):18.2f}")
steps = [("original grid", orig, {}), ("G1 taper", g1, {}), ("G1+G2", g12, {}), ("+cut1 draws=1 at all (already)", g12, {}),
         ("+cut2 C2 canary M=1", g12, {"canary_M": 1}), ("+cut3 draws/2, seeds 5->2", half, {"canary_M": 1}),
         ("+cut4 Wagenaar M 3->1", half, {"canary_M": 1, "M": 1})]
out = []
for name, bl, kw in steps:
    c, tot, fits = project(bl, **kw); out.append({"step": name, "total_h": round(tot, 2), "bl_a2_fits": fits, "bl_a2_grid": {str(k): v for k, v in bl.items()}, **{k: round(v, 2) for k, v in c.items()}})
    print(f"{name:<32} {tot:6.2f} h | fits {fits:4d} | " + " ".join(f"{k.split('_',1)[1] if k.startswith('kapucu') else k}={v:.2f}" for k, v in c.items()))
vp = {4: (30, 5), "all": (1, 5)}
c, tot, _ = project({"all": (1, 5)}, canary_M=1, M=1); print(f"[info] verdict points only, BL-A2 at k=all only, cuts 1,2,4: {tot:.2f} h")
json.dump(out, open("artifacts/g_time_grid.json", "w"), indent=1)
