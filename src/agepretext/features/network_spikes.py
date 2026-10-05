"""Network-spike detection (stretch S-1).

Contract
--------
`detect_network_spikes(spikes_by_electrode, n_active, *, bin_ms, threshold_fraction)` returns
network-spike events (time, peak active-electrode fraction, duration, spikes in event), with the
threshold expressed as a FRACTION of active electrodes so 16- and 60-electrode arrays are
comparable. Default parameters reproduce EPA's absolute threshold on 16-electrode wells.
"""


def detect_network_spikes(spikes_by_electrode, n_active: int, *, bin_ms: int, threshold_fraction: float):
    raise NotImplementedError("S-1")
