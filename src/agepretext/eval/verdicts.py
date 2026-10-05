"""Verdict engine (WI-04). Verdicts are computed from protocol/prereg.yaml, never typed by hand.

Contract
--------
`verdict(hypothesis_id, results, prereg) -> Verdict` implements, exactly:
  relative rule (D5): survives iff the favourable-direction cluster-bootstrap bound of the claim beats
    the best POINT estimate among `gating_baselines` (lower bound > max point for higher-is-better;
    upper bound < min point for error metrics); otherwise REFUTES; TooFewClusters -> INCONCLUSIVE.
  H-B additionally requires the calibration gate (held-out control mean Δ CI contains 0).
  H-C uses its own rule: SUPPORTS iff canary_power >= required_power and real_batch_p >= alpha;
    REFUTES iff canary_power >= required_power and real_batch_p < alpha; INCONCLUSIVE otherwise.
Returns label, kill_condition_triggered, and reasons citing every compared quantity and its source.
Unknown hypothesis IDs, missing baselines, or non-gating baselines passed as gating raise.
"""
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Verdict:
    label: str
    kill_condition_triggered: bool
    reasons: list = field(default_factory=list)


def verdict(hypothesis_id: str, results: dict, prereg: dict) -> Verdict:
    raise NotImplementedError("WI-04")
