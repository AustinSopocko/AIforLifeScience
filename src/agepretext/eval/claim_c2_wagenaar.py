"""H-C2: encoder batch-identity probe on Wagenaar (WI-P4). PRIMARY, wording-only (see PLAN §5.7).
configs/eval/claim_c2.yaml. Confounded with culture biology by construction.

Contract
--------
- Representation: final-encoder z (all 8 batches), stratified into the 4 DIV bins.
- `run_c2(z, index, cfg)`: identity_probe.probe(labels=batch, groups=div_bin,
  split_spec="culture_within_batch"), 1,000 culture-level permutations; hand-crafted features probed
  as a reported comparator.
- `inject_noisy_electrode_canary(spikes, index, seed, cfg)`: per batch, a seeded random 10% of
  electrodes receive extra Poisson spikes at the corpus median per-electrode rate for the DIV bin.
- `canary(...)`: 10 seeds; each calls train.pretext.train_with_canary, re-embeds, re-probes.
- Outputs (artifacts/.../potter/claim_c2/) feed viz.probe. Verdict via eval.verdicts; it selects
  Claim C's wording only.
"""


def run_c2(z, index, cfg) -> dict:
    raise NotImplementedError("WI-P4")


def inject_noisy_electrode_canary(spikes, index, seed: int, cfg):
    raise NotImplementedError("WI-P4")


def canary(index, spikes, cfg) -> dict:
    raise NotImplementedError("WI-P4")
