"""WI-P3 (under Seal 1, confirmatory): H-AGE-P. Out-of-fold MAE log-DIV of the encoder vs BL-0 and BL-1 on held-out
Wagenaar batches (splits/potter_cv4.json); batch-clustered percentile bootstrap (headline), culture-clustered
(sensitivity); per-DIV-bin MAE (reported). Verdict by the relative rule from prereg.yaml. Appends ledger rows."""
import hashlib, os
import numpy as np, pandas as pd, yaml
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from agepretext.data.index import RecordingIndex
from agepretext.data.splits import SplitManifest
from agepretext.eval.bootstrap import cluster_bootstrap
from agepretext.eval.verdicts import verdict
from agepretext.validation import ledger as L
from agepretext.validation.guards import require_clean_tree, require_sealed_protocol

require_clean_tree(); seal = require_sealed_protocol(min_seal=1)
pre = yaml.safe_load(open("protocol/prereg.yaml")); bs = pre["statistics"]["bootstrap"]
bcfg = yaml.safe_load(open("configs/eval/baselines.yaml"))["BL-1"]
idx = RecordingIndex.load(); man = SplitManifest.from_json("splits/potter_cv4.json", idx)
hc = pd.read_parquet("data/processed/potter_handcrafted.parquet")
d = idx.table[idx.table.source == "potter"].merge(hc, on="recording_id"); d = d[d.usable].copy()
d = d.merge(pd.read_parquet("artifacts/potter/oof.parquet")[["recording_id", "y_pred_log_div"]], on="recording_id", how="left")
assert d.y_pred_log_div.notna().all()
d["y"] = np.log(d["div"]); X = np.log1p(d[["mean_firing_rate", "network_burst_rate"]].to_numpy())
for f in man.folds.values():
    tr, te = d.prep_id.isin(f["train"]).to_numpy(), d.prep_id.isin(f["test"]).to_numpy()
    sc = StandardScaler().fit(X[tr]); m = Ridge(alpha=bcfg["alpha"]).fit(sc.transform(X[tr]), d.y[tr])
    d.loc[te, "BL-1"] = m.predict(sc.transform(X[te])); d.loc[te, "BL-0"] = d.y[tr].mean()
d["enc"] = d.y_pred_log_div
res = {}
for col in ("enc", "BL-0", "BL-1"):
    e = d.assign(err=(d[col] - d.y).abs())
    stat = lambda x: x.err.mean()
    res[col] = {"batch": cluster_bootstrap(e, stat, cluster_col="prep_id", n_resamples=bs["n_resamples"], seed=bs["seed"]),
                "culture": cluster_bootstrap(e, stat, cluster_col="plate_id", n_resamples=bs["n_resamples"], seed=bs["seed"]),
                "days": float((np.exp(d[col]) - d["div"]).abs().mean())}
v = verdict("H-AGE-P", {"claim": res["enc"]["batch"], "baselines": {b: res[b]["batch"].point for b in ("BL-0", "BL-1")}}, pre)
bins = pre["hypotheses"]["H-AGE-P"]["report_by_div_bin"]
for lo, hi in bins:
    s = d[(d["div"] >= lo) & (d["div"] <= hi)]
    print(f"DIV {lo:>2}-{hi:<2} n={len(s):3d}  MAE enc {(s.enc-s.y).abs().mean():.3f}  BL-1 {(s['BL-1']-s.y).abs().mean():.3f}  BL-0 {(s['BL-0']-s.y).abs().mean():.3f}")
for col in ("enc", "BL-0", "BL-1"):
    b, c = res[col]["batch"], res[col]["culture"]
    print(f"{col:5s} MAE {b.point:.3f}  batch CI [{b.lower:.3f}, {b.upper:.3f}]  culture CI [{c.lower:.3f}, {c.upper:.3f}]  ({res[col]['days']:.2f} days)")
print("H-AGE-P:", v.label, "|", v.reasons[0])
head = os.popen("git rev-parse HEAD").read().strip()
for col, hid, claim, verd in (("enc", "H-AGE-P", "age", v.label), ("BL-0", "BL-0", "baseline", "N/A"), ("BL-1", "BL-1", "baseline", "N/A")):
    b, c = res[col]["batch"], res[col]["culture"]
    L.append(L.infra_row("mae_log_div",
        f"WI-P3 confirmatory under {seal.seal_id}: out-of-fold over potter_cv4, {len(d)} recordings, 8 batches. Culture-clustered "
        f"sensitivity CI [{c.lower:.4f}, {c.upper:.4f}] ({c.n_clusters} cultures). MAE days {res[col]['days']:.3f}."
        + (f" Verdict: {v.reasons[0]}" if col == "enc" else ""),
        phase="confirmatory", hypothesis_id=hid, claim=claim, value=b.point, ci_lower=b.lower, ci_upper=b.upper,
        ci_method="cluster_percentile_bootstrap", n_clusters=b.n_clusters, cluster_unit="batch", verdict=verd,
        kill_condition_triggered=(col == "enc" and v.kill_condition_triggered), protocol_hash=seal.protocol_hash,
        seal_id=seal.seal_id, split_manifest_sha256=man.sha256(), seeds=[bs["seed"]],
        artifacts=[{"path": "artifacts/potter/oof.parquet", "sha256": hashlib.sha256(open("artifacts/potter/oof.parquet", "rb").read()).hexdigest()}]))
