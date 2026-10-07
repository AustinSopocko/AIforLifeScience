"""RecordingIndex: the single typed table every component reads (WI-03). Shared by both pipelines.

Contract
--------
One row per recording with non-null hierarchy columns:
    recording_id (str, unique, sha1 of source|prep|plate|well|div)
    source ("potter" | "nfa" | "kapucu_rat" | "epameadev" | "epa_mi" | "g2chvc" | "fragilex")
    lab (LABS[source])  prep_id  cluster_id ("<lab>:<prep_id>", the bootstrap / split unit across sources)
    plate_id  well_id  div (int > 0)
    species ("rat" | "mouse" | "human")  region ("cortex" | "hippocampus")  genotype ("wt" | "fmr1_ko")
    electrodes (int)  is_control (bool)
    compound (str | None)  dose_uM (float >= 0)  subset (NFA: "TC" | "NTP"; else None)
    row (str | None)  col (int | None)      # NFA / Kapucu plate layout
    inferential (bool)                      # False for Kapucu hPSC (PLAN §2.2)
    payload (str)                           # source-specific pointer (spike file or feature-table row)
    duration_s (float | NaN)                # recording length; NaN for NFA (feature table) and Kapucu (confirmatory,
                                            # not opened for this); QC (>= 600 s) is applied at binning, not here
Potter: prep = batch, plate = well = culture. Phase 2 (D19): two sources of one lab share a prep when the culture date
coincides (EPAmeadev / EPA-MI), so `cluster_id`, not (source, prep_id), is the unit for pooled splits. `validate()` raises on nulls in hierarchy columns, duplicate
recording_ids, a well under two preps/plates, or is_control != (dose_uM == 0).
Built by scripts/build_index.py -> data/processed/recording_index.parquet. No activity values are stored here.
"""
import hashlib
from dataclasses import dataclass

import pandas as pd

HIER = ["recording_id", "source", "lab", "prep_id", "cluster_id", "plate_id", "well_id", "div", "species", "region",
        "genotype", "electrodes", "is_control", "dose_uM", "inferential", "payload"]
LABS = {"potter": "potter_gatech", "nfa": "epa_shafer", "epameadev": "epa_shafer", "epa_mi": "epa_shafer",
        "kapucu_rat": "kapucu_tuni", "g2chvc": "eglen_grant", "fragilex": "giugliano"}
SPECIES = {"rat", "mouse", "human"}


@dataclass(frozen=True)
class RecordingIndex:
    table: pd.DataFrame

    def validate(self) -> None:
        t = self.table
        if t[HIER].isna().any().any():
            raise ValueError(f"nulls in hierarchy columns: {t[HIER].isna().sum()[lambda s: s > 0].to_dict()}")
        if t.recording_id.duplicated().any():
            raise ValueError(f"duplicate recording_id: {t[t.recording_id.duplicated()].payload.head(3).tolist()}")
        if (t["div"] <= 0).any():
            raise ValueError("non-positive DIV")
        if (t.lab != t.source.map(LABS)).any() or (t.cluster_id != t.lab + ":" + t.prep_id).any():
            raise ValueError("lab / cluster_id inconsistent with source / prep_id")
        if not set(t.species) <= SPECIES:
            raise ValueError(f"unknown species {set(t.species) - SPECIES}")
        g = t.groupby(["lab", "well_id", "plate_id"]).prep_id.nunique()
        if (g > 1).any():
            raise ValueError(f"a well appears under more than one prep: {g[g > 1].index[:5].tolist()}")
        if (t.is_control != (t.dose_uM == 0)).any():
            raise ValueError("is_control inconsistent with dose")

    def sha256(self) -> str:
        t = self.table.sort_values("recording_id")
        return hashlib.sha256(pd.util.hash_pandas_object(t, index=False).values.tobytes()).hexdigest()

    @classmethod
    def load(cls, path: str = "data/processed/recording_index.parquet") -> "RecordingIndex":
        idx = cls(pd.read_parquet(path))
        idx.validate()
        return idx
