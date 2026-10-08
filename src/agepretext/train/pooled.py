"""Phase 3 pooled age-pretext training on DEV clusters (configs/train/sampling.yaml option A, configs/model/set_encoder.yaml,
configs/train/pretext.yaml optimiser/epochs). The Seal-1 trainer (train/pretext.py) is untouched.

Contract
--------
- `load_dev(meta)` -> list of dicts {recording_id, lab, cluster_id, platform, div, counts [W, E, T] uint16} from
  data/processed/dev_bins (scripts/bin_dev.py). Asserts no confirmatory source is present.
- `scheme_a_weights(recs)` -> per-recording probability under option A (cluster-equal; DIV uniform within cluster;
  recording uniform within cluster-DIV). Used for target standardisation and for baseline sample weights.
- `epoch_draws(recs, m, rng)` -> m (recording, window) draws per cluster, by option A, shuffled.
- `train_pooled(recs, mcfg, tcfg, m, seed)` trains one SetEncoder for tcfg.epochs epochs (no early stopping) on
  scheme-A-standardised log-DIV; per-window uniform electrode subset of size in [min(16, E), E]. Returns (model, stats).
- `predict(model, stats, recs)` -> per recording: mean over ALL windows (all electrodes) of z and of the
  de-standardised log-DIV prediction.
Deterministic on CPU for a given seed.
"""
import numpy as np
import pandas as pd
import torch

from agepretext.models.set_encoder import SetEncoder
from agepretext.train.pretext import _batch


def load_dev(meta: pd.DataFrame, root: str = "data/processed/dev_bins") -> list[dict]:
    assert not meta.source.isin(["fragilex", "kapucu_rat", "nfa"]).any()
    out = []
    for r in meta.sort_values("recording_id").itertuples(index=False):
        out.append({"recording_id": r.recording_id, "lab": r.lab, "cluster_id": r.cluster_id, "platform": r.platform,
                    "div": int(r.div), "counts": np.load(f"{root}/{r.recording_id}.npz")["counts"]})
    return out


def scheme_a_weights(recs: list[dict]) -> np.ndarray:
    d = pd.DataFrame({"c": [r["cluster_id"] for r in recs], "v": [r["div"] for r in recs]})
    n_cl = d.c.nunique()
    n_div = d.groupby("c").v.transform("nunique")
    n_cell = d.groupby(["c", "v"]).v.transform("size")
    return (1.0 / n_cl / n_div / n_cell).to_numpy()


def epoch_draws(recs: list[dict], m: int, rng: np.random.Generator) -> list[tuple[int, int]]:
    cells: dict = {}
    for i, r in enumerate(recs):
        cells.setdefault(r["cluster_id"], {}).setdefault(r["div"], []).append(i)
    draws = []
    for c in sorted(cells):
        divs = sorted(cells[c])
        for v in rng.choice(divs, size=m):
            i = int(rng.choice(cells[c][int(v)]))
            draws.append((i, int(rng.integers(recs[i]["counts"].shape[0]))))
    rng.shuffle(draws)
    return draws


def train_pooled(recs: list[dict], mcfg: dict, tcfg: dict, m: int, seed: int):
    torch.manual_seed(seed)
    torch.use_deterministic_algorithms(True)
    torch.set_num_threads(tcfg.get("threads", 4))
    rng = np.random.default_rng(seed)
    y = np.log([r["div"] for r in recs])
    w = scheme_a_weights(recs)
    mu = float((w * y).sum()); sd = float(np.sqrt((w * (y - mu) ** 2).sum()))
    stats = {"mean": mu, "sd": sd}
    yz = (y - mu) / sd
    model = SetEncoder(mcfg)
    opt = torch.optim.AdamW(model.parameters(), lr=tcfg["lr"], weight_decay=tcfg["weight_decay"])
    bs, emin = tcfg["batch_size"], mcfg["augment"]["electrode_subsample_min"]
    model.train()
    for _ in range(tcfg["epochs"]):
        draws = epoch_draws(recs, m, rng)
        for b in range(0, len(draws), bs):
            xs, ts = [], []
            for i, wi in draws[b:b + bs]:
                x = recs[i]["counts"][wi]
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
def predict(model, stats: dict, recs: list[dict], bs: int = 128) -> pd.DataFrame:
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
