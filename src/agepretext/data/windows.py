"""Spike-train binning for the age-pretext encoder (WI-P1). configs/model/set_encoder.yaml.

Contract
--------
`bin_recording(spike_times, channels, electrode_ids, *, bin_ms=200, window_s=120)` returns
  counts: int16 array [n_windows, n_electrodes, n_bins] (non-overlapping windows, no window spans
          two recordings, a trailing partial window is dropped),
  pop:    float32 array [n_windows, n_bins] population rate,
  electrode_ids: the electrode order used (carries no meaning: set semantics).
Noisy/inactive electrodes listed by the source are dropped, not zero-filled.
Invariant (tested): counts.sum() equals the number of spikes inside the kept windows.
Used identically for Potter (core) and Kapucu (stretch S-1).
"""


def bin_recording(spike_times, channels, electrode_ids, *, bin_ms: int = 200, window_s: int = 120):
    raise NotImplementedError("WI-P1")
