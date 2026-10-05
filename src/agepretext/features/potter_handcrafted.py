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


def compute(spikes, n_electrodes: int, duration_s: float) -> dict:
    raise NotImplementedError("WI-P1")
