"""Cluster-bagged deep ensemble (WI-08). PLAN §5.5.

Contract
--------
`ClusterBaggedEnsemble(member_factory, n_members=5, bagging_unit="prep")`:
  fit(train_index, manifest, fold) -> each member trains on a bootstrap resample of the fold's
  train PREPS (not wells), its own seed = base_seed + member; returns per-member artefacts.
  predict(X) -> array [n_members, N] of log-DIV predictions; embed(X) -> [n_members, N, d].
Reported per-recording prediction = member mean; epistemic spread = member SD.
Group-level intervals are NOT computed here — they come from eval.bootstrap over preps.
"""


class ClusterBaggedEnsemble:
    def __init__(self, member_factory, n_members: int = 5, bagging_unit: str = "prep"):
        raise NotImplementedError("WI-08")
