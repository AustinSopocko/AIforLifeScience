"""WI-P1: bin-count invariant and burst detector on synthetic trains with planted bursts."""
import numpy as np

from agepretext.data.windows import bin_recording
from agepretext.features.potter_handcrafted import compute


def _train(n_bursts, seed=0, dur=600.0, n_el=20):
    rng = np.random.default_rng(seed)
    t = [rng.uniform(0, dur, 3000)]
    c = [rng.integers(0, n_el, 3000)]
    for s in np.linspace(10, dur - 10, n_bursts):          # each burst: 40 spikes on all electrodes within 50 ms
        t.append(s + rng.uniform(0, 0.05, 40 * n_el)); c.append(np.repeat(np.arange(n_el), 40))
    t, c = np.concatenate(t), np.concatenate(c)
    return t, c


def test_bin_counts_match_spikes():
    t, c = _train(5)
    counts, pop, eids = bin_recording(t, c, np.unique(c), bin_ms=200, window_s=120, duration_s=600)
    assert counts.shape == (5, 20, 600) and counts.sum() == (t < 600).sum() and pop.sum() == counts.sum()


def test_burst_detector_counts_planted_bursts():
    for n in (0, 6, 30):
        t, c = _train(n, seed=n)
        f = compute(t, c, duration_s=600)
        assert abs(f["network_burst_rate"] * 10 - n) <= 1, (n, f)
