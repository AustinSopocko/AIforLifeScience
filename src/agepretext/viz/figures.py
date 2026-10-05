"""Report figure registry (WI-O1). Every report figure is a registered function of artefacts + ledger.

Contract
--------
`REGISTRY: dict[str, Callable[[FigureInputs], Figure]]` keyed per PLAN §6b: F1 corpora/roles, F2 protocol
workflow (static, versioned), F3 ledger timeline with verdict rows, F4 age calibration (Wagenaar by DIV bin,
NFA), F5 Claim C panel (C1 + C2 with canaries), F6 Claim A full curve per held-out Kapucu prep, F7 Claim B
trajectories, F8 Claim B detection vs BL-B1/B2 (+B3 reported). Every figure has SUPPORTS/REFUTES/
INCONCLUSIVE caption variants; main-text vs appendix placement follows \\CaseNumber. `build_all(out_dir)` renders each to
report/generated/fig_<key>.pdf, stamped with protocol hash and source row_ids; byte-identical re-runs.
"""
REGISTRY: dict = {}


def build_all(out_dir: str = "report/generated") -> list[str]:
    raise NotImplementedError("WI-O1")
