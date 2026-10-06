"""Verdict engine (WI-04). Verdicts are computed from protocol/prereg.yaml, never typed by hand.

Contract
--------
`verdict(hypothesis_id, results, prereg) -> Verdict` implements, exactly:
  relative rule (D5): survives iff the favourable-direction cluster-bootstrap bound of the claim beats
    the best POINT estimate among `gating_baselines` (lower bound > max point for higher-is-better;
    upper bound < min point for error metrics); otherwise REFUTES; TooFewClusters -> INCONCLUSIVE.
  H-B additionally requires the calibration gate (held-out control mean Δ CI contains 0).
  H-A uses the inference rule named in prereg (default worst_fold: the relative rule must hold in EVERY
    held-out Kapucu prep, with well-level bootstrap bounds within each prep).
  H-C1 / H-C2 use the identity rule: SUPPORTS iff canary_power >= required_power and real p >= alpha;
    REFUTES iff power >= required_power and p < alpha; INCONCLUSIVE otherwise.
`claim_status(verdicts, prereg) -> dict` applies prereg `claim_status` (B falls if H-C1 REFUTES; C holds
iff H-C1 SUPPORTS; C2 selects wording). `case_number(status, prereg) -> int` returns 1-8 per PLAN §6b.
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
    """Implemented so far: the relative rule (H-AGE-P/N style). results = {"claim": BootstrapResult,
    "baselines": {id: point}}; direction from prereg hypothesis metric."""
    h = prereg["hypotheses"][hypothesis_id]
    gating = h["gating_baselines"]
    missing = [b for b in gating if b not in results["baselines"]]
    if missing:
        raise KeyError(f"missing gating baselines {missing}")
    c = results["claim"]
    if h["metric"]["direction"] == "lower":
        best = min(results["baselines"][b] for b in gating)
        ok = c.upper < best
        pts = ", ".join(f"{b}={results['baselines'][b]:.4f}" for b in gating)
        reason = f"UB(claim)={c.upper:.4f} vs min baseline point={best:.4f} ({pts})"
    else:
        best = max(results["baselines"][b] for b in gating)
        ok = c.lower > best
        reason = f"LB(claim)={c.lower:.4f} vs max baseline point={best:.4f}"
    return Verdict("SUPPORTS" if ok else "REFUTES", not ok, [reason])


def claim_status(verdicts: dict, prereg: dict) -> dict:
    raise NotImplementedError("WI-04")


def case_number(status: dict, prereg: dict) -> int:
    raise NotImplementedError("WI-04")
