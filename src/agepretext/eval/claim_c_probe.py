"""Claim C: batch-identity probe with canary validity gate (WI-P4). configs/eval/claim_c.yaml.

Contract
--------
- `probe_batch(z, index, cfg) -> dict`: within each DIV bin, multinomial logistic probe (inner-CV C)
  predicting batch; split = cultures within batch (SplitPurpose.IDENTITY_PROBE, caller-checked);
  statistic = excess balanced accuracy pooled over bins; p from 1,000 culture-level permutations
  (eval.nulls.grouped_label_permutation). Run on primary z (final encoder, all batches), secondary z
  (out-of-fold), and reported comparators (hand-crafted features, random-init encoder).
- `inject_canary(spikes, index, seed, cfg) -> spikes'`: per batch, a seeded random 10% of electrodes get
  extra Poisson spikes at the corpus median per-electrode rate for the recording's DIV bin.
- `canary_power(index, spikes, cfg) -> dict`: for each of 10 seeds: inject into training spikes,
  train.pretext.train_with_canary, re-embed, probe_batch; power = share of seeds with p < 0.05.
- Verdict via eval.verdicts (H-C rule). Outputs (artifacts/.../potter/claim_c/): confusion matrices,
  null distributions, observed statistics, per-seed canary results — inputs of viz.probe (shot 3).
"""


def probe_batch(z, index, cfg) -> dict:
    raise NotImplementedError("WI-P4")


def inject_canary(spikes, index, seed: int, cfg):
    raise NotImplementedError("WI-P4")


def canary_power(index, spikes, cfg) -> dict:
    raise NotImplementedError("WI-P4")
