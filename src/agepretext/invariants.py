"""Splitting and data-use invariants (WI-04). See PLAN.md §5.6.

INVARIANT-1  No culture prep contributes to more than one partition of a split. Wells, plates and
             recordings inherit their prep's partition. Normalisers/imputers/hyperparameters are
             fit on train preps only.
INVARIANT-2  Treated recordings (dose > 0) never enter pretext (age) training.
INVARIANT-3  Lockbox preps are read only by a run with a sealed protocol on a clean tree.

Enforcement contract
--------------------
- `assert_group_disjoint(manifest, index)` raises `InvariantViolation` if any prep_id appears in
  more than one partition, if any recording's prep is unassigned, or if the manifest's sha256
  does not match its contents. Called by every dataset constructor, trainer, normaliser.fit and
  evaluator before data is touched.
- `assert_controls_only(index_subset)` raises if any row has dose > 0. Called by pretext datasets.
- `SplitPurpose.IDENTITY_PROBE` is the ONLY purpose permitting shared preps/plates across
  partitions (split by DIV within plate). `require_purpose_caller` raises unless the caller
  module is `agepretext.eval.claim_c_probe`; every use is recorded in the ledger row.
- No public function anywhere in the package accepts raw row indices to define a split.
"""
from enum import Enum


class InvariantViolation(RuntimeError):
    """Raised on any breach of INVARIANT-1/2/3. CLI maps it to exit code 2."""


class SplitPurpose(Enum):
    PRETEXT_CROSSFIT = "pretext_crossfit"      # grouped by prep, K folds
    LOCKBOX = "lockbox"                        # dev preps vs lockbox preps
    FEWSHOT = "fewshot"                        # labelled pool from train-fold preps only
    IDENTITY_PROBE = "identity_probe"          # sole exception: split by DIV within plate


def assert_group_disjoint(manifest, index) -> None:
    raise NotImplementedError("WI-04")


def assert_controls_only(index_subset) -> None:
    raise NotImplementedError("WI-04")


def require_purpose_caller(purpose: SplitPurpose) -> None:
    raise NotImplementedError("WI-04")
