"""Shared identity-probe + canary engine for Claim C (WI-04). Used by C1 (NFA) and C2 (Wagenaar).

Contract
--------
- `probe(reprs, labels, groups, split_spec, cfg) -> ProbeResult`: multinomial logistic probe (inner-CV
  regularisation) predicting identity `labels` (plate or batch) within each stratum in `groups`
  (prep for C1, DIV bin for C2), under `split_spec` — the only callers allowed to request
  SplitPurpose.IDENTITY_PROBE:
      "leave_one_well_out_within_plate"  (C1, exception 2)
      "culture_within_batch"             (C2, exception 1)
  Statistic = excess balanced accuracy (observed - permutation-null mean) pooled over strata;
  p from cfg.permutations grouped permutations (eval.nulls.grouped_label_permutation at the declared
  level: well-within-prep for C1, culture for C2). Returns confusion matrices per stratum.
- `canary_power(run_pipeline_with_canary, seeds, cfg) -> CanaryResult`: for each seed, calls the
  caller-supplied closure that injects the canary, re-runs the FULL upstream pipeline (C1: transform +
  ridge refit + Δ; C2: encoder retrain + re-embed) and probes; power = share of seeds with p < alpha.
- Verdict is NOT computed here: eval.verdicts applies the identity rule from prereg.yaml.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class ProbeResult:
    excess_balanced_accuracy: float
    p_value: float
    n_strata: int
    confusion: dict


@dataclass(frozen=True)
class CanaryResult:
    power: float
    detected_per_seed: tuple


def probe(reprs, labels, groups, split_spec: str, cfg) -> ProbeResult:
    raise NotImplementedError("WI-04")


def canary_power(run_pipeline_with_canary, seeds, cfg) -> CanaryResult:
    raise NotImplementedError("WI-04")
