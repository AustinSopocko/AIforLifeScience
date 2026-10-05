"""Group splits and SplitManifest (WI-03). The only way to split data in this package.

Contract
--------
- `make_group_splits(index, *, unit, purpose, seed, n_folds=None, lockbox_subset=None)` sorts
  unique group IDs, permutes them with numpy.random.default_rng(seed), assigns partitions, and
  returns a frozen SplitManifest. Identical inputs -> identical manifest bytes.
- `unit` is "prep" (Potter batch / NFA culture date) for every claim split. "culture"/"plate" only
  for declared sensitivity analyses.
- Potter: purpose=PRETEXT_CROSSFIT, 4 folds x 2 batches -> splits/potter_cv4.json.
- NFA (D2): purpose=LOCKBOX puts subset NTP in `lockbox`, TC in `dev` -> splits/nfa_lockbox.json;
  purpose=PRETEXT_CROSSFIT splits TC preps into 6 folds x 2 -> splits/nfa_dev_cv6.json.
- purpose=IDENTITY_PROBE (Claim C only): within each batch, cultures are split into probe-train /
  probe-test; requires >= 2 cultures per batch (asserted; true for all 8 dense batches).
- Manifests are committed; `agepretext split --check` re-derives and compares byte-for-byte.
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
        raise NotImplementedError("WI-03")

    def to_json(self, path: str) -> None:
        raise NotImplementedError("WI-03")

    @classmethod
    def from_json(cls, path: str, index=None) -> "SplitManifest":
        raise NotImplementedError("WI-03")


def make_group_splits(index, *, unit: str, purpose: SplitPurpose, seed: int,
                      n_folds: int | None = None, lockbox_subset: str | None = None) -> SplitManifest:
    raise NotImplementedError("WI-03")
