"""Hand-crafted Potter features (WI-P1). configs/features/potter_handcrafted.yaml.

Contract
--------
`compute(spikes, n_electrodes, duration_s) -> dict` returns, for one recording:
  mean_firing_rate   spikes / (active electrodes x duration); active = rate >= configured minimum
  network_burst_rate bursts per minute, using the single fixed detector in the config
                     (100 ms population bins; threshold = max(4 x median bin count, >= 25% of active
                     electrodes spiking); consecutive supra-threshold bins merge)
Both are returned raw; log/log1p transforms are applied by consumers.
Phase 2 (F2): `compute(..., params=None)`; params = {bin_ms, median_mult, active_frac, min_rate_hz} per platform from
configs/features/burst_calibration.yaml `selected`. params=None keeps the Seal-1 constants (Seal-1 runs reproduce).
These definitions are frozen at Seal #1 and are shared by: BL-1, BL-A1, and the Claim A target
(the burst rate at DIV t' ~ t+7). Unit-tested on synthetic trains with planted bursts.
"""


import numpy as np

MIN_RATE_HZ = 0.1      # configs/features/potter_handcrafted.yaml
BIN_MS = 100
MEDIAN_MULT = 4.0
ACTIVE_FRAC = 0.25


def compute(spike_times, channels, duration_s: float, params: dict | None = None) -> dict:
    """Threshold reading (fixed, pre-seal): a 100 ms population bin is supra-threshold if its spike count exceeds
    max(4 x median bin count, 0.25 x active electrodes); consecutive supra-threshold bins merge into one burst."""
    p = params or {}
    min_rate, bin_ms = p.get("min_rate_hz", MIN_RATE_HZ), p.get("bin_ms", BIN_MS)
    mult, frac = p.get("median_mult", MEDIAN_MULT), p.get("active_frac", ACTIVE_FRAC)
    t = np.asarray(spike_times, dtype=np.float64)
    c = np.asarray(channels)
    keep = t < duration_s
    t, c = t[keep], c[keep]
    ch, n_per = np.unique(c, return_counts=True)
    active = ch[n_per / duration_s >= min_rate]
    n_active = len(active)
    on = np.isin(c, active)
    mfr = float(on.sum() / (n_active * duration_s)) if n_active else 0.0
    nb = int(np.ceil(duration_s * 1000 / bin_ms))
    pop = np.bincount((t[on] * 1000 // bin_ms).astype(np.int64), minlength=nb)[:nb]
    thr = max(mult * float(np.median(pop)), frac * n_active)
    sup = pop > thr if n_active else np.zeros(nb, bool)
    n_bursts = int(np.sum(sup[1:] & ~sup[:-1]) + (sup[0] if len(sup) else 0))
    return {"n_spikes": int(len(t)), "n_active": n_active, "duration_s": duration_s,
            "mean_firing_rate": mfr, "network_burst_rate": n_bursts / (duration_s / 60.0)}
