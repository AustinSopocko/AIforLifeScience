"""Group splits and SplitManifest (WI-04). The only way to split data in this package.

Contract
--------
- `make_group_splits(index, *, unit="prep", purpose, n_folds=None, lockbox_subset=None, seed)`
  sorts unique group IDs, permutes them with `numpy.random.default_rng(seed)`, assigns
  partitions, and returns a frozen `SplitManifest`. Identical inputs -> identical manifest bytes.
- `unit` must be "prep" except for declared sensitivity analyses ("plate"/"dish"), which are
  recorded in the manifest and ledger.
- NFA design (D2): purpose=LOCKBOX puts subset NTP in `lockbox`, TC in `dev`;
  purpose=PRETEXT_CROSSFIT splits dev preps into 6 folds (2 preps each).
- Manifests are written to `splits/*.json` and committed; `--check` re-derives and compares.
- `assert_group_disjoint` is called on construction and on every load.
"""
from dataclasses import dataclass, field

from agepretext.invariants import SplitPurpose


@dataclass(frozen=True)
class SplitManifest:
    purpose: SplitPurpose
    unit: str
    seed: int
    partitions: dict = field(default_factory=dict)   # name -> sorted tuple of group ids
    folds: dict = field(default_factory=dict)        # fold_id -> {"train": (...), "test": (...)}

    def sha256(self) -> str:
        raise NotImplementedError("WI-04")

    def to_json(self, path: str) -> None:
        raise NotImplementedError("WI-04")

    @classmethod
    def from_json(cls, path: str, index=None) -> "SplitManifest":
        raise NotImplementedError("WI-04")


def make_group_splits(index, *, unit: str = "prep", purpose: SplitPurpose, seed: int,
                      n_folds: int | None = None, lockbox_subset: str | None = None) -> SplitManifest:
    raise NotImplementedError("WI-04")
