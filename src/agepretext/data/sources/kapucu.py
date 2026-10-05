"""Kapucu et al. 2022 loader. CC BY 4.0.
CORE (WI-K1): rat preps 190617, 250417, 31017 — Claim A cross-lab transfer target.
STRETCH (S-1): hPSC preps — non-inferential demonstration.

Contract
--------
Fetches only `*_spikes.csv`, `*_expLog.csv`, `noisy_electrodes_*.csv` from the GIN raw endpoint for the
scope requested (configs/data/kapucu.yaml `rat_preps_claim_a` / `hpsc_preps_stretch`); opening any
`*.h5` raises. Spike CSV header `Channel,Time`, channel `<well>_<electrode>`.
prep_id = culture-date token from the filename, cross-checked against expLog.csv (A7);
plate_id = MEA plate; well_id = well; species from prefix. Noisy electrodes dropped (not zero-filled).
Rat prep 50618 (single timepoint) is excluded and asserted absent. hPSC rows carry inferential=False.
Post-conditions: verified prep/DIV table asserted; >= 8 wells with spikes at both ends of the
overlap-window pair per rat prep, else K3 fires (alternative target).
Binning is done by data.windows.bin_recording, identical to Potter.
"""


def load(cfg: dict, scope: str = "rat_preps_claim_a"):
    raise NotImplementedError("WI-K1 / S-1")
