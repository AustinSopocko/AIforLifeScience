"""Verdict engine (WI-06). Verdicts are computed from protocol/prereg.yaml, never typed by hand.

Contract
--------
`verdict(hypothesis_id, results: dict, prereg: dict) -> Verdict` where Verdict has
`label in {"SUPPORTS", "REFUTES", "INCONCLUSIVE"}`, `kill_condition_triggered: bool`, and
`reasons: list[str]` citing each threshold and the value it was compared with.
Rules mirror PREREGISTRATION.md §2 exactly, including: H-C is INCONCLUSIVE whenever the canary
validity gate fails; H-A ceiling rule switches task (not a verdict); H-B wording downgrade when
only dose-dependence fails. Unknown hypothesis IDs or missing thresholds raise.
"""
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Verdict:
    label: str
    kill_condition_triggered: bool
    reasons: list = field(default_factory=list)


def verdict(hypothesis_id: str, results: dict, prereg: dict) -> Verdict:
    raise NotImplementedError("WI-06")
