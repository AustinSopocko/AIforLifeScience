"""Prediction heads (WI-P2; shared age-target code).

Contract
--------
- `AgeHead(embedding_dim)`: linear map z -> predicted log(DIV).
- `SpeciesAgeHeads({"rat": AgeHead, ...})`: one head per species. A head shared across species is
  forbidden (PLAN §5.4): constructing one, or applying a rat head to human data as if it predicted
  days, raises. S-1 evaluates the rat axis on hPSC by within-plate rank correlation only.
- `RidgeProbe`: sklearn ridge/logistic wrapper used by Claim A (forecast head) and Claim C (probe).
"""


class AgeHead:
    def __init__(self, embedding_dim: int):
        raise NotImplementedError("WI-P2")


class SpeciesAgeHeads:
    def __init__(self, heads: dict):
        raise NotImplementedError("WI-P2")
