"""Prep-level cross-fitting, shared by both pipelines (WI-P2 / WI-N2).

Contract
--------
`crossfit(index, payload, manifest, fit_fold) -> oof_table`: calls `fit_fold` per fold and predicts
every recording (NFA: controls AND treated) with the model from the fold where its prep was held out.
Output columns: recording_id, fold, member, y_true_log_div, y_pred_log_div [, z_0..z_31 for P].
Post-condition (asserted): each recording is predicted by exactly one fold whose train preps exclude
the recording's prep.
`fit_final(...)` trains on all dev preps: P -> final encoder; N -> model applied to the NTP lockbox
under Seal #2 (WI-O2).
"""


def crossfit(index, payload, manifest, fit_fold):
    raise NotImplementedError("WI-P2 / WI-N2")


def fit_final(index, payload, manifest, fit_fold):
    raise NotImplementedError("WI-P2 / WI-O2")
