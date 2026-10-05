"""Splitting and data-use invariants (WI-03). See PLAN.md §5.5 and PREREGISTRATION.md §1.

INVARIANT-1  No culture prep (Potter: dissection batch; NFA: culture date) contributes to more than
             one partition of a split. Cultures, plates, wells and recordings inherit their prep's
             partition. Transforms and model parameters are fit on train preps only.
INVARIANT-2  NFA treated recordings (dose > 0) never enter age training.
INVARIANT-3  NFA lockbox (NTP) preps are read only by a run with Seal #2 on a clean tree.

Enforcement contract
--------------------
- `assert_group_disjoint(manifest, index)` raises InvariantViolation if a prep appears in >1
  partition, a recording's prep is unassigned, or the manifest sha256 mismatches its contents.
  Called by every dataset constructor, trainer, transform.fit and evaluator before data is touched.
- `assert_controls_only(index_subset)` raises if any row has dose > 0 (NFA age training).
- `SplitPurpose.IDENTITY_PROBE` is the ONLY purpose that shares preps across partitions (Claim C
  splits by culture within batch). `require_purpose_caller` raises unless called from
  `agepretext.eval.claim_c_probe`; each use is recorded in the ledger row.
- No public function in the package accepts raw row indices to define a split.
"""
from enum import Enum


class InvariantViolation(RuntimeError):
    """Raised on any breach of INVARIANT-1/2/3. CLI maps it to exit code 2."""


class SplitPurpose(Enum):
    PRETEXT_CROSSFIT = "pretext_crossfit"      # grouped by prep, K folds (Potter 4, NFA 6)
    LOCKBOX = "lockbox"                        # NFA: TC dev vs NTP lockbox
    FEWSHOT = "fewshot"                        # Claim A labelled pool: train-fold preps only
    IDENTITY_PROBE = "identity_probe"          # sole exception: cultures split within batch


def assert_group_disjoint(manifest, index) -> None:
    raise NotImplementedError("WI-03")


def assert_controls_only(index_subset) -> None:
    raise NotImplementedError("WI-03")


def require_purpose_caller(purpose: SplitPurpose) -> None:
    raise NotImplementedError("WI-03")
