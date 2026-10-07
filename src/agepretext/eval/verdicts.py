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
  Phase 2 (prereg v4, decision_rule.name == paired_vs_each_gating_baseline): results = {"paired": {b: BootstrapResult
    of stat(claim) - stat(b)}}; survives iff UB < 0 for EVERY gating b (lower-is-better; LB > 0 otherwise).
    Missing interval (TooFewClusters) -> INCONCLUSIVE. Hypotheses may live under `hypotheses` or `dev_evaluation`.
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


def _paired(h: dict, results: dict) -> Verdict:
    gating = h["gating_baselines"]
    paired = results["paired"]
    missing = [b for b in gating if b not in paired]
    if missing:
        raise KeyError(f"missing gating baselines {missing}")
    if any(paired[b] is None for b in gating):
        return Verdict("INCONCLUSIVE", False, [f"interval not computable for {[b for b in gating if paired[b] is None]}"])
    lower = h["metric"]["direction"] == "lower"
    reasons_null = []
    if "detection_null" in h:           # H-B2: exact permutation detection is a co-condition
        a, p = h["detection_null"]["alpha"], results["null_p"]
        reasons_null = [f"detection p={p:.4f} vs alpha {a}"]
        if not p < a:
            return Verdict("REFUTES", True, reasons_null)
    ok = all((paired[b].upper < 0) if lower else (paired[b].lower > 0) for b in gating)
    side = "UB" if lower else "LB"
    reasons = [f"{side}(claim-{b})={(paired[b].upper if lower else paired[b].lower):.4f} "
               f"(point {paired[b].point:.4f}, {paired[b].n_clusters} clusters)" for b in gating]
    return Verdict("SUPPORTS" if ok else "REFUTES", not ok, reasons_null + reasons)


def verdict(hypothesis_id: str, results: dict, prereg: dict) -> Verdict:
    """Relative rule (v3, Seal 1: H-AGE-P) or paired rule (v4), selected by prereg decision_rule.name.
    v3 results = {"claim": BootstrapResult, "baselines": {id: point}}; v4 results = {"paired": {id: BootstrapResult}}."""
    h = prereg.get("hypotheses", {}).get(hypothesis_id) or prereg.get("dev_evaluation", {}).get(hypothesis_id)
    if h is None:
        raise KeyError(hypothesis_id)
    if prereg["decision_rule"]["name"] == "paired_vs_each_gating_baseline":
        return _paired(h, results)
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
