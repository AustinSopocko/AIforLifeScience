"""Prep-level cross-fitting (WI-08).

Contract
--------
`crossfit(index, features, manifest, cfg) -> oof_table` trains one FoldArtefact per fold and
predicts every dev recording (controls AND treated) with the model from the fold where its
prep was held out. Output `artifacts/.../oof_age.parquet`:
  recording_id, fold, member, y_true_log_div, y_pred_log_div, z_0..z_15
Post-condition (asserted): each recording is predicted by exactly one fold, and that fold's
train preps exclude the recording's prep. `fit_final(...)` trains on all dev preps for the
lockbox run (WI-13).
"""


def crossfit(index, features, manifest, cfg):
    raise NotImplementedError("WI-08")


def fit_final(index, features, manifest, cfg):
    raise NotImplementedError("WI-13")
