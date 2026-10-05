"""Spike-train windowing for the set encoder (stretch S-4).

Contract
--------
`bin_spikes(spike_times, channels, n_electrodes, *, bin_ms=100, window_s=300, hop_s=300)`
returns an array [n_windows, n_electrodes, n_bins] of int16 counts plus a population-rate
channel. Electrode order carries no meaning (set semantics). Windows never span two
recordings. Inactive/noisy electrodes (source metadata) are dropped, not zero-filled, so the
set size reflects the real array.
"""


def bin_spikes(spike_times, channels, n_electrodes: int, *, bin_ms: int = 100,
               window_s: int = 300, hop_s: int = 300):
    raise NotImplementedError("S-4")
