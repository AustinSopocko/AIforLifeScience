"""INVARIANT-1 tests (WI-03) on a synthetic prep > plate > well hierarchy, plus the committed manifests."""
import glob

import pandas as pd
import pytest

from agepretext.data.index import RecordingIndex
from agepretext.data.splits import SplitManifest, make_group_splits, make_pooled_splits
from agepretext.invariants import InvariantViolation, SplitPurpose, assert_controls_only, assert_group_disjoint


def _idx():
    rows = [dict(recording_id=f"r{p}{w}{d}", source="s", prep_id=f"p{p}", plate_id=f"pl{p}", well_id=f"w{p}{w}", div=d,
                 species="rat", electrodes=16, is_control=True, dose_uM=0.0, inferential=True, payload="x",
                 compound=None, subset="TC" if p < 4 else "NTP", row=None, col=None)
            for p in range(6) for w in range(3) for d in (5, 7)]
    return RecordingIndex(pd.DataFrame(rows))


def _pooled():
    """Three dev labs (two sources share lab epa_shafer and prep 'd1') + one confirmatory source."""
    spec = [("potter", "potter_gatech", ["1", "2"]), ("epameadev", "epa_shafer", ["d1", "d2"]),
            ("epa_mi", "epa_shafer", ["d1", "d3"]), ("g2chvc", "eglen_grant", ["h1", "h2"]), ("nfa", "epa_shafer", ["n1"])]
    rows = [dict(recording_id=f"{s}{p}{d}", source=s, lab=lab, prep_id=p, cluster_id=f"{lab}:{p}", plate_id=f"{s}{p}",
                 well_id=f"{s}{p}", div=d, species="rat", region="cortex", genotype="wt", electrodes=16, is_control=True,
                 dose_uM=0.0, inferential=True, payload="x")
            for s, lab, preps in spec for p in preps for d in (7, 9)]
    return RecordingIndex(pd.DataFrame(rows))


DEV = ["potter", "epameadev", "epa_mi", "g2chvc"]


def test_pooled_index_validates_and_merges_shared_prep():
    idx = _pooled()
    idx.validate()
    m = make_pooled_splits(idx, name="t", purpose=SplitPurpose.DEV_CONFIRMATORY, seed=1, dev_sources=DEV,
                           confirmatory_sources=["nfa"])
    assert m.partitions["dev"].count("epa_shafer:d1") == 1 and m.partitions["confirmatory"] == ["epa_shafer:n1"]


def test_lolo_one_lab_per_fold():
    m = make_pooled_splits(_pooled(), name="t", purpose=SplitPurpose.LEAVE_ONE_LAB_OUT, seed=1, dev_sources=DEV,
                           confirmatory_sources=["nfa"])
    assert sorted(m.folds) == ["eglen_grant", "epa_shafer", "potter_gatech"]
    assert m.folds["epa_shafer"]["test"] == ["epa_shafer:d1", "epa_shafer:d2", "epa_shafer:d3"]


def test_lolo_mixed_lab_fold_raises():
    idx = _pooled()
    dev = sorted(set(idx.table[idx.table.source.isin(DEV)].cluster_id))
    mixed = ["eglen_grant:h1", "potter_gatech:1"]
    rest = [c for c in dev if c not in mixed]
    m = SplitManifest("t", "pooled", SplitPurpose.LEAVE_ONE_LAB_OUT, "cluster", 0, {"dev": dev},
                      {"a": {"test": mixed, "train": rest}, "b": {"test": rest, "train": mixed}})
    with pytest.raises(InvariantViolation):
        assert_group_disjoint(m, idx)


def test_lab_inconsistent_with_source_raises():
    t = _pooled().table.copy()
    t.loc[t.source == "g2chvc", "lab"] = "giugliano"
    with pytest.raises(ValueError):
        RecordingIndex(t).validate()


def test_crossfit_partitions_preps():
    m = make_group_splits(_idx(), name="t", source="s", unit="prep", purpose=SplitPurpose.PRETEXT_CROSSFIT, seed=1, n_folds=3)
    tests = sorted(p for f in m.folds.values() for p in f["test"])
    assert tests == sorted(f"p{i}" for i in range(6))


def test_shared_prep_raises():
    m = SplitManifest("t", "s", SplitPurpose.LOCKBOX, "prep", 0, {"dev": ["p0", "p1"], "lockbox": ["p1"]}, {})
    with pytest.raises(InvariantViolation):
        assert_group_disjoint(m, _idx())


def test_fold_overlap_raises():
    m = SplitManifest("t", "s", SplitPurpose.PRETEXT_CROSSFIT, "prep", 0, {"all": ["p0", "p1"]},
                      {"f0": {"train": ["p0", "p1"], "test": ["p1"]}, "f1": {"train": ["p1"], "test": ["p0"]}})
    with pytest.raises(InvariantViolation):
        assert_group_disjoint(m, _idx())


def test_non_prep_unit_refused():
    with pytest.raises(ValueError):
        make_group_splits(_idx(), name="t", source="s", unit="well", purpose=SplitPurpose.PRETEXT_CROSSFIT, seed=1, n_folds=2)


def test_identity_probe_purpose_caller_restricted():
    m = SplitManifest("t", "s", SplitPurpose.IDENTITY_PROBE, "prep", 0, {}, {})
    with pytest.raises(InvariantViolation):
        assert_group_disjoint(m, _idx())


def test_treated_rows_in_age_training_raise():
    t = _idx().table.assign(dose_uM=1.0)
    with pytest.raises(InvariantViolation):
        assert_controls_only(t)


def test_committed_manifests_hash_valid():
    paths = glob.glob("splits/*.json")
    assert len(paths) == 6
    for p in paths:
        SplitManifest.from_json(p)
