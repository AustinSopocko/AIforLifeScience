"""Claim A: cross-lab few-shot transfer engine, Wagenaar -> Kapucu rat (WI-P5). configs/eval/claim_a.yaml.

Contract
--------
- Encoder: the final Wagenaar encoder, frozen; never trained or tuned on Kapucu.
- Folds: leave-one-prep-out over Kapucu rat preps 190617, 250417, 31017 (SplitPurpose.FEWSHOT; the
  labelled pool is the two training preps' wells only).
- Pairs: within each well, (recording at DIV t, target = log1p network-burst rate at DIV t'),
  t' - t in [6, 8]. Training uses all pairs of labelled wells; evaluation uses the held-out prep's
  pairs with t in {21, 24} (common overlap window).
- `run_fewshot(z_kapucu, pairs, index, manifest, cfg) -> Iterator[FewShotEvent]` yields events
  INCREMENTALLY for k in {1, 2, 4, 8, 16, all} x 30 draws x 3 folds (demo shot 2 is built from them).
  Methods at EVERY k, all receiving DIV: ours ([frozen z, DIV] -> ridge), BL-A0, BL-A1, BL-A2
  (same arch from scratch, 5 seeds per draw), BL-A3.
- `summarise(events, prereg) -> dict`: full curve per fold with well-level bootstrap bands, and the
  H-A verdict via eval.verdicts using the inference rule in prereg.yaml (default worst_fold: in EVERY
  held-out prep, UB_well(MAE ours@4) < min baseline point MAE @all). Also reports zero-shot age MAE
  of the Wagenaar age head on Kapucu rat per prep (non-gating).
"""
from dataclasses import dataclass
from typing import Iterator


@dataclass(frozen=True)
class FewShotEvent:
    k: int | str
    method: str
    draw: int
    seed: int
    fold: str
    mae: float


def run_fewshot(z_kapucu, pairs, index, manifest, cfg) -> Iterator[FewShotEvent]:
    raise NotImplementedError("WI-P5")


def summarise(events, prereg: dict) -> dict:
    raise NotImplementedError("WI-P5")
