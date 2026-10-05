"""Claim A: held-out-batch forecasting few-shot engine (WI-P5). configs/eval/claim_a.yaml.

Contract
--------
Pairs: within each Potter culture, (recording at DIV t, target = log1p network-burst rate at DIV t')
with t' - t in [6, 8], nearest to 7 (alternative target if K3 fires: log mean firing rate at t').
`run_fewshot(oof_z, pairs, index, manifest, cfg) -> Iterator[FewShotEvent]` yields events INCREMENTALLY
(for demo shot 2). For each fold, k in {1,2,4,8,all}, draw in 1..30: sample k labelled CULTURES from the
fold's train batches only (SplitPurpose.FEWSHOT); fit each method; evaluate MAE on all pairs of the
fold's held-out batches. Methods: ours ([frozen out-of-fold z, DIV] -> ridge), BL-A0, BL-A1, BL-A2,
BL-A3 — every method at every k; every method receives DIV.
`summarise(events, prereg) -> dict`: curve with batch-clustered CIs (culture-clustered sensitivity) and
the primary verdict (UB(ours@k=4) < min baseline point MAE @k=all) via eval.verdicts.
"""
from dataclasses import dataclass
from typing import Iterator


@dataclass(frozen=True)
class FewShotEvent:
    k: int | str
    method: str
    draw: int
    fold: str
    mae: float


def run_fewshot(oof_z, pairs, index, manifest, cfg) -> Iterator[FewShotEvent]:
    raise NotImplementedError("WI-P5")


def summarise(events, prereg: dict) -> dict:
    raise NotImplementedError("WI-P5")
