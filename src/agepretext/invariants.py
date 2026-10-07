"""Splitting and data-use invariants (WI-03). See PLAN.md §5.5 and PREREGISTRATION.md §1.

INVARIANT-1  No culture prep (Potter: dissection batch; Kapucu: culture-date token; NFA: culture date) contributes
             to more than one partition of a split. Cultures, plates, wells and recordings inherit their prep's
             partition. Transforms and model parameters are fit on train preps only.
INVARIANT-2  NFA treated recordings (dose > 0) never enter age training.
INVARIANT-3  NFA lockbox preps are read only by a run with Seal #2 on a clean tree.
INVARIANT-4  (Phase 2) Confirmatory clusters (splits/dev_confirmatory.json: all NFA + Kapucu rat) are read only by the
             single confirmatory run under Seal 2 on a clean tree. Pooled splits are by cluster_id = "<lab>:<prep>";
             a leave-one-lab-out test fold holds exactly one lab, absent from its train fold.

Enforcement contract
--------------------
- `assert_group_disjoint(manifest, index)` raises InvariantViolation if partitions share a prep, a fold's train and
  test share a prep, the union of fold test sets is not the manifest's prep set, or any prep is unknown to the index.
- `assert_controls_only(index_subset)` raises if any row has dose > 0 (NFA age training).
- `SplitPurpose.IDENTITY_PROBE` is the ONLY purpose that shares preps across partitions, with exactly two sanctioned
  split specs (C2 cultures-within-batch, C1 wells-within-plate); `require_purpose_caller` raises unless called from
  `agepretext.eval.identity_probe`.
- Kapucu data never enters encoder training (asserted in train.pretext).
- No public function in the package accepts raw row indices to define a split.
"""
import inspect
from enum import Enum


class InvariantViolation(RuntimeError):
    """Raised on any breach of INVARIANT-1/2/3. CLI maps it to exit code 2."""


class SplitPurpose(Enum):
    PRETEXT_CROSSFIT = "pretext_crossfit"      # grouped by prep, K folds (Potter 4, NFA 6)
    LOCKBOX = "lockbox"                        # NFA: TC dev vs NTP-only lockbox
    FEWSHOT = "fewshot"                        # Kapucu rat leave-one-prep-out; labelled pool = train-fold preps
    IDENTITY_PROBE = "identity_probe"          # sole exception: C2 cultures-within-batch, C1 wells-within-plate
    DEV_CONFIRMATORY = "dev_confirmatory"      # Phase 2: pooled clusters -> dev (tuning) vs confirmatory (one run, Seal 2)
    LEAVE_ONE_LAB_OUT = "leave_one_lab_out"    # Phase 2 primary dev evaluation: one fold per dev lab


def assert_group_disjoint(manifest, index) -> None:
    if manifest.purpose is SplitPurpose.IDENTITY_PROBE:
        require_purpose_caller(manifest.purpose)
        return
    if manifest.unit == "cluster":
        known = set(index.table.cluster_id)
    else:
        known = set(index.table[index.table.source == manifest.source].prep_id)
    parts = list(manifest.partitions.values())
    for i in range(len(parts)):
        for j in range(i + 1, len(parts)):
            if set(parts[i]) & set(parts[j]):
                raise InvariantViolation(f"{manifest.name}: prep in two partitions")
    allp = set().union(*map(set, parts)) if parts else set()
    if allp - known:
        raise InvariantViolation(f"{manifest.name}: unknown preps {sorted(allp - known)}")
    if manifest.folds:
        tests = []
        for f, d in manifest.folds.items():
            if set(d["train"]) & set(d["test"]):
                raise InvariantViolation(f"{manifest.name}/{f}: train and test share a prep")
            tests += d["test"]
        if sorted(tests) != sorted(allp) or len(tests) != len(set(tests)):
            raise InvariantViolation(f"{manifest.name}: fold test sets do not partition the preps")
    if manifest.purpose is SplitPurpose.LEAVE_ONE_LAB_OUT:
        lab = dict(zip(index.table.cluster_id, index.table.lab))
        for f, d in manifest.folds.items():
            test_labs, train_labs = {lab[c] for c in d["test"]}, {lab[c] for c in d["train"]}
            if len(test_labs) != 1 or test_labs & train_labs:
                raise InvariantViolation(f"{manifest.name}/{f}: test fold must be exactly one lab absent from train")


def assert_controls_only(index_subset) -> None:
    if (index_subset.dose_uM > 0).any():
        raise InvariantViolation("treated recordings in age training")


def require_purpose_caller(purpose: SplitPurpose) -> None:
    if purpose is SplitPurpose.IDENTITY_PROBE:
        mods = {inspect.getmodule(f.frame).__name__ for f in inspect.stack()[1:] if inspect.getmodule(f.frame)}
        if "agepretext.eval.identity_probe" not in mods:
            raise InvariantViolation("IDENTITY_PROBE splits may only be built by agepretext.eval.identity_probe")
