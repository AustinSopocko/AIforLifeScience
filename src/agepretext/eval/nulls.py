"""Null distributions (WI-06).

Contract
--------
- `within_prep_label_permutation(labels, prep_ids, n, seed)` yields label vectors permuted
  only within each prep (Claim C null).
- `control_vs_control_null(delta_table, statistic)` builds pseudo-treatments from control wells:
  each control well vs the remaining same-plate controls, through the identical Δ-AUC pipeline
  (Claim B detection threshold at the pre-declared FPR). The same function is applied to BL-5/BL-6
  so all readouts are thresholded identically.
"""


def within_prep_label_permutation(labels, prep_ids, n: int, seed: int):
    raise NotImplementedError("WI-06")


def control_vs_control_null(delta_table, statistic):
    raise NotImplementedError("WI-06")
