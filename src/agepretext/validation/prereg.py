"""Preregistration loading and validation (WI-05).

Contract
--------
`load_prereg(path="protocol/prereg.yaml", *, require_sealed=True) -> dict` parses the YAML,
validates it against the v1 schema (every hypothesis has a metric, thresholds, and a kill rule;
every baseline ID referenced exists in configs/eval/baselines.yaml), raises on any TBD_WI00
when require_sealed, and returns the thresholds consumed by eval.verdicts. Thresholds are never
read from anywhere else.
"""


def load_prereg(path: str = "protocol/prereg.yaml", *, require_sealed: bool = True) -> dict:
    raise NotImplementedError("WI-05")
