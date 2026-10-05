"""Group splits and SplitManifest (WI-03). The only way to split data in this package.

Contract
--------
- `make_group_splits(index, *, source, unit, purpose, seed, n_folds=None, subset=None, dev_subset=None,
  lockbox_subset=None)` sorts unique prep IDs, permutes them with numpy.random.default_rng(seed), and returns a
  frozen SplitManifest. Identical inputs -> identical manifest bytes. `unit` must be "prep".
- Potter: PRETEXT_CROSSFIT, 4 folds x 2 batches -> splits/potter_cv4.json.
- Kapucu rat: FEWSHOT leave-one-prep-out, 3 folds -> splits/kapucu_rat_lopo.json.
- NFA: LOCKBOX dev = every prep present in subset TC; lockbox = NTP preps NOT present in TC (prep 20171011
  appears in both files and is assigned to dev; see ledger) -> splits/nfa_lockbox.json.
  PRETEXT_CROSSFIT over TC dev preps, 6 folds x 2 -> splits/nfa_dev_cv6.json.
- IDENTITY_PROBE splits (Claim C) are built inside eval.identity_probe, never written here.
- Manifests are committed; `agepretext split --check` re-derives and compares byte-for-byte.
"""
import hashlib
import json
from dataclasses import dataclass, field

import numpy as np

from agepretext.invariants import SplitPurpose, assert_group_disjoint


@dataclass(frozen=True)
class SplitManifest:
    name: str
    source: str
    purpose: SplitPurpose
    unit: str
    seed: int
    partitions: dict = field(default_factory=dict)   # name -> sorted list of prep ids
    folds: dict = field(default_factory=dict)        # fold_id -> {"train": [...], "test": [...]}

    def body(self) -> dict:
        return {"name": self.name, "source": self.source, "purpose": self.purpose.value, "unit": self.unit,
                "seed": self.seed, "partitions": self.partitions, "folds": self.folds}

    def sha256(self) -> str:
        return hashlib.sha256(json.dumps(self.body(), sort_keys=True, separators=(",", ":")).encode()).hexdigest()

    def to_json(self) -> str:
        return json.dumps({**self.body(), "sha256": self.sha256()}, sort_keys=True, indent=1) + "\n"

    @classmethod
    def from_json(cls, path: str, index=None) -> "SplitManifest":
        d = json.load(open(path))
        m = cls(d["name"], d["source"], SplitPurpose(d["purpose"]), d["unit"], d["seed"], d["partitions"], d["folds"])
        if m.sha256() != d["sha256"]:
            raise ValueError(f"{path}: sha256 mismatch")
        if index is not None:
            assert_group_disjoint(m, index)
        return m


def make_group_splits(index, *, name: str, source: str, unit: str, purpose: SplitPurpose, seed: int,
                      n_folds: int | None = None, subset: str | None = None, dev_subset: str | None = None,
                      lockbox_subset: str | None = None) -> SplitManifest:
    if unit != "prep":
        raise ValueError("claim splits are by prep only")
    t = index.table[index.table.source == source]
    if purpose is SplitPurpose.LOCKBOX:
        dev = sorted(set(t[t.subset == dev_subset].prep_id))
        lock = sorted(set(t[t.subset == lockbox_subset].prep_id) - set(dev))
        m = SplitManifest(name, source, purpose, unit, seed, {"dev": dev, "lockbox": lock}, {})
    else:
        if subset is not None:
            t = t[t.subset == subset]
        preps = sorted(set(t.prep_id))
        perm = [preps[i] for i in np.random.default_rng(seed).permutation(len(preps))]
        chunks = [sorted(c.tolist()) for c in np.array_split(np.array(perm, dtype=object), n_folds)]
        folds = {f"fold{i}": {"test": c, "train": sorted(set(preps) - set(c))} for i, c in enumerate(chunks)}
        m = SplitManifest(name, source, purpose, unit, seed, {"all": preps}, folds)
    assert_group_disjoint(m, index)
    return m
