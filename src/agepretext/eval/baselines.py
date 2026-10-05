"""Pre-declared baselines (WI-P3, WI-P5, WI-N3). Definitions: protocol/prereg.yaml `baselines`.

Contract
--------
Each baseline runs under the SAME SplitManifest (and, for NFA, the same FeatureTransform) as the
model it competes with, so comparisons are paired:
  Age (both pipelines): BL-0 train mean; BL-1 ridge(log mean firing rate, log burst rate).
  Claim A (Potter):     BL-A0 DIV only; BL-A1 hand-crafted state + DIV; BL-A2 same-arch from scratch
                        (40 epochs, no early stopping); BL-A3 frozen random-init encoder + DIV.
  Claim B (NFA):        BL-B1 residual of the BL-1 age model; BL-B2 best single raw-feature deviation
                        AUC (feature chosen on TC dev, recorded); BL-B3 Mahalanobis (reported, non-gating).
Every baseline run appends a ledger row regardless of outcome.
"""


def run_baseline(baseline_id: str, index, payload, manifest, cfg) -> dict:
    raise NotImplementedError("WI-P3 / WI-P5 / WI-N3")
