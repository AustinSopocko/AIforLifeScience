"""Electrode-set age-pretext encoder (WI-P2, CORE). configs/model/set_encoder.yaml.

Contract
--------
Input: counts [B, E, T] (variable E with padding mask) + population rate [B, T].
Shared per-electrode dilated 1-D CNN (channels 16->32->32, kernel 5, dilations 1/4/16; ~17 s
receptive field at 200 ms bins) -> per-electrode tokens -> pooling = concat(attention PMA with one
seed, mean, max) -> z [B, 32]. Recording-level z / prediction = mean over its windows.
Invariance: for any electrode permutation P, encode(x[:, P]) == encode(x) to 1e-6 (unit-tested).
Training augmentation: uniform electrode subsampling to E' in [16, E].
Electrode coordinates are NOT an input (Claim C). `random_init(seed)` gives BL-A3's frozen encoder;
BL-A2 trains this same class from scratch on the forecasting target.
Deterministic on CPU under torch.use_deterministic_algorithms(True) with a fixed seed.
"""


class SetEncoder:  # becomes torch.nn.Module in WI-P2
    def __init__(self, cfg: dict):
        raise NotImplementedError("WI-P2")
