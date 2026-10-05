"""Kapucu et al. 2022 loader (stretch S-1: non-inferential human transfer demo). CC BY 4.0.

Contract
--------
Fetches only `*_spikes.csv`, `*_expLog.csv`, `noisy_electrodes_*.csv` from the GIN raw endpoint;
opening any `*.h5` raises (2.3 TiB raw). Spike CSV header `Channel,Time`; channel `<well>_<electrode>`.
prep_id = culture-date token from the filename (e.g. `20517`), plate_id = MEA plate, well_id = well.
Species from prefix (hPSC_ -> human, Rat_ -> rat). The verified prep table in configs/data/kapucu.yaml
is asserted. Results from this source carry `inferential: false` in every ledger row because the
whole hPSC age series is a single prep (PLAN §2.2).
"""


def load(cfg: dict):
    raise NotImplementedError("S-1")
