"""Permutation-invariant electrode-set encoder (stretch S-4). configs/model/set_encoder.yaml.

Contract
--------
Input [B, E, T] binned counts with variable E (mask for padding) + population-rate channel.
Shared per-electrode dilated 1-D CNN -> per-electrode tokens -> pooling = concat(attention PMA
with 1 seed, mean, max) -> z[B, 32]. Invariance: for any permutation P of electrodes,
encode(x[:, P]) == encode(x) to 1e-6 (unit-tested). Training-time augmentation subsamples
electrodes uniformly to E' in [16, E]. Electrode coordinates are NOT an input (Claim C);
an ablation flag exists but is off by default.
"""


class SetEncoder:
    def __init__(self, cfg: dict):
        raise NotImplementedError("S-4")
