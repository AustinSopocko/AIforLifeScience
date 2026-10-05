"""Claim A: few-shot transfer engine (WI-11). configs/eval/claim_a.yaml.

Contract
--------
`run_fewshot(task, oof_embeddings, index, manifest, cfg) -> Iterator[FewShotEvent]` yields
events (k, method, draw, fold, auroc) INCREMENTALLY so viz.fewshot_curve can animate live
(demo shot 2). For each k in cfg.k_values and each of cfg.draws_per_k draws: sample k labelled
recordings, class-balanced, ONLY from train-fold preps (SplitPurpose.FEWSHOT); evaluate on
held-out-fold preps. Methods: ours (frozen z + logistic), BL-2, BL-3, BL-4 — all at every k.
`summarise(events, prereg) -> dict` computes the curve with cluster CIs, the ceiling rule, and
the primary non-inferiority test (ours@10 vs best of BL-2/BL-3 @50) via eval.verdicts.
Labels for T1 are compound-dose level (AB < 0.7); recordings of the same compound-dose never
straddle train and test because compounds are nested in preps.
"""
from dataclasses import dataclass
from typing import Iterator


@dataclass(frozen=True)
class FewShotEvent:
    k: int | str
    method: str
    draw: int
    fold: str
    auroc: float


def run_fewshot(task: str, oof_embeddings, index, manifest, cfg) -> Iterator[FewShotEvent]:
    raise NotImplementedError("WI-11")


def summarise(events, prereg: dict) -> dict:
    raise NotImplementedError("WI-11")
