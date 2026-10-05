"""Claim B: age-deviation readout (WI-10). configs/eval/claim_b.yaml.

Contract
--------
Inputs: out-of-fold predictions (controls AND treated), index, viability table.
  Δ = y_pred_log_div - log(DIV) per recording (member mean; member SD kept).
  E(c, d, t) = mean Δ(treated c, dose d, DIV t) - mean Δ(same-plate controls, DIV t).
  Δ-AUC(c, d) = trapezoid of E over DIV 5..12.
Outputs (artifacts/.../claim_b/):
  calibration.json         held-out control mean Δ with CI (B(i), reported FIRST)
  effects.parquet          E and Δ-AUC per compound-dose-DIV with ensemble spread
  detection.json           detection rate at 5% control-null FPR, highest non-cytotoxic dose,
                           for Δ, BL-5, BL-6; paired cluster-bootstrap differences (B(ii))
  dose_response.json       per-compound Spearman ρ(dose, Δ-AUC) (B(iii))
  sensitivity.json         lowest-dose reference; cytotoxic doses separately; plate clusters
  trajectories.parquet     per compound-dose-DIV Δ in days with bands — input to viz.trajectory
Cytotoxic doses (AB < non_cytotoxic_ab_ge) are never pooled into headline numbers.
"""


def run_claim_b(oof_table, index, viability, cfg, prereg: dict) -> dict:
    raise NotImplementedError("WI-10")
