"""EXPLORATORY, pre-Seal-#1, operator-requested: BL-0 and BL-1 (ridge on log1p mean firing rate, log1p network-burst
rate -> log DIV) on Wagenaar, out-of-fold over the frozen splits/potter_cv4.json; MAE log-DIV with a percentile cluster
bootstrap over batches (prep). Appends an exploratory ledger row. Not part of reproduce.sh; tunes nothing."""
import glob, hashlib, json, subprocess
import numpy as np, pandas as pd, yaml
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from agepretext.data.index import RecordingIndex
from agepretext.data.splits import SplitManifest
from agepretext.validation import ledger as L

idx = RecordingIndex.load(); man = SplitManifest.from_json("splits/potter_cv4.json", idx)
hc = pd.read_parquet("data/processed/potter_handcrafted.parquet")
d = idx.table[idx.table.source == "potter"].merge(hc, on="recording_id"); d = d[d.usable].copy()
d["y"] = np.log(d["div"]); X = np.log1p(d[["mean_firing_rate", "network_burst_rate"]].to_numpy())
d["bl0"] = np.nan; d["bl1"] = np.nan
for f in man.folds.values():
    tr, te = d.prep_id.isin(f["train"]).to_numpy(), d.prep_id.isin(f["test"]).to_numpy()
    sc = StandardScaler().fit(X[tr]); m = Ridge(alpha=1.0).fit(sc.transform(X[tr]), d.y[tr])
    d.loc[te, "bl1"] = m.predict(sc.transform(X[te])); d.loc[te, "bl0"] = d.y[tr].mean()
assert d[["bl0", "bl1"]].notna().all().all()
bs = yaml.safe_load(open("protocol/prereg.yaml"))["statistics"]["bootstrap"]
rng = np.random.default_rng(bs["seed"]); preps = np.array(sorted(d.prep_id.unique()))
res = {}
for b in ("bl0", "bl1"):
    e = (d[b] - d.y).abs(); g = e.groupby(d.prep_id).agg(["sum", "count"]).loc[preps]
    boots = [(lambda s: s["sum"].sum() / s["count"].sum())(g.iloc[rng.integers(0, len(preps), len(preps))]) for _ in range(bs["n_resamples"])]
    days = (np.exp(d[b]) - d["div"]).abs().mean()
    res[b] = dict(mae=float(e.mean()), lo=float(np.percentile(boots, 2.5)), hi=float(np.percentile(boots, 97.5)), mae_days=float(days))
cat = b"".join(open(p, "rb").read() for p in ["protocol/prereg.yaml", "PREREGISTRATION.md", *sorted(glob.glob("configs/**/*.yaml", recursive=True)), *sorted(glob.glob("splits/*.json"))])
head = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
ph = hashlib.sha256(cat + head.encode()).hexdigest()
for b, hid in (("bl0", "BL-0"), ("bl1", "BL-1")):
    r = L.infra_row("mae_log_div", "EXPLORATORY pre-Seal-#1 (operator request): out-of-fold over splits/potter_cv4.json, "
        f"{len(d)} usable recordings, 8 batches; MAE in days {res[b]['mae_days']:.2f}. protocol_hash is an UNSEALED hash "
        "(prereg + configs + splits + HEAD). No hyperparameter or rule is chosen from this result.",
        phase="exploratory", hypothesis_id=hid, claim="baseline", value=res[b]["mae"], ci_lower=res[b]["lo"], ci_upper=res[b]["hi"],
        ci_method="cluster_percentile_bootstrap", n_clusters=len(preps), cluster_unit="batch", protocol_hash=ph,
        split_manifest_sha256=man.sha256(), seeds=[bs["seed"]])
    L.append(r)
for b in res: print(b, {k: round(v, 3) for k, v in res[b].items()})
print("n_recordings", len(d), "n_batches", len(preps))
