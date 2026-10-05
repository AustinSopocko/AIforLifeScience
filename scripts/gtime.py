"""G-time gate (D8): time one forward+backward(+AdamW step) pass over ONE real Potter culture's full tensor set with a
random-init encoder, extrapolate total training wall-clock, write artifacts/g_time.json. Never applies the shrink ladder."""
import glob, json, os, time
import numpy as np, pandas as pd, torch, yaml
from agepretext.data.index import RecordingIndex
from agepretext.models.set_encoder import SetEncoder

torch.manual_seed(0); torch.set_num_threads(os.cpu_count())
mcfg = yaml.safe_load(open("configs/model/set_encoder.yaml")); tcfg = yaml.safe_load(open("configs/train/pretext.yaml"))
acfg = yaml.safe_load(open("protocol/prereg.yaml"))["hypotheses"]["H-A"]
idx = RecordingIndex.load().table; hc = pd.read_parquet("data/processed/potter_handcrafted.parquet")
pot = idx[idx.source == "potter"].merge(hc[["recording_id", "usable", "n_windows", "n_electrodes"]], on="recording_id")
pot = pot[pot.usable]
per_cult = pot.groupby("plate_id").size().sort_values(kind="stable")
cult = per_cult.index[len(per_cult) // 2]                                  # median-size culture, deterministic
recs = pot[pot.plate_id == cult]
X = [np.load(f"data/processed/potter_bins/{r}.npz")["counts"] for r in recs.recording_id]
W = np.concatenate([x.reshape(-1, *x.shape[1:]) if True else x for x in [np.pad(x, ((0, 0), (0, max(a.shape[1] for a in X) - x.shape[1]), (0, 0))) for x in X]])
M = np.concatenate([np.pad(np.ones((x.shape[0], x.shape[1]), bool), ((0, 0), (0, W.shape[1] - x.shape[1]))) for x in X])
model = SetEncoder(mcfg); opt = torch.optim.AdamW(model.parameters(), lr=tcfg["lr"], weight_decay=tcfg["weight_decay"])
bs = tcfg["batch_size"]; y = torch.zeros(bs)
def step(i, train=True):
    xb = torch.from_numpy(W[i:i + bs].astype(np.float32)); mb = torch.from_numpy(M[i:i + bs])
    if train:
        _, p = model(xb, mb); loss = ((p - y[: len(p)]) ** 2).mean(); opt.zero_grad(); loss.backward(); opt.step()
    else:
        with torch.no_grad(): model(xb, mb)
step(0); t0 = time.perf_counter()
for i in range(0, len(W), bs): step(i)
t_train = (time.perf_counter() - t0) / len(W)
t0 = time.perf_counter()
for i in range(0, len(W), bs): step(i, train=False)
t_inf = (time.perf_counter() - t0) / len(W)
E = W.shape[1]; Mbr = mcfg["ensemble"]["members"]; ep = tcfg["epochs"]; wpr = mcfg["input"]["windows_per_recording_per_epoch"]
folds = json.load(open("splits/potter_cv4.json"))["folds"]
pb = pot.groupby("prep_id").size()
h = lambda s: s / 3600
comp = {}
comp["potter_crossfit_train"] = h(sum(wpr * pb[f["train"]].sum() * ep * Mbr * t_train for f in folds.values()))
comp["potter_oof_inference"] = h(pot.n_windows.sum() * Mbr * t_inf)
comp["potter_final_train"] = h(wpr * len(pot) * ep * Mbr * t_train)
comp["potter_final_inference"] = h(pot.n_windows.sum() * Mbr * t_inf)
comp["c2_canary_10_retrains_M3"] = 10 * (comp["potter_final_train"] + comp["potter_final_inference"])
# Kapucu BL-A2: from scratch on k labelled wells, 40 epochs, 30 draws (1 for k=all) x 5 seeds x 3 folds; E=64 scaled
ka = idx[idx.source == "kapucu_rat"]; recs_per_well = ka.groupby(["prep_id", "well_id"]).size()
tk = t_train * 64 / E; kap = 0.0
for hold in acfg["folds"]["preps"]:
    pool = recs_per_well.drop(hold, level=0); rbar = pool.mean(); n_pool = len(pool)
    for k in acfg["k_values"]:
        kk = n_pool if k == "all" else k; draws = 1 if k == "all" else acfg["draws_per_k"]
        kap += draws * acfg["bl_a2_seeds_per_draw"] * ep * wpr * kk * rbar * tk
comp["kapucu_bl_a2_from_scratch"] = h(kap)
comp["kapucu_frozen_inference"] = h(len(ka) * 5 * (Mbr + 1) * t_inf * 64 / E)
total = sum(comp.values())
out = {"culture": cult, "recordings": int(len(recs)), "windows": int(len(W)), "electrodes": int(E), "threads": torch.get_num_threads(),
       "batch_size": bs, "sec_per_window_train": t_train, "sec_per_window_infer": t_inf,
       "projection_hours": {k: round(v, 2) for k, v in comp.items()}, "total_hours": round(total, 2),
       "limit_hours": mcfg["g_time"]["max_projected_wallclock_h"], "pass": bool(total <= mcfg["g_time"]["max_projected_wallclock_h"]),
       "shrink_applied": False}
os.makedirs("artifacts", exist_ok=True); json.dump(out, open("artifacts/g_time.json", "w"), indent=1)
print(json.dumps(out, indent=1))
