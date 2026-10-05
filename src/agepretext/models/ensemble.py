"""Cluster-bagged ensemble, shared by both pipelines (WI-P2 / WI-N2). PLAN §5.3.

Contract
--------
`ClusterBaggedEnsemble(member_factory, n_members, bagging_unit)` (P: M=3, unit=batch; N: M=5, unit=prep):
  fit(index, manifest, fold) -> each member trains on a bootstrap resample of the fold's train PREPS
  (never wells/recordings), seed = base_seed + member.
  predict(X) -> [n_members, N] log-DIV; embed(X) -> [n_members, N, d] (P only).
Per-recording estimate = member mean; epistemic spread = member SD.
Group-level intervals are NOT computed here: they come from eval.bootstrap over preps.
"""


class ClusterBaggedEnsemble:
    def __init__(self, member_factory, n_members: int, bagging_unit: str):
        raise NotImplementedError("WI-P2")
