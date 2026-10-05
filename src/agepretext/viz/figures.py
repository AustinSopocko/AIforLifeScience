"""Report figure registry (WI-12). Every report figure is a registered function of artefacts + ledger.

Contract
--------
`REGISTRY: dict[str, Callable[[FigureInputs], Figure]]` with keys F1..F8 (PLAN §11):
F1 data/hierarchy overview, F2 age calibration, F3 Claim C panel, F4 Claim B trajectories,
F5 Claim B detection vs baselines, F6 Claim A curve, F7 validation workflow (static, versioned),
F8 ledger timeline. `build_all(out_dir)` renders each to report/generated/fig_<key>.pdf, stamped
with protocol hash and source row_ids. Re-running is byte-identical.
"""
REGISTRY: dict = {}


def build_all(out_dir: str = "report/generated") -> list[str]:
    raise NotImplementedError("WI-12")
