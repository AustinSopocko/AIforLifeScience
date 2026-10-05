"""Age-model evaluation, H-AGE (WI-08).

Contract
--------
`evaluate_age(oof_table, index, prereg) -> dict` on held-out CONTROL recordings: R² and MAE on
log-DIV, MAE in days, per-DIV bias, each with cluster-bootstrap CIs over preps; paired
comparison with BL-0 and BL-1; verdict via eval.verdicts; one ledger row per metric.
"""


def evaluate_age(oof_table, index, prereg: dict) -> dict:
    raise NotImplementedError("WI-08")
