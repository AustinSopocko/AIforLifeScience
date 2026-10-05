"""Pre-declared baselines BL-0..BL-7 (WI-07). configs/eval/baselines.yaml.

Contract
--------
Each baseline is a function with the same signature as the model path it competes with, run
under the SAME SplitManifest and FeatureTransform, so comparisons are paired:
  BL-0 predict_mean            BL-1 ridge(log1p MFR, log1p burst rate)
  BL-2 linear on all inputs    BL-3 same-arch from scratch (fixed epochs; no early stopping at small k)
  BL-4 frozen random-init encoder + logistic regression
  BL-5 best single raw-feature within-plate deviation AUC (feature chosen on dev only, recorded)
  BL-6 Mahalanobis deviation AUC from same-plate controls (Ledoit-Wolf covariance)
  BL-7 EPA published hit calls (external reference; never a competitor in a verdict)
Every baseline run appends a ledger row regardless of outcome.
"""


def run_baseline(baseline_id: str, index, features, manifest, cfg) -> dict:
    raise NotImplementedError("WI-07")
