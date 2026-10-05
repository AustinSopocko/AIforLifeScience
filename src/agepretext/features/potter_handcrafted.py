"""Hand-crafted Potter features (WI-P1). configs/features/potter_handcrafted.yaml.

Contract
--------
`compute(spikes, n_electrodes, duration_s) -> dict` returns, for one recording:
  mean_firing_rate   spikes / (active electrodes x duration); active = rate >= configured minimum
  network_burst_rate bursts per minute, using the single fixed detector in the config
                     (100 ms population bins; threshold = max(4 x median bin count, >= 25% of active
                     electrodes spiking); consecutive supra-threshold bins merge)
Both are returned raw; log/log1p transforms are applied by consumers.
These definitions are frozen at Seal #1 and are shared by: BL-1, BL-A1, and the Claim A target
(the burst rate at DIV t' ~ t+7). Unit-tested on synthetic trains with planted bursts.
"""


import numpy as np

MIN_RATE_HZ = 0.1      # configs/features/potter_handcrafted.yaml
BIN_MS = 100
MEDIAN_MULT = 4.0
ACTIVE_FRAC = 0.25


def compute(spike_times, channels, duration_s: float) -> dict:
    """Threshold reading (fixed, pre-seal): a 100 ms population bin is supra-threshold if its spike count exceeds
    max(4 x median bin count, 0.25 x active electrodes); consecutive supra-threshold bins merge into one burst."""
    t = np.asarray(spike_times, dtype=np.float64)
    c = np.asarray(channels)
    keep = t < duration_s
    t, c = t[keep], c[keep]
    ch, n_per = np.unique(c, return_counts=True)
    active = ch[n_per / duration_s >= MIN_RATE_HZ]
    n_active = len(active)
    on = np.isin(c, active)
    mfr = float(on.sum() / (n_active * duration_s)) if n_active else 0.0
    nb = int(np.ceil(duration_s * 1000 / BIN_MS))
    pop = np.bincount((t[on] * 1000 // BIN_MS).astype(np.int64), minlength=nb)[:nb]
    thr = max(MEDIAN_MULT * float(np.median(pop)), ACTIVE_FRAC * n_active)
    sup = pop > thr if n_active else np.zeros(nb, bool)
    n_bursts = int(np.sum(sup[1:] & ~sup[:-1]) + (sup[0] if len(sup) else 0))
    return {"n_spikes": int(len(t)), "n_active": n_active, "duration_s": duration_s,
            "mean_firing_rate": mfr, "network_burst_rate": n_bursts / (duration_s / 60.0)}
