"""Phase 1.2: projected 95% interval width vs number of independent clusters, from the Wagenaar dev results
(H-AGE-P out-of-fold, 8 batches). Cluster-level ratio-estimator SE: SE(MAE) = sd_c(sum_err_c - MAE*n_c)/mean(n_c)/sqrt(C).
Also the paired difference (encoder - BL-1), which is what a comparison needs. Assumes new clusters resemble current
batches (no extra between-lab variance) -> an OPTIMISTIC lower bound on width."""
import json
import numpy as np, pandas as pd
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from agepretext.data.index import RecordingIndex
from agepretext.data.splits import SplitManifest
idx = RecordingIndex.load(); man = SplitManifest.from_json("splits/potter_cv4.json", idx)
hc = pd.read_parquet("data/processed/potter_handcrafted.parquet")
d = idx.table[idx.table.source == "potter"].merge(hc, on="recording_id"); d = d[d.usable].copy()
d = d.merge(pd.read_parquet("artifacts/potter/oof.parquet")[["recording_id", "y_pred_log_div"]], on="recording_id")
d["y"] = np.log(d["div"]); X = np.log1p(d[["mean_firing_rate", "network_burst_rate"]].to_numpy())
for f in man.folds.values():
    tr, te = d.prep_id.isin(f["train"]).to_numpy(), d.prep_id.isin(f["test"]).to_numpy()
    sc = StandardScaler().fit(X[tr]); d.loc[te, "bl1"] = Ridge(alpha=1.0).fit(sc.transform(X[tr]), d.y[tr]).predict(sc.transform(X[te]))
d["e_enc"] = (d.y_pred_log_div - d.y).abs(); d["e_bl1"] = (d.bl1 - d.y).abs(); d["e_diff"] = d.e_enc - d.e_bl1
g = d.groupby("prep_id").agg(n=("y", "size"), s_enc=("e_enc", "sum"), s_bl1=("e_bl1", "sum"), s_diff=("e_diff", "sum"))
def se(col, C):
    m = g[col].sum() / g.n.sum()
    return np.std(g[col] - m * g.n, ddof=1) / g.n.mean() / np.sqrt(C), m
out = {"clusters_now": len(g), "rows": []}
m_enc, m_bl1, m_diff = (g[c].sum() / g.n.sum() for c in ("s_enc", "s_bl1", "s_diff"))
print(f"current (C=8): enc MAE {m_enc:.3f}, BL-1 {m_bl1:.3f}, paired diff {m_diff:+.3f}")
print(" C   halfwidth(enc)  halfwidth(diff)  rule UB(enc)<BL1pt?  paired diff excludes 0?")
for C in (8, 16, 25, 40, 60, 100, 150):
    h_enc = 1.96 * se("s_enc", C)[0]; h_dif = 1.96 * se("s_diff", C)[0]
    r = {"C": C, "halfwidth_enc": round(h_enc, 4), "halfwidth_paired_diff": round(h_dif, 4),
         "rule_passes_if_effect_holds": bool(m_enc + h_enc < m_bl1), "paired_excludes_zero": bool(m_diff + h_dif < 0)}
    out["rows"].append(r)
    print(f"{C:3d}   {h_enc:.4f}          {h_dif:.4f}           {r['rule_passes_if_effect_holds']!s:5}               {r['paired_excludes_zero']}")
for col, name in (("s_enc", "rule (UB enc < BL-1 point)"), ("s_diff", "paired difference")):
    s1 = se(col, 1)[0] * 1.96
    need = (s1 / (m_bl1 - m_enc)) ** 2
    print(f"clusters needed for {name} at the observed effect ({m_bl1 - m_enc:.3f} log-DIV): ~{int(np.ceil(need))}")
    out[f"clusters_needed_{col}"] = int(np.ceil(need))
json.dump(out, open("research/power_projection.json", "w"), indent=1)
