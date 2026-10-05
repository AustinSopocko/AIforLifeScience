"""EPA ontogeny (Cotterill 2016, EPAmeadev) loader (stretch S-1).

Contract
--------
Reads Axion 48-well HDF5 spike files (per-electrode spike times, well dose/treatment fields).
Primary role: validation target for features/canonical.py — recomputed endpoints are compared
with EPA's own published values for the same recordings (acceptance: Spearman >= 0.9 per
endpoint). Secondary role: extra rat pretext data for S-2.
"""


def load(cfg: dict):
    raise NotImplementedError("S-1")
