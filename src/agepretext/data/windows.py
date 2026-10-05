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


import numpy as np


def bin_recording(spike_times, channels, electrode_ids, *, bin_ms: int = 200, window_s: int = 120,
                  duration_s: float | None = None):
    t = np.asarray(spike_times, dtype=np.float64)
    c = np.asarray(channels)
    eids = np.asarray(sorted(electrode_ids))
    dur = float(t.max()) if duration_s is None else duration_s
    n_bins = int(round(window_s * 1000 / bin_ms))
    n_win = int(dur // window_s)
    keep = (t < n_win * window_s) & np.isin(c, eids)
    t, c = t[keep], c[keep]
    e_idx = np.searchsorted(eids, c)
    b = (t * 1000 // bin_ms).astype(np.int64)
    w, bi = b // n_bins, b % n_bins
    counts = np.zeros((n_win, len(eids), n_bins), dtype=np.uint16)
    np.add.at(counts, (w, e_idx, bi), 1)
    pop = counts.sum(axis=1, dtype=np.float32)
    assert int(counts.sum()) == int(keep.sum()), "bin-count invariant violated"
    return counts, pop, eids
