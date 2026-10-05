"""Preregistration loading and validation (WI-05).

Contract
--------
`load_prereg(path="protocol/prereg.yaml", *, require_sealed=True) -> dict` parses the YAML,
validates it against the v2 schema (every hypothesis names a metric with a direction and its
gating baselines — or, for H-C, its canary rule; every referenced baseline is defined under `baselines`;
no absolute claim thresholds exist outside H-C's canary design parameters), raises on any TBD_WI00
when require_sealed, and returns the thresholds consumed by eval.verdicts. Thresholds are never
read from anywhere else.
"""


def load_prereg(path: str = "protocol/prereg.yaml", *, require_sealed: bool = True) -> dict:
    raise NotImplementedError("WI-05")
