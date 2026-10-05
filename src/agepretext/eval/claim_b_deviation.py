"""Claim B: NFA age-deviation readout (WI-N3). configs/eval/claim_b.yaml.

Contract
--------
Inputs: out-of-fold ridge-age predictions (controls AND treated), index, viability table.
  Δ = y_pred_log_div - log(DIV); E(c,d,t) = mean Δ(treated) - mean Δ(same-plate controls);
  Δ-AUC = trapezoid of E over DIV 5..12. Non-cytotoxic = AB >= 5th percentile of control AB.
Outputs (artifacts/.../nfa/claim_b/):
  calibration.json     held-out control mean Δ with prep-clustered CI (gate; reported FIRST)
  detection.json       detection rate at the 5% control-null FPR (highest non-cytotoxic dose) for Δ,
                       BL-B1, BL-B2 (gating) and BL-B3 (reported); prep-clustered + plate-clustered CIs;
                       verdict via eval.verdicts
  sensitivity.json     lowest-dose reference; cytotoxic doses separately; dose-response
  trajectories.parquet per compound-dose-DIV Δ in days with bands (input to viz.trajectory)
Run on TC (exploratory, cross-fit) and once on NTP (confirmatory, Seal #2, model fit on all TC).
"""


def run_claim_b(oof_table, index, viability, cfg, prereg: dict, phase: str) -> dict:
    raise NotImplementedError("WI-N3")
