"""H-C1: artefact-only identity probe on the Claim B readout (WI-N4). PRIMARY for Claim C.
configs/eval/claim_c1.yaml. Same cells, same prep, same plating day; only the plate differs.

Contract
--------
- Representation: per NFA control well, the Δ trajectory over DIV 5/7/9/12 (TC: out-of-fold from the
  6-fold cross-fit; NTP: final TC model under Seal #2). All 18 preps; run once, confirmatory.
- `run_c1(delta_table, index, cfg)`: identity_probe.probe(labels=plate, groups=prep,
  split_spec="leave_one_well_out_within_plate"); also on the 25 transformed inputs (reported).
- `inject_plate_canary(features, index, seed, cfg)`: per plate, add N(0, (0.5 * sigma_w)^2) to every
  transformed feature of all wells of that plate; sigma_w = within-plate between-control-well SD per
  feature, estimated on TC train preps only.
- `canary(...)`: 20 seeds; each re-fits FeatureTransform + ridge, recomputes Δ, re-probes.
- Outputs (artifacts/.../nfa/claim_c1/): probe results, null distributions, canary power, confusion
  matrices for viz.probe. Verdict via eval.verdicts (identity rule).
- The report MUST state: C1 certifies the readout pipeline, not the Wagenaar encoder.
"""


def run_c1(delta_table, index, cfg) -> dict:
    raise NotImplementedError("WI-N4")


def inject_plate_canary(features, index, seed: int, cfg):
    raise NotImplementedError("WI-N4")


def canary(index, features, cfg) -> dict:
    raise NotImplementedError("WI-N4")
