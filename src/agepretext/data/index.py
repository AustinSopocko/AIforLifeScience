"""RecordingIndex: the single typed table every component reads (WI-04).

Contract
--------
One row per recording (well x DIV) with non-null columns:
    recording_id (str, unique, stable hash of source|prep|plate|well|div)
    source (str)  prep_id (str)  plate_id (str)  well_id (str)  div (int > 0)
    species ("rat" | "human")  electrodes (int)  is_control (bool)
    compound (str | None)  dose_uM (float >= 0)  subset (e.g. "TC" | "NTP")
    row (str | None)  col (int | None)       # plate layout; needed for Claim B position sensitivity
plus a pointer to the feature table / spike file.

`RecordingIndex.validate()` raises on nulls in hierarchy columns, duplicate recording_ids,
a well appearing under two preps/plates, or is_control != (dose_uM == 0).
Feature values are NOT stored here; they live in source-specific processed tables keyed by
recording_id, so the index can be hashed cheaply.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class RecordingIndex:
    table: "object"  # pandas.DataFrame

    def validate(self) -> None:
        raise NotImplementedError("WI-04")

    def sha256(self) -> str:
        raise NotImplementedError("WI-04")


def build_index(source: str, processed_path: str) -> RecordingIndex:
    raise NotImplementedError("WI-04")
