"""Pipeline P age-pretext training (WI-P2). configs/train/pretext.yaml + configs/model/set_encoder.yaml (frozen at Seal 1).

Contract
--------
- `load_potter()` -> list of dicts {recording_id, prep_id, plate_id, div, counts [W, E, T] uint16} for usable Wagenaar
  recordings only (asserts every row is source == potter: Kapucu never enters encoder training).
- `train_model(recs, mcfg, tcfg, seed)` trains one SetEncoder on log-DIV z-scored with the training recordings' mean/SD,
  for exactly tcfg.epochs epochs (no early stopping). Each epoch samples tcfg.windows_per_recording_per_epoch windows per
  recording without replacement; each training window keeps a uniform-random electrode subset of size in [16, E].
  Returns (model, target_stats).
- `predict(model, stats, recs)` -> per recording: mean over ALL windows (all electrodes) of z and of the de-standardised
  log-DIV prediction.
- Deterministic on CPU for a given seed (torch.use_deterministic_algorithms).
"""
import json
import os

import numpy as np
import pandas as pd
import torch

from agepretext.models.set_encoder import SetEncoder


def load_potter() -> list[dict]:
    idx = pd.read_parquet("data/processed/recording_index.parquet")
    hc = pd.read_parquet("data/processed/potter_handcrafted.parquet")
    d = idx[idx.source == "potter"].merge(hc[["recording_id", "usable"]], on="recording_id")
    d = d[d.usable].sort_values("recording_id")
    assert (d.source == "potter").all()
    out = []
    for r in d.itertuples(index=False):
        z = np.load(f"data/processed/potter_bins/{r.recording_id}.npz")
        out.append({"recording_id": r.recording_id, "prep_id": r.prep_id, "plate_id": r.plate_id, "div": int(r.div),
                    "counts": z["counts"]})
    return out


def _batch(items):
    E = max(x.shape[0] for x in items)
    X = np.zeros((len(items), E, items[0].shape[1]), np.float32)
    M = np.zeros((len(items), E), bool)
    for i, x in enumerate(items):
        X[i, : x.shape[0]] = x
        M[i, : x.shape[0]] = True
    return torch.from_numpy(X), torch.from_numpy(M)


def train_model(recs: list[dict], mcfg: dict, tcfg: dict, seed: int):
    torch.manual_seed(seed)
    torch.use_deterministic_algorithms(True)
    torch.set_num_threads(tcfg.get("threads", 4))
    rng = np.random.default_rng(seed)
    y = np.log([r["div"] for r in recs])
    stats = {"mean": float(y.mean()), "sd": float(y.std())}
    yz = (y - stats["mean"]) / stats["sd"]
    model = SetEncoder(mcfg)
    opt = torch.optim.AdamW(model.parameters(), lr=tcfg["lr"], weight_decay=tcfg["weight_decay"])
    k, bs, emin = tcfg["windows_per_recording_per_epoch"], tcfg["batch_size"], mcfg["augment"]["electrode_subsample_min"]
    model.train()
    for _ in range(tcfg["epochs"]):
        items = []
        for i, r in enumerate(recs):
            W = r["counts"].shape[0]
            for w in rng.choice(W, size=min(k, W), replace=False):
                items.append((i, int(w)))
        rng.shuffle(items)
        for b in range(0, len(items), bs):
            xs, ts = [], []
            for i, w in items[b:b + bs]:
                x = recs[i]["counts"][w]
                E = x.shape[0]
                keep = np.sort(rng.choice(E, size=int(rng.integers(min(emin, E), E + 1)), replace=False))
                xs.append(x[keep]); ts.append(yz[i])
            X, M = _batch(xs)
            _, p = model(X, M)
            loss = ((p - torch.tensor(ts, dtype=torch.float32)) ** 2).mean()
            opt.zero_grad(); loss.backward(); opt.step()
    model.eval()
    return model, stats


@torch.no_grad()
def predict(model, stats: dict, recs: list[dict], bs: int = 64) -> pd.DataFrame:
    rows = []
    for r in recs:
        zs, ps = [], []
        for b in range(0, r["counts"].shape[0], bs):
            X, M = _batch(list(r["counts"][b:b + bs]))
            z, p = model(X, M)
            zs.append(z.numpy()); ps.append(p.numpy())
        z, p = np.concatenate(zs).mean(0), np.concatenate(ps).mean()
        rows.append({"recording_id": r["recording_id"], "y_true_log_div": float(np.log(r["div"])),
                     "y_pred_log_div": float(p * stats["sd"] + stats["mean"]), **{f"z_{j}": float(v) for j, v in enumerate(z)}})
    return pd.DataFrame(rows)


def save(model, stats: dict, path: str, meta: dict) -> None:
    os.makedirs(path, exist_ok=True)
    torch.save(model.state_dict(), os.path.join(path, "model.pt"))
    json.dump({"target_stats": stats, **meta}, open(os.path.join(path, "meta.json"), "w"), indent=1, sort_keys=True)


def train_fold(*a, **k):
    raise NotImplementedError("use scripts/train_potter.py (cross-fit) — kept for contract compatibility")


def train_final(*a, **k):
    raise NotImplementedError("use scripts/train_potter.py (final) — kept for contract compatibility")


def train_with_canary(index, spikes, cfg, canary_seed: int):
    raise NotImplementedError("WI-P4")
