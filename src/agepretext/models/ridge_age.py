"""NFA age model (WI-N2). configs/model/ridge_age.yaml.

Contract
--------
`RidgeAge(alpha=1.0)`: fit(X_transformed, log_div) on train-fold CONTROL rows only (asserted via
invariants.assert_controls_only); predict(X) -> log-DIV. Wrapped by models.ensemble with
bagging_unit="prep", M=5. No hyperparameter search (alpha fixed at Seal #1). Deliberately minimal:
Pipeline N tests the age-residual READOUT, not a representation.
"""


class RidgeAge:
    def __init__(self, alpha: float = 1.0):
        raise NotImplementedError("WI-N2")
