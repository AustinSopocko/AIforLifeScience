"""Per-fold NFA feature transforms (WI-N1). The ONLY place NFA transforms are fit.

Contract
--------
`FeatureTransform.fit(table, manifest, fold)` calls assert_group_disjoint, then fits on rows whose
prep is in the fold's train partition AND is_control (INVARIANT-1/2), per configs/features/nfa17.yaml:
log1p / logit_pct (eps) / fraction_of_electrodes / identity; one binary `<name>__undefined`
column per `nan_means: undefined` feature; train-fold median imputation; train-fold standardisation.
`.transform(table)` applies frozen parameters to any rows (incl. treated / lockbox).
`.state_dict()` is JSON-serialisable and part of the fold artefact (hence of the protocol hash).
Fitting with rows from non-train preps raises InvariantViolation.
"""


class FeatureTransform:
    def fit(self, table, manifest, fold: str) -> "FeatureTransform":
        raise NotImplementedError("WI-N1")

    def transform(self, table):
        raise NotImplementedError("WI-N1")

    def state_dict(self) -> dict:
        raise NotImplementedError("WI-N1")
