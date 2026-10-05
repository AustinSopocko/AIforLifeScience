"""Claim C: identity probes with canary power calibration (WI-09). configs/eval/claim_c.yaml.

Contract
--------
- C-primary `probe_plate_within_prep(reprs, index)`: per prep, control recordings only;
  multinomial logistic probe (inner-CV C) predicting plate_id; leave-one-DIV-out within plate via
  SplitPurpose.IDENTITY_PROBE (the sole sanctioned exception to INVARIANT-1, caller-checked);
  statistic = excess balanced accuracy vs 1,000 within-prep permutations, pooled over preps and
  held-out DIVs. Run on each representation in cfg.representations (z16, inputs, inputs PCA-16,
  random-init encoder) to compute the amplification comparison.
- C-secondary `probe_prep_identity(...)`: prep identity across preps, age-matched; reported only.
- Canary `canary_power(index, features, magnitudes_sd, seeds)`: inject a per-plate random-direction
  offset of the given SD into inputs, re-run feature transform + pretext training + probe end to
  end, return power per magnitude. Validity gate per prereg.
Outputs (artifacts/.../claim_c/): confusion matrices, null distributions, observed statistics,
canary power curve — the inputs of viz.probe (demo shot 3).
"""


def probe_plate_within_prep(reprs: dict, index, cfg) -> dict:
    raise NotImplementedError("WI-09")


def probe_prep_identity(reprs: dict, index, cfg) -> dict:
    raise NotImplementedError("WI-09")


def canary_power(index, features, cfg) -> dict:
    raise NotImplementedError("WI-09")
