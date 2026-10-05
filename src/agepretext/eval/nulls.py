"""Null distributions (WI-04). Shared.

Contract
--------
- `grouped_label_permutation(labels, group_ids, n, seed)`: permutes labels at the GROUP level (Claim C:
  batch labels shuffled across cultures, all recordings of a culture moving together).
- `control_vs_control_null(delta_table, statistic)`: pseudo-treatments built from NFA control wells (each
  control vs the remaining same-plate controls) through the identical Δ-AUC pipeline; returns the
  null distribution used to set the 5% FPR threshold. Applied identically to BL-B1/B2/B3.
"""


def grouped_label_permutation(labels, group_ids, n: int, seed: int):
    raise NotImplementedError("WI-04")


def control_vs_control_null(delta_table, statistic):
    raise NotImplementedError("WI-04")
