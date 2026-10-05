"""EPA NFA 2018 loader (WI-N1; Pipeline N, Claim B only — never encoder input). Facts verified in PLAN.md §3.

Contract
--------
`load(cfg)` reads ONLY the archive members listed in configs/data/nfa.yaml (any path containing
"DEPRECATED" raises), and returns:
  - processed table: one row per (prep=date, plate=Plate.SN, well, DIV) with the canonical
    feature columns (configs/features/nfa17.yaml), Mutual.Information joined on
    (date, Plate.SN, DIV, well) losslessly, viability (AB/LDH replicate means at the
    compound-dose level), plate layout (row letter, column number), subset in {"TC", "NTP"};
  - a validated RecordingIndex.
Post-conditions (asserted): TC rows == 11,512 and NTP rows == 5,712 unless WI-00 records a
different verified count; every prep has controls at >= 3 DIVs; DIV in {5, 7, 9, 12}.
No transforms are applied here — transforms are fit per fold in features/harmonise.py.
The NFA plate layout (row, col) is kept for the Claim B column-2 position sensitivity analysis.
"""


def load(cfg: dict):
    raise NotImplementedError("WI-N1")
