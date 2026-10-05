"""Prediction heads (WI-08, S-3).

Contract
--------
- `AgeHead(embedding_dim)`: linear map z -> predicted log(DIV).
- Species-specific heads only: `SpeciesAgeHeads({"rat": AgeHead, "human": AgeHead})`. A single
  head shared across species is forbidden (PLAN §5.4) — constructing one raises.
- `ProbeHead`: logistic-regression wrapper used by Claim A and Claim C on frozen z (sklearn).
"""


class AgeHead:
    def __init__(self, embedding_dim: int):
        raise NotImplementedError("WI-08")


class SpeciesAgeHeads:
    def __init__(self, heads: dict):
        raise NotImplementedError("S-3")
