"""Per-fold feature transforms (WI-03/WI-08). The ONLY place transforms are fit.

Contract
--------
`FeatureTransform.fit(table, manifest, fold)` — calls assert_group_disjoint, then fits on rows
whose prep is in the fold's train partition AND is_control (INVARIANT-1/2):
  per configs/features/nfa17.yaml: log1p / logit_pct (eps) / fraction_of_electrodes /
  identity; adds one binary `<name>__undefined` column per `nan_means: undefined` feature;
  imputes with train-fold medians; standardises with train-fold mean/std.
`.transform(table)` applies the frozen parameters to any rows (incl. treated / held-out).
`.state_dict()` is JSON-serialisable and included in the fold artefact (and so in the
protocol hash of any evaluation that uses it).
Calling `.fit` with rows from non-train preps raises InvariantViolation.
"""


class FeatureTransform:
    def fit(self, table, manifest, fold: str) -> "FeatureTransform":
        raise NotImplementedError("WI-08")

    def transform(self, table):
        raise NotImplementedError("WI-08")

    def state_dict(self) -> dict:
        raise NotImplementedError("WI-08")
