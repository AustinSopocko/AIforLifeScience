"""RecordingIndex: the single typed table every component reads (WI-03). Shared by both pipelines.

Contract
--------
One row per recording with non-null hierarchy columns:
    recording_id (str, unique, sha1 of source|prep|plate|well|div)
    source ("potter" | "nfa" | "kapucu_rat")  prep_id  plate_id  well_id  div (int > 0)
    species ("rat" | "human")  electrodes (int)  is_control (bool)
    compound (str | None)  dose_uM (float >= 0)  subset (NFA: "TC" | "NTP"; else None)
    row (str | None)  col (int | None)      # NFA / Kapucu plate layout
    inferential (bool)                      # False for Kapucu hPSC (PLAN §2.2)
    payload (str)                           # source-specific pointer (spike file or feature-table row)
Potter: prep = batch, plate = well = culture. `validate()` raises on nulls in hierarchy columns, duplicate
recording_ids, a well under two preps/plates, or is_control != (dose_uM == 0).
Built by scripts/build_index.py -> data/processed/recording_index.parquet. No activity values are stored here.
"""
import hashlib
from dataclasses import dataclass

import pandas as pd

HIER = ["recording_id", "source", "prep_id", "plate_id", "well_id", "div", "species", "electrodes", "is_control",
        "dose_uM", "inferential", "payload"]


@dataclass(frozen=True)
class RecordingIndex:
    table: pd.DataFrame

    def validate(self) -> None:
        t = self.table
        if t[HIER].isna().any().any():
            raise ValueError(f"nulls in hierarchy columns: {t[HIER].isna().sum()[lambda s: s > 0].to_dict()}")
        if t.recording_id.duplicated().any():
            raise ValueError("duplicate recording_id")
        if (t["div"] <= 0).any():
            raise ValueError("non-positive DIV")
        g = t.groupby(["source", "well_id", "plate_id"]).prep_id.nunique()
        if (g > 1).any():
            raise ValueError("a well appears under more than one prep")
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
