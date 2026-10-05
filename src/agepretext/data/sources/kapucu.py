"""Kapucu et al. 2022 loader (stretch S-3/S-5). CC BY 4.0.

Contract
--------
Reads per-plate `*_spikes.csv` and `expLog.csv`/`noisy_electrodes_*.csv` only. Raw `*.h5` is
forbidden (2.3 TiB) and attempting to open one raises. prep_id = plate (few clusters: results
from this source are labelled qualitative). Species is taken from plate name (hPSC_* -> human,
Rat_* -> rat). Pharmacology recordings (hPSC DIV29, rat DIV22) are tagged with drug and
baseline/treatment phase for S-5.
"""


def load(cfg: dict):
    raise NotImplementedError("S-3")
