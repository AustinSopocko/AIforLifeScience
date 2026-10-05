"""Age evaluation, shared by both pipelines: H-AGE-P and H-AGE-N (WI-P3 / WI-N2).

Contract
--------
`evaluate_age(oof_table, index, baselines_oof, prereg, hypothesis_id) -> dict`: on held-out recordings
(NFA: controls only), MAE of log-DIV for the model and each gating baseline (BL-0, BL-1), MAE in days,
per-DIV-bin MAE (Potter bins from prereg), each with prep-clustered bootstrap CIs plus plate/culture-
clustered sensitivity CIs; verdict via eval.verdicts (relative rule: UB(model MAE) < min baseline
point MAE); one ledger row per metric.
"""


def evaluate_age(oof_table, index, baselines_oof, prereg: dict, hypothesis_id: str) -> dict:
    raise NotImplementedError("WI-P3 / WI-N2")
