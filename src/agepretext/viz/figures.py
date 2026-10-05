"""Report figure registry (WI-O1). Every report figure is a registered function of artefacts + ledger.

Contract
--------
`REGISTRY: dict[str, Callable[[FigureInputs], Figure]]` keyed F1..F8: F1 corpora/roles/hierarchy
overview (Potter, NFA, Kapucu-as-stretch), F2 Potter age calibration by DIV bin, F3 Claim C panel,
F4 Claim B trajectories, F5 Claim B detection vs BL-B1/B2 (+B3 reported), F6 Claim A curve, F7
validation workflow (static, versioned), F8 ledger timeline. `build_all(out_dir)` renders each to
report/generated/fig_<key>.pdf, stamped with protocol hash and source row_ids; byte-identical re-runs.
"""
REGISTRY: dict = {}


def build_all(out_dir: str = "report/generated") -> list[str]:
    raise NotImplementedError("WI-O1")
