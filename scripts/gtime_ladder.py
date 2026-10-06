"""Shrink-ladder timing (D8): measure per-window train/inference cost for ladder configs on the SAME real Potter
culture used by G-time (1-2), as a ratio to a same-session baseline; scale the ledgered 42.517/11.297 ms by that ratio
(conservative); project on top of G1+G2 + cut 2 (canary M=1) + cut 4 (Wagenaar M=1). No fits, random-init weights."""
import copy, json, os, statistics, time
import numpy as np, pandas as pd, torch, yaml
from agepretext.models.set_encoder import SetEncoder
torch.manual_seed(0); torch.set_num_threads(os.cpu_count())
base_cfg = yaml.safe_load(open("configs/model/set_encoder.yaml"))
idx = pd.read_parquet("data/processed/recording_index.parquet"); hc = pd.read_parquet("data/processed/potter_handcrafted.parquet")
pot = idx[idx.source == "potter"].merge(hc[["recording_id", "usable", "n_windows"]], on="recording_id"); pot = pot[pot.usable]
X = [np.load(f"data/processed/potter_bins/{r}.npz")["counts"] for r in pot[pot.plate_id == "1-2"].recording_id]
Emax = max(x.shape[1] for x in X)
W200 = np.concatenate([np.pad(x, ((0, 0), (0, Emax - x.shape[1]), (0, 0))) for x in X]).astype(np.float32)
MASK = np.concatenate([np.pad(np.ones(x.shape[:2], bool), ((0, 0), (0, Emax - x.shape[1]))) for x in X])
def timeit(cfg, W, reps=3):
    model = SetEncoder(cfg); opt = torch.optim.AdamW(model.parameters(), lr=1e-3); bs = 64
    def run(train):
        t0 = time.perf_counter()
        for i in range(0, len(W), bs):
            xb, mb = torch.from_numpy(W[i:i + bs]), torch.from_numpy(MASK[i:i + bs])
            if train:
                _, p = model(xb, mb); loss = (p ** 2).mean(); opt.zero_grad(); loss.backward(); opt.step()
            else:
                with torch.no_grad(): model(xb, mb)
        return (time.perf_counter() - t0) / len(W)
    run(True)
    return statistics.median(run(True) for _ in range(reps)), statistics.median(run(False) for _ in range(reps))
W400 = W200.reshape(*W200.shape[:2], 300, 2).sum(-1)
c1 = copy.deepcopy(base_cfg); c2 = copy.deepcopy(base_cfg); c2["electrode_encoder"]["channels"] = [8, 16, 16]
configs = [("base 200ms [16,32,32]", base_cfg, W200), ("L1 400ms [16,32,32]", c1, W400), ("L2 400ms [8,16,16]", c2, W400)]
meas = {n: timeit(c, w) for n, c, w in configs}
b_tr, b_in = meas["base 200ms [16,32,32]"]
LED_TR, LED_IN = 0.042517, 0.011297
folds = json.load(open("splits/potter_cv4.json"))["folds"]; pb = pot.groupby("prep_id").size()
rpw = idx[idx.source == "kapucu_rat"].groupby(["prep_id", "well_id"]).size(); E = W200.shape[1]
BL = {1: (30, 5), 2: (20, 5), 4: (30, 5), 8: (6, 5), 16: (3, 5), "all": (1, 5)}            # G1 + G2
def project(tw, ti, ep, M=1, cM=1, WPR=2):
    h = lambda s: s / 3600; c = {}
    c["wagenaar_crossfit"] = h(sum(WPR * pb[f["train"]].sum() * ep * M * tw for f in folds.values()) + pot.n_windows.sum() * M * ti)
    c["wagenaar_final"] = h(WPR * len(pot) * ep * M * tw + pot.n_windows.sum() * M * ti)
    c["c2_canary_x10"] = 10 * h(WPR * len(pot) * ep * cM * tw + pot.n_windows.sum() * cM * ti)
    s = 0
    for hold in ["190617", "250417", "31017"]:
        pool = rpw.drop(hold, level=0)
        for k, (d, sd) in BL.items():
            s += d * sd * ep * WPR * (len(pool) if k == "all" else k) * pool.mean() * tw * 64 / E
    c["kapucu_bl_a2"] = h(s); c["kapucu_inference"] = h(192 * 5 * (M + 1) * ti * 64 / E)
    return c, sum(c.values())
steps = [("start: G1+G2+cut2+cut4", "base 200ms [16,32,32]", 40), ("ladder 1: bins 400 ms", "L1 400ms [16,32,32]", 40),
         ("ladder 2: channels [8,16,16]", "L2 400ms [8,16,16]", 40), ("ladder 3: epochs 25", "L2 400ms [8,16,16]", 25)]
out = []
for name, cfgname, ep in steps:
    mtr, min_ = meas[cfgname]; tw, ti = LED_TR * mtr / b_tr, LED_IN * min_ / b_in
    c, tot = project(tw, ti, ep)
    out.append({"step": name, "measured_ms_train": round(mtr * 1e3, 2), "conservative_ms_train": round(tw * 1e3, 2),
                "conservative_ms_infer": round(ti * 1e3, 2), "epochs": ep, "total_h": round(tot, 2), **{k: round(v, 2) for k, v in c.items()}})
    print(f"{name:<30} measured {mtr*1e3:5.1f} ms | conservative {tw*1e3:5.1f} ms train, {ti*1e3:4.1f} ms infer | ep {ep} | "
          f"TOTAL {tot:5.2f} h | " + " ".join(f"{k}={v:.2f}" for k, v in c.items()))
    if tot < 8:
        print("-> under 8 h; stop."); break
json.dump(out, open("artifacts/g_time_ladder.json", "w"), indent=1)
