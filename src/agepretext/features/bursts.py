"""Single-electrode burst detection (stretch S-1).

Contract
--------
`max_interval_bursts(spike_times, params) -> list[(start_s, end_s, n_spikes)]` implements the
maximum-interval method with the parameter values EPA used for the NFA (recorded verbatim in
WI-00 from the meadq source). Pure function; no I/O; deterministic.
"""


def max_interval_bursts(spike_times, params: dict) -> list:
    raise NotImplementedError("S-1")
