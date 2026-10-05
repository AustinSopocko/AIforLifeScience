"""Canonical spike-time -> 17-endpoint extractor (stretch S-1).

Contract
--------
`extract(spikes, n_electrodes, duration_s) -> dict[str, float]` computes, for one recording,
the same 17 endpoints as the EPA NFA tables (names identical to configs/features/nfa17.yaml),
following the EPA `meadq` definitions (bursts: maximum-interval method, bursts.py; network
spikes: network_spikes.py), with geometry harmonisation: active-electrode counts as fractions,
network-spike threshold as a fraction of active electrodes, per-electrode statistics averaged
over active electrodes (never summed). Undefined quantities return NaN (not 0).
Acceptance (S-1): on EPAmeadev recordings, Spearman >= 0.9 vs EPA-published values per endpoint;
geometry check: ICC(full 60-el vs random 16-el subsample) reported per endpoint, < 0.7 => dropped
from cross-source models (pre-declared).
"""


def extract(spikes, n_electrodes: int, duration_s: float) -> dict:
    raise NotImplementedError("S-1")
