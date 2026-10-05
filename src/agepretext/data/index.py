"""RecordingIndex: the single typed table every component reads (WI-03). Shared by both pipelines.

Contract
--------
One row per recording with non-null columns:
    recording_id (str, unique, stable hash of source|prep|plate|well|div)
    source ("potter" | "nfa" | "kapucu")  prep_id  plate_id  well_id  div (int > 0)
    species ("rat" | "human")  electrodes (int)  is_control (bool)
    compound (str | None)  dose_uM (float >= 0)  subset (NFA: "TC" | "NTP"; else None)
    row (str | None)  col (int | None)      # NFA plate layout (Claim B position sensitivity)
    inferential (bool)                      # False for Kapucu (PLAN §2.2)
plus a pointer to the source payload (spike file or feature row). Potter: plate_id = well_id = culture.
`validate()` raises on nulls in hierarchy columns, duplicate recording_ids, a well under two
preps/plates, or is_control != (dose_uM == 0).
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class RecordingIndex:
    table: "object"  # pandas.DataFrame

    def validate(self) -> None:
        raise NotImplementedError("WI-03")

    def sha256(self) -> str:
        raise NotImplementedError("WI-03")


def build_index(source: str, payload) -> RecordingIndex:
    raise NotImplementedError("WI-03")
